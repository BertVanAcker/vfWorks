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

class ModelStructure(baseElement):
    def __init__(self, name='tbd',description='tbd',inports=None,outports=None,mapping=None,verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        if inports is None:
            self._inports = []
        else:
            self._inports = inports

        if outports is None:
            self._outports = []
        else:
            self._outports = outports

        # TRACEABILITY TO PROPERTIES (POI/INFLUENCE)
        if mapping is None:
            self._mapping = []
        else:
            self._mapping = mapping

    @property
    def inports(self):
        return self._inports

    @inports.setter
    def inports(self, value):
        self._inports = value

    def add_inport(self,inport):
        self._inports.append(inport)

    @property
    def outports(self):
        return self._inports

    @outports.setter
    def outports(self, value):
        self._outports = value

    def add_outport(self, outport):
        self._outports.append(outport)

    @property
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, value):
        self._mapping = value

    def add_mapping_relation(self, value):
        self._mapping.append(value)


class Port(baseElement):
    def __init__(self, name='tbd', description='tbd',domain=DomainType.CONTROL,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_64,min=0,max=0,mapping=None, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)


        self._domain = domain
        self._unit=unit
        self._datatype=datatype
        self._min=min
        self._max=max

        # TRACEABILITY TO PROPERTIES (POI/INFLUENCE)
        if mapping is None:
            self._mapping = []
        else:
            self._mapping = mapping


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
    def mapping(self):
        return self._mapping

    @mapping.setter
    def mapping(self, value):
        self._mapping = value

    def add_mapping_relation(self, value):
        self._mapping.append(value)

class Inport(Port):

    def __init__(self, name='tbd', description='tbd',domain=DomainType.CONTROL,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_64,min=0,max=0,mapping=None, verbose=False):
        super().__init__(name=name, description=description,domain=domain,unit=unit,datatype=datatype,min=min,max=max,mapping=mapping, verbose=verbose)


class Outport(Port):

    def __init__(self, name='tbd', description='tbd', domain=DomainType.CONTROL, unit=UnitType.UNIT_none,
                 datatype=DataType.FLOAT_64, min=0, max=0, mapping=None, verbose=False):
        super().__init__(name=name, description=description, domain=domain, unit=unit, datatype=datatype, min=min,
                         max=max, mapping=mapping, verbose=verbose)

