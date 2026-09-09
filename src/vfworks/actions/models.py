"""Request and result models for scheduler-callable vfWorks actions.

Every model contains only JSON-compatible values or :class:`ArtifactRef`
instances. Large or backend-specific objects therefore cross action boundaries
through durable references instead of process-local Python state.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Protocol, Sequence, cast

from vfworks.actions.contracts import (
    ArtifactRef,
    ExecutionInfo,
    JSONValue,
    _copy_json_value,
    _require_non_empty_string,
)
from vfworks.actions.exceptions import (
    InvalidActionInput,
    ModelEvaluationError,
    ModelTrainingError,
    VFWorksActionError,
)

LOGGER = logging.getLogger(__name__)


def _validate_mapping(
    value: Mapping[str, JSONValue], field_name: str
) -> Mapping[str, JSONValue]:
    if not isinstance(value, Mapping):
        raise InvalidActionInput(f"{field_name} must be a mapping")
    copied = _copy_json_value(dict(value), field_name)
    return MappingProxyType(cast(dict[str, JSONValue], copied))


def _validate_metrics(value: Mapping[str, float]) -> Mapping[str, float]:
    if not isinstance(value, Mapping):
        raise InvalidActionInput("metrics must be a mapping")
    result: dict[str, float] = {}
    for name, metric in value.items():
        _require_non_empty_string(name, "metric name")
        if isinstance(metric, bool) or not isinstance(metric, (int, float)):
            raise InvalidActionInput(f"metric {name!r} must be numeric")
        numeric = float(metric)
        if numeric != numeric or numeric in (float("inf"), float("-inf")):
            raise InvalidActionInput(f"metric {name!r} must be finite")
        result[name] = numeric
    return MappingProxyType(result)


def _validate_count(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InvalidActionInput(f"{field_name} must be a non-negative integer")


def _validate_fraction(value: float, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidActionInput(f"{field_name} must be between 0 and 1")
    if not 0 <= value <= 1:
        raise InvalidActionInput(f"{field_name} must be between 0 and 1")


def _validate_columns(value: tuple[str, ...]) -> None:
    if not isinstance(value, tuple):
        raise InvalidActionInput("columns must be a tuple of strings")
    for column in value:
        _require_non_empty_string(column, "column")


def _reject_unknown(value: Mapping[str, Any], allowed: set[str], model: str) -> None:
    if not isinstance(value, Mapping):
        raise InvalidActionInput(f"{model} must be a mapping")
    unknown = set(value) - allowed
    if unknown:
        raise InvalidActionInput(f"{model} contains unknown fields: {sorted(unknown)!r}")


def _required(value: Mapping[str, Any], name: str, model: str) -> Any:
    try:
        return value[name]
    except KeyError as error:
        raise InvalidActionInput(f"{model} is missing required field {name!r}") from error


def _artifact(value: Any, field_name: str) -> ArtifactRef:
    if isinstance(value, ArtifactRef):
        return value
    if isinstance(value, Mapping):
        return ArtifactRef.from_dict(value)
    raise InvalidActionInput(f"{field_name} must be an artifact reference")


def _optional_artifact(value: Any, field_name: str) -> ArtifactRef | None:
    return None if value is None else _artifact(value, field_name)


def _execution(value: Any) -> ExecutionInfo:
    if isinstance(value, ExecutionInfo):
        return value
    if isinstance(value, Mapping):
        return ExecutionInfo.from_dict(value)
    raise InvalidActionInput("execution must be execution metadata")


def _mapping_dict(value: Mapping[str, JSONValue]) -> dict[str, JSONValue]:
    return cast(dict[str, JSONValue], _copy_json_value(dict(value), "mapping"))


@dataclass(frozen=True, slots=True)
class CollectDataRequest:
    validity_frame: ArtifactRef
    experiment_label: str
    execution: ExecutionInfo
    output_media_type: str = "application/x-parquet"
    options: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "validity_frame", _artifact(self.validity_frame, "validity_frame"))
        object.__setattr__(self, "execution", _execution(self.execution))
        _require_non_empty_string(self.experiment_label, "experiment_label")
        _require_non_empty_string(self.output_media_type, "output_media_type")
        object.__setattr__(self, "options", _validate_mapping(self.options, "options"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "validity_frame": self.validity_frame.to_dict(),
            "experiment_label": self.experiment_label,
            "execution": self.execution.to_dict(),
            "output_media_type": self.output_media_type,
            "options": _mapping_dict(self.options),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> CollectDataRequest:
        model = "collect data request"
        _reject_unknown(value, {"validity_frame", "experiment_label", "execution", "output_media_type", "options"}, model)
        return cls(
            validity_frame=_artifact(_required(value, "validity_frame", model), "validity_frame"),
            experiment_label=_required(value, "experiment_label", model),
            execution=_execution(_required(value, "execution", model)),
            output_media_type=value.get("output_media_type", "application/x-parquet"),
            options=value.get("options", {}),
        )


@dataclass(frozen=True, slots=True)
class CollectDataResult:
    dataset: ArtifactRef
    row_count: int
    columns: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "dataset", _artifact(self.dataset, "dataset"))
        _validate_count(self.row_count, "row_count")
        _validate_columns(self.columns)

    def to_dict(self) -> dict[str, JSONValue]:
        return {"dataset": self.dataset.to_dict(), "row_count": self.row_count, "columns": list(self.columns)}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> CollectDataResult:
        model = "collect data result"
        _reject_unknown(value, {"dataset", "row_count", "columns"}, model)
        columns = _required(value, "columns", model)
        if not isinstance(columns, list) or not all(isinstance(item, str) for item in columns):
            raise InvalidActionInput("columns must be a list of strings")
        return cls(
            dataset=_artifact(_required(value, "dataset", model), "dataset"),
            row_count=_required(value, "row_count", model),
            columns=tuple(columns),
        )


@dataclass(frozen=True, slots=True)
class PrepareDataRequest:
    dataset: ArtifactRef
    execution: ExecutionInfo
    train_fraction: float = 0.6
    test_fraction: float = 0.2
    shuffle: bool = True
    random_seed: int | None = None
    options: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "dataset", _artifact(self.dataset, "dataset"))
        object.__setattr__(self, "execution", _execution(self.execution))
        _validate_fraction(self.train_fraction, "train_fraction")
        _validate_fraction(self.test_fraction, "test_fraction")
        if self.train_fraction + self.test_fraction > 1:
            raise InvalidActionInput("train_fraction plus test_fraction must not exceed 1")
        if not isinstance(self.shuffle, bool):
            raise InvalidActionInput("shuffle must be a boolean")
        if self.random_seed is not None and (isinstance(self.random_seed, bool) or not isinstance(self.random_seed, int)):
            raise InvalidActionInput("random_seed must be an integer")
        object.__setattr__(self, "options", _validate_mapping(self.options, "options"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "dataset": self.dataset.to_dict(), "execution": self.execution.to_dict(),
            "train_fraction": self.train_fraction, "test_fraction": self.test_fraction,
            "shuffle": self.shuffle, "random_seed": self.random_seed,
            "options": _mapping_dict(self.options),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> PrepareDataRequest:
        model = "prepare data request"
        allowed = {"dataset", "execution", "train_fraction", "test_fraction", "shuffle", "random_seed", "options"}
        _reject_unknown(value, allowed, model)
        return cls(
            dataset=_artifact(_required(value, "dataset", model), "dataset"),
            execution=_execution(_required(value, "execution", model)),
            train_fraction=value.get("train_fraction", 0.6), test_fraction=value.get("test_fraction", 0.2),
            shuffle=value.get("shuffle", True), random_seed=value.get("random_seed"), options=value.get("options", {}),
        )


@dataclass(frozen=True, slots=True)
class PrepareDataResult:
    training_dataset: ArtifactRef
    test_dataset: ArtifactRef
    validation_dataset: ArtifactRef | None
    training_row_count: int
    test_row_count: int
    validation_row_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "training_dataset", _artifact(self.training_dataset, "training_dataset"))
        object.__setattr__(self, "test_dataset", _artifact(self.test_dataset, "test_dataset"))
        object.__setattr__(self, "validation_dataset", _optional_artifact(self.validation_dataset, "validation_dataset"))
        _validate_count(self.training_row_count, "training_row_count")
        _validate_count(self.test_row_count, "test_row_count")
        _validate_count(self.validation_row_count, "validation_row_count")
        if self.validation_dataset is None and self.validation_row_count:
            raise InvalidActionInput("validation_row_count must be zero without a validation dataset")

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "training_dataset": self.training_dataset.to_dict(),
            "test_dataset": self.test_dataset.to_dict(),
            "validation_dataset": None if self.validation_dataset is None else self.validation_dataset.to_dict(),
            "training_row_count": self.training_row_count, "test_row_count": self.test_row_count,
            "validation_row_count": self.validation_row_count,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> PrepareDataResult:
        model = "prepare data result"
        allowed = {"training_dataset", "test_dataset", "validation_dataset", "training_row_count", "test_row_count", "validation_row_count"}
        _reject_unknown(value, allowed, model)
        return cls(
            training_dataset=_artifact(_required(value, "training_dataset", model), "training_dataset"),
            test_dataset=_artifact(_required(value, "test_dataset", model), "test_dataset"),
            validation_dataset=_optional_artifact(value.get("validation_dataset"), "validation_dataset"),
            training_row_count=_required(value, "training_row_count", model),
            test_row_count=_required(value, "test_row_count", model),
            validation_row_count=value.get("validation_row_count", 0),
        )


@dataclass(frozen=True, slots=True)
class LoadModelRequest:
    model: ArtifactRef
    backend: str
    execution: ExecutionInfo
    options: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "model", _artifact(self.model, "model"))
        object.__setattr__(self, "execution", _execution(self.execution))
        _require_non_empty_string(self.backend, "backend")
        object.__setattr__(self, "options", _validate_mapping(self.options, "options"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {"model": self.model.to_dict(), "backend": self.backend, "execution": self.execution.to_dict(), "options": _mapping_dict(self.options)}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> LoadModelRequest:
        model = "load model request"
        _reject_unknown(value, {"model", "backend", "execution", "options"}, model)
        return cls(
            model=_artifact(_required(value, "model", model), "model"), backend=_required(value, "backend", model),
            execution=_execution(_required(value, "execution", model)), options=value.get("options", {}),
        )


@dataclass(frozen=True, slots=True)
class LoadModelResult:
    model: ArtifactRef
    backend: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "model", _artifact(self.model, "model"))
        _require_non_empty_string(self.backend, "backend")

    def to_dict(self) -> dict[str, JSONValue]:
        return {"model": self.model.to_dict(), "backend": self.backend}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> LoadModelResult:
        model = "load model result"
        _reject_unknown(value, {"model", "backend"}, model)
        return cls(model=_artifact(_required(value, "model", model), "model"), backend=_required(value, "backend", model))


@dataclass(frozen=True, slots=True)
class FitModelRequest:
    training_dataset: ArtifactRef
    model_specification: ArtifactRef
    backend: str
    execution: ExecutionInfo
    validation_dataset: ArtifactRef | None = None
    parameters: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "training_dataset", _artifact(self.training_dataset, "training_dataset"))
        object.__setattr__(self, "model_specification", _artifact(self.model_specification, "model_specification"))
        object.__setattr__(self, "validation_dataset", _optional_artifact(self.validation_dataset, "validation_dataset"))
        object.__setattr__(self, "execution", _execution(self.execution))
        _require_non_empty_string(self.backend, "backend")
        object.__setattr__(self, "parameters", _validate_mapping(self.parameters, "parameters"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "training_dataset": self.training_dataset.to_dict(), "model_specification": self.model_specification.to_dict(),
            "backend": self.backend, "execution": self.execution.to_dict(),
            "validation_dataset": None if self.validation_dataset is None else self.validation_dataset.to_dict(),
            "parameters": _mapping_dict(self.parameters),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> FitModelRequest:
        model = "fit model request"
        allowed = {"training_dataset", "model_specification", "backend", "execution", "validation_dataset", "parameters"}
        _reject_unknown(value, allowed, model)
        return cls(
            training_dataset=_artifact(_required(value, "training_dataset", model), "training_dataset"),
            model_specification=_artifact(_required(value, "model_specification", model), "model_specification"),
            backend=_required(value, "backend", model), execution=_execution(_required(value, "execution", model)),
            validation_dataset=_optional_artifact(value.get("validation_dataset"), "validation_dataset"),
            parameters=value.get("parameters", {}),
        )


@dataclass(frozen=True, slots=True)
class FitModelResult:
    model: ArtifactRef
    metrics: Mapping[str, float] = field(default_factory=dict)
    training_output: ArtifactRef | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "model", _artifact(self.model, "model"))
        object.__setattr__(self, "training_output", _optional_artifact(self.training_output, "training_output"))
        object.__setattr__(self, "metrics", _validate_metrics(self.metrics))

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "model": self.model.to_dict(), "metrics": dict(self.metrics),
            "training_output": None if self.training_output is None else self.training_output.to_dict(),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> FitModelResult:
        model = "fit model result"
        _reject_unknown(value, {"model", "metrics", "training_output"}, model)
        return cls(
            model=_artifact(_required(value, "model", model), "model"), metrics=value.get("metrics", {}),
            training_output=_optional_artifact(value.get("training_output"), "training_output"),
        )


@dataclass(frozen=True, slots=True)
class EvaluateModelRequest:
    model: ArtifactRef
    dataset: ArtifactRef
    backend: str
    execution: ExecutionInfo
    requirements: ArtifactRef | None = None
    parameters: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "model", _artifact(self.model, "model"))
        object.__setattr__(self, "dataset", _artifact(self.dataset, "dataset"))
        object.__setattr__(self, "requirements", _optional_artifact(self.requirements, "requirements"))
        object.__setattr__(self, "execution", _execution(self.execution))
        _require_non_empty_string(self.backend, "backend")
        object.__setattr__(self, "parameters", _validate_mapping(self.parameters, "parameters"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "model": self.model.to_dict(), "dataset": self.dataset.to_dict(), "backend": self.backend,
            "execution": self.execution.to_dict(),
            "requirements": None if self.requirements is None else self.requirements.to_dict(),
            "parameters": _mapping_dict(self.parameters),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> EvaluateModelRequest:
        model = "evaluate model request"
        allowed = {"model", "dataset", "backend", "execution", "requirements", "parameters"}
        _reject_unknown(value, allowed, model)
        return cls(
            model=_artifact(_required(value, "model", model), "model"), dataset=_artifact(_required(value, "dataset", model), "dataset"),
            backend=_required(value, "backend", model), execution=_execution(_required(value, "execution", model)),
            requirements=_optional_artifact(value.get("requirements"), "requirements"), parameters=value.get("parameters", {}),
        )


@dataclass(frozen=True, slots=True)
class EvaluateModelResult:
    metrics: Mapping[str, float]
    requirements_satisfied: bool
    report: ArtifactRef | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "report", _optional_artifact(self.report, "report"))
        object.__setattr__(self, "metrics", _validate_metrics(self.metrics))
        if not isinstance(self.requirements_satisfied, bool):
            raise InvalidActionInput("requirements_satisfied must be a boolean")

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "metrics": dict(self.metrics), "requirements_satisfied": self.requirements_satisfied,
            "report": None if self.report is None else self.report.to_dict(),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> EvaluateModelResult:
        model = "evaluate model result"
        _reject_unknown(value, {"metrics", "requirements_satisfied", "report"}, model)
        return cls(
            metrics=_required(value, "metrics", model),
            requirements_satisfied=_required(value, "requirements_satisfied", model),
            report=_optional_artifact(value.get("report"), "report"),
        )


@dataclass(frozen=True, slots=True)
class PostprocessModelRequest:
    model: ArtifactRef
    backend: str
    execution: ExecutionInfo
    output_media_type: str
    parameters: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "model", _artifact(self.model, "model"))
        object.__setattr__(self, "execution", _execution(self.execution))
        _require_non_empty_string(self.backend, "backend")
        _require_non_empty_string(self.output_media_type, "output_media_type")
        object.__setattr__(self, "parameters", _validate_mapping(self.parameters, "parameters"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "model": self.model.to_dict(), "backend": self.backend, "execution": self.execution.to_dict(),
            "output_media_type": self.output_media_type, "parameters": _mapping_dict(self.parameters),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> PostprocessModelRequest:
        model = "postprocess model request"
        allowed = {"model", "backend", "execution", "output_media_type", "parameters"}
        _reject_unknown(value, allowed, model)
        return cls(
            model=_artifact(_required(value, "model", model), "model"), backend=_required(value, "backend", model),
            execution=_execution(_required(value, "execution", model)), output_media_type=_required(value, "output_media_type", model),
            parameters=value.get("parameters", {}),
        )


@dataclass(frozen=True, slots=True)
class PostprocessModelResult:
    model: ArtifactRef
    source_model: ArtifactRef

    def __post_init__(self) -> None:
        object.__setattr__(self, "model", _artifact(self.model, "model"))
        object.__setattr__(self, "source_model", _artifact(self.source_model, "source_model"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {"model": self.model.to_dict(), "source_model": self.source_model.to_dict()}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> PostprocessModelResult:
        model = "postprocess model result"
        _reject_unknown(value, {"model", "source_model"}, model)
        return cls(
            model=_artifact(_required(value, "model", model), "model"),
            source_model=_artifact(_required(value, "source_model", model), "source_model"),
        )


@dataclass(frozen=True, slots=True)
class ExportValidityFrameRequest:
    validity_frame: ArtifactRef
    destination_uri: str
    execution: ExecutionInfo
    model: ArtifactRef | None = None
    options: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "validity_frame", _artifact(self.validity_frame, "validity_frame"))
        object.__setattr__(self, "model", _optional_artifact(self.model, "model"))
        object.__setattr__(self, "execution", _execution(self.execution))
        _require_non_empty_string(self.destination_uri, "destination_uri")
        from urllib.parse import urlparse
        if not urlparse(self.destination_uri).scheme:
            raise InvalidActionInput("destination_uri must include a URI scheme")
        object.__setattr__(self, "options", _validate_mapping(self.options, "options"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "validity_frame": self.validity_frame.to_dict(), "destination_uri": self.destination_uri,
            "execution": self.execution.to_dict(), "model": None if self.model is None else self.model.to_dict(),
            "options": _mapping_dict(self.options),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ExportValidityFrameRequest:
        model = "export validity frame request"
        allowed = {"validity_frame", "destination_uri", "execution", "model", "options"}
        _reject_unknown(value, allowed, model)
        return cls(
            validity_frame=_artifact(_required(value, "validity_frame", model), "validity_frame"),
            destination_uri=_required(value, "destination_uri", model), execution=_execution(_required(value, "execution", model)),
            model=_optional_artifact(value.get("model"), "model"), options=value.get("options", {}),
        )


@dataclass(frozen=True, slots=True)
class ExportValidityFrameResult:
    package: ArtifactRef
    manifest: ArtifactRef | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "package", _artifact(self.package, "package"))
        object.__setattr__(self, "manifest", _optional_artifact(self.manifest, "manifest"))

    def to_dict(self) -> dict[str, JSONValue]:
        return {"package": self.package.to_dict(), "manifest": None if self.manifest is None else self.manifest.to_dict()}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ExportValidityFrameResult:
        model = "export validity frame result"
        _reject_unknown(value, {"package", "manifest"}, model)
        return cls(
            package=_artifact(_required(value, "package", model), "package"),
            manifest=_optional_artifact(value.get("manifest"), "manifest"),
        )


@dataclass(frozen=True, slots=True)
class BackendFitRequest:
    """Backend-facing model fit request containing materialized row data."""

    public_request: FitModelRequest
    training_rows: Sequence[Mapping[str, JSONValue]]
    validation_rows: Sequence[Mapping[str, JSONValue]] | None = None


@dataclass(frozen=True, slots=True)
class FittedModel:
    """Model payload returned by a backend before artifact persistence."""

    payload: Mapping[str, JSONValue]
    metrics: Mapping[str, float] = field(default_factory=dict)
    media_type: str = "application/vnd.vfworks.model+json"

    def __post_init__(self) -> None:
        _require_non_empty_string(self.media_type, "media_type")
        object.__setattr__(self, "payload", _validate_mapping(self.payload, "payload"))
        object.__setattr__(self, "metrics", _validate_metrics(self.metrics))


class TrainingDatasetStore(Protocol):
    """Storage boundary used by fit actions to read prepared datasets."""

    def read_rows(self, reference: ArtifactRef) -> Sequence[Mapping[str, JSONValue]]: ...


class ModelArtifactStore(Protocol):
    """Storage boundary used by fit actions to persist trained models."""

    def write_json(
        self,
        document: Mapping[str, JSONValue],
        *,
        media_type: str,
        metadata: Mapping[str, JSONValue],
    ) -> ArtifactRef: ...


class ModelBackend(Protocol):
    """Backend boundary for fitting a model from materialized training rows."""

    def fit(self, request: BackendFitRequest) -> FittedModel: ...


def fit_model(
    request: FitModelRequest,
    *,
    dataset_store: TrainingDatasetStore,
    model_store: ModelArtifactStore,
    model_backend: ModelBackend,
) -> FitModelResult:
    """Fit a model from dataset artifacts and persist the trained model artifact."""

    try:
        LOGGER.info(
            "fitting model",
            extra={
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
                "attempt": request.execution.attempt,
                "backend": request.backend,
                "training_dataset_uri": request.training_dataset.uri,
                "model_specification_uri": request.model_specification.uri,
            },
        )
        training_rows = dataset_store.read_rows(request.training_dataset)
        validation_rows = (
            dataset_store.read_rows(request.validation_dataset)
            if request.validation_dataset is not None
            else None
        )
        fitted = model_backend.fit(
            BackendFitRequest(
                public_request=request,
                training_rows=training_rows,
                validation_rows=validation_rows,
            )
        )
        model = model_store.write_json(
            fitted.payload,
            media_type=fitted.media_type,
            metadata={
                "backend": request.backend,
                "model_specification_uri": request.model_specification.uri,
                "training_dataset_uri": request.training_dataset.uri,
                "validation_dataset_uri": (
                    None
                    if request.validation_dataset is None
                    else request.validation_dataset.uri
                ),
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
                "attempt": request.execution.attempt,
            },
        )
        return FitModelResult(model=model, metrics=fitted.metrics)
    except VFWorksActionError:
        raise
    except Exception as error:
        raise ModelTrainingError(
            "failed to fit model",
            details={
                "backend": request.backend,
                "training_dataset_uri": request.training_dataset.uri,
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
            },
        ) from error


@dataclass(frozen=True, slots=True)
class BackendEvaluateRequest:
    """Backend-facing evaluation request with materialized model and rows."""

    public_request: EvaluateModelRequest
    model_document: Mapping[str, JSONValue]
    evaluation_rows: Sequence[Mapping[str, JSONValue]]
    requirements_document: Mapping[str, JSONValue] | None = None


@dataclass(frozen=True, slots=True)
class ModelEvaluation:
    """Evaluation result returned by a backend before public result shaping."""

    metrics: Mapping[str, float]
    requirements_satisfied: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "metrics", _validate_metrics(self.metrics))
        if not isinstance(self.requirements_satisfied, bool):
            raise InvalidActionInput("requirements_satisfied must be a boolean")


class ModelDocumentStore(Protocol):
    """Storage boundary used by evaluation actions to read model documents."""

    def read_json(self, reference: ArtifactRef) -> Mapping[str, JSONValue]: ...


class ModelEvaluator(Protocol):
    """Backend boundary for evaluating a model against materialized rows."""

    def evaluate(self, request: BackendEvaluateRequest) -> ModelEvaluation: ...


def evaluate_model(
    request: EvaluateModelRequest,
    *,
    dataset_store: TrainingDatasetStore,
    model_store: ModelDocumentStore,
    model_evaluator: ModelEvaluator,
) -> EvaluateModelResult:
    """Evaluate a model artifact against a dataset artifact."""

    try:
        LOGGER.info(
            "evaluating model",
            extra={
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
                "attempt": request.execution.attempt,
                "backend": request.backend,
                "model_uri": request.model.uri,
                "dataset_uri": request.dataset.uri,
            },
        )
        model_document = model_store.read_json(request.model)
        evaluation_rows = dataset_store.read_rows(request.dataset)
        requirements_document = (
            model_store.read_json(request.requirements)
            if request.requirements is not None
            else None
        )
        evaluation = model_evaluator.evaluate(
            BackendEvaluateRequest(
                public_request=request,
                model_document=model_document,
                evaluation_rows=evaluation_rows,
                requirements_document=requirements_document,
            )
        )
        return EvaluateModelResult(
            metrics=evaluation.metrics,
            requirements_satisfied=evaluation.requirements_satisfied,
        )
    except VFWorksActionError:
        raise
    except Exception as error:
        raise ModelEvaluationError(
            "failed to evaluate model",
            details={
                "backend": request.backend,
                "model_uri": request.model.uri,
                "dataset_uri": request.dataset.uri,
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
            },
        ) from error
