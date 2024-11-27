#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from vfworks.metamodels.common import *
from vfworks.utils.constants import *

class Monitor(baseElement):

    def __init__(self, name='tbd', description='tbd',type=MonitorType.PROPERTY_RANGE,status=StatusType.,observes=None, verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self.type = type
        self.status = status

        # OBSERVED PROPERTIES (POI/INFLUENCE)
        if observes is None:
            self.observes = []
        else:
            self.observes = observes
