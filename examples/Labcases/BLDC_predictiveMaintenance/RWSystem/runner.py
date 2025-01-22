from D5065experiments import RWSystem_BLDC_D5065
from vfworks.clientLibraries.vfclpy.data_forwarders.experiment import *

DEPLOYED=False
system = RWSystem_BLDC_D5065(name="D5065 system under study",INITIALIZED=True, CALIBRATED=True,monitorPeriod=0.1,DEPLOYED=DEPLOYED)

#-----------------------------------------------------------------------------------------------------------------------
#                                   VF_BLDC reference
#-----------------------------------------------------------------------------------------------------------------------
# VF_BLDC reference can be found in config.yaml
#-----------------------------------------------------------------------------------------------------------------------
#                                   EXPERIMENT 1
#-----------------------------------------------------------------------------------------------------------------------
experimentTime = 100    #100 sec
cmd = 100               #100% velocity

#STORE EXPERIMENTAL SETUP
EXP1 = Experiment(ID="EXP1",config="config.yaml",label="nominal")
EXP1.addCondition(condition="experimentTime",value=experimentTime)
EXP1.addCondition(condition="velocityCommand",value=cmd)
EXP1.addCondition(condition="temperature",value=20.0)

if DEPLOYED:
    measurements = system.experiment_constant_velocity(experimentTime=experimentTime,percentage=cmd)        #measurements [timestamp,power,rpm,busVoltage]
    EXP1.addMeasurement(key="timestamp",value=measurements[0],clean=True)
    EXP1.addMeasurement(key="power", value=measurements[1],clean=True)
    EXP1.addMeasurement(key="rpm", value=measurements[2],clean=True)
    EXP1.addMeasurement(key="busVoltage", value=measurements[3],clean=True)
else:
    #ADD DUMMY DATA!
    EXP1.addMeasurement(key="timestamp", value=[0.1,0.2,0.3,0.4,0.5,0.6],clean=True)
    EXP1.addMeasurement(key="power", value=[0.8,0.8,1.5,1.6,0.6,0.8],clean=True)
    EXP1.addMeasurement(key="rpm", value=[360.0,360.0,345.0,340.0,375.0,360.0],clean=True)
    EXP1.addMeasurement(key="busVoltage", value=[12.0,12.5,12.5,12.5,12.0,12.0],clean=True)
