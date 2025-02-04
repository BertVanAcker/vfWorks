#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.metamodels.validity_frame import *

#-------------------------LOAD EXISTING VF------------------------------------------------
VF = ValidityFrame(name="VF_BLDC", description="Populate VF_BLDC package",config="config.yaml",loadExistingVF=True,VFPackage="")
x=1