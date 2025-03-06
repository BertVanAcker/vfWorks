#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from examples.Labcases.BLDC_predictiveMaintenance.RWSystem.D5065experiments import RWSystem_BLDC_D5065
from vfworks.metamodels.validity_frame import ValidityFrame
from vfworks.utils.model.modelLoader import ModelLoader

DEPLOYED=True
SERIAL=True

system = RWSystem_BLDC_D5065(name="D5065 system under study",INITIALIZED=True, CALIBRATED=True,monitorPeriod=0.5,DEPLOYED=DEPLOYED,SERIAL=SERIAL)

#-----------------------------------------------------------------------------------------------------------------------------------
#   LOAD ANOMALY DETECTOR FROM VF
#-----------------------------------------------------------------------------------------------------------------------------------
VF = ValidityFrame(name="VF_TORCH", description="Populate VF_BLDC package",config="config.yaml",loadExistingVF=True,VFPackage="")
VF.setActiveModelStructure(GUID="efb0eabb-185c-4bcf-8e15-2255ae34506c")

_model_loader = ModelLoader(name="VF_model_loader",validityFrame=VF)
_model_loader.loadModel(type="torch")
model = _model_loader.model
model.n_features_in_ = 1

#-----------------------------------------------------------------------------------------------------------------------------------
#   ASSIGN ANOMALY DETECTOR TO RW SYSTEM
#-----------------------------------------------------------------------------------------------------------------------------------
system.loadAnomalyDetectionModel(model=model,type="torch")

#-----------------------------------------------------------------------------------------------------------------------------------
#   SPECIFY ANOMALY DETECTOR FUNCTIONALITY, THREADED EXECUTION
#-----------------------------------------------------------------------------------------------------------------------------------
def anomalyDetection(self):
    # input formatting
    _in1 = [[self.power]]
    # model use
    _prediction = model.predict(_in1)
    # output formatting
    anomaly = 1 if _prediction[0] == -1 else 0
    label = "Anomaly" if _prediction[0] == -1 else "Normal"
    anomaly_score = model.decision_function(_in1)  # Higher = normal, Lower = anomaly
    certainty = 1

    print("Power usage:" + self.power.__str__() + " prediction:" + label + " score: " + anomaly_score.__str__())

    #remote monitoring
    data = f"{anomaly},{certainty}\n"
    self.serialPort.write(data.encode())


system.anomalyDetection= anomalyDetection

#----------------------------------------------------------------------------------------------------------------------------------
#   Execute an experiment to demonstrate the anomaly detector case
#----------------------------------------------------------------------------------------------------------------------------------

measurements = system.experiment_constant_velocity(experimentTime=60,percentage=100)