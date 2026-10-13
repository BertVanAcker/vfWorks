import os
from pathlib import Path

from modelguard import MonitoredModel, HookedTorchModel
from modelguard.utils.hooked_model_helpers import TupleOutputTorchModelAdapter
from screw_assembly_monitoring.reduction_methods import FeatureMatrixReduceMethod
from ultralytics import YOLO


def load_model(modelRef):
    monitored_model = MonitoredModel.from_checkpoint(
        hooked_model=HookedTorchModel(
            model=TupleOutputTorchModelAdapter(
                YOLO(modelRef).model,  # type: ignore
                output_idx=0,
            ),
            hooks_config={
                "latent_vector": "model.model[10].m[0].ffn[1].act",
            },
            reductions={"latent_vector": FeatureMatrixReduceMethod()},
        ),
        path=Path("testLocation/VF_SCREWDETECTION/Sources/monitor_checkpoint.tar"),
    )
    return monitored_model