#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import uuid
import datetime
class baseElement(object):

    def __init__(self, name='tbd', description='tbd', verbose=False):
        self._name = name
        self._description = description
        self._verbose = verbose
        self._GUID = uuid.uuid4()
        self._timestamp = datetime.datetime.now()

    @property
    def name(self):
        """The name property (read-only)."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        """The description property (read-only)."""
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def GUID(self):
        return self._GUID

    @GUID.setter
    def GUID(self, value):
        self._GUID = value

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

