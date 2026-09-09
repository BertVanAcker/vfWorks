"""Exceptions raised at the public vfWorks action boundary."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping


class VFWorksActionError(Exception):
    """Base class for failures a scheduler may record and classify."""

    retryable = False

    def __init__(
        self,
        message: str,
        *,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.details = MappingProxyType(dict(details or {}))


class InvalidActionInput(VFWorksActionError, ValueError):
    """The request violates the action's public contract."""


class ArtifactNotFound(VFWorksActionError, FileNotFoundError):
    """A referenced artifact does not exist or is inaccessible."""


class ArtifactIntegrityError(VFWorksActionError):
    """Artifact size, checksum, format, or provenance validation failed."""


class BackendUnavailable(VFWorksActionError):
    """A required service or optional action backend is temporarily unavailable."""

    retryable = True


class DataPreparationError(VFWorksActionError):
    """Input data could not be transformed into the required representation."""


class ModelTrainingError(VFWorksActionError):
    """A model backend failed while fitting a model."""


class ModelEvaluationError(VFWorksActionError):
    """A trained model could not be evaluated."""


class ValidityFrameExportError(VFWorksActionError):
    """A validity-frame artifact could not be exported or published."""
