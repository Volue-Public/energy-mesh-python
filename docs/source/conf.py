import sphinx_rtd_theme

# -- Path setup --------------------------------------------------------------

import os
import sys

ROOT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..')
VOLUE_FOLDER = os.path.join(ROOT_FOLDER, 'src', 'volue')
MESH_FOLDER = os.path.join(VOLUE_FOLDER, 'mesh')
MESH_AIO_FOLDER = os.path.join(MESH_FOLDER, 'aio')
EXAMPLE_FOLDER = os.path.join(MESH_FOLDER, 'examples')
TESTS_FOLDER = os.path.join(MESH_FOLDER, 'tests')
sys.path.insert(0, VOLUE_FOLDER)
sys.path.insert(0, MESH_FOLDER)
sys.path.insert(0, MESH_AIO_FOLDER)
sys.path.insert(0, EXAMPLE_FOLDER)
sys.path.insert(0, TESTS_FOLDER)

# -- Project information -----------------------------------------------------

project = 'volue.mesh'
copyright = '2022, Volue AS'
author = 'Volue AS'

import re
version = ''
with open('../../pyproject.toml') as f:
    version = re.search(r'^version\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

# The full version, including alpha/beta/rc tags
release = version

# -- Extension configuration -------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autodoc.typehints',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.napoleon',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx_copybutton'
]

# Options for: sphinx.ext.autosectionlabel
# all auto labels need to be prefixed with doc name:
autosectionlabel_prefix_document = True
# auto generate labels down 2 levels,
# anything from level 3 needs to be manually referenced:
autosectionlabel_maxdepth = 2

# Options for: sphinx.ext.napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# Options for: sphinx.ext.todo
todo_include_todos = True

# Options for: sphinx.ext.autodoc
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'special-members': False
}

# Options for: sphinx.ext.extlinks
extlinks = {
    'issue': ('https://github.com/PowelAS/sme-mesh-python/issues/%s', '[%s]'),
}

# Options for: sphinx.ext.intersphinx
# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None),
  'aio': ('https://docs.aiohttp.org/en/stable/', None),
  'grpc': ('https://grpc.github.io/grpc/python/', None)
}

# prefixing mesh_ for anything strictly mesh object model
# prefixing resource_ for anything only in the resource silo

rst_prolog = """
.. |deprecated| replace:: **Deprecated**.

.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine

.. |test| replace:: Requires |pytest_link|_.
.. |pytest_link| replace:: *pytest*
.. _pytest_link: https://github.com/pytest-dev/pytest
.. |testaio| replace:: Requires |pytest_asyncio_link|_.
.. |pytest_asyncio_link| replace:: *pytest-asyncio*
.. _pytest_asyncio_link: https://github.com/pytest-dev/pytest-asyncio

.. |mesh_session_uuid| replace:: the id of the session you are (or want to be) connected to
.. |mesh_object_model_name| replace:: the name of the :ref:`Mesh object model <mesh object model>` you want to work within
.. |mesh_object_id| replace:: unique way of identifying a Mesh object that contains a time series. Using either a |mesh_object_uuid|, a |mesh_object_full_name| or a |timskey|
.. |mesh_object_uuid| replace:: Universal Unique Identifier for Mesh objects
.. |mesh_object_full_name| replace:: path in the :ref:`Mesh object model <mesh object model>`
.. |mesh_service| replace:: the gRPC generated mesh .service use to communicate with the :doc:`Mesh server <mesh_server>`
.. |mesh_expression| replace:: expression which consists of a function to call. See :ref:`expressions <mesh expression>`
.. |mesh_query| replace:: a search formulated using the :doc:`Mesh search language <mesh_search>`

.. |host| replace:: Mesh server host name in the form an ip
.. |port| replace:: Mesh server port number for gRPC communication
.. |root_pem_certificates| replace::  PEM-encoded root certificate(s) as a byte string. If this argument is set then a secured connection will be created, otherwise it will be an insecure connection.
.. |authentication_parameters| replace:: TODO
.. |service_principal_name| replace:: name of an active directory service, e.g.: 'HOST/hostname.ad.examplecompany.com
.. |user_principal_name| replace:: name of an active directory user, e.g.: 'ad\\user.name'
.. |relative_to| replace:: a Mesh object to perform actions relative to
.. |available_at_timepoint| replace:: must be available around this time
.. |timezone| replace:: timezone
.. |start_time| replace:: the start date and time of the time series interval
.. |end_time| replace:: the end date and time of the time series interval
.. |timskey| replace:: integer that only applies to specific raw time series.
.. |time_series_entry| replace:: time series entry. *Time series entry* is the raw timestamps, values and flags of a times series. It is stored in the resource catalog and will often be connected to a :doc:`time series attribute <mesh_object_attributes>`.

.. |resource_path| replace:: path in the resource model.
.. |resource_curve_type| replace:: curve type for the time series.
.. |resource_unit_of_measurement| replace:: unit of measurement for the time series.

.. |grpc_rpc_error| replace:: Error message raised if the gRPC request could not be completed
.. |runtime_error| replace:: Error message raised if the input is not valid
.. |type_error| replace:: Error message raised if the returned result from the request is not as expected
"""


# -- General configuration ---------------------------------------------------

templates_path = ['_templates']
exclude_patterns = []
source_suffix = ['.rst', '.md']
master_doc = 'index'
language = 'en'


# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
#html_static_path = ['_static']
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'logo_only': True,
    'display_version': False,
}
