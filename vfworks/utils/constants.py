#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************


class DomainType:
    CONTROL = "CONTROL"
    MECHANICAL = "MECHANICAL"
    ELECTRICAL = "ELECTRICAL"
    NONE = "None"

class UnitType:
    DISTANCE_mm= "mm"
    DISTANCE_cm= "cm"
    DISTANCE_m = "m"
    DISTANCE_km = "km"
    SPEED_M_S = "m/s"
    ANGLE_DEGREES = "degrees"
    ANGLE_RADIANS = "radians"
    ANG_SPEED_RADIANS = "radians/s"
    ANG_SPEED_DEGREES = "degrees/s"
    FORCE_N= "Newton"
    Power_Watt = "Watt"
    UNIT_none = "-"


class DataType:
    FLOAT_64 = "float_64"
    FLOAT_32 = "float_32"
    FLOAT_16 = "float_16"
    FLOAT_8 = "float_8"
    INTEGER_32 = "int_32"
    INTEGER_16 = "int_16"
    INTEGER_8 = "int_8"
    STRING = "string"
    BOOLEAN = "boolean"

class MonitorType:
    PROPERTY_RANGE= "property_range"
    PROPERTY_MEAN = "property_mean"

class StatusType:
    PROPERTY_RANGE= "property_range"
    PROPERTY_MEAN = "property_mean"

class StatusType:
    UNKNOWN = "unknown"
    VALID = "valid"
    INVALID = "invalid"

class StepStatus:
    PENDING = "Pending"
    RUNNING = "Running"
    PASSED = "Passed"
    FAILED = "Failed"
