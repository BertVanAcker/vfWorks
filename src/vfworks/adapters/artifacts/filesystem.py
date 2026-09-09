"""Restricted local filesystem artifact store implementations."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Mapping, cast
from urllib.parse import unquote, urlparse

from vfworks.actions.contracts import ArtifactRef, JSONValue, _copy_json_value
from vfworks.actions.data import TabularRow
from vfworks.actions.exceptions import (
    ArtifactIntegrityError,
    ArtifactNotFound,
    InvalidActionInput,
)

JSON_ROWS_MEDIA_TYPES = frozenset(
    {
        "application/json",
        "application/vnd.vfworks.rows+json",
    }
)
JSON_DOCUMENT_MEDIA_TYPES = JSON_ROWS_MEDIA_TYPES | frozenset(
    {
        "application/vnd.vfworks.model+json",
    }
)


class RestrictedFilesystemTabularArtifactStore:
    """JSON row artifact store confined to one configured filesystem root."""

    def __init__(
        self,
        root: str | Path,
        *,
        default_media_type: str = "application/vnd.vfworks.rows+json",
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        if default_media_type not in JSON_ROWS_MEDIA_TYPES:
            raise InvalidActionInput("default_media_type must be a supported JSON rows media type")
        self.default_media_type = default_media_type

    def read_rows(self, reference: ArtifactRef) -> Sequence[TabularRow]:
        if reference.media_type not in JSON_ROWS_MEDIA_TYPES:
            raise ArtifactIntegrityError(
                "artifact media type is not supported by the JSON row store",
                details={"uri": reference.uri, "media_type": reference.media_type},
            )

        path = self._path_from_reference(reference)
        if not path.exists():
            raise ArtifactNotFound("artifact file was not found", details={"uri": reference.uri})
        payload = path.read_bytes()
        if reference.size_bytes is not None and len(payload) != reference.size_bytes:
            raise ArtifactIntegrityError("artifact size does not match", details={"uri": reference.uri})
        if reference.checksum is not None and _sha256(payload) != reference.checksum:
            raise ArtifactIntegrityError("artifact checksum does not match", details={"uri": reference.uri})

        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ArtifactIntegrityError("artifact is not valid JSON rows", details={"uri": reference.uri}) from error

        if not isinstance(decoded, list):
            raise ArtifactIntegrityError("artifact JSON payload must be a list of rows", details={"uri": reference.uri})
        return [_copy_row(row, f"row {index}") for index, row in enumerate(decoded)]

    def write_rows(
        self,
        rows: Sequence[TabularRow],
        *,
        media_type: str | None = None,
        metadata: Mapping[str, JSONValue],
    ) -> ArtifactRef:
        selected_media_type = media_type or self.default_media_type
        if selected_media_type not in JSON_ROWS_MEDIA_TYPES:
            raise InvalidActionInput("media_type must be a supported JSON rows media type")

        copied_rows = [_copy_row(row, f"row {index}") for index, row in enumerate(rows)]
        copied_metadata = _copy_mapping(metadata, "metadata")
        payload = _encode_rows(copied_rows)
        checksum = _sha256(payload)
        digest = checksum.removeprefix("sha256:")
        path = self.root / f"{digest}.json"

        if not path.exists():
            self._atomic_write(path, payload)
        elif path.read_bytes() != payload:
            raise ArtifactIntegrityError("content-addressed artifact path is corrupt")

        return ArtifactRef(
            uri=path.as_uri(),
            media_type=selected_media_type,
            checksum=checksum,
            size_bytes=len(payload),
            metadata=copied_metadata,
        )

    def read_json(self, reference: ArtifactRef) -> Mapping[str, JSONValue]:
        if reference.media_type not in JSON_DOCUMENT_MEDIA_TYPES:
            raise ArtifactIntegrityError(
                "artifact media type is not supported by the JSON document store",
                details={"uri": reference.uri, "media_type": reference.media_type},
            )

        path = self._path_from_reference(reference)
        if not path.exists():
            raise ArtifactNotFound("artifact file was not found", details={"uri": reference.uri})
        payload = path.read_bytes()
        if reference.size_bytes is not None and len(payload) != reference.size_bytes:
            raise ArtifactIntegrityError("artifact size does not match", details={"uri": reference.uri})
        if reference.checksum is not None and _sha256(payload) != reference.checksum:
            raise ArtifactIntegrityError("artifact checksum does not match", details={"uri": reference.uri})

        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ArtifactIntegrityError("artifact is not valid JSON", details={"uri": reference.uri}) from error
        return _copy_mapping(decoded, "document")

    def write_json(
        self,
        document: Mapping[str, JSONValue],
        *,
        media_type: str,
        metadata: Mapping[str, JSONValue],
    ) -> ArtifactRef:
        if media_type not in JSON_DOCUMENT_MEDIA_TYPES:
            raise InvalidActionInput("media_type must be a supported JSON document media type")

        copied_document = _copy_mapping(document, "document")
        copied_metadata = _copy_mapping(metadata, "metadata")
        payload = _encode_json(copied_document)
        checksum = _sha256(payload)
        digest = checksum.removeprefix("sha256:")
        path = self.root / f"{digest}.json"

        if not path.exists():
            self._atomic_write(path, payload)
        elif path.read_bytes() != payload:
            raise ArtifactIntegrityError("content-addressed artifact path is corrupt")

        return ArtifactRef(
            uri=path.as_uri(),
            media_type=media_type,
            checksum=checksum,
            size_bytes=len(payload),
            metadata=copied_metadata,
        )

    def _path_from_reference(self, reference: ArtifactRef) -> Path:
        parsed = urlparse(reference.uri)
        if parsed.scheme != "file":
            raise InvalidActionInput("filesystem artifact references must use file: URIs")
        if parsed.netloc not in ("", "localhost"):
            raise InvalidActionInput("filesystem artifact references must be local file URIs")

        path = Path(unquote(parsed.path)).expanduser().resolve()
        try:
            path.relative_to(self.root)
        except ValueError as error:
            raise InvalidActionInput(
                "filesystem artifact reference is outside the configured root"
            ) from error
        return path

    @staticmethod
    def _atomic_write(path: Path, payload: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
        )
        try:
            with os.fdopen(fd, "wb") as temporary_file:
                temporary_file.write(payload)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_name, path)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise


def _copy_row(row: object, field_name: str) -> dict[str, JSONValue]:
    if not isinstance(row, Mapping):
        raise ArtifactIntegrityError(f"{field_name} must be a mapping")
    copied = _copy_json_value(dict(row), field_name)
    return cast(dict[str, JSONValue], copied)


def _copy_mapping(
    value: object,
    field_name: str,
) -> dict[str, JSONValue]:
    if not isinstance(value, Mapping):
        raise InvalidActionInput(f"{field_name} must be a mapping")
    copied = _copy_json_value(dict(value), field_name)
    return cast(dict[str, JSONValue], copied)


def _encode_rows(rows: Sequence[TabularRow]) -> bytes:
    return json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _encode_json(document: Mapping[str, JSONValue]) -> bytes:
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"
