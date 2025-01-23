#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import yaml
import struct
import logging
from vfworks.clientLibraries.vfclpy.data_platform import *

class Experiment(object):
    def __init__(self, config, ID="EXP_001", label="nominal", verbose=False):
        self.ID = ID
        self.config = self.load_config(config)
        self.logger = self.initialize_logger()
        self.data_platform = self._initialize_data_platform()  # Initialize knowledge within the component

        probe_config = self.config.get("validityframe", {})
        self.base_key = f"{probe_config.get("name", "base")}:Experiments"
        self.experiment_key = self.base_key+":"+ID
        self.conditions_key = self.experiment_key+":"+"Conditions"
        self.measurements_key = self.experiment_key + ":" + "Measurements"

        # set experiment label
        self.addLabel(label=label)



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
        self.logger.info(f"Initializing the data platform.")
        return DataPlatform(config=self.config['dp_config'])

    #-------------------------EXTERNAL FUNCTIONS-------------------------------------
    def addCondition(self,condition,value):
        """Add a condition to the experiment description"""
        _condition_key = self.conditions_key + ":" + condition
        try:
            self.data_platform.write(_condition_key, value)
            self.logger.info("Condition <" + condition + "> with value " + str(value) + " written to vfWorks backend!")
        except:
            self.logger.warning("Condition <" + condition + "> with value " + str(value)+ " failed to write to vfWorks backend!")

    def addLabel(self,label="nominal"):
        _label_key = self.experiment_key + ":" + "label"
        try:
            self.data_platform.write(_label_key, label)
            self.logger.info("Label <" + label + "> written to vfWorks backend!")
        except:
            self.logger.warning("Label <" + label + "> failed to write to vfWorks backend!")

    def addMeasurement(self,key,value,batch=True,clean=True):
        _measurement_key = self.measurements_key + ":" + key
        if clean:
            self.data_platform.delete(_measurement_key)
        if batch:
            value.reverse()
            for point in value:
                self.data_platform.write_storage(_measurement_key, point)       #TODO: add batch writer to data_platform!
        else:
            self.data_platform.write_storage(_measurement_key, value)

    def getMeasurement(self,key):
        _measurement_key = self.measurements_key + ":" + key
        try:
            values = self.data_platform.read_list(key=_measurement_key,all=True)
            # TODO: HACKED byte to float - THIS NEEDS TO BE MORE GENERIC!
            for i in range(0,len(values),1):
                values[i] = float(values[i])

            self.logger.info("Reading values for measurement <" + key + "> from vfWorks backend!")
            return values
        except:
            self.logger.warning("Failed to read values for measurement <" + key + "> from vfWorks backend!")



