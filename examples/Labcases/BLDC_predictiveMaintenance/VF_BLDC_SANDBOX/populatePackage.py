#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import os

from vfworks.metamodels.specification import *
from vfworks.metamodels.validity_frame import *
from vfworks.metamodels.model_structure import *
from vfworks.metamodels.monitors import *
from vfworks.metamodels.properties import *
from vfworks.clientLibraries.vfclpy.data_digest.digest import remoteExperiments
from vfworks.metamodels.experiment import *
import yaml

#-------------------------REMOTE OR LOCAL DATA------------------------------------------
REMOTE_DATA = True

#---------------------------------------------------------------------------------------
#                     PLACEHOLDER FUNCTION TO POPULATE VF_BLDC PACKAGE                      #
#---------------------------------------------------------------------------------------

#-------------------------VALIDITY FRAME------------------------------------------------
VF = ValidityFrame(name="VF_BLDC_SANDBOX", description="Populate VF_BLDC_SANDBOX package",config="config.yaml")

#-------------------------EXPERIMENTS----------------------------------------
if not REMOTE_DATA:
    # ------ MANUALLY ADD MEASUREMENTS AND ALLOCATE TO EXPERIMENTS ------
    print("Manually adding experiment to "+VF.name)

    # ---- EXPERIMENT1 ----
    EXP1 = Experiment(name="EXP1",description="First experiment",label="nominal")
    EXP1.addCondition(ExperimentCondition(name="experimentTime",value=50))
    EXP1.addCondition(ExperimentCondition(name="velocityCommand",value=100))
    EXP1.addCondition(ExperimentCondition(name="temperature",value=20.0))
    m1 = Measurement(name="timestamp",dataPoints=[],reference="Experiments/EXP1/timestamp.csv")
    m2 = Measurement(name="power",dataPoints=[],reference="Experiments/EXP1/power.csv")
    EXP1.addMeasurement(measurement=m1)
    EXP1.addMeasurement(measurement=m2)

    # ---- EXPERIMENT2 ----
    EXP2 = Experiment(name="EXP2",description="Second experiment",label="anomaly")
    EXP2.addCondition(ExperimentCondition(name="experimentTime",value=50))
    EXP2.addCondition(ExperimentCondition(name="velocityCommand",value=100))
    EXP2.addCondition(ExperimentCondition(name="temperature",value=20.0))
    m3 = Measurement(name="timestamp",dataPoints=[],reference="Experiments/EXP2/timestamp.csv")
    m4 = Measurement(name="power",dataPoints=[],reference="Experiments/EXP2/power.csv")
    EXP2.addMeasurement(measurement=m3)
    EXP2.addMeasurement(measurement=m4)

    VF.addExperiment(EXP1)
    VF.addExperiment(EXP2)

else:
    # ------ FETCH REMOTE EXPERIMENTS IN vfWorks BACKEND ------

    print("Fetching remote experiment and add to "+VF.name)

    exp_remote = remoteExperiments(config='config.yaml', VFName=VF.name)
    VF.experiments = exp_remote.loadExperiments(measerementStorage="csv")


#-------------------------SPECIFICATIONS------------------------------------------------
spec1 = Specification(name="Environment temperature", description="Required operation temperature", feature="temperature", type=PropertyType.PROPERTY_RANGE, valueMin=-10, valueMax=30, granularity=5, runtimeSpecification=False)
spec2 = Specification(name="operation speed", description="", feature="velocityCommand", type=PropertyType.PROPERTY_MEAN, average=100, deviation=0.5)
VF.addSpecification(spec1)
VF.addSpecification(spec2)

#------------------------------POI------------------------------------------------------
poi1 = PropertyofInterest(name="Power",description="Electrical power of the BLDC motor",domain=DomainType.ELECTRICAL,unit=UnitType.Power_Watt,datatype=DataType.FLOAT_64,min=-50,max=100,satisfies=None)
poi2 = PropertyofInterest(name="rpm",description="Rotational speed of the BLDC motor",domain=DomainType.MECHANICAL,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_64,min=0,max=3000,satisfies=None)
poi3 = PropertyofInterest(name="Anomaly",description="Classification of anomaly",domain=DomainType.NONE,unit=UnitType.UNIT_none,datatype=DataType.INTEGER_8,min=0,max=1,satisfies=None)
poi4 = PropertyofInterest(name="AnomalyScore",description="Classification score of anomaly",domain=DomainType.NONE,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_64,min=-50,max=50,satisfies=None)

VF.addProperty(poi1)
VF.addProperty(poi2)
VF.addProperty(poi3)
VF.addProperty(poi4)

#-----------------POI LINKING TO EXPERIMENT MEASUREMENTS--------------------------------
VF.assign_poi2measurement(poi=poi1,measurementName="power")
VF.assign_poi2measurement(poi=poi2,measurementName="rpm")

#-------------------------MODEL STRUCTURE-----------------------------------------------
IN1 = Inport(name="power", unit=UnitType.Power_Watt)
IN1.add_mapping_relation(type="poi",poi=poi1)
IN2 = Inport(name="rpm", unit=UnitType.UNIT_none)
IN2.add_mapping_relation(type="poi",poi=poi2)

OUT1 = Outport(name="anomaly", unit=UnitType.UNIT_none)
OUT1.add_mapping_relation(type="poi",poi=poi3)
OUT2= Outport(name="anomalyScore", unit=UnitType.UNIT_none)
OUT2.add_mapping_relation(type="poi",poi=poi4)

SM = ModelStructure(name="anomalyDetector_1D", inports=[IN1], outports=[OUT1,OUT2], modelType=ModelType.ISOLATIONFOREST)
SM2 = ModelStructure(name="anomalyDetector_2D", inports=[IN1, IN2], outports=[OUT1,OUT2], modelType=ModelType.ISOLATIONFOREST, redundancy=6)
VF.addModelStructure(SM)
VF.addModelStructure(SM2)
#-----------------------------PROCESSES-----------------------------------------------

#-----------------------------MONITORS------------------------------------------------
monitor1 = Monitor(name="Runtime monitor", description="Online monitoring of the model", observes=[spec2], monitor_type=MonitorType.RUN_TIME)
monitor2 = Monitor(name="design monitor", description="design time monitoring of the model", observes=[spec1], monitor_type=MonitorType.DESIGN_TIME)
VF.addMonitor(monitor1)
VF.addMonitor(monitor2)
#-------------------------------EXPORT VF_BLDC TO TEMPLATE PACKAGE-------------------------------------------
packageName="VF_TORCH"
VF.export(packageName=None)     #VF package is current working directory


