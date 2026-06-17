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
import importlib.util
import inspect
import os

class Monitor(baseElement):

    def __init__(self, name='tbd', description='tbd', status=StatusType.UNKNOWN, monitor_time=MonitorTime.RUN_TIME, observes=None, verbose=False, spec_status=None, last_observed_values=None, packageName=None):
        super().__init__(name=name, description=description, verbose=verbose)

        self._status = status
        self._type = monitor_time
        self._validate_point_function = None
        self._packageName = packageName

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

    def setup(self):
        """Setup the monitor, including loading any custom validation hooks."""
        self._load_custom_validation_hook()

    @property
    def packageName(self):
        return self._packageName
    @packageName.setter
    def packageName(self, value):
        self._packageName = value

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

    def validate_point(self, data, feature=None):
        """
        Validates operational data against monitor specs.
        
        Supports:
        1. Legacy single feature inputs: validate_point(255, "red")
        2. Multi-feature vector inputs: validate_point({"red": 255, "green": 120, "blue": 30})
        """
        # 1. Backward Compatibility Layer (Normalize inputs to a data vector map)
        if feature is not None:
            data_vector = {feature: data}
        elif isinstance(data, dict):
            data_vector = data
        else:
            raise ValueError("Data must be a dictionary vector if 'feature' is not provided.")

        # 2. Monitor-Level Custom Macro Overloading (e.g., Custom RGB Checks)
        # The custom function can evaluate the full vector and return a mapping of:
        # {feature_name: is_valid_boolean}
        custom_evaluations = {}
        if self._validate_point_function is not None:
            # Custom function processes the full dictionary vector at once
            validate_point_signature = inspect.signature(self._validate_point_function)
            if "monitor" in validate_point_signature.parameters:
                custom_evaluations = self._validate_point_function(data_vector, monitor=self)
            else:
                custom_evaluations = self._validate_point_function(data_vector)

        # 3. Process specs based on the vector values
        global_is_valid = True
        
        for spec in self.observes:
            # Only evaluate if the feature is present in our current incoming data vector
            if spec.feature in data_vector:
                current_feature_val = data_vector[spec.feature]
                
                # Check if a custom monitor macro already evaluated this feature
                if spec.feature in custom_evaluations:
                    spec_is_valid = custom_evaluations[spec.feature]
                else:
                    # Fallback to the spec's specific value logic (built-in or custom value plugin)
                    spec_is_valid = spec.value.validate_point(current_feature_val)
                
                # Update metric state tracking
                if spec_is_valid:
                    self.spec_status[spec.feature] = StatusType.VALID
                else:
                    self.spec_status[spec.feature] = StatusType.INVALID
                    global_is_valid = False
                    
                self.last_observed_values[spec.feature] = current_feature_val

        # 4. Global Monitor Status Rollup
        if StatusType.INVALID in self.spec_status.values():
            self._status = StatusType.INVALID
        elif StatusType.UNKNOWN in self.spec_status.values():
            self._status = StatusType.UNKNOWN
        else:
            self._status = StatusType.VALID

        return global_is_valid

    def _load_custom_validation_hook(self):
        """Private helper to locate and bind custom vector validation scripts."""
        package_root = os.getcwd()
        custom_script_path = os.path.join(
            package_root, self.packageName, "Resources", "monitors", f"{self.name}.py"
        )

        # Check if the user wrote a custom plugin matching this monitor type
        if os.path.exists(custom_script_path):
            try:
                # Load the file dynamically as a Python module
                spec = importlib.util.spec_from_file_location(self.name, custom_script_path)
                custom_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(custom_module)

                # Look for our standardized function name contract
                if hasattr(custom_module, "custom_validate_vector"):
                    self._validate_point_function = custom_module.custom_validate_vector
                    print(f"Successfully bound custom validation function for '{self.name}'")
                else:
                    print(
                        f"Found custom script '{self.name}.py', but it is missing 'custom_validate_vector'. "
                        f"Falling back to default built-in validation rules.",
                        level="warning"
                    )
            except Exception as e:
                print(f"Failed to compile custom monitor plugin '{self.name}': {str(e)}")
        else:
            # No custom script found; perfectly fine, it will use default built-in value.validate_point rules
            print(f"No custom override found for '{self.name}'. Running baseline configurations.")

