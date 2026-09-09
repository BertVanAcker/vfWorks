#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from os import mkdir
from os.path import exists, dirname, join, isfile
import jinja2


def vf2swc(vf=None,path="output/generated"):

    if not exists(path):
        mkdir(path)

    # Initialize the Templates engine.
    this_folder = dirname(__file__)
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(this_folder), trim_blocks=True, lstrip_blocks=True)

    # Load the template
    template = jinja_env.get_template('templates/swc_py.template')
    #templateConfig = jinja_env.get_template('templates/swc_config.template')
    #templateMessages = jinja_env.get_template('templates/messages_py.template')

    folder = path + "/" + vf.name + "_deploy"
    if not exists(folder):
        mkdir(folder)
    # 1. Generate code from AADL processes
    with open(join(folder, vf.name + "_deploy.py"), 'w') as f:
        f.write(template.render(vf=vf))



