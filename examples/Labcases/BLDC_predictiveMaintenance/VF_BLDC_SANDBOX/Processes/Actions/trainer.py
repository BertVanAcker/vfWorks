#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import numpy as np

from vfworks.utils.auxiliary import store_as_onnx, store_as_pickled
from scipy.stats import chisquare
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

        self.data_full = None
        self.data_RAW = None
        self.data_train = None
        self.data_test = None

    def t_collect_data(self):
        try:
            #load train data from model structure
            self.data_full = self._data_loader.loadData(experimentLabel="all",prefix=self._prefix,type="numpy",shuffle=True)
            return True
        except:
            return False

    def t_validate_data(self):
        try:
            f_conditions = {}
            for experiment in self._validityFrame.experiments:
                for specification in self._validityFrame.specifications:
                    for condition in experiment.conditions:
                        if specification.feature == condition.name:
                            if condition.name not in f_conditions:
                                f_conditions[condition.name] = [condition.value]
                            else:
                                f_conditions[condition.name].append(condition.value)
            for specification in self._validityFrame.specifications:
                valueMin = specification.minValue
                valueMax = specification.maxValue
                f_measure = np.histogram(f_conditions[specification.feature], range=(valueMin,valueMax))[0]

                if 0 in f_measure:
                    print("WARNING: design property not satisfied: {} dataset not complete".format(specification.feature))
                    return False

            return True
        except:
            return False

    def t_prepare_data(self):
        try:
            train_size = int(len(self.data_full)*0.8)
            self.data_train = self.data_full[:train_size]
            self.data_test = self.data_full[train_size:]
            return True
        except:
            return False

    def t_load_model(self):
        try:
            num_inputs = len(self._validityFrame.activeModelStructure.inports)
            self.model = IsolationForest(contamination="auto", random_state=0, max_features=num_inputs)
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
            model_name = self._validityFrame.activeModelStructure.name
            store_as_pickled(model=self.model,file_name=self._prefix+'Sources/'+ model_name + "_model.pkl",modelType="torch")
            self._validityFrame.modelReference = "Sources/" + model_name + "_model.pkl"
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