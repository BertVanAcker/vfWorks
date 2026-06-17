from vfworks.metamodels.validity_frame import ValidityFrame
from vfworks.utils.model.modelLoader import ModelLoader

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
        model_loader = ModelLoader(name="VF_model_loader", validityFrame=frame)
        model_loader.loadModel()
    

vfloader = VFLoader(package_path="")
loaded_vf = vfloader.load()
vfloader.load_model(loaded_vf)
x=1