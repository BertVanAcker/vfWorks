from vfworks.metamodels.validity_frame import ValidityFrame

class VFLoader:
    def __init__(self, package_path):
        self.package_path = package_path
        self.name = "Loaded_VF"
        self.model = None

    def load(self) -> ValidityFrame:
        # Load the VF from the package path
        # This is a placeholder implementation and should be replaced with actual loading logic
        return ValidityFrame(name="Loaded_VF", description="Loaded VF from package", VFPackage=self.package_path, loadExistingVF=True, verbose=True)
    
    def load_model(self, frame):
        model = frame.get_current_active_model()
        return model
    def load_monitors(self, frame):
        monitors = frame.runtime_monitors
        return monitors
    

vfloader = VFLoader(package_path="VF_SCREWDETECTION")
loaded_vf = vfloader.load()
loaded_vf.graphify()
loaded_vf.setActiveModelStructure(loaded_vf.modelStructures[0].GUID)
model = vfloader.load_model(loaded_vf)
monitors = vfloader.load_monitors(loaded_vf)
for monitor in monitors:
    monitor.validate_point({"colorRed": 20, "colorGreen": 255, "colorBlue": 255})
loaded_vf.graphify()
x=1