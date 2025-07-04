#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.metamodels.validity_frame import *
from vfworks.transformations.transformations import *

#load the VF
VF = ValidityFrame(name="VF_TEST", description="Populate VF_TEST package",config="input/VF_TEST/config.yaml",loadExistingVF=True,VFPackage="input/VF_TEST/")
x=1

vf2swc(vf=VF,path="output/generated")