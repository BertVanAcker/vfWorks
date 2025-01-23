#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import os

import vfworks.clientLibraries.vfclpy.data_digest.digest
from vfworks.metamodels.model_structure import *
from vfworks.metamodels.validity_frame import *
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

#-------------------------MODEL STRUCTURE-----------------------------------------------


#-----------------------------PROCESSES-----------------------------------------------


#-------------------------------EXPORT VF_BLDC TO TEMPLATE PACKAGE-------------------------------------------
print(os.getcwd())
packageName="VF_BLDC"
VF.export(packageName=None)     #VF package is current working directory


