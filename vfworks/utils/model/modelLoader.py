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
from ultralytics import YOLO
import importlib.util
import inspect
import os


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
        self._models = []


    @property
    def model(self):
        return self._model

    @model.setter
    def model(self,m):
        self._model = m

    @property
    def models(self):
        return self._models

    @models.setter
    def models(self,ms):
        self._models = ms

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

    def loadModel(self,model_location=None,type="pycaret"):
        if model_location is None:
            model_location = self._validityframe.activeModelStructure.modelRef
        
        # 1. Handle Built-in Model Types
        if type == "pycaret":
            self._model = load_model(model_location)
        elif type == "YOLO":
            self._model = YOLO(model_location)
        elif type == "torch":
            if self._validityframe.activeModelStructure.redundancy == 1:
                self._models.append(load_model_from_pickle(file_name=model_location, modelType="torch"))
            else:
                for model in os.listdir(model_location):
                    self._models.append(load_model_from_pickle(file_name=os.path.join(model_location,model), modelType="torch"))
        # 2. Look for Custom Overrides/Plugins in the Sources Folder
        else:
            # Determine the path to the Sources directory
            # (Adjust this logic depending on how your package tracks its root directory)
            packageName = self._validityframe.package_manager.packageName
            package_root = os.getcwd()  # Or use a reference from self._validityframe
            sources_dir = os.path.join(package_root, packageName, "Resources")
            custom_loader_path = os.path.join(sources_dir, "loaders", f"{type}.py")
            legacy_loader_path = os.path.join(sources_dir, f"{type}.py")

            if not os.path.exists(custom_loader_path) and os.path.exists(legacy_loader_path):
                custom_loader_path = legacy_loader_path
            
            if os.path.exists(custom_loader_path):
                try:
                    # Dynamically load the python file as a module
                    spec = importlib.util.spec_from_file_location(type, custom_loader_path)
                    custom_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(custom_module)
                    
                    # Enforce a naming convention for the custom loading function
                    if hasattr(custom_module, "load_model"):
                        # Execute the custom loader and pass necessary context
                        load_model_signature = inspect.signature(custom_module.load_model)
                        if "validityframe" in load_model_signature.parameters:
                            self._model = custom_module.load_model(model_location, validityframe=self._validityframe)
                        else:
                            self._model = custom_module.load_model(model_location)
                        self._validityframe.logger.info(msg=f"Successfully loaded custom model type '{type}'")
                        return self._model
                    else:
                        self._validityframe.logger.error(
                            msg=f"Custom file '{type}.py' found, but it is missing the required 'load_model' function."
                        )
                except Exception as e:
                    self._validityframe.logger.error(msg=f"Failed to execute custom loader '{type}': {str(e)}")
            else:
                self._validityframe.logger.info(msg=f"Unable to load the model. Type '{type}' is unrecognized.")
                return None

