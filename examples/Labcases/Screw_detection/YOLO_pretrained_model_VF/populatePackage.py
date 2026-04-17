import os

from matplotlib.dviread import Vf

from vfworks.metamodels.specification import *
from vfworks.metamodels.validity_frame import *
from vfworks.metamodels.model_structure import *
from vfworks.metamodels.monitors import *
from vfworks.metamodels.properties import *
from vfworks.clientLibraries.vfclpy.data_digest.digest import remoteExperiments
from vfworks.metamodels.experiment import *
from pathlib import Path
import yaml


#-------------------------REMOTE OR LOCAL DATA------------------------------------------
REMOTE_DATA = False

#---------------------------------------------------------------------------------------
#                     PLACEHOLDER FUNCTION TO POPULATE VF_SCREWDETECTION PACKAGE                      #
#---------------------------------------------------------------------------------------

#-------------------------VALIDITY FRAME------------------------------------------------
VF = ValidityFrame(name="Screw_detection_model_VF", description="Populate Screw_detection_VF package",config="config.yaml")

#-------------------------EXPERIMENTS----------------------------------------
if not REMOTE_DATA:
    # ------ MANUALLY ADD MEASUREMENTS AND ALLOCATE TO EXPERIMENTS ------
    print("Manually adding experiment to "+VF.name)

    local_path = Path(__file__).parent.parent
    conditions_path = local_path / "ScrewDetectionSystem/conditions.yaml"

    with open(conditions_path,"r") as f, open("Experiments/EXP1/annotations_metadata.yaml", "r") as f2:
        conditions = yaml.load(f, Loader=yaml.FullLoader)
        annotations_metadata = yaml.load(f2, Loader=yaml.FullLoader)
    # ---- EXPERIMENT1 ----
    EXP1 = Experiment(name="EXP1",description="Blue light experiment",label="nominal")
    for condition in conditions:
        EXP1.addCondition(ExperimentCondition(name=condition,value=int(conditions[condition])))
    for data in annotations_metadata:
        EXP1.addCondition(ExperimentCondition(name=data,value=annotations_metadata[data]))

    m1 = Measurement(name="images",dataPoints=[],reference="Experiments/EXP1/dataset_metadata.yaml")
    m2 = Measurement(name="labels", dataPoints=[], reference="Experiments/EXP1/dataset_metadata.yaml")

    EXP1.addMeasurement(m1)
    EXP1.addMeasurement(m2)


    VF.addExperiment(EXP1)
else:
    # ------ FETCH REMOTE EXPERIMENTS IN vfWorks BACKEND ------

    print("Fetching remote experiment and add to "+VF.name)

    exp_remote = remoteExperiments(config='config.yaml', VFName=VF.name)
    VF.experiments = exp_remote.loadExperiments(measerementStorage="csv")

#-------------------------SPECIFICATIONS------------------------------------------------
#TODO: add integration with DSL tool to import generated specs by reading specs and generating the correct specification objects in VF. For now, we will manually add specifications to the VF package.
#spec1 = Specification(name="Number of Screws", description="expected amount of screws to be detected", feature="temperature", type=PropertyType.PROPERTY_RANGE, valueMin=-10, valueMax=30, granularity=5)
spec1 = Specification(name="screw_count",description="number of screw instances in the dataset", feature="screws_samples",type=PropertyType.PROPERTY_MIN, valueMin=100)
spec2 = Specification(name="no_screw_count",description="number of screw instances in the dataset", feature="noscrews_samples",type=PropertyType.PROPERTY_MIN, valueMin=100)
spec3 = Specification(name="lighting color red",description="color of the surrounding lighting", feature="colorRed",type=PropertyType.PROPERTY_RANGE, valueMin=0, valueMax=255, granularity=1)
spec4 = Specification(name="lighting color green",description="color of the surrounding lighting", feature="colorGreen",type=PropertyType.PROPERTY_RANGE, valueMin=0, valueMax=255, granularity=5)
spec5 = Specification(name="lighting color blue",description="color of the surrounding lighting", feature="colorBlue",type=PropertyType.PROPERTY_RANGE, valueMin=0, valueMax=255, granularity=1)
spec6 = Specification(name="model confidence", description="", feature="Confidence", type=PropertyType.PROPERTY_MEAN, average=0.70, deviation=10)
spec7 = Specification(name="model accuracy", description="", feature="mAP50-95", type=PropertyType.PROPERTY_MIN, valueMin=0.40)
VF.addSpecification(spec1)
VF.addSpecification(spec2)
VF.addSpecification(spec3)
VF.addSpecification(spec4)
VF.addSpecification(spec5)
VF.addSpecification(spec6)
VF.addSpecification(spec7)
#------------------------------POI------------------------------------------------------
#runtime POIs
poi1 = PropertyofInterest(name="image", description="input image", domain=DomainType.NONE, unit=UnitType.UNIT_none)
poi2 = PropertyofInterest(name="label", description="detections of the model")
poi3 = PropertyofInterest(name="Confidence",description="model output confidence",domain=DomainType.NONE,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_64,min=0,max=1,satisfies=[spec6])
#design time POIs
poi4 = PropertyofInterest(name="accuracy", description="model accuracy", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64,min=0,max=1,satisfies=[spec7])
#influencing factors
if1 = InfluenceFactor(name="Environment Color", description="Environment color", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64,min=0,max=1,satisfies=[spec3,spec4,spec5])
if2 = InfluenceFactor(name="Dataset Sample Count", description="Number of samples in the used dataset", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.INTEGER_16, min=0,max=1,satisfies=[spec1, spec2])
VF.addProperty(poi1)
VF.addProperty(poi2)
VF.addProperty(poi3)
VF.addProperty(poi4)
VF.addProperty(if1)
VF.addProperty(if2)

#-----------------POI LINKING TO EXPERIMENT MEASUREMENTS--------------------------------
VF.assign_poi2measurement(poi=poi1, measurementName="images")
VF.assign_poi2measurement(poi=poi2,measurementName="labels")
#-------------------------MODEL STRUCTURE-----------------------------------------------
IN1 = Inport(name="image", description="input image")
IN1.add_mapping_relation(type="poi",poi=poi1)
OUT1 = Outport(name="detections", unit=UnitType.UNIT_none)
OUT1.add_mapping_relation(type="poi",poi=poi2)
OUT2= Outport(name="certainties", unit=UnitType.UNIT_none)
OUT2.add_mapping_relation(type="poi",poi=poi3)

SM = ModelStructure(name="Screw_detections_model_YOLO", inports=[IN1], outports=[OUT1,OUT2], modelType=ModelType.CONVOLUTIONAL_NEURAL_NETWORK)
VF.addModelStructure(SM)
#-----------------------------PROCESSES-----------------------------------------------

#-----------------------------MONITORS------------------------------------------------
#TODO: add integration with DSL tool to autmatically generate monitors based on specifications 
monitor1 = Monitor(name="Design time environment monitor", description="monitor of the dataset environment", observes=[spec3, spec4, spec5], monitor_time=MonitorTime.DATA_VALIDATION)
monitor2 = Monitor(name="Class sample count monitor", description="monitor the number of screws in the dataset during design time", observes=[spec1, spec2], monitor_time=MonitorTime.DATA_VALIDATION)
monitor3 = Monitor(name="Accuracy monitor", description="monitor the accuracy and recall during the validation phase of design time", observes=[spec7], monitor_time=MonitorTime.MODEL_VALIDATION)
monitor4 = Monitor(name="Confidence monitor", description="monitor the confidence of the model during runtime", observes=[spec6], monitor_time=MonitorTime.RUN_TIME)
monitor5 = Monitor(name="Environment monitor", description="monitor the system environment during runtime", observes=[spec3, spec4, spec5], monitor_time=MonitorTime.RUN_TIME)

VF.addMonitor(monitor1)
VF.addMonitor(monitor2)
VF.addMonitor(monitor3)
VF.addMonitor(monitor4)
VF.addMonitor(monitor5)
#-------------------------------EXPORT VF_BLDC TO TEMPLATE PACKAGE-------------------------------------------
packageName="VF_TORCH"
VF.export(packageName=None)     #VF package is current working directory
VF.neo4j_export()