from vfworks.metamodels.validity_frame import ValidityFrame
from vfworks.utils.constants import StatusType


def validate_point_override(value):
    return True
    
VF = ValidityFrame(name="VF_TORCH", description="Populate VF_TORCH package",config="config.yaml",loadExistingVF=True,VFPackage="")
VF.graphify()
for monitor in VF.runtime_monitors:
    monitor.set_validate_point_function(validate_point_override)
    monitor.validate_point(-1,"trust")
    monitor.validate_point(-1,"colorBlue")
VF.graphify()


x=1