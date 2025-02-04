#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import pandas as pd
from pycaret.anomaly import *
class trainingActions(object):
    def __init__(self, name="userActions class"):
        self._name = name

        self.data_RAW = None
        self.data_train = None
        self.data_test = None

    def t_collect_data(self):
        try:
            print("WARNING: Data collection action not implemented yet!")
            #data = pd.read_csv("input/nominal.csv") #TODO: resolve via model structure, and fill self.data_RAW

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
            self.trainerSetup = setup(self.data, session_id=123)
            # 3. Define KNN model
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
            save_model(self.model, 'Sources/model')     #TODO: store model with GUID!!
            return True
        except:
            return False