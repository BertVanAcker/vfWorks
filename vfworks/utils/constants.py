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

class UnitType:
    DISTANCE_mm= "mm"
    DISTANCE_cm= "cm"
    DISTANCE_m = "m"
    DISTANCE_km = "km"
    ANGLE_DEGREES = "degrees"
    ANGLE_RADIANS = "radians"
    FORCE_N= "Newton"
    UNIT_none = "-"

class Datatype:
    FLOAT_64 = "flaot_64"
    FLOAT_32 = "flaot_32"
    FLOAT_16 = "flaot_16"
    FLOAT_8 = "flaot_8"

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
