import time
import struct
import numpy as np
from examples.Labcases.Turtlebot_Lidar.TurtlebotSystem.TurtlebotExperiments import TurtlebotSystem
from vfworks.clientLibraries.vfclpy.data_forwarders.experiment import *
from vfworks.utils.auxiliary import *

DEPLOYED = False
system = TurtlebotSystem("Turtlebot4 Lidar system", DEPLOYED=DEPLOYED)

experimentTime = 300    #100 sec
cmd = 100               #100% velocity

#STORE EXPERIMENTAL SETUP
EXP1 = Experiment(ID="EXP1",config="config.yaml",label="test1")
EXP1.addCondition(condition="experimentTime",value=experimentTime)
EXP1.addCondition(condition="velocityCommand",value=cmd)
EXP1.addCondition(condition="temperature",value=20.0)


EXP1.logger.info("Starting experiment <"+EXP1.ID+">...")
measurements = system.perform_nominal_experiment(duration=experimentTime)
ranges_table = np.array([m["ranges"] for m in measurements])
label_list = ['normal' for m in measurements]
for i in range(360):
    key = "angle"+str(i)
    measurement = ranges_table[:,i]
    EXP1.addMeasurement(key=key, value=measurement.tolist(), clean=True)
EXP1.addMeasurement(key="labels", value=label_list, clean=True)
EXP1.logger.info("Experiment <" + EXP1.ID + "> finished.")

print("experiment finished: waiting 5 seconds...")
time.sleep(5)

experimentTime = 60
EXP2 = Experiment(ID="EXP2",config="config.yaml",label="test1")
EXP2.addCondition(condition="experimentTime",value=experimentTime)
EXP2.addCondition(condition="velocityCommand",value=cmd)
EXP2.addCondition(condition="temperature",value=30.0)


EXP2.logger.info("Starting experiment <"+EXP2.ID+">...")
measurements = system.perform_random_occluded_experiment(duration=experimentTime)
ranges_table = np.array([m["ranges"] for m in measurements])
label_list = ['anomaly' for m in measurements]
for i in range(360):
    key = "angle"+str(i)
    measurement = ranges_table[:,i]
    EXP2.addMeasurement(key=key, value=measurement.tolist(), clean=True)
EXP2.addMeasurement(key="labels", value=label_list, clean=True)
EXP2.logger.info("Experiment <" + EXP2.ID + "> finished.")
print("experiment finished")