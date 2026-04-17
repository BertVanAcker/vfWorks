 #***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import numpy as np
from vfworks.metamodels.common import *
from vfworks.utils.constants import *
from py2neo import Node

class Specification(baseElement):
    def __init__(self, name='tbd', description='tbd', feature='tbd', type=None, verbose=False, **kwargs):
        super().__init__(name=name, description=description, verbose=verbose)

        self._feature = feature
        self._status = StatusType.UNKNOWN
        self._type = type

        if type == PropertyType.PROPERTY_RANGE:
            self._value = ValueRange(valueMin=kwargs['valueMin'], valueMax=kwargs['valueMax'], granularity=kwargs['granularity'])
        if type == PropertyType.PROPERTY_MEAN:
            self._value = AverageValue(average=kwargs['average'], deviation=kwargs['deviation'])
        if type == PropertyType.PROPERTY_MIN:
            self._value = ValueMin(valueMin=kwargs['valueMin'])
        if type == PropertyType.PROPERTY_MAX:
            self._value = ValueMax(valueMax=kwargs['valueMax'])

    @property
    def feature(self):
        return self._feature

    @feature.setter
    def feature(self, feature):
        self._feature = feature

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def status(self):
        return self._status

    def create_neo4j_node(self):
        color_map = {
            StatusType.INVALID: "#E76F51",
            StatusType.VALID: "#8AB17D",
            StatusType.UNKNOWN: "#B0B0B0",
        }
        return Node(
            "specification",
            name=self.name,
            description=self.description,
            value=self.feature + ": " + self.value.tostring(),
            status=self.status,
            viz_color=color_map.get(self.status, "#B0B0B0")
        )

class AverageValue(baseElement):
    def __init__(self, name='tbd',description='tbd', average=0.0, deviation=0.0, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)
        self._average = average
        self._deviation = deviation

    def validate_data(self, data):
        data_average = np.average(data)
        if data_average < self._average-self._deviation or data_average > self._average+self._deviation:
            return False
        return True

    def validate_point(self, point):
        if point < self._average-self._deviation or point > self._average+self._deviation:
            return False
        return True
    
    def tostring(self):
        return f"{self._average} +/- {self._deviation}"

class ValueRange(baseElement):
    def __init__(self, name='tbd',description='tbd', valueMin=0.0, valueMax=0.0, granularity=10, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)
        self._valueMin = valueMin
        self._valueMax = valueMax
        self._granularity = granularity

    def validate_data(self, data):
        f_measure = np.histogram(data, range=(self._valueMin, self._valueMax), bins=self._granularity)[0]
        if 0 in f_measure:
            return False
        return True

    def validate_point(self, point):
        if point < self._valueMin or point > self._valueMax:
            return False
        return True
    
    def tostring(self):
        return f"[{self._valueMin} - {self._valueMax}]"

class ValueMin(baseElement):
    def __init__(self, name='tbd',description='tbd', valueMin=0.0, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)
        self._valueMin = valueMin

    def validate_data(self, data):
        data_min = np.min(data)
        if data_min <= self._valueMin:
            return False
        return True

    def validate_point(self, point):
        if point <= self._valueMin:
            return False
        return True
    
    def tostring(self):
        return f">={self._valueMin}"

class ValueMax(baseElement):
    def __init__(self, name='tbd',description='tbd', valueMax=0.0, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)
        self._valueMax = valueMax

    def validate_data(self, data):
        data_max = np.max(data)
        if data_max >= self._valueMax:
            return False
        return True

    def validate_point(self, point):
        if point >= self._valueMax:
            return False
        return True
    
    def tostring(self):
        return f"<={self._valueMax}"

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

