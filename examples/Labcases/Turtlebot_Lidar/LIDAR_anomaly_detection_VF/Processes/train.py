"""Training entry point. Imports are side-effect free; execution is synchronous."""

from pathlib import Path


def build_tasks():
    import importlib.util
    from vfworks.metamodels.validity_frame import ValidityFrame

    trainer_file = Path(__file__).resolve().parent / "Actions" / "trainer.py"
    spec = importlib.util.spec_from_file_location("example_training_actions", trainer_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    VF = ValidityFrame(name="VF_TORCH", description="Populate VF_TORCH package",config="../config.yaml",loadExistingVF=True,VFPackage="../")
    VF.setActiveModelStructure(name="anomalyDetector_1D")
    trainer = module.trainingActions(name='custom_trainer_class', validityFrame=VF)
    tasks = {
        "Collect data": trainer.t_collect_data,
        "Validate data": trainer.t_validate_data,
        "Process data": trainer.t_prepare_data,
        "Load model": trainer.t_load_model,
        "Model fitting": trainer.t_fit_model,
        "Evaluate model": trainer.t_evaluate_model,
        "Store model snapshot - pickled": trainer.t_store_model_snapshot_pickled,
        #"Store model snapshot - onnx": trainer.t_store_model_snapshot,
        "Update validity frame package": trainer.t_store_vf
    }
    return tasks

def main():
    import os

    previous = Path.cwd()
    os.chdir(Path(__file__).resolve().parent)
    try:
        for name, action in build_tasks().items():
            if action() is False:
                raise RuntimeError(f"Training task {name!r} failed")
    finally:
        os.chdir(previous)


if __name__ == "__main__":
    main()
