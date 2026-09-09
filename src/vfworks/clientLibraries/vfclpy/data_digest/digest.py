#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import yaml
import os
from os import mkdir
from os.path import exists, dirname, join, isfile
import logging
from vfworks.clientLibraries.vfclpy.data_platform import *
from vfworks.metamodels.experiment import *
from vfworks.utils.auxiliary import *

class remoteExperiments(object):
    def __init__(self, config,VFName,verbose=False):
        self.config = self.load_config(config)
        self.logger = self.initialize_logger()
        self.data_platform = self._initialize_data_platform()  # Initialize knowledge within the component

        probe_config = VFName
        self.base_key = f"{VFName}:Experiments"

        #----------------INSTANTIATE EXPERIMENTS---------------------
        self.experiments = []


    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def initialize_logger(self):
        """Initialize the logger (same as before)."""
        log_config = self.config.get("logging", {})
        logger = logging.getLogger(self.__class__.__name__)
        log_level = log_config.get("level", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_file = log_config.get("file", None)

        formatter = logging.Formatter(log_format)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def _initialize_data_platform(self):
        """Initialize the data plaform object based on the config."""
        #self.logger.info(f"Initializing the data platform.")
        return DataPlatform(config=self.config['dp_config'])

    def loadExperiments(self, measerementStorage = "full",timestamped=False):             # full => both in the datapoints and csv | csv => store only csv file
        timestamp = None
        experimentIDs = self._getExperimentIDs()

        for experiment in experimentIDs:
            # instantiate an empty experiment
            label = self.data_platform.read(self.base_key + ":" + experiment + ":label")
            exp = Experiment(name=experiment, description="tbd", label=label)
            # fetch all conditions
            conditionIDs = self._getConditionIDs(experimentID=experiment)
            for condition in conditionIDs:
                key = self.base_key + ":" + experiment + ":Conditions:" + condition
                value = self.data_platform.read(key)
                exp.addCondition(ExperimentCondition(name=condition, value=value))
            measurementIDs = self._getMeasurementIDs(experimentID=experiment)
            for measurement in measurementIDs:
                key = self.base_key + ":" + experiment + ":Measurements:" + measurement
                dataPoints=self.data_platform.read_list(key,all=True)
                if measurement!= "timestamp":
                    reference = "Experiments/" + experiment +"/"+ measurement+".csv"
                    if measerementStorage=="full":
                        exp.addMeasurement(Measurement(name=measurement,dataPoints=dataPoints,reference=reference))
                    else:
                        exp.addMeasurement(Measurement(name=measurement, dataPoints=[], reference=reference))
                else:
                    key = self.base_key + ":" + experiment + ":Measurements:" + measurement
                    timestamp = self.data_platform.read_list(key, all=True)

            for measurement in measurementIDs:
                key = self.base_key + ":" + experiment + ":Measurements:" + measurement
                dataPoints = self.data_platform.read_list(key, all=True)
                #CREATE FOLDER IF NON EXISTING
                path = "Experiments/" + experiment
                if not exists(path):
                    mkdir(path)

                reference = path + "/" + measurement + ".csv"
                if timestamped:
                    save_lists_to_csv(reference, timestamp, dataPoints,headers=['timestamp', measurement])
                else:
                    save_lists_to_csv(reference, dataPoints, headers=[measurement])
            #TODO: STORE THE MEASUREMENTS AS FILES AND REFERENCE!
            self.experiments.append(exp)
            self.logger.info(msg="experiment added to the VF frame, GUID {"+exp.GUID+"}")
        return self.experiments


    def _getExperimentIDs(self):
        """Get the experiment from the vfWorks backend"""
        unique_values = set()
        keys = self.data_platform.getKeys(self.base_key+":*")
        for key in keys:
            try:
                value = key.split('Experiments:')[1].split(":")[0]
                unique_values.add(value)
            except IndexError:
                print(f"Skipping key due to formatting issue: {key}")


        return  list(unique_values)

    def _getConditionIDs(self, experimentID):
        """Get the experiment from the vfWorks backend"""
        unique_values = set()
        keys = self.data_platform.getKeys(self.base_key+":"+experimentID+":Conditions:*")
        for key in keys:
            try:
                value = key.split('Conditions:')[1]
                unique_values.add(value)
            except IndexError:
                print(f"Skipping key due to formatting issue: {key}")
        return  list(unique_values)

    def _getMeasurementIDs(self, experimentID):
        """Get the experiment from the vfWorks backend"""
        unique_values = set()
        keys = self.data_platform.getKeys(self.base_key+":"+experimentID+":Measurements:*")
        for key in keys:
            try:
                value = key.split('Measurements:')[1]
                unique_values.add(value)
            except IndexError:
                print(f"Skipping key due to formatting issue: {key}")
        return  list(unique_values)






