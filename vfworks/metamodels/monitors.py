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

class Monitor(baseElement):

    def __init__(self, name='tbd', description='tbd',type=MonitorType.PROPERTY_RANGE,status=StatusType.UNKNOWN,observes=None, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._type = type
        self._status = status

        # OBSERVED PROPERTIES (POI/INFLUENCE)
        if observes is None:
            self.observes = []
        else:
            self.observes = observes

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self,t):
        self._type = t

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self,t):
        self._status = t
