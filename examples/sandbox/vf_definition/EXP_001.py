from vfworks.metamodels.monitors import Monitor
from vfworks.metamodels.validity_frame import *
from vfworks.metamodels.properties import *
from vfworks.metamodels.specification import *
from vfworks.metamodels.model_structure import *
from vfworks.utils.constants import *

def dummyVF():
    #-------------------------------------------------------------------------------------
    #                           SPECIFY MODEL SPECIFICATIONS
    #-------------------------------------------------------------------------------------
    spec1 = Specification(name="SPECIFICATION1",description="THIS IS A DUMMY SPECIFICATION",standard="ISO26262-part3",paragraph="3.1.2 - processes",DOI=None,isMandatory=True)
    spec2 = Specification(name="SPECIFICATION2",description="THIS IS A DUMMY SPECIFICATION",standard="ISO26262-part2",paragraph="2.5 - V&V",DOI=None,isMandatory=True)
    spec3 = Specification(name="SPECIFICATION3", description="THIS IS A DUMMY SPECIFICATION", standard="ISO26262-part2",paragraph="2.5 - V&V", DOI=None, isMandatory=True)
    #-------------------------------------------------------------------------------------
    #                           SPECIFY VALIDITY FRAME
    #-------------------------------------------------------------------------------------
    vf = ValidityFrame(name="VF_example",description="This is a dummy validity frame",specifications=[spec1,spec2,spec3],verbose=True)

    # -------------------------------------------------------------------------------------
    #                           SPECIFY POI and IF
    # -------------------------------------------------------------------------------------
    poi1 = PropertyofInterest(name="propellerLenght",description="The lenght of the propeller",domain=DomainType.MECHANICAL,unit=UnitType.DISTANCE_mm,datatype=DataType.FLOAT_64,min=0,max=100,satisfies=[spec1])
    poi2 = PropertyofInterest(name="propellerPitch", description="The pitch of the propeller",domain=DomainType.MECHANICAL, unit=UnitType.ANGLE_RADIANS, datatype=DataType.FLOAT_32,min=0, max=2,satisfies=[spec2])
    poi3 = PropertyofInterest(name="motorThrust", description="The pitch of the propeller",domain=DomainType.ELECTRICAL, unit=UnitType.FORCE_N, datatype=DataType.FLOAT_64,min=0, max=10000, satisfies=[spec3])
    vf.properties = [poi1, poi2, poi3]
    #-------------------------------------------------------------------------------------
    #                           SPECIFY MODEL STRUCTURE
    #-------------------------------------------------------------------------------------
    in1 = Inport(name="in1",description="input1",domain=DomainType.MECHANICAL,unit=UnitType.DISTANCE_mm,datatype=DataType.FLOAT_32,min=0,max=100,mapping=[poi1])
    in2 = Inport(name="in2",description="input2",domain=DomainType.MECHANICAL,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_32,min=0,max=2,mapping=[poi2])
    out1 = Outport(name="out1",description="output1",domain=DomainType.ELECTRICAL,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_64,min=0,max=10000,mapping=[poi3])
    ms = ModelStructure(name="MS_example",description="This is a dummy model structure",inports=[in1,in2],outports=[out1])
    vf.modelStructure = ms

    # -------------------------------------------------------------------------------------
    #                           SPECIFY MONITORS
    # -------------------------------------------------------------------------------------
    monitor1= Monitor(name="poi1_monitor", description="Monitor for the poi1", type=PropertyType.PROPERTY_RANGE, status=StatusType.UNKNOWN, observes=[poi1])
    monitor2 = Monitor(name="poi2_monitor", description="Monitor for the poi2", type=PropertyType.PROPERTY_RANGE, status=StatusType.UNKNOWN, observes=[poi2])
    monitor3 = Monitor(name="poi3_monitor", description="Monitor for the poi3", type=PropertyType.PROPERTY_RANGE, status=StatusType.UNKNOWN, observes=[poi3])
    vf.monitors = [monitor1,monitor2,monitor3]

    # -------------------------------------------------------------------------------------
    #                           SPECIFY MODEL
    # -------------------------------------------------------------------------------------
    vf.modelReference = "input/model1.py"

    return vf



if __name__ == "__main__":
    vf = dummyVF()
    # before monitor status update
    print("----------MONITORS NOT RUNNING----------------")
    vf.check_specifications()
    # monitors all valid
    print("----------MONITORS REPORTED VALID----------------")
    vf.monitors[0].status = StatusType.VALID
    vf.monitors[1].status = StatusType.VALID
    vf.monitors[2].status = StatusType.VALID
    vf.check_specifications()
    # one monitor reports invalid
    print("----------MONITORS REPORTED VALID OR INVALID----------------")
    vf.monitors[0].status = StatusType.VALID
    vf.monitors[1].status = StatusType.VALID
    vf.monitors[2].status = StatusType.INVALID
    vf.check_specifications()

    x=1
