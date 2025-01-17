import pickle

import torch
import numpy as np
from torch import nn

from vfworks.clientLibraries.vfclpy.probe import Probe
from vfworks.metamodels.model_structure import *


class Model(nn.Module):
    def __init__(self, net_location, scalars_location=None):
        super(Model, self).__init__()
        self.net = nn.Sequential(nn.LazyLinear(256), nn.ReLU(),
                                 nn.LazyLinear(256), nn.ReLU(),
                                 nn.LazyLinear(256), nn.ReLU(),
                                 nn.LazyLinear(256), nn.ReLU(),
                                 nn.LazyLinear(256), nn.ReLU(),
                                 nn.LazyLinear(256), nn.ReLU(),
                                 nn.LazyLinear(256), nn.ReLU(),
                                 nn.LazyLinear(256), nn.ReLU(),
                                 nn.LazyLinear(6))
        self.double()
        self.probe = Probe(config="input/config.yaml", storage=False)

        self.load_state_dict(torch.load(net_location, weights_only=False))
        if scalars_location is not None:
            with open(scalars_location, 'rb') as f:
                self.scalars = pickle.load(f)
        else:
            self.scalars = None

    def forward(self, x):
        return self.net(x)

    def predict(self, IN1,IN2,IN3,IN4,IN5,IN6,IN7,IN8,IN9):

        # write inputs to redis
        self.probe.write(key="poi1", message=IN1)
        self.probe.write(key="poi2", message=IN2)
        self.probe.write(key="poi3", message=IN3)
        self.probe.write(key="poi4", message=IN4)
        self.probe.write(key="poi5", message=IN5)
        self.probe.write(key="poi6", message=IN6)
        self.probe.write(key="poi7", message=IN7)
        self.probe.write(key="poi8", message=IN8)
        self.probe.write(key="poi9", message=IN9)

        scalar_in = self.scalars["scaler_in"]
        scalar_out = self.scalars["scaler_out"]

        state = np.array([IN1, IN2, IN3, IN4, IN5, IN6, IN7, IN8, IN9])
        state = scalar_in.transform(state)
        state = torch.tensor(state, dtype=torch.double)
        output = self.net(state)
        output = scalar_out.inverse(output)

        OUT1, OUT2, OUT3, OUT4, OUT5, OUT6 = output[0].item(), output[1].item(), output[2].item(), output[3].item(), \
        output[4].item(), output[5].item()

        self.probe.write(key="poi10", message=OUT1)
        self.probe.write(key="poi11", message=OUT2)
        self.probe.write(key="poi12", message=OUT3)
        self.probe.write(key="poi13", message=OUT4)
        self.probe.write(key="poi14", message=OUT5)
        self.probe.write(key="poi15", message=OUT6)

        return OUT1, OUT2, OUT3, OUT4, OUT5, OUT6



if __name__ == "__main__":
    model = Model('../Boat_Model_VF/input/model.pt', '../Boat_Model_VF/input/scalers.pkl')

    model.predict(5.410456583221194,3.51579246299568e-12,-3.719296635999916e-14,-6.803446694902959e-13,876.8838382981982,-1.8239832400013256e-07,0.0,3.141592653589793,0.0)
