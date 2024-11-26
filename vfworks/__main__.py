#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************

import click

from vfworks.commands.version import versionCmds


cli=click.CommandCollection(sources=[versionCmds],help="vfWorks command line tool")


if __name__ == '__main__':
    cli()
