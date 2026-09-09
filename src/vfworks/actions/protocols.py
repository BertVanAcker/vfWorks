"""Structural interfaces for implementations of scheduler-facing actions."""

from typing import Protocol

from vfworks.actions.models import (
    CollectDataRequest,
    CollectDataResult,
    EvaluateModelRequest,
    EvaluateModelResult,
    ExportValidityFrameRequest,
    ExportValidityFrameResult,
    FitModelRequest,
    FitModelResult,
    LoadModelRequest,
    LoadModelResult,
    PostprocessModelRequest,
    PostprocessModelResult,
    PrepareDataRequest,
    PrepareDataResult,
)


class ActionProvider(Protocol):
    """Operations a complete vfWorks action implementation may provide.

    Implementations may use injected services internally, but every value that
    crosses a scheduled action boundary is supplied in the request and returned
    in the result. Implementations must not require a previous method call to
    have mutated the same provider instance.
    """

    def collect_data(self, request: CollectDataRequest) -> CollectDataResult: ...

    def prepare_data(self, request: PrepareDataRequest) -> PrepareDataResult: ...

    def load_model(self, request: LoadModelRequest) -> LoadModelResult: ...

    def fit_model(self, request: FitModelRequest) -> FitModelResult: ...

    def evaluate_model(self, request: EvaluateModelRequest) -> EvaluateModelResult: ...

    def postprocess_model(
        self, request: PostprocessModelRequest
    ) -> PostprocessModelResult: ...

    def export_validity_frame(
        self, request: ExportValidityFrameRequest
    ) -> ExportValidityFrameResult: ...
