#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.metamodels.common import *

class ValidityFrame(baseElement):
    def __init__(self, name='tbd',description='tbd',modelStructure=None,modelRef=None,specifications=None,properties=None,monitors=None,verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._modelReference = modelRef  #CAN EITHER BE A SINGLE FILE OF A FOLDER WITH MULTIPLE FILES
        self._modelStructure = modelStructure

        if specifications is None:
            self._specifications = []
        else:
            self._specifications = specifications

        if properties is None:
            self._properties = []
        else:
            self._properties = properties

        if monitors is None:
            self._monitors = []
        else:
            self._monitors = monitors

    @property
    def modelReference(self):
        return self._modelReference

    @modelReference.setter
    def modelReference(self, value):
        self._modelReference = value

    @property
    def modelStructure(self):
        return self._modelStructure

    @modelStructure.setter
    def modelStructure(self, value):
        self._modelStructure = value

    @property
    def specifications(self):
        return self._specifications

    @specifications.setter
    def specifications(self, value):
        self._specifications = value

    def addSpecification(self, spec):
        self._specifications.append(spec)

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    def addProperty(self, spec):
        self._properties.append(spec)

    @property
    def monitors(self):
        return self._monitors

    @monitors.setter
    def monitors(self, value):
        self._monitors = value

    def addMonitor(self, monitor):
        self._monitors.append(monitor)