"""CSV data-source adapters implemented with the Python standard library."""

from __future__ import annotations

import csv
from collections.abc import Mapping, Sequence
from pathlib import Path

from vfworks.actions.contracts import JSONValue
from vfworks.actions.data import CollectedRows, TabularRow
from vfworks.actions.exceptions import ArtifactIntegrityError, ArtifactNotFound
from vfworks.actions.models import CollectDataRequest


class OneColumnCSVDataCollector:
    """Collect aligned rows from one-column CSV measurement files.

    ``files_by_label`` maps an experiment label to columns and file paths:

    ```python
    {
        "all": {
            "power": ["Experiments/EXP1/power.csv"],
            "rpm": ["Experiments/EXP1/rpm.csv"],
        }
    }
    ```

    Multiple files for one column are concatenated. All selected columns must
    produce the same number of values.
    """

    def __init__(
        self,
        base_path: str | Path,
        files_by_label: Mapping[str, Mapping[str, Sequence[str | Path]]],
    ) -> None:
        self.base_path = Path(base_path).expanduser().resolve()
        self.files_by_label = {
            label: {
                column: tuple(paths)
                for column, paths in column_files.items()
            }
            for label, column_files in files_by_label.items()
        }

    def collect_rows(self, request: CollectDataRequest) -> CollectedRows:
        try:
            column_files = self.files_by_label[request.experiment_label]
        except KeyError as error:
            raise ArtifactNotFound(
                "experiment label was not configured",
                details={"experiment_label": request.experiment_label},
            ) from error

        columns = tuple(column_files)
        if not columns:
            raise ArtifactIntegrityError("no CSV columns were configured")

        values_by_column = {
            column: self._read_column_values(paths)
            for column, paths in column_files.items()
        }
        row_count = len(values_by_column[columns[0]])
        for column, values in values_by_column.items():
            if len(values) != row_count:
                raise ArtifactIntegrityError(
                    "CSV columns do not contain the same number of values",
                    details={"column": column, "expected_rows": row_count, "actual_rows": len(values)},
                )

        rows: list[TabularRow] = []
        for index in range(row_count):
            rows.append({column: values_by_column[column][index] for column in columns})
        return CollectedRows(rows=rows, columns=columns)

    def _read_column_values(self, paths: Sequence[str | Path]) -> list[JSONValue]:
        values: list[JSONValue] = []
        for path in paths:
            resolved = self._resolve_path(path)
            if not resolved.exists():
                raise ArtifactNotFound(
                    "CSV file was not found",
                    details={"path": str(resolved)},
                )
            with resolved.open(newline="", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                header = next(reader, None)
                if header is None or len(header) != 1:
                    raise ArtifactIntegrityError(
                        "CSV file must contain exactly one header column",
                        details={"path": str(resolved)},
                    )
                for row_number, row in enumerate(reader, start=2):
                    if len(row) != 1:
                        raise ArtifactIntegrityError(
                            "CSV row must contain exactly one value",
                            details={"path": str(resolved), "row_number": row_number},
                        )
                    values.append(_parse_json_scalar(row[0]))
        return values

    def _resolve_path(self, path: str | Path) -> Path:
        resolved = (self.base_path / path).expanduser().resolve()
        try:
            resolved.relative_to(self.base_path)
        except ValueError as error:
            raise ArtifactNotFound(
                "CSV file is outside the configured base path",
                details={"path": str(path)},
            ) from error
        return resolved


def _parse_json_scalar(value: str) -> JSONValue:
    stripped = value.strip()
    if stripped == "":
        return None
    try:
        return int(stripped)
    except ValueError:
        pass
    try:
        return float(stripped)
    except ValueError:
        return stripped
