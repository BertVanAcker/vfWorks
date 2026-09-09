Development
===========

You should grab all the requirements first::

    uv venv
    uv sync
    uv pip install -r pyproject.toml --all-extras

Don’t forget to run the tests after making changes::

    uv run pytest tests

You can also build the documentation::

    uv run sphinx-build -b html ./docs public

