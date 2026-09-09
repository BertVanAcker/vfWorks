#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.metamodels.common import *
from vfworks.utils.constants import *

class Process(baseElement):

    def __init__(self, name='tbd', description='tbd',reference="Processes/train.py", verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._reference = reference

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self,ref):
        self._reference = ref

