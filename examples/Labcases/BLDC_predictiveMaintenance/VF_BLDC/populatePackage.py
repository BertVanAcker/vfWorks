#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import os

from vfworks.metamodels.validity_frame import *
from vfworks.metamodels.model_structure import *
from vfworks.metamodels.properties import *
from vfworks.clientLibraries.vfclpy.data_digest.digest import remoteExperiments
from vfworks.metamodels.experiment import *
import yaml

#---------------------------------------------------------------------------------------
#                     PLACEHOLDER FUNCTION TO POPULATE VF_BLDC PACKAGE                      #
#---------------------------------------------------------------------------------------

#-------------------------VALIDITY FRAME------------------------------------------------
VF = ValidityFrame(name="VF_BLDC", description="Populate VF_BLDC package")
#-------------------------Real-World EXPERIMENTS----------------------------------------
#ASSUMPTIONS: measurements are available in the vfWorks back-end!

exp_remote = remoteExperiments(config='config.yaml',VFName=VF.name)
VF.experiments = exp_remote.loadExperiments(measerementStorage="csv")      #full= store both in class as csv | csv= store only in csv for limiting the metadata size

#-------------------------SPECIFICATIONS------------------------------------------------

#------------------------------POI------------------------------------------------------
poi1 = PropertyofInterest(name="Power",description="Electrical power of the BLDC motor",domain=DomainType.ELECTRICAL,unit=UnitType.Power_Watt,datatype=DataType.FLOAT_64,min=-50,max=100,satisfies=None)
poi2 = PropertyofInterest(name="Anomaly",description="Classification of anomaly",domain=DomainType.NONE,unit=UnitType.UNIT_none,datatype=DataType.INTEGER_8,min=0,max=1,satisfies=None)
poi3 = PropertyofInterest(name="AnomalyScore",description="Classification score of anomaly",domain=DomainType.NONE,unit=UnitType.UNIT_none,datatype=DataType.FLOAT_64,min=-50,max=50,satisfies=None)

VF.addProperty(poi1)
VF.addProperty(poi2)
VF.addProperty(poi3)

#-----------------POI LINKING TO EXPERIMENT MEASUREMENTS--------------------------------
VF.assign_poi2measurement(poi=poi1,measurementName="power")

#-------------------------MODEL STRUCTURE-----------------------------------------------
IN1 = Inport(name="power", unit=UnitType.Power_Watt)
IN1.add_mapping_relation(poi1)

OUT1 = Outport(name="anomaly", unit=UnitType.UNIT_none)
OUT1.add_mapping_relation(poi2)
OUT2= Outport(name="anomalyScore", unit=UnitType.UNIT_none)
OUT2.add_mapping_relation(poi2)



structure = ModelStructure(name="anomalyDetector", inports=[IN1], outports=[OUT1,OUT2])
VF.modelStructure = structure
#-----------------------------PROCESSES-----------------------------------------------


#-------------------------------EXPORT VF_BLDC TO TEMPLATE PACKAGE-------------------------------------------
print(os.getcwd())
packageName="VF_BLDC"
VF.export(packageName=None)     #VF package is current working directory


