#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import os

from textx import metamodel_from_file

class Specification_parser(object):
    def __init__(self, specificationModel):
        self._specificationModel = specificationModel

        currentDir = os.path.dirname(os.path.abspath(__file__))
        metamodelPath = os.path.join(currentDir,'..','grammar/specificationModel.tx')
        self._specificationModel_metamodel = metamodel_from_file(metamodelPath)

    def parse(self):
        specificationModel = self._specificationModel_metamodel.model_from_file(self._specificationModel)
        return specificationModel

