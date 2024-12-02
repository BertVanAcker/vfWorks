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
from py2neo import Node

class Property(baseElement):
    def __init__(self, name='tbd',description='tbd',domain=DomainType.CONTROL,unit=UnitType.UNIT_none,datatype=Datatype.FLOAT_64,min=0,max=0,satisfies=None,verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._domain = domain
        self._unit=unit
        self._datatype=datatype
        self._min=min
        self._max=max

        # TRACEABILITY TO SPECIFICATION
        if satisfies is None:
            self._satisfies = []
        else:
            self._satisfies = satisfies


    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        self._domain = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def datatype(self):
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        self._datatype = value

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        self._min = value

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        self._max = value

    @property
    def satisfies(self):
        return self._satisfies

    @satisfies.setter
    def satisfies(self, value):
        self._satisfies = value

    def add_satisfies_relation(self, value):
        self._satisfies.append(value)


class PropertyofInterest(Property):
    def __init__(self, name='tbd',description='tbd',domain=DomainType.CONTROL,unit=UnitType.UNIT_none,datatype=Datatype.FLOAT_64,min=0,max=0,satisfies=None,verbose=False):
        super().__init__(name=name, description=description,domain=domain,unit=unit,datatype=Datatype,min=min,max=max,satisfies=satisfies, verbose=verbose)

    def create_neo4j_node(self):
        return Node("Property-of-interest", name=self.name, domain=self.domain,unit=self.unit,datatype=self.datatype,minimum=self.min,maximum=self.max)


class InfluenceFactor(Property):
    def __init__(self, name='tbd',description='tbd',domain=DomainType.CONTROL,unit=UnitType.UNIT_none,datatype=Datatype.FLOAT_64,min=0,max=0,satisfies=None,verbose=False):
        super().__init__(name=name, description=description,domain=domain,unit=unit,datatype=Datatype,min=min,max=max,satisfies=satisfies, verbose=verbose)

    def create_neo4j_node(self):
        return Node("InfluenceFactor", name=self.name, domain=self.domain,unit=self.unit,datatype=self.datatype,minimum=self.min,maximum=self.max)