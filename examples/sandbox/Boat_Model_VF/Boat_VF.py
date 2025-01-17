from vfworks.metamodels.model_structure import *
from vfworks.metamodels.validity_frame import *
import pickle


def make_VF():
    inports = [Inport(name="Surge Speed", unit=UnitType.SPEED_M_S),
               Inport(name="Sway Speed", unit=UnitType.SPEED_M_S),
               Inport(name="Yaw Rate", unit=UnitType.ANG_SPEED_RADIANS),
               Inport(name="Heading", unit=UnitType.ANGLE_RADIANS),
               Inport(name="x", unit=UnitType.DISTANCE_m),
               Inport(name="y", unit=UnitType.DISTANCE_m),
               Inport(name="Rudder Angle", unit=UnitType.ANGLE_RADIANS),
               Inport(name="Wind Direction", unit=UnitType.ANGLE_RADIANS),
               Inport(name="Wind Speed", unit=UnitType.SPEED_M_S)
               ]

    outports = [Outport(name="Surge Speed", unit=UnitType.SPEED_M_S),
                Outport(name="Sway Speed", unit=UnitType.SPEED_M_S),
                Outport(name="Yaw Rate", unit=UnitType.ANGLE_RADIANS),
                Outport(name="Heading", unit=UnitType.ANGLE_RADIANS),
                Outport(name="x", unit=UnitType.DISTANCE_m),
                Outport(name="y", unit=UnitType.DISTANCE_m),
                ]

    with open('../Boat_Model_VF/input/scalers.pkl', 'rb') as f:
        scalars = pickle.load(f)

    structure = ModelStructure(name="BoatModel", inports=inports, outports=outports, scalars=scalars)

    VF = ValidityFrame(name="Boat model VF", description="Example VF for boat model",modelStructure=structure, modelRef="examples/sandbox/Boat_Model_VF/input/model.pt", trainingDataReference="examples/sandbox/Boat_Model_VF/input/TrainingData")

    return VF

if __name__ == '__main__':
    vf = make_VF()      #TODO: gives an version error of pickle (1.5.2 pickled file but unpickle 1.6.0 -> not working)
    pass

