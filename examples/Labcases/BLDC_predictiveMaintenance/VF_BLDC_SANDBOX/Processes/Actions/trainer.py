#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.utils.auxiliary import store_as_onnx, store_as_pickled
from vfworks.utils.data.dataLoader import *
from vfworks.utils.model.modelLoader import *
from sklearn.ensemble import IsolationForest

class trainingActions(object):
    def __init__(self, name="userActions class", validityFrame=None):
        self._name = name
        self._validityFrame = validityFrame
        self._prefix = "../"

        # define dataloader
        self._data_loader = DataLoader(name="VF_data_loader",validityframe=self._validityFrame)
        # define modelloader
        self._model_loader = ModelLoader(name="VF_model_loader",validityFrame=self._validityFrame)

        self.data_RAW = None
        self.data_train = None
        self.data_test = None

    def t_collect_data(self):
        try:
            #load train data from model structure
            self.data_train = self._data_loader.loadData(experimentLabel="all",prefix=self._prefix,type="numpy",shuffle=True)
            #load test data from model structure
            self.data_test = self._data_loader.loadData(experimentLabel="anomaly",prefix=self._prefix,type="numpy")
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
            self.model = IsolationForest(contamination="auto", random_state=0,max_features=1)
            return True
        except:
            return False

    def t_fit_model(self):
        try:
            self.model.fit(self.data_train)
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
            store_as_onnx(model=self.model,file_name=self._prefix+'Sources/'+"model.onnx",modelType="torch")
            self._validityFrame.modelReference = "Sources/model.onnx"
            return True
        except Exception as e:
            print(e)
            return False

    def t_store_model_snapshot_pickled(self):
        try:
            store_as_pickled(model=self.model,file_name=self._prefix+'Sources/'+"model.pkl",modelType="torch")
            self._validityFrame.modelReference = "Sources/model.pkl"
            return True
        except Exception as e:
            print(e)
            return False

    def t_store_vf(self):
        try:
            self._validityFrame.export(packageName="..")  # VF package is top level structure
            return True
        except:
            return False