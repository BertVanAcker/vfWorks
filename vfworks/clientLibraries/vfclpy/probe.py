#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import yaml
from vfworks.clientLibraries.vfclpy.data_platform import *
class Probe(object):
    def __init__(self, config, verbose=False):
        self.config = self.load_config(config)
        self.data_platform = self.initialize_data_platform()  # Initialize knowledge within the component


    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def initialize_data_platform(self):
        """Initialize the data plaform object based on the config."""
        return DataPlatform(config=self.config['dp_config'])

    def write(self, key, message = True):
        """Write data on the data platform."""
        if self.data_platform:
            (self.data_platform.write(key, message))
        else:
            print("Probe is not set for writing.")