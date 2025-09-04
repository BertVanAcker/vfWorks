import time
import struct
import numpy as np
from examples.Labcases.Turtlebot_Lidar.TurtlebotSystem.TurtlebotExperiments import TurtlebotSystem
from vfworks.clientLibraries.vfclpy.data_forwarders.experiment import *
from vfworks.utils.auxiliary import *

DEPLOYED = False
system = TurtlebotSystem("Turtlebot4 Lidar system", DEPLOYED=DEPLOYED)

experimentTime = 60    #100 sec
cmd = 100               #100% velocity

#STORE EXPERIMENTAL SETUP
EXP1 = Experiment(ID="EXP1",config="config.yaml",label="test1")
EXP1.addCondition(condition="experimentTime",value=experimentTime)
EXP1.addCondition(condition="velocityCommand",value=cmd)
EXP1.addCondition(condition="temperature",value=20.0)


EXP1.logger.info("Starting experiment <"+EXP1.ID+">...")
measurements = system.perform_experiment(duration=experimentTime)
ranges_table = np.array([m["ranges"] for m in measurements])
for i in range(360):
    key = "angle"+str(i)
    measurement = ranges_table[:,i]
    EXP1.addMeasurement(key=key, value=measurement.tolist(), clean=True)
EXP1.logger.info("Experiment <" + EXP1.ID + "> finished.")