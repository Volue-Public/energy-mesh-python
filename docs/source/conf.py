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
with open('../../src/volue/mesh/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

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

# Options for: sphinx.ext.napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = True

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

