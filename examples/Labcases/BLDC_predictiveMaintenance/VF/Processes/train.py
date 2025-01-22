#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from Actions.userActions import *
from vfworks.workflows.tasks import *
from vfworks.workflows.executer import Executer_GUI,Executer_headless

# 1 . define the tasks
tasks = {
    "Collect data": t_collect_data,
    "Prepare data": t_prepare_data,
    "user-specified pre-processing":t_user_preprocessing,
    "Load model": t_load_model,
    "Model fitting": t_fit_model,
    "Evaluate model": t_evaluate_model,
    "Model post-processing": t_postprocess_model
}

# 2. Launch the graphical executer
app = Executer_GUI(tasks=tasks,name="TrainingProcess")
app.root.mainloop()
