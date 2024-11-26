#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************

import click
from vfworks import __version__


@click.group()
@click.pass_context
def versionCmds():
    pass

@versionCmds.command()
def version():
    """Display the current version."""
    version = __version__
    click.echo("vfWorks v"+version)