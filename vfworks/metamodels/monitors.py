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

    def __init__(self, name='tbd', description='tbd', status=StatusType.UNKNOWN, monitor_type=MonitorType.RUN_TIME, observes=None, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._status = status
        self._type = monitor_type

        # OBSERVED PROPERTIES (POI/INFLUENCE)
        if observes is None:
            self.observes = []
        else:
            self.observes = observes

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self,t):
        self._status = t

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self,t):
        self._type = t

    def validate_data(self, data, feature):
        is_valid = True
        for spec in self.observes:
            if spec.feature == feature:
                is_valid = spec.value.validate_data(data)
                if is_valid:
                    self._status = StatusType.VALID
                else:
                    self._status = StatusType.INVALID
        return is_valid

    def validate_point(self, data, feature):
        is_valid = True
        for spec in self.observes:
            if spec.feature == feature:
                is_valid = spec.value.validate_point(data)
                if is_valid:
                    self._status = StatusType.VALID
                else:
                    self._status = StatusType.INVALID
        return is_valid