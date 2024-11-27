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

class Specification(baseElement):

    def __init__(self, name='tbd', description='tbd',ID="tbd",standard="ISO26262-part 3",paragraph="3.1.1 DUMMY",DOI=None,specifications=None,isMandatory=True, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._ID=ID
        self._standard = standard
        self._paragraph = paragraph
        self._DOI=DOI
        self._status = StatusType.UNKNOWN

        if specifications is None:
            self._specifications=[]
        else:
            self._specifications=specifications
        self._isMandatory = isMandatory


    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, value):
        self._ID = value

    @property
    def standard(self):
        return self._standard

    @standard.setter
    def standard(self, value):
        self._standard = value

    @property
    def paragraph(self):
        return self._paragraph

    @paragraph.setter
    def paragraph(self, value):
        self._paragraph = value

    @property
    def DOI(self):
        return self._DOI

    @DOI.setter
    def DOI(self, value):
        self._DOI = value

    @property
    def specifications(self):
        return self._specifications

    def addSpecification(self,specification):
        self._specifications.append(specification)

    @specifications.setter
    def specifications(self, value):
        self._specifications = value

    @property
    def isMandatory(self):
        return self._isMandatory

    @isMandatory.setter
    def isMandatory(self, value):
        self._isMandatory = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self,value):
        self._status = value

