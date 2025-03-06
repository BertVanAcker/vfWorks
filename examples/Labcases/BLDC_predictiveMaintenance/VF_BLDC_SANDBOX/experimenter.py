#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import time
import struct
from examples.Labcases.BLDC_predictiveMaintenance.RWSystem.D5065experiments import RWSystem_BLDC_D5065
from vfworks.clientLibraries.vfclpy.data_forwarders.experiment import *
from vfworks.utils.auxiliary import *

DEPLOYED=True
system = RWSystem_BLDC_D5065(name="D5065 system under study",INITIALIZED=True, CALIBRATED=False,monitorPeriod=0.1,DEPLOYED=DEPLOYED)

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
    EXP1.logger.info("Starting experiment <"+EXP1.ID+">...")
    measurements = system.experiment_constant_velocity(experimentTime=experimentTime,percentage=cmd)        #measurements [timestamp,power,rpm,busVoltage]
    EXP1.addMeasurement(key="timestamp",value=measurements[0],clean=True)
    EXP1.addMeasurement(key="power", value=measurements[1],clean=True)
    EXP1.addMeasurement(key="rpm", value=measurements[2],clean=True)
    EXP1.addMeasurement(key="busVoltage", value=measurements[3],clean=True)
    EXP1.logger.info("Experiment <" + EXP1.ID + "> finished.")

time.sleep(2)
#-----------------------------------------------------------------------------------------------------------------------
#                                   EXPERIMENT 2
#-----------------------------------------------------------------------------------------------------------------------
experimentTime = 100    #100 sec
cmd = 100               #100% velocity

#STORE EXPERIMENTAL SETUP
EXP2 = Experiment(ID="EXP2",config="config.yaml",label="anomaly")
EXP2.addCondition(condition="experimentTime",value=experimentTime)
EXP2.addCondition(condition="velocityCommand",value=cmd)
EXP2.addCondition(condition="temperature",value=20.0)

if DEPLOYED:
    EXP2.logger.info("Starting experiment <" + EXP2.ID + ">...")
    measurements = system.experiment_constant_velocity(experimentTime=experimentTime,percentage=cmd)        #measurements [timestamp,power,rpm,busVoltage]
    EXP2.addMeasurement(key="timestamp",value=measurements[0],clean=True)
    EXP2.addMeasurement(key="power", value=measurements[1],clean=True)
    EXP2.addMeasurement(key="rpm", value=measurements[2],clean=True)
    EXP2.addMeasurement(key="busVoltage", value=measurements[3],clean=True)
    EXP1.logger.info("Experiment <" + EXP2.ID + "> finished.")

