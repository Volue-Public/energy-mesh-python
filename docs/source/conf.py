import sphinx_rtd_theme

# -- Path setup --------------------------------------------------------------

import os
import sys

ROOT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..')
EXAMPLE_FOLDER = os.path.join(ROOT_FOLDER, 'examples')
VOLUE_FOLDER = os.path.join(ROOT_FOLDER, 'src', 'volue')
sys.path.insert(0, os.path.join(VOLUE_FOLDER, 'mesh'))
sys.path.insert(0, os.path.join(EXAMPLE_FOLDER, 'mesh'))

# -- Project information -----------------------------------------------------

project = 'volue.mesh'
copyright = '2021, Volue AS'
author = 'Volue AS'

import re
version = ''
with open('../../src/volue/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

# The full version, including alpha/beta/rc tags
release = version

# -- Extension configuration -------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autodoc.typehints',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage'
]

napoleon_google_docstring = True
napoleon_numpy_docstring = True

autodoc_default_options = {
    'members': None,
}

extlinks = {
    'issue': ('https://github.com/Powel/sme-mesh-python/issues/%s', 'issue %s'),
}

# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None),
  'aio': ('https://docs.aiohttp.org/en/stable/', None),
  'grpc': ('https://grpc.github.io/grpc/python/', None)
}

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""


# -- General configuration ---------------------------------------------------

templates_path = ['_templates']
exclude_patterns = []
source_suffix = ['.rst', '.md']
master_doc = 'index'
language = 'en'


# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'logo_only': True,
    'display_version': False,
}

