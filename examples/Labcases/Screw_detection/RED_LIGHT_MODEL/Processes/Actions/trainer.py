#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import shutil

import sklearn.metrics
import torch
import tqdm

from vfworks.utils.auxiliary import store_as_onnx, store_as_pickled
from vfworks.utils.data.dataLoader import *
from vfworks.utils.model.modelLoader import *
from ultralytics import YOLO


class trainingActions(object):
    def __init__(self, name="userActions class", validityFrame=None):
        self._name = name
        self._validityFrame = validityFrame
        self._prefix = "../"
        self.monitors = self._validityFrame.design_time_monitors

        # define dataloader
        self._data_loader = DataLoader(name="VF_data_loader",validityframe=self._validityFrame)
        # define modelloader
        self._model_loader = ModelLoader(name="VF_model_loader",validityFrame=self._validityFrame)

        self.data_full = None
        self.data_RAW = None
        self.data_train = None
        self.data_test = None
        self.data_validate = None
        self.DEBUG = False

        self.model = None

    def t_collect_data(self):
        try:
            #load train data from model structure
            self.data_full = self._data_loader.loadData(experimentLabel="all",prefix=self._prefix,type="prepared_data_yaml")
            return True
        except:
            return False

    def t_validate_data(self):
        #TODO: check function again, maybe make simpler through better monitor implementation
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
            return True
        except:
            return False

    def t_load_model(self):
        try:
            self.model = YOLO("yolo11n.pt")
            return True
        except:
            return False

    def t_fit_model(self):
        try:
            if self.DEBUG:
                self.model = YOLO("screw_detection_model/weights/best.pt")
                return True
            self.model.train(data=self.data_full, epochs=20, project="C:\\Users\jan_g\PycharmProjects\\vfWorks\examples\Labcases\Screw_detection\YOLO_pretrained_model_VF\Processes", name="screw_detection_model", workers=0)
            return True

        except Exception as e:
            print(f"Error in training: {e}")
            return False

    def t_evaluate_model(self):
        #TODO: improve/simplify function through better monitor implementation and clearer link with actual specs and VF retrieval functions.
        try:
            evaluated_features = {"mAP50-95": []}
            evaluation_pass = True
            metrics = self.model.val(data=self.data_full, project="C:\\Users\jan_g\PycharmProjects\\vfWorks\examples\Labcases\Screw_detection\YOLO_pretrained_model_VF\Processes", workers=0)
            evaluated_features["mAP50-95"] = metrics.results_dict["metrics/mAP50-95(B)"]
            for monitor in self._validityFrame.design_time_monitors:
                for feature in evaluated_features:
                    is_valid = monitor.validate_point(data=evaluated_features[feature], feature=feature)
                    if not is_valid:
                        evaluation_pass = False
                        print("WARNING: model requirement not satisfied: {} not sufficient".format(feature))
            return evaluation_pass
        except Exception as e:
            print(f"Error in t_evaluate_model: {e}")
            return False

    def t_store_model_snapshot(self):
        try:
            self.model.export(format="onnx")
            return True
        except Exception as e:
            print(e)
            return False

    def t_store_model_snapshot_pickled(self):
        try:
            model_name = self._validityFrame.activeModelStructure.name
            shutil.copy2("screw_detection_model/weights/best.pt", self._prefix+'Sources/' + model_name + "_best.pt")
            return True
        except Exception as e:
            print(e)
            return False

    def t_store_vf(self):
        try:
            self._validityFrame.graphify()  # optional, only for visualization purposes, not needed for export
            self._validityFrame.export(packageName="..")  # VF package is top level structure
            return True
        except:
            return False