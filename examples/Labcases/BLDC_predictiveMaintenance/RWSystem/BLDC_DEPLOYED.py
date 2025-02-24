from D5065experiments import RWSystem_BLDC_D5065
from pycaret.anomaly import *
import pandas as pd
import tkinter as tk

DEPLOYED=True

#TODO: pycaret only works with python 3.9-3.11

system = RWSystem_BLDC_D5065(name="D5065 system under study",INITIALIZED=True, CALIBRATED=True,monitorPeriod=0.5,DEPLOYED=DEPLOYED)

#-----------------------------------------------------------------------------------------------------------------------------------
#   PREPARE ANOMALY DETECTOR TODO: LOAD FROM VF!
#-----------------------------------------------------------------------------------------------------------------------------------
system.loadAnomalyDetectionModel(model="output/model_knn")  #TODO: LOAD FROM VF HERE

def anomalyDetection(self):
    data = [[self.timestamp, self.power]]
    df = pd.DataFrame(data, columns=['timestamp', 'power'])
    prediction = predict_model(self.model, data=df)
    anomaly = prediction["Anomaly"].values[0]
    print(anomaly)

system.anomalyDetection= anomalyDetection

#----------------------------------------------------------------------------------------------------------------------------------
#   Deploy BLDC controller with anomaly detector
#----------------------------------------------------------------------------------------------------------------------------------

measurements = system.experiment_constant_velocity(experimentTime=60,percentage=100)