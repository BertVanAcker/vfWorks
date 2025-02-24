#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from pycaret.anomaly import *
from vfworks.utils.auxiliary import load_model_from_pickle


class ModelLoader(object):
    def __init__(self,name="customLoader",validityFrame = None,verbose=False):
        """Initialize a dataLoader component.

                Parameters
                ----------
                name : string
                    name of the property components

                verbose : bool
                    component verbose execution

                See Also
                --------
                ..

                Examples
                --------
                >> data_loader = dataLoader(verbose=False)

                """

        # --- dataLoader configuration ---
        self._name = name
        self._verbose = verbose
        self._validityframe = validityFrame

        self._model = None


    @property
    def model(self):
        return self._model

    @model.setter
    def model(self,m):
        self._model = m

    #------------------------------------------------------------------------------------------------
    #                               PYCARET specific functions
    #------------------------------------------------------------------------------------------------

    def loadEnvironment(self,data=None,pycaretModel="knn"):
        id = 123
        self._validityframe.logger.info(msg="Setting up pycaret environment with session ID " +id.__str__()+", initializing model type:" + pycaretModel)
        self._trainerSetup = setup(data, session_id=id)
        self._model = create_model(pycaretModel, fraction=0.1)
        return self._model

    def fit(self):
        self._validityframe.logger.info(msg="Training pycaret model")
        self._model_results = assign_model(self._model)
        return self._model_results, self._model

    def loadModel(self,model=None,type="pycaret"):
        if model is None:
            model = self._validityframe.activeModelStructure.modelRef
        if type == "pycaret":
            self._model = load_model(model)
        elif type == "torch":
            self._model = load_model_from_pickle(file_name=model,modelType="torch")
        else:
            self._validityframe.logger.info(msg="Unable to load the model")

