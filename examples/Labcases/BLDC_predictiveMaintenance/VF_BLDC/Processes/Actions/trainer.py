#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.utils.data.dataLoader import *
from pycaret.anomaly import *
class trainingActions(object):
    def __init__(self, name="userActions class", validityFrame=None):
        self._name = name
        self._validityFrame = validityFrame
        self._prefix = "../"

        # define dataloader
        self._data_loader = DataLoader(name="VF_data_loader")

        self.data_RAW = None
        self.data_train = None
        self.data_test = None

    def t_collect_data(self):
        try:
            #load train data from model structure
            self.data_train = self._data_loader.loadData(validityFrame=self._validityFrame,experimentLabel="nominal",prefix=self._prefix)
            #load test data from model structure
            self.data_test = self._data_loader.loadData(validityFrame=self._validityFrame, experimentLabel="anomaly",prefix=self._prefix)
            return True
        except:
            return False

    def t_prepare_data(self):
        try:
            print("WARNING: Prepare data action not implemented yet!")
            #TODO: process self.data_RAW and fill self.data
            return True
        except:
            return False

    def t_load_model(self):
        try:
            self.trainerSetup = setup(self.data_train, session_id=123)
            self.model = create_model('knn', fraction=0.1)
            return True
        except:
            return False

    def t_fit_model(self):
        try:
            self.model_results = assign_model(self.model)
            return True
        except:
            return False

    def t_evaluate_model(self):
        try:
            print("WARNING: Model evaluation action not implemented yet!")
            return True
        except:
            return False

    def t_store_model_snapshot(self):
        try:
            save_model(self.model, self._prefix+'Sources/model')     #TODO: store model with GUID!!
            self._validityFrame.modelReference = "Sources/model"
            return True
        except:
            return False

    def t_store_vf(self):
        try:
            self._validityFrame.export(packageName="..")  # VF package is top level structure
            return True
        except:
            return False