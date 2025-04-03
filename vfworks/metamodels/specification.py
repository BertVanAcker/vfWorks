 #***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import numpy as np
from scipy.stats import chisquare
from vfworks.metamodels.common import *
from vfworks.utils.constants import *

class Specification(baseElement):
    def __init__(self, name='tbd', description='tbd', feature='tbd', minValue=0, maxValue=0, runtimeSpecification=True, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._feature = feature
        self._minValue = minValue
        self._maxValue = maxValue
        self._runtimeSpecification = runtimeSpecification


    @property
    def feature(self):
        return self._feature

    @feature.setter
    def feature(self, feature):
        self._feature = feature

    @property
    def minValue(self):
        return self._minValue

    @minValue.setter
    def minValue(self, value):
        self._minValue = value

    @property
    def maxValue(self):
        return self._maxValue

    @maxValue.setter
    def maxValue(self, value):
        self._maxValue = value

    @property
    def runtimeSpecification(self):
        return self._runtimeSpecification

    @runtimeSpecification.setter
    def runtimeSpecification(self, value):
        self._runtimeSpecification = value

class Requirement(baseElement):

    def __init__(self, name='tbd', description='tbd',ID="tbd",standard="ISO26262-part 3",paragraph="3.1.1 DUMMY",DOI=None,specifications=None,isMandatory=True, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._ID=ID
        self._standard = standard
        self._paragraph = paragraph
        self._DOI=DOI
        self._status = StatusType.UNKNOWN

        if specifications is None:
            self._specifications=[]
        else:
            self._specifications=specifications
        self._isMandatory = isMandatory


    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value):
        self._ID = value

    @property
    def standard(self):
        return self._standard

    @standard.setter
    def standard(self, value):
        self._standard = value

    @property
    def paragraph(self):
        return self._paragraph

    @paragraph.setter
    def paragraph(self, value):
        self._paragraph = value

    @property
    def DOI(self):
        return self._DOI

    @DOI.setter
    def DOI(self, value):
        self._DOI = value

    @property
    def specifications(self):
        return self._specifications

    def addSpecification(self,specification):
        self._specifications.append(specification)

    @specifications.setter
    def specifications(self, value):
        self._specifications = value

    @property
    def isMandatory(self):
        return self._isMandatory

    @isMandatory.setter
    def isMandatory(self, value):
        self._isMandatory = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self,value):
        self._status = value

