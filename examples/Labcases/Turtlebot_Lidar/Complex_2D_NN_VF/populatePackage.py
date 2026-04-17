import os

from matplotlib.dviread import Vf
from os.path import exists
from os import mkdir

from vfworks.metamodels.specification import *
from vfworks.metamodels.validity_frame import *
from vfworks.metamodels.model_structure import *
from vfworks.metamodels.monitors import *
from vfworks.metamodels.properties import *
from vfworks.clientLibraries.vfclpy.data_digest.digest import remoteExperiments
from vfworks.metamodels.experiment import *
import yaml
import pandas as pd


#-------------------------REMOTE OR LOCAL DATA------------------------------------------
REMOTE_DATA = False

#---------------------------------------------------------------------------------------
#                     PLACEHOLDER FUNCTION TO POPULATE VF_BLDC PACKAGE                      #
#---------------------------------------------------------------------------------------

#-------------------------VALIDITY FRAME------------------------------------------------
VF = ValidityFrame(name="LIDAR_anomaly_detection_VF", description="Populate LIDAR_anomaly_detection_VF package",config="config.yaml")

#-------------------------EXPERIMENTS----------------------------------------
if not REMOTE_DATA:
    # ------ MANUALLY ADD MEASUREMENTS AND ALLOCATE TO EXPERIMENTS ------
    print("Manually adding experiment to "+VF.name)

    # ---- EXPERIMENT1 ----
    df = pd.read_csv("Sources/run1_lidar_data.csv")
    df_occlusion_data = pd.read_csv("Sources/run1_occlusion.csv")

    EXP1 = Experiment(name="EXP1",description="First experiment",label="nominal")
    EXP1.addCondition(ExperimentCondition(name="experimentTime",value=50))
    EXP1.addCondition(ExperimentCondition(name="velocityCommand",value=100))
    EXP1.addCondition(ExperimentCondition(name="temperature",value=20.0))

    path = "Experiments/" + EXP1.name
    if not exists(path):
        mkdir(path)

    timestamp_file = os.path.join(path, "timestamp.csv")
    df.iloc[:,0].to_csv(timestamp_file, index=False)

    m_timestamp = Measurement(
        name="timestamp",
        dataPoints=[],
        reference=timestamp_file
    )

    distances_file = os.path.join(path, "distances.csv")
    df.iloc[:,1:].to_csv(distances_file, index=False)

    m_liDAR = Measurement(
        name="distances",
        dataPoints=[],
        reference=distances_file
    )

    labels_file = os.path.join(path, "labels.csv")
    labels = df_occlusion_data.iloc[:,1]
    labels_mapped = ["anomaly" if p > 0 else "normal" for p in labels]
    labels_dataframe = pd.DataFrame({"labels": labels_mapped})
    labels_dataframe.to_csv(labels_file, index=False)

    EXP1.addMeasurement(measurement=m_timestamp)
    EXP1.addMeasurement(measurement=m_liDAR)

else:
    # ------ FETCH REMOTE EXPERIMENTS IN vfWorks BACKEND ------

    print("Fetching remote experiment and add to "+VF.name)

    exp_remote = remoteExperiments(config='config.yaml', VFName=VF.name)
    VF.experiments = exp_remote.loadExperiments(measerementStorage="csv")

#-------------------------SPECIFICATIONS------------------------------------------------
spec1 = Specification(name="Environment temperature", description="Required operation temperature", feature="temperature", type=PropertyType.PROPERTY_RANGE, valueMin=-10, valueMax=30, granularity=5, runtimeSpecification=False)
spec2 = Specification(name="operation speed", description="", feature="velocityCommand", type=PropertyType.PROPERTY_MEAN, average=100, deviation=0.5)
spec3 = Specification(name="model accuracy", description="", feature="accuracy", type=PropertyType.PROPERTY_MEAN, average=97, deviation=3)
spec4 = Specification(name="model recall", description="", feature="recall", type=PropertyType.PROPERTY_MEAN, average=100, deviation=0)
spec5 = Specification(name="model precision", description="", feature="precision", type=PropertyType.PROPERTY_MEAN, average=80, deviation=20)
VF.addSpecification(spec1)
VF.addSpecification(spec2)
VF.addSpecification(spec3)
VF.addSpecification(spec4)
VF.addSpecification(spec5)

#------------------------------POI------------------------------------------------------
pois = []
for i in range(360):
    poi = PropertyofInterest(name="Measured_distance",description="Measured distance by a lidar sensor",domain=DomainType.MECHANICAL,unit=UnitType.DISTANCE_m,datatype=DataType.FLOAT_64,min=-50,max=100,satisfies=None)
    pois.append(poi)
    VF.addProperty(poi)

poi3 = PropertyofInterest(name="Label",description="Classification of anomaly",domain=DomainType.NONE,unit=UnitType.UNIT_none,datatype=DataType.INTEGER_8,min=0,max=1,satisfies=None)
poi4 = PropertyofInterest(name="AnomalyScore",description="Classification score of anomaly",domain=DomainType.NONE,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_64,min=-50,max=50,satisfies=None)

VF.addProperty(poi3)
VF.addProperty(poi4)

#-----------------POI LINKING TO EXPERIMENT MEASUREMENTS--------------------------------
for i in range(360):
    VF.assign_poi2measurement(poi=pois[i],measurementName="angle"+str(i))
VF.assign_poi2measurement(poi=poi3,measurementName="labels")

#-------------------------MODEL STRUCTURE-----------------------------------------------
inports = []
for i in range(360):        #TODO: make number of inputs more generic
    name = "angle"+str(i)
    IN = Inport(name=name, unit=UnitType.DISTANCE_m)
    IN.add_mapping_relation(type="poi", poi=pois[i])
    inports.append(IN)

OUT1 = Outport(name="label", unit=UnitType.UNIT_none)
OUT1.add_mapping_relation(type="poi",poi=poi3)
OUT2= Outport(name="anomalyScore", unit=UnitType.UNIT_none)
OUT2.add_mapping_relation(type="poi",poi=poi4)

SM = ModelStructure(name="LiDAR_anomaly_detector_CNN", inports=inports, outports=[OUT1,OUT2], modelType=ModelType.CONVOLUTIONAL_NEURAL_NETWORK)
VF.addModelStructure(SM)
#-----------------------------PROCESSES-----------------------------------------------

#-----------------------------MONITORS------------------------------------------------
monitor1 = Monitor(name="Runtime monitor", description="Online monitoring of the model", observes=[spec2], monitor_type=MonitorType.RUN_TIME)
monitor2 = Monitor(name="design monitor", description="design time monitoring of the model", observes=[spec1], monitor_type=MonitorType.DESIGN_TIME)
monitor3 = Monitor(name="Accuracy monitor", description="monitor the accuracy and recall during the validation phase of design time", observes=[spec3, spec4, spec5], monitor_type=MonitorType.DESIGN_TIME)
VF.addMonitor(monitor1)
VF.addMonitor(monitor2)
VF.addMonitor(monitor3)
#-------------------------------EXPORT VF_BLDC TO TEMPLATE PACKAGE-------------------------------------------
packageName="VF_TORCH"
VF.export(packageName=None)     #VF package is current working directory