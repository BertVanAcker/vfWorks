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

class Experiment(baseElement):

    def __init__(self, name='tbd', description='tbd',label="nominal",conditions = [],measurements=[], verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._label = label
        self._conditions = []
        self._measurements = []


    @property
    def label(self):
        return self._label

    @label.setter
    def label(self,l):
        self._label = l
    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    def conditions(self,condition):
        self._conditions = condition

    def addCondition(self,condition):
        self._conditions.append(condition)

    @property
    def measurements(self):
        return self._measurements

    @measurements.setter
    def measurements(self, measurements):
        self._measurements = measurements

    def addMeasurement(self, measurement):
        self._measurements.append(measurement)



class ExperimentCondition(baseElement):

    def __init__(self, name='tbd', description='tbd',value="tbd", verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,v):
        self._value = v

class Measurement(baseElement):

    def __init__(self, name='tbd', description='tbd',dataPoints=[],reference=None, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._dataPoints = dataPoints
        self._reference = reference                 #relative reference in VF!

    @property
    def dataPoints(self):
        return self._dataPoints

    @dataPoints.setter
    def dataPoints(self,data):
        self._dataPoints = data

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, ref):
        self._reference = ref