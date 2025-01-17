#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.metamodels.model_structure import *
from vfworks.metamodels.validity_frame import *
from vfworks.metamodels.process import *
from vfworks.metamodels.specification import *
from vfworks.metamodels.properties import *

#---------------------------------------------------------------------------------------
#                     PLACEHOLDER FUNCTION TO POPULATE VF PACKAGE                      #
#---------------------------------------------------------------------------------------

#-------------------------VALIDITY FRAME------------------------------------------------
VF = ValidityFrame(name="VF_PACKAGE_TEMPLATE", description="Populate VF package")

#-------------------------SPECIFICATIONS------------------------------------------------
spec1 = Specification(name="SPECIFICATION1", description="THIS IS A DUMMY SPECIFICATION", standard="ISO26262-part3", paragraph="3.1.2 - processes", DOI=None, isMandatory=True)
spec2 = Specification(name="SPECIFICATION2", description="THIS IS A DUMMY SPECIFICATION", standard="ISO26262-part2",paragraph="2.5 - V&V", DOI=None, isMandatory=True)
spec3 = Specification(name="SPECIFICATION3", description="THIS IS A DUMMY SPECIFICATION", standard="ISO26262-part2",paragraph="2.5 - V&V", DOI=None, isMandatory=True)

VF.addSpecification(spec1)
VF.addSpecification(spec2)
VF.addSpecification(spec3)
#------------------------------POI------------------------------------------------------
poi1 = PropertyofInterest(name="propellerLenght",description="The lenght of the propeller",domain=DomainType.MECHANICAL,unit=UnitType.DISTANCE_mm,datatype=DataType.FLOAT_64,min=0,max=100,satisfies=[spec1])
poi2 = PropertyofInterest(name="propellerPitch", description="The pitch of the propeller",domain=DomainType.MECHANICAL, unit=UnitType.ANGLE_RADIANS, datatype=DataType.FLOAT_32,min=0, max=2,satisfies=[spec2])
poi3 = PropertyofInterest(name="motorThrust", description="The pitch of the propeller",domain=DomainType.ELECTRICAL, unit=UnitType.FORCE_N, datatype=DataType.FLOAT_64,min=0, max=10000, satisfies=[spec3])
VF.properties = [poi1, poi2, poi3]

#-------------------------MODEL STRUCTURE-----------------------------------------------
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

structure = ModelStructure(name="BoatModel", inports=inports, outports=outports)
VF.modelStructure = structure   # TODO: THINK WE NEED MORE THAN 1 MODEL STRUCTURE (monitored model has more ports)

#-----------------------------PROCESSES-----------------------------------------------
p_train = Process(name="TrainingProcess",description="Training process",reference="Processes/train.py")
VF.addProcess(p_train)


#-------------------------------EXPORT VF TO TEMPLATE PACKAGE-------------------------------------------
packageName="vf_package"
VF.export(packageName=packageName)


