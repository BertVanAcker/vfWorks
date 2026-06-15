#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import torch

import numpy as np
import sklearn.metrics
import tqdm
from click.core import batch

from examples.Labcases.Turtlebot_Lidar.Torch_NN_VF.Sources.CNN_model import LiDAR_CNN
from vfworks.utils.auxiliary import store_as_onnx, store_as_pickled
from scipy.stats import chisquare
from vfworks.utils.data.dataLoader import *
from vfworks.utils.model.modelLoader import *
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, recall_score

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
        self.data_validate = None

        self.model = None

    def t_collect_data(self):
        try:
            #load train data from model structure
            self.data_full = self._data_loader.loadData(experimentLabel="all",prefix=self._prefix,type="pandas",shuffle=True)
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
            # Replace inf values with large finite number
            processed_df = self.data_full.replace([np.inf, -np.inf], 15)

            # Shuffle the dataset
            processed_df = processed_df.sample(frac=1).reset_index(drop=True)

            # Split into train and test sets (60/20/20)
            train_size = int(len(processed_df) * 0.6)
            test_size = int(len(processed_df) * 0.2)
            self.data_train = processed_df.iloc[:train_size]
            self.data_test = processed_df.iloc[train_size:train_size+test_size]
            self.data_validate = processed_df.iloc[train_size + test_size:]

            return True
        except:
            return False

    def t_load_model(self):
        try:
            self.model = LiDAR_CNN()
            return True
        except:
            return False

    def t_fit_model(self):
        try:
            label_map = {"normal":0, "anomaly":1}
            train_data_X = self.data_train.iloc[:, :-1].values.astype(np.float32)
            train_data_Y = self.data_train.iloc[:, -1].map(label_map).values.astype(np.float32)

            test_data_X = self.data_test.iloc[:, :-1].values.astype(np.float32)
            test_data_Y = self.data_test.iloc[:, -1].map(label_map).values.astype(np.float32)

            train_tensor_X = torch.tensor(train_data_X).view(-1, 1, 360)
            train_tensor_Y = torch.tensor(train_data_Y).unsqueeze(1)

            test_tensor_X = torch.tensor(test_data_X).view(-1, 1, 360)
            test_tensor_Y = torch.tensor(test_data_Y).unsqueeze(1)

            optimizer = torch.optim.Adam(self.model.parameters(), lr=0.1)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=10)
            batch_size = 32
            batch_start = torch.arange(0, len(self.data_train), batch_size)

            loss_function = torch.nn.BCEWithLogitsLoss()

            best_loss = float('inf')
            best_weights = None
            epoch_losses = []
            batch_losses = []
            test_losses = []

            num_epochs = 100
            for epoch in range(num_epochs):
                self.model.train()
                with tqdm.tqdm(batch_start, unit='batch', mininterval=0, disable=False, colour='green') as pbar:
                    pbar.set_description(f"Epoch {epoch + 1}/{num_epochs}")
                    for start in pbar:
                        X_batch, y_batch = train_tensor_X[start:start + batch_size], train_tensor_Y[
                                                                                   start:start + batch_size]
                        y_pred = self.model(X_batch)
                        loss = loss_function(y_pred, y_batch)

                        optimizer.zero_grad()
                        loss.backward()
                        optimizer.step()
                        pbar.set_postfix(loss=loss.item())
                        batch_losses.append(loss.item())
                epoch_losses.append(sum(batch_losses) / len(batch_losses))
                batch_losses = []
                self.model.eval()
                y_pred = self.model(test_tensor_X)
                loss = loss_function(y_pred, test_tensor_Y)
                test_losses.append(loss.item())
                if loss.item() < best_loss:
                    best_loss = loss.item()
                    best_weights = self.model.state_dict()
                scheduler.step(loss)

            self.model.load_state_dict(best_weights)
            return True

        except Exception as e:
            print(f"Error in training: {e}")
            return False

    def t_evaluate_model(self):
        try:
            evaluated_features = {"accuracy": [], "recall": [], "precision": []}
            # Split features (all except last col) and labels (last col)
            X_test = self.data_validate.iloc[:, :-1].values.astype(np.float32)
            X_test_tensor = torch.tensor(X_test).view(-1, 1, 360)
            Y_test = self.data_validate.iloc[:, -1]

            evaluation_pass = True

            self.model.eval()
            predictions = self.model(X_test_tensor)

            predictions_mapped = ["anomaly" if p > 0 else "normal" for p in predictions]

            evaluated_features["accuracy"] = sklearn.metrics.accuracy_score(Y_test, predictions_mapped)*100
            evaluated_features["recall"] = sklearn.metrics.recall_score(Y_test, predictions_mapped, pos_label="anomaly")*100
            evaluated_features["precision"] = sklearn.metrics.precision_score(Y_test, predictions_mapped, pos_label="anomaly")*100

            print("----------------EVALUATION METRICS----------------------")
            print("Accuracy: {}".format(evaluated_features["accuracy"]))
            print("Recall: {}".format(evaluated_features["recall"]))
            print("Precision: {}".format(evaluated_features["precision"]))

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