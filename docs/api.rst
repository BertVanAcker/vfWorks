BLDC action worker API
======================

The API executes configured actions and retains datasets and models in worker
sessions. It does not choose action order, retries, backtracking, or acceptance.
Those decisions belong to the calling workflow.

Packages and components
-----------------------

Workflow enactment uses three components:

* `vfworks <https://github.com/BertVanAcker/vfWorks>`_: model frames and the
  action worker API.
* `ewe <https://git.rys.app/phd/robosapiens/ewe>`_: workflow definitions,
  enactment, and recovery decisions.
* `toasty <https://git.rys.app/phd/toasty>`_: the Svelte frontend.

Use `uv <https://docs.astral.sh/uv/>`_ for the Python packages and
`Bun <https://bun.sh/>`_ for toasty. Run each component from its own repository
in a separate terminal. EWE calls the worker over HTTP; it does not need the
vfworks package installed in its environment.

Run in WSL
----------

From the repository, using an environment with the selected example's training
dependencies installed:

.. code-block:: bash

   uv run --extra api python -m vfworks example serve \
     examples/Labcases/BLDC_predictiveMaintenance/VF_BLDC/example.yaml \
     --host 127.0.0.1 --port 8000

Other BLDC configurations are VF_TORCH/example.yaml and
VF_BLDC_SANDBOX/example.yaml under the same BLDC directory. Each server process
serves one configuration. The API extra alone does not install every example's
ML dependencies.

Open http://127.0.0.1:8000/docs for endpoint documentation.
GET /service/list lists available actions and their ports.

Start ewe from its repository:

.. code-block:: bash

   export VFWORKS_SERVICE_URL="http://127.0.0.1:8000"
   export VFWORKS_BLDC_VARIANT="bldc"
   uv run python -m ewe.main

The variant must match the worker configuration: ``bldc`` for VF_BLDC,
``torch`` for VF_TORCH, or ``sandbox`` for VF_BLDC_SANDBOX.

Start toasty from its repository:

.. code-block:: bash

   bun run dev

Then open the frontend at http://127.0.0.1:5173.
EWE's API documentation is available at http://127.0.0.1:7999/docs.

Docker
------

The companion services also have Docker images:

.. code-block:: text

   registry.rys.app/phd/robosapiens/ewe:latest
   registry.rys.app/phd/robosapiens/toasty:latest

Worker contract
---------------

Call POST /service/execute/Create%20session first:

.. code-block:: json

   {"incoming": {}, "outgoing": ["context", "report"]}

Keep the returned outgoing.context artifact and pass it to every subsequent
action, using the URL-encoded action name:

.. code-block:: json

   {
     "incoming": {"context": {"run_id": "<returned session ID>"}},
     "outgoing": ["report"]
   }
