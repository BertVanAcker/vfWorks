from __future__ import annotations

import asyncio
import json
import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from vfworks.examples import load_example_config
from vfworks.services import TrainingServiceManager


class _ProgressStreams:
    def __init__(self):
        self.channels: dict[str, set[asyncio.Queue]] = {}

    def subscribe(self, channel: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self.channels.setdefault(channel, set()).add(queue)
        return queue

    def unsubscribe(self, channel: str, queue: asyncio.Queue) -> None:
        queues = self.channels.get(channel, set())
        queues.discard(queue)
        if not queues:
            self.channels.pop(channel, None)

    async def publish(self, channel: str, update: dict[str, Any]) -> None:
        for queue in list(self.channels.get(channel, ())):
            await queue.put(update)


def _read_file_uri(uri: str, storage_root: Path) -> Any:
    parsed = urlparse(uri)
    if parsed.scheme != "file" or parsed.netloc not in {"", "localhost"}:
        raise ValueError("Unsupported artifact URI")
    path = Path(unquote(parsed.path)).resolve()
    root = storage_root.resolve()
    if not path.is_relative_to(root):
        raise ValueError("Artifact URI is outside the example root")
    data = path.read_bytes()
    mime_type, _ = mimetypes.guess_type(path.name)
    if mime_type and (mime_type.startswith("text/") or mime_type in {"application/json", "application/xml", "application/x-yaml"}):
        return data.decode("utf-8", errors="replace")
    return data


def _deserialize_artifact(value: Any, storage_root: Path) -> Any:
    if isinstance(value, dict):
        if "value" in value:
            return value.get("value")
        uri = value.get("uri")
        if isinstance(uri, str) and uri:
            return _read_file_uri(uri, storage_root)
    return value


def _service_metadata(manager: TrainingServiceManager) -> list[dict[str, Any]]:
    metadata = []
    for task in manager.service_names:
        metadata.append(
            {
                "name": task,
                "description": f"Execute the {task!r} stage for {manager.config.name}.",
                "runtime_status": "runtime",
                "data_input": {} if task == "Create session" else {"context": {"description": "Worker session", "type": "object"}},
                "data_output": {
                    "context": {"description": "Worker session reference", "type": "object"},
                    "report": {"description": "Action outcome and diagnostic", "type": "object"},
                },
                "control_input": {"start": {"description": "Start this training stage"}},
                "control_output": {
                    "ok": {"description": "Training stage completed"},
                    "error": {"description": "Training stage failed"},
                    "nok": {"description": "Action reported an unsuccessful result"},
                    "not_implemented": {"description": "Action requires manual implementation or review"},
                },
            }
        )
    return metadata


def create_training_app(configuration: str | Path):
    """Expose an example's training actions through the HTTP service API."""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import StreamingResponse
        from starlette.middleware.cors import CORSMiddleware
    except ImportError as error:
        raise RuntimeError("Install vfWorks with the 'api' extra to serve training actions") from error

    manager = TrainingServiceManager(load_example_config(configuration))
    streams = _ProgressStreams()
    app = FastAPI(
        title="vfWorks Training Service",
        description=f"Remote training actions for {manager.config.name}",
        version="1.0",
    )
    app.state.training_manager = manager
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    @app.get("/health/")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "version": "1.0", "example": manager.config.name}

    @app.get("/service/")
    async def service_list() -> dict[str, str]:
        return {item["name"]: item["description"] for item in _service_metadata(manager)}

    @app.get("/service/list")
    async def service_list_all() -> list[dict[str, Any]]:
        return _service_metadata(manager)

    @app.post("/service/execute/{task_name}")
    async def execute(task_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        incoming_values = payload.get("incoming", {})
        outgoing = payload.get("outgoing", [])
        progress_channel = payload.get("progress_channel")
        if not isinstance(incoming_values, dict) or not isinstance(outgoing, list):
            raise HTTPException(status_code=422, detail="'incoming' must be an object and 'outgoing' a list")
        if any(not isinstance(port, str) or port not in {"context", "report"} for port in outgoing):
            raise HTTPException(status_code=422, detail="Supported output ports: context, report")
        try:
            incoming = {
                key: _deserialize_artifact(value, manager.config.root)
                for key, value in incoming_values.items()
            }
            updates: list[dict[str, Any]] = []
            loop = asyncio.get_running_loop()

            def progress(label: str, percent: int) -> None:
                update = {"label": label, "percent": min(100, max(0, int(percent)))}
                updates.append(update)
                if isinstance(progress_channel, str) and progress_channel:
                    loop.call_soon_threadsafe(
                        asyncio.create_task,
                        streams.publish(progress_channel, update),
                    )

            execution = await asyncio.to_thread(manager.execute, task_name, incoming, progress)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except (ValueError, RuntimeError) as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return {
            "result": execution["result"],
            "outgoing": {port: execution[port] for port in outgoing},
            "progress": updates,
        }

    @app.get("/service/progress/{channel}/stream/")
    async def stream_progress(channel: str, limit: int | None = None):
        queue = streams.subscribe(channel)

        async def events():
            emitted = 0
            try:
                while limit is None or emitted < limit:
                    try:
                        update = await asyncio.wait_for(queue.get(), timeout=25)
                        yield f"event: service_progress\ndata: {json.dumps(update)}\n\n"
                        emitted += 1
                    except asyncio.TimeoutError:
                        yield 'event: heartbeat\ndata: {"type":"heartbeat"}\n\n'
            finally:
                streams.unsubscribe(channel, queue)

        return StreamingResponse(events(), media_type="text/event-stream")

    @app.delete("/training/runs/{run_id}")
    async def discard_run(run_id: str) -> dict[str, Any]:
        if not manager.discard(run_id):
            raise HTTPException(status_code=404, detail="Training session not found")
        return {"discarded": run_id}

    return app
