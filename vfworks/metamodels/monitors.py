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

    def __init__(self, name='tbd', description='tbd', status=StatusType.UNKNOWN, monitor_time=MonitorTime.RUN_TIME, observes=None, verbose=False, spec_status=None, last_observed_values=None, validate_point_function=None):
        super().__init__(name=name, description=description, verbose=verbose)

        self._status = status
        self._type = monitor_time
        self._validate_point_function = validate_point_function

        self.observes = observes
        self.spec_status = {}
        self.last_observed_values = {}
        # OBSERVED PROPERTIES (POI/INFLUENCE)
        if observes is not None:
            for observe in observes:
                self.spec_status[observe.feature] = StatusType.UNKNOWN
                self.last_observed_values[observe.feature] = None

        if spec_status is not None:
            self.spec_status = spec_status
        if last_observed_values is not None:
            self.last_observed_values = last_observed_values

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

    @property
    def validate_point_function(self):
        return self._validate_point_function

    @validate_point_function.setter
    def validate_point_function(self, function):
        self._validate_point_function = function

    def set_validate_point_function(self, function):
        self.validate_point_function = function

    def create_neo4j_node(self):
        evaluation = ", ".join(f"{key}: {value}" for key, value in self.last_observed_values.items())
        return {
            'label': 'Monitor',
            'properties': {
                'name': self.name,
                'description': self.description,
                'status': str(self.status),  # Serialize enum if needed
                'evaluation': evaluation
            }
        }

    def validate_data(self, data, feature):
        is_valid = True
        for spec in self.observes:
            if spec.feature == feature:
                is_valid, observed_value = spec.value.validate_data(data)
                self.last_observed_values[spec.feature] = observed_value
                if is_valid:
                    self.spec_status[spec.feature] = StatusType.VALID
                else:
                    self.spec_status[spec.feature] = StatusType.INVALID
        if StatusType.INVALID in self.spec_status.values():
            self._status = StatusType.INVALID
        elif StatusType.UNKNOWN in self.spec_status.values():
            self._status = StatusType.UNKNOWN
        else:
            self._status = StatusType.VALID
        return is_valid

    def validate_point(self, data, feature):
        is_valid = True
        for spec in self.observes:
            if spec.feature == feature:
                if self._validate_point_function is not None:
                    is_valid = self._validate_point_function(data, feature)
                else:
                    is_valid = spec.value.validate_point(data)
                if is_valid:
                    self.spec_status[spec.feature] = StatusType.VALID
                    self.last_observed_values[spec.feature] = data
                else:
                    self.spec_status[spec.feature] = StatusType.INVALID
                    self.last_observed_values[spec.feature] = data
                    self._status = StatusType.INVALID
        if StatusType.INVALID in self.spec_status.values():
            self._status = StatusType.INVALID
        elif StatusType.UNKNOWN in self.spec_status.values():
            self._status = StatusType.UNKNOWN
        else:
            self._status = StatusType.VALID
        return is_valid