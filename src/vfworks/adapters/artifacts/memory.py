"""In-memory artifact stores for tests and local process composition."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Mapping, cast

from vfworks.actions.contracts import ArtifactRef, JSONValue, _copy_json_value
from vfworks.actions.data import TabularRow
from vfworks.actions.exceptions import ArtifactIntegrityError, ArtifactNotFound


class InMemoryTabularArtifactStore:
    """A deterministic row artifact store backed by process memory.

    The store is useful for tests and for local proof-of-concept chains. It is
    not durable and should not be used as a scheduler boundary across workers.
    """

    def __init__(self, *, uri_prefix: str = "mem://vfworks") -> None:
        self._uri_prefix = uri_prefix.rstrip("/")
        self._rows_by_uri: dict[str, list[dict[str, JSONValue]]] = {}
        self._json_by_uri: dict[str, dict[str, JSONValue]] = {}
        self._refs_by_uri: dict[str, ArtifactRef] = {}

    def read_rows(self, reference: ArtifactRef) -> Sequence[TabularRow]:
        try:
            stored = self._rows_by_uri[reference.uri]
            stored_reference = self._refs_by_uri[reference.uri]
        except KeyError as error:
            raise ArtifactNotFound(
                "artifact was not found",
                details={"uri": reference.uri},
            ) from error

        if reference.checksum and reference.checksum != stored_reference.checksum:
            raise ArtifactIntegrityError(
                "artifact checksum does not match stored content",
                details={"uri": reference.uri},
            )
        return [_copy_row(row, "row") for row in stored]

    def write_rows(
        self,
        rows: Sequence[TabularRow],
        *,
        media_type: str,
        metadata: Mapping[str, JSONValue],
    ) -> ArtifactRef:
        copied_rows = [_copy_row(row, f"row {index}") for index, row in enumerate(rows)]
        copied_metadata = _copy_mapping(metadata, "metadata")
        payload = _encode_rows(copied_rows)
        checksum = _sha256(payload)
        uri = f"{self._uri_prefix}/{checksum.removeprefix('sha256:')}.json"
        reference = ArtifactRef(
            uri=uri,
            media_type=media_type,
            checksum=checksum,
            size_bytes=len(payload),
            metadata=copied_metadata,
        )
        self._rows_by_uri.setdefault(uri, copied_rows)
        self._refs_by_uri.setdefault(uri, reference)
        return self._refs_by_uri[uri]

    def read_json(self, reference: ArtifactRef) -> Mapping[str, JSONValue]:
        try:
            stored = self._json_by_uri[reference.uri]
            stored_reference = self._refs_by_uri[reference.uri]
        except KeyError as error:
            raise ArtifactNotFound(
                "artifact was not found",
                details={"uri": reference.uri},
            ) from error

        if reference.checksum and reference.checksum != stored_reference.checksum:
            raise ArtifactIntegrityError(
                "artifact checksum does not match stored content",
                details={"uri": reference.uri},
            )
        return _copy_mapping(stored, "document")

    def write_json(
        self,
        document: Mapping[str, JSONValue],
        *,
        media_type: str,
        metadata: Mapping[str, JSONValue],
    ) -> ArtifactRef:
        copied_document = _copy_mapping(document, "document")
        copied_metadata = _copy_mapping(metadata, "metadata")
        payload = _encode_json(copied_document)
        checksum = _sha256(payload)
        uri = f"{self._uri_prefix}/{checksum.removeprefix('sha256:')}.json"
        reference = ArtifactRef(
            uri=uri,
            media_type=media_type,
            checksum=checksum,
            size_bytes=len(payload),
            metadata=copied_metadata,
        )
        self._json_by_uri.setdefault(uri, copied_document)
        self._refs_by_uri.setdefault(uri, reference)
        return self._refs_by_uri[uri]


def _copy_row(row: TabularRow, field_name: str) -> dict[str, JSONValue]:
    if not isinstance(row, Mapping):
        raise ArtifactIntegrityError(f"{field_name} must be a mapping")
    copied = _copy_json_value(dict(row), field_name)
    return cast(dict[str, JSONValue], copied)


def _copy_mapping(
    value: Mapping[str, JSONValue],
    field_name: str,
) -> dict[str, JSONValue]:
    if not isinstance(value, Mapping):
        raise ArtifactIntegrityError(f"{field_name} must be a mapping")
    copied = _copy_json_value(dict(value), field_name)
    return cast(dict[str, JSONValue], copied)


def _encode_rows(rows: Sequence[TabularRow]) -> bytes:
    return json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _encode_json(document: Mapping[str, JSONValue]) -> bytes:
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"
