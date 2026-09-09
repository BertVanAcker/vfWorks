#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************

import click

from vfworks.commands.examples import example_cmds


@click.group(help="vfWorks command line tool")
def cli():
    pass


cli.add_command(example_cmds)


if __name__ == '__main__':
    cli()
