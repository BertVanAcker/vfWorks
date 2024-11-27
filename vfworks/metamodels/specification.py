#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.metamodels.common import *

class Specification(baseElement):

    def __init__(self, name='tbd', description='tbd',ID="tbd",standard="ISO26262-part 3",paragraph="3.1.1 DUMMY",DOI=None,specifications=None,isMandatory=True, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self.ID=ID
        self.standard = standard
        self.paragraph = paragraph
        self.DOI=DOI
        if specifications is None:
            self.specifications=[]
        else:
            self.specifications=specifications
        self.isMandatory = isMandatory


    @property
    def ID(self):
        return self

    @ID.setter
    def ID(self, value):
        self._ID = value

    @property
    def standard(self):
        return self.standard

    @standard.setter
    def standard(self, value):
        self._standard = value

    @property
    def paragraph(self):
        return self.paragraph

    @paragraph.setter
    def paragraph(self, value):
        self._paragraph = value

    @property
    def DOI(self):
        return self.DOI

    @DOI.setter
    def DOI(self, value):
        self._DOI = value

    @property
    def specifications(self):
        return self.specifications

    def addSpecification(self,specification):
        self.specifications.append(specification)

    @specifications.setter
    def specifications(self, value):
        self._specifications = value

    @property
    def isMandatory(self):
        return self.isMandatory

    @isMandatory.setter
    def isMandatory(self, value):
        self._isMandatory = value
