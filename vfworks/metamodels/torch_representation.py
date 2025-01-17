from vfworks.metamodels.common import *
from vfworks.utils.constants import *
import torch
import pickle

class TorchRepresentation(baseElement):

    def __init__(self,name='tbd',description='tbd',model_structure=None,model_location=None,scalars_location=None,verbose=False):
        super().__init__(name, description, verbose)

        self.model_structure = model_structure

        # load ML model
        if model_location is None:
            self.model = None
        else:
            self.model = torch.load(model_location)

        # import and load scalars used for normalized models (if applicable)
        if scalars_location is None:
            self.scalars = None
        else:
            with open(scalars_location, "rb") as f:
                self.scalars = pickle.load(f)


    def predict(self):
        if self.model is not None:
            pass

    def import_model(self, model_location):
        self.model = torch.load(model_location)
        return