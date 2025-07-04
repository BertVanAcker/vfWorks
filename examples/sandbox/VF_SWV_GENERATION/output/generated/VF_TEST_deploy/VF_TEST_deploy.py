#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from flexCommunicator.clientLibraries.flcpy.flexNode import flexNode
from flexCommunicator.clientLibraries.flcpy.validityFrame.runtimeMonitor import *
from flexCommunicator.clientLibraries.flcpy.utils.constants import *
import time

#<!-- cc_include START--!>
# user includes here
#<!-- cc_include END--!>

#<!-- cc_code START--!>
# user code here
#<!-- cc_code END--!>

class VF_TEST_deploy(flexNode):

    def __init__(self, config='config.yaml',loaded_config=False,communicationMatrix=None,verbose=True):
        super().__init__(config=config,loaded_config=loaded_config,communicationMatrix=communicationMatrix,verbose=verbose)

        self._name = "VF_TEST"
        self.logger.info("VF_TEST instantiated")
        #periodic function
        self.timer = self.create_timer(timer_period=1, callback=self.execute,autostart=True)

        # instantiate runtime monitors
        self.velocityCommand = runtimeMonitor(name="velocityCommand",initial_value=1.0,type=VF_RUNTIME_MONITOR_TYPE.LOCAL,bound=[0.0,10.0])
        self.register_runtime_monitor(self.velocityCommand)

        # SET STATUS TO INITIALIZED AND RUNNING
        self.application_status.set(value=APPLICATION_STATUS.INITIALIZING)
        time.sleep(1)
        self.application_status.set(value=APPLICATION_STATUS.RUNNING)


    def execute(self):
        #<!-- cc_code START--!>
        _velocityCommand = self.velocityCommand.get()

        # user code here

        self.velocityCommand.set(10.0)
        #<!-- cc_code END--!>


    def register_callbacks(self):
        # NO CALLBACKS
        return -1

if __name__ == '__main__':
    node = VF_TEST_deploy(config='config.yaml')
    node.register_callbacks()
    node.start()
    try:
       while True:
           time.sleep(1)
    except:
       exit()