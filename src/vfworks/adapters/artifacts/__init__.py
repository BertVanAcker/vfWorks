"""Artifact-store adapters for scheduler-callable actions."""

from vfworks.adapters.artifacts.filesystem import RestrictedFilesystemTabularArtifactStore
from vfworks.adapters.artifacts.memory import InMemoryTabularArtifactStore

__all__ = [
    "InMemoryTabularArtifactStore",
    "RestrictedFilesystemTabularArtifactStore",
]
