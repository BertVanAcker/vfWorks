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

        if self.inports is None:
            self.inports = []
        else:
            self.inports = inports

        if self.outports is None:
            self.outports = []
        else:
            self.outports = outports

        # TRACEABILITY TO PROPERTIES (POI/INFLUENCE)
        if mapping is None:
            self.mapping = []
        else:
            self.mapping = mapping

    @property
    def inports(self):
        return self.inports

    @inports.setter
    def inports(self, value):
        self.inports = value

    def add_inport(self,inport):
        self.inports.append(inport)

    @property
    def outports(self):
        return self.inports

    @outports.setter
    def outports(self, value):
        self.outports = value

    def add_outport(self, outport):
        self.outports.append(outport)

    @property
    def mapping(self):
        return self.mapping

    @mapping.setter
    def mapping(self, value):
        self.mapping = value

    def add_mapping_relation(self, value):
        self.mapping.append(value)


class Port(baseElement):
    def __init__(self, name='tbd', description='tbd',domain=DomainType.CONTROL,unit=UnitType.UNIT_none,datatype=Datatype.FLOAT_64,min=0,max=0,mapping=None, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)


        self.domain = domain
        self.unit=unit
        self.datatype=datatype
        self.min=min
        self.max=max

        # TRACEABILITY TO PROPERTIES (POI/INFLUENCE)
        if mapping is None:
            self.mapping = []
        else:
            self.mapping = mapping


    @property
    def domain(self):
        return self.domain

    @domain.setter
    def domain(self, value):
        self._domain = value

    @property
    def unit(self):
        return self.unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def datatype(self):
        return self.datatype

    @datatype.setter
    def datatype(self, value):
        self._datatype = value

    @property
    def min(self):
        return self.min

    @min.setter
    def min(self, value):
        self._min = value

    @property
    def max(self):
        return self.max

    @max.setter
    def max(self, value):
        self._max = value

    @property
    def mapping(self):
        return self.mapping

    @mapping.setter
    def mapping(self, value):
        self.mapping = value

    def add_mapping_relation(self, value):
        self.mapping.append(value)

class Inport(Port):

    def __init__(self, name='tbd', description='tbd',domain=DomainType.CONTROL,unit=UnitType.UNIT_none,datatype=Datatype.FLOAT_64,min=0,max=0,mapping=None, verbose=False):
        super().__init__(name=name, description=description,domain=domain,unit=unit,datatype=datatype,min=min,max=max,mapping=mapping, verbose=verbose)


class Outport(Port):

    def __init__(self, name='tbd', description='tbd', domain=DomainType.CONTROL, unit=UnitType.UNIT_none,
                 datatype=Datatype.FLOAT_64, min=0, max=0, mapping=None, verbose=False):
        super().__init__(name=name, description=description, domain=domain, unit=unit, datatype=datatype, min=min,
                         max=max, mapping=mapping, verbose=verbose)

