"""Scheduler-callable data actions.

The functions in this module are plain synchronous callables. They accept
explicit request objects and injected services so external schedulers can call
them without constructing the vfWorks workflow runner or GUI.
"""

from __future__ import annotations

import logging
import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Mapping, Protocol, cast

from vfworks.actions.contracts import ArtifactRef, JSONValue, _copy_json_value
from vfworks.actions.exceptions import DataPreparationError, VFWorksActionError
from vfworks.actions.models import (
    CollectDataRequest,
    CollectDataResult,
    PrepareDataRequest,
    PrepareDataResult,
)

LOGGER = logging.getLogger(__name__)

TabularRow = Mapping[str, JSONValue]


@dataclass(frozen=True, slots=True)
class CollectedRows:
    """Rows collected from a source system before artifact persistence."""

    rows: Sequence[TabularRow]
    columns: tuple[str, ...]


class TabularDataCollector(Protocol):
    """Source boundary used by collect actions for tabular data."""

    def collect_rows(self, request: CollectDataRequest) -> CollectedRows: ...


class TabularArtifactStore(Protocol):
    """Storage boundary used by data actions for tabular artifacts."""

    def read_rows(self, reference: ArtifactRef) -> Sequence[TabularRow]: ...

    def write_rows(
        self,
        rows: Sequence[TabularRow],
        *,
        media_type: str,
        metadata: Mapping[str, JSONValue],
    ) -> ArtifactRef: ...


def collect_data(
    request: CollectDataRequest,
    *,
    data_collector: TabularDataCollector,
    artifact_store: TabularArtifactStore,
) -> CollectDataResult:
    """Collect tabular source data and persist it as an artifact."""

    try:
        LOGGER.info(
            "collecting dataset",
            extra={
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
                "attempt": request.execution.attempt,
                "validity_frame_uri": request.validity_frame.uri,
                "experiment_label": request.experiment_label,
            },
        )
        collected = data_collector.collect_rows(request)
        rows = _materialize_rows(collected.rows)
        dataset = artifact_store.write_rows(
            rows,
            media_type=request.output_media_type,
            metadata={
                "validity_frame_uri": request.validity_frame.uri,
                "experiment_label": request.experiment_label,
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
                "attempt": request.execution.attempt,
                "row_count": len(rows),
                "columns": list(collected.columns),
            },
        )
        return CollectDataResult(
            dataset=dataset,
            row_count=len(rows),
            columns=collected.columns,
        )
    except VFWorksActionError:
        raise
    except Exception as error:
        raise DataPreparationError(
            "failed to collect dataset",
            details={
                "validity_frame_uri": request.validity_frame.uri,
                "experiment_label": request.experiment_label,
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
            },
        ) from error


def prepare_data(
    request: PrepareDataRequest,
    *,
    artifact_store: TabularArtifactStore,
) -> PrepareDataResult:
    """Split a tabular dataset into train, test, and optional validation artifacts.

    The split is deterministic when ``request.random_seed`` is set. The action
    has no process-local memory: all downstream values are returned as
    :class:`ArtifactRef` instances.
    """

    try:
        LOGGER.info(
            "preparing dataset",
            extra={
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
                "attempt": request.execution.attempt,
                "dataset_uri": request.dataset.uri,
            },
        )
        rows = _materialize_rows(artifact_store.read_rows(request.dataset))
        ordered_rows = _shuffle_rows(rows, request)

        training_count = int(len(ordered_rows) * request.train_fraction)
        test_count = int(len(ordered_rows) * request.test_fraction)
        training_rows = ordered_rows[:training_count]
        test_rows = ordered_rows[training_count : training_count + test_count]
        validation_rows = ordered_rows[training_count + test_count :]

        training_dataset = _write_split(
            artifact_store,
            request,
            "train",
            training_rows,
        )
        test_dataset = _write_split(
            artifact_store,
            request,
            "test",
            test_rows,
        )
        validation_dataset = (
            _write_split(artifact_store, request, "validation", validation_rows)
            if validation_rows
            else None
        )

        return PrepareDataResult(
            training_dataset=training_dataset,
            test_dataset=test_dataset,
            validation_dataset=validation_dataset,
            training_row_count=len(training_rows),
            test_row_count=len(test_rows),
            validation_row_count=len(validation_rows),
        )
    except VFWorksActionError:
        raise
    except Exception as error:
        raise DataPreparationError(
            "failed to prepare dataset",
            details={
                "dataset_uri": request.dataset.uri,
                "workflow_run_id": request.execution.workflow_run_id,
                "task_run_id": request.execution.task_run_id,
            },
        ) from error


def _materialize_rows(rows: Iterable[TabularRow]) -> list[dict[str, JSONValue]]:
    result: list[dict[str, JSONValue]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise TypeError(f"row {index} must be a mapping")
        copied = _copy_json_value(dict(row), f"row {index}")
        result.append(cast(dict[str, JSONValue], copied))
    return result


def _shuffle_rows(
    rows: Sequence[TabularRow],
    request: PrepareDataRequest,
) -> list[TabularRow]:
    result = list(rows)
    if request.shuffle:
        random.Random(request.random_seed).shuffle(result)
    return result


def _write_split(
    artifact_store: TabularArtifactStore,
    request: PrepareDataRequest,
    split_name: str,
    rows: Sequence[TabularRow],
) -> ArtifactRef:
    return artifact_store.write_rows(
        rows,
        media_type=request.dataset.media_type,
        metadata={
            "source_uri": request.dataset.uri,
            "split": split_name,
            "workflow_run_id": request.execution.workflow_run_id,
            "task_run_id": request.execution.task_run_id,
            "attempt": request.execution.attempt,
            "row_count": len(rows),
        },
    )
