"""Standard-library subprocess reference adapter."""

from vfworks.integrations.subprocess.runner import (
    SubprocessActionResult,
    SubprocessActionSpec,
    run_action,
)

__all__ = ["SubprocessActionResult", "SubprocessActionSpec", "run_action"]
