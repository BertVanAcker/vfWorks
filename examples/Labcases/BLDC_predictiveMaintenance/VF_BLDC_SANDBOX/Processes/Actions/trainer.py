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

        self.models = []

    def t_collect_data(self):
        try:
            #load train data from model structure
            self.data_full = self._data_loader.loadData(experimentLabel="all",prefix=self._prefix,type="numpy",shuffle=True)
            return True
        except:
            return False

    def t_validate_data(self):
        try:
            validation_pass = True
            f_conditions = {}
            for experiment in self._validityFrame.experiments:
                for specification in self._validityFrame.specifications:
                    for condition in experiment.conditions:
                        if specification.feature == condition.name:
                            if condition.name not in f_conditions:
                                f_conditions[condition.name] = [condition.value]
                            else:
                                f_conditions[condition.name].append(condition.value)
            for monitor in self._validityFrame.design_time_monitors:
                for feature in f_conditions:
                    is_valid = monitor.validate_data(data=f_conditions[feature], feature=feature)
                    if not is_valid:
                        validation_pass = False
                        print("WARNING: design property not satisfied: {} dataset not complete".format(feature))

            return validation_pass
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
            for model_number in range(self._validityFrame.activeModelStructure.redundancy):
                self.models.append(IsolationForest(contamination="auto", random_state=model_number, max_features=num_inputs))
            return True
        except:
            return False

    def t_fit_model(self):
        try:
            for model in self.models:
                model.fit(self.data_train)
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
            if len(self.models) > 1:
                folder_name = self._validityFrame.activeModelStructure.name
                for model_number in range(len(self.models)):
                    store_as_pickled(model=self.models[model_number], file_name=self._prefix + 'Sources/' + folder_name + "/model" + str(model_number) + ".pkl",
                                     modelType="torch")
                    self._validityFrame.modelReference = "Sources/" + folder_name
            else:
                model_name = self._validityFrame.activeModelStructure.name
                store_as_pickled(model=self.models[0],file_name=self._prefix+'Sources/'+ model_name + "_model.pkl",modelType="torch")
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