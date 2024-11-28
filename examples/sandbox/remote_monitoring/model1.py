#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import random
import time

from vfworks.clientLibraries.vfclpy.probe import *
class model(object):
    def __init__(self, name='tbd', description='tbd', verbose=False):
        self._name = name
        self._description = description
        self._verbose = verbose

        # INITIALIZE PROBE(S)
        self.probe = Probe(config="input/config.yaml")

        # --- MODEL INPUTS
        self.IN1 = 0
        self.IN2 = 0

        # --- MODEL OUTPUTS
        self.OUT1 = 0



    def predict(self,IN1,IN2):

        #--------------------REMOTE PROBING------------------------
        self.probe.write(key="poi1",message=IN1)
        self.probe.write(key="poi2", message=IN2)

        #------------------ NORMAL EXECUTION START-----------------
        #1. SET INPUTS
        self.IN1 = IN1
        self.IN2 = IN2
        #2. EXECUTE A PREDICTION (DUMMY)
        _out1 = self.IN1*self.IN2*100
        #3. SET OUTPUTS
        self.OUT1 = _out1

        #----------------- NORMAL EXECUTION END--------------------

        #--------------------REMOTE PROBING------------------------
        self.probe.write(key="poi3", message=-_out1)





if __name__ == "__main__":
    model = model()

    for i in range(0,4,1):
        for j in range(0,120,1):
            model.predict(IN1=i,IN2=j)
            time.sleep(2)


