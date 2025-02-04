#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from Actions.trainer import *
from vfworks.workflows.tasks import *
from vfworks.metamodels.validity_frame import *
from vfworks.workflows.executer import Executer_GUI,Executer_headless

# 0 . Load validity frame in memory
VF = ValidityFrame(name="VF_BLDC", description="Populate VF_BLDC package",config="config.yaml",loadExistingVF=True,VFPackage="")

# 1 . Select model structure used for training
#TODO: set active model structure, default is the first!

# 2 . Instantiate the training class
trainer = trainingActions(name="custom_trainer_class")

# 3 . define the tasks
tasks = {
    "Collect data": trainer.t_collect_data,
    "Prepare data": trainer.t_prepare_data,
    "Load model": trainer.t_load_model,
    "Model fitting": trainer.t_fit_model,
    "Evaluate model": trainer.t_evaluate_model,
    "Store model snapshot": trainer.t_store_model_snapshot
}

# 4. Launch the graphical executer
app = Executer_GUI(tasks=tasks,name="TrainingProcess")
app.root.mainloop()
