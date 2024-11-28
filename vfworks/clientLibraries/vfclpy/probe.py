#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import yaml
import logging
from vfworks.clientLibraries.vfclpy.data_platform import *
class Probe(object):
    def __init__(self, config, verbose=False):
        self.config = self.load_config(config)
        self.logger = self.initialize_logger()
        self.data_platform = self.initialize_data_platform()  # Initialize knowledge within the component


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


    def initialize_data_platform(self):
        """Initialize the data plaform object based on the config."""
        self.logger.info(f"Initializing the data platform.")
        return DataPlatform(config=self.config['dp_config'])

    def write(self, key, message = True):
        """Write data on the data platform."""
        if self.data_platform:
            self.logger.info("Probing property (ID:"+key+") with value "+ str(message))
            (self.data_platform.write(key, message))
        else:
            self.logger.warning("Probe is not set for writing")