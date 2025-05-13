=================
Mesh Availability
=================

A Mesh availability event provides information about periods during which Mesh
objects are unavailable or partially available. The availability functionality
helps track and model the operational status of assets throughout time.

Types of Availability Events
*****************************

Mesh Python SDK supports three types of availability events:

* **Revision** - Represents periods when an object is completely unavailable (e.g., during maintenance or outage)
* **Restriction** - Represents periods when an object is partially available with reduced capacity

Availability Recurrence
************************

Availability events can be defined with various recurrence patterns:

* **Single occurrence** - One-time events with a specific start and end time
* **Daily** - Repeating pattern on a daily basis
* **Weekly** - Repeating pattern on a weekly basis
* **Monthly** - Repeating pattern on a monthly basis
* **Yearly** - Repeating pattern on a yearly basis

Each recurrence pattern allows specifying:

* How often the pattern repeats (e.g., every 2 weeks)
* When the pattern ends (if applicable)
* The time interval for each occurrence

Instances
**********

An **instance** is a single occurrence of a revision or restriction according
to its recurrence pattern. When analyzing availability, you can search for 
all instances that occur within a specified time period.

For example, a weekly revision occurring every Monday for two months would 
have approximately eight instances, one for each Monday in the specified 
period.

Categories and Statuses
************************

Availability events can have:

* **Status** - Indicates the current state of the event (e.g., planned, confirmed, cancelled)
* **Category** - Classifies the type of event (e.g., maintenance, external constraints)
* **Reason** - Text description explaining why the event exists

Common Use Cases
*****************

The availability functionality can be used for:

* **Maintenance Planning** - Scheduling and tracking planned downtime periods
* **Capacity Management** - Modeling partial capacity constraints
* **Outage Tracking** - Documenting unexpected unavailability periods
* **Resource Allocation** - Planning operations around known availability constraints

When working with availability data, you can search for events affecting specific
objects, find all instances occurring within a time period, and incorporate
availability information into operational planning and analysis.

The following example shows different ways of working with availability.

.. literalinclude:: /../../src/volue/mesh/examples/availability.py

Detailed API specification can be found here: :ref:`api:volue.mesh.availability`