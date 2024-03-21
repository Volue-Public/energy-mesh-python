HydSim
------

The Mesh Python SDK includes experimental functionality to run hydro simulations, run inflow
calculations and generate inputs for Marginal Cost using HydSim on the Mesh server. This
functionality is under development. Therefore, it is subject to change in future releases.
Planned but not yet implemented functionality includes:

- Selection the resolution to use.
- Retrieve datasets from the simulation. These are used by Volue for debugging.

The functionality may be used both through a synchronous
:py:class:`volue.mesh.Connection.Session` and through an asynchronous
:py:class:`volue.mesh.aio.Connection.Session` using the following methods.
Further below you'll find synchronous and asynchronous examples.


API documentation
*****************

.. automethod:: volue.mesh._base_session.Session.run_simulation
   :noindex:

.. automethod:: volue.mesh._base_session.Session.run_inflow_calculation
   :noindex:

.. automethod:: volue.mesh._base_session.Session.get_mc_file
   :noindex:


Example of simulations
**********************

.. literalinclude:: /../../src/volue/mesh/examples/run_simulation.py
   :language: python


Example of inflow calculations
******************************

.. literalinclude:: /../../src/volue/mesh/examples/run_inflow_calculation.py
   :language: python
