import numpy as np

from examples.Labcases.Turtlebot_Lidar.TurtlebotSystem.TurtlebotExperiments import TurtlebotSystem
from vfworks.metamodels.validity_frame import ValidityFrame
from vfworks.utils.model.modelLoader import ModelLoader

DEPLOYED=True
system = TurtlebotSystem("Turtlebot4 Lidar system", DEPLOYED=DEPLOYED)

#-----------------------------------------------------------------------------------------------------------------------------------
#   LOAD ANOMALY DETECTOR FROM VF
#-----------------------------------------------------------------------------------------------------------------------------------
VF = ValidityFrame(name="LIDAR_anomaly_detection_VF", description="validity frame for the Turtlebot4 LIDAR occlusion detector",config="config.yaml",loadExistingVF=True,VFPackage="")
VF.setActiveModelStructure(name="anomalyDetector_1D")

_model_loader = ModelLoader(name="VF_model_loader",validityFrame=VF)
_model_loader.loadModel(type="torch")
models = _model_loader.models
for model in models:
    model.n_features_in_ = 360
    system.loadAnomalyDetectionModel(model=model, type="torch")
#-----------------------------------------------------------------------------------------------------------------------------------
#   SPECIFY ANOMALY DETECTOR FUNCTIONALITY, THREADED EXECUTION
#-----------------------------------------------------------------------------------------------------------------------------------
def anomalyDetection(self):
    # model use
    predictions = []
    anomaly_scores = []
    processed_measurement = np.where(np.isinf(self.measurement), 50, self.measurement)
    for model in self.models:
        predictions.append(model.predict([processed_measurement])[0])
        anomaly_scores.append(model.decision_function([processed_measurement])[0]) # Higher = normal, Lower = anomaly

    # output formatting
    anomaly = 1 if predictions.count(-1) >= len(predictions)/2 else 0
    label = "Anomaly" if predictions.count(-1) >= len(predictions)/2 else "Normal"

    score = sum(anomaly_scores)/len(anomaly_scores)

    if label == "Normal":
        certainty = predictions.count(1) / len(predictions)
    else:
        certainty = predictions.count(-1) / len(predictions)
    print(" prediction:" + label)
    certainty_rounded = float(round(certainty,2))

system.anomalyDetection= anomalyDetection
#----------------------------------------------------------------------------------------------------------------------------------
#   Execute an experiment to demonstrate the anomaly detector case
#----------------------------------------------------------------------------------------------------------------------------------

measurements = system.perform_nominal_experiment(duration=20)