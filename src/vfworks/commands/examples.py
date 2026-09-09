from pathlib import Path

import click

from vfworks.examples import ExampleRuntime, load_example_config


@click.group(name="example")
def example_cmds():
    """Run a configured vfWorks example."""


@example_cmds.command(name="run")
@click.argument("configuration", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def run_example(configuration: Path):
    """Load CONFIGURATION and run its training workflow."""
    runtime = ExampleRuntime(load_example_config(configuration))
    runtime.run_headless()
    click.echo(f"Example '{runtime.config.name}' completed")


@example_cmds.command(name="serve")
@click.argument("configuration", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=8000, show_default=True, type=click.IntRange(1, 65535))
def serve_example(configuration: Path, host: str, port: int):
    """Expose configured training actions through the HTTP service API."""
    try:
        import uvicorn
    except ImportError as error:
        raise click.ClickException("Install vfWorks with the 'api' extra") from error

    from vfworks.api import create_training_app

    uvicorn.run(create_training_app(configuration), host=host, port=port)
