import os
import sys

import sphinx_rtd_theme

# -- Path setup --------------------------------------------------------------


ROOT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..")
VOLUE_FOLDER = os.path.join(ROOT_FOLDER, "src", "volue")
MESH_FOLDER = os.path.join(VOLUE_FOLDER, "mesh")
MESH_AIO_FOLDER = os.path.join(MESH_FOLDER, "aio")
MESH_AVAILABILITY_FOLDER = os.path.join(MESH_FOLDER, "availability")
EXAMPLE_FOLDER = os.path.join(MESH_FOLDER, "examples")
TESTS_FOLDER = os.path.join(MESH_FOLDER, "tests")
sys.path.insert(0, VOLUE_FOLDER)
sys.path.insert(0, MESH_FOLDER)
sys.path.insert(0, MESH_AIO_FOLDER)
sys.path.insert(0, MESH_AVAILABILITY_FOLDER)
sys.path.insert(0, EXAMPLE_FOLDER)
sys.path.insert(0, TESTS_FOLDER)

# -- Project information -----------------------------------------------------

project = "volue.mesh"
copyright = "2024, Volue AS"
author = "Volue AS"

import re

version = ""
with open("../../pyproject.toml") as f:
    version = re.search(
        r'^version\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)

# The full version, including alpha/beta/rc tags
release = version

# -- Extension configuration -------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx_copybutton",
]

# Options for: sphinx.ext.autosectionlabel
# all auto labels need to be prefixed with doc name:
autosectionlabel_prefix_document = True
# auto generate labels down 2 levels,
# anything from level 3 needs to be manually referenced:
autosectionlabel_maxdepth = 2

# Options for: sphinx.ext.napoleon
napoleon_google_docstring = True
napoleon_include_init_with_doc = True

# Options for: sphinx.ext.todo
todo_include_todos = True

# Options for: sphinx.ext.autodoc
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "special-members": False,
}


def process_docstring(app, what, name, obj, options, lines):
    if name.startswith("volue.mesh.proto."):
        for index, line in enumerate(lines):
            # protofile contains '------------' which are recognized by
            # sphinx as 'Unexpected section title.', therefore, removing it.
            if line.startswith("--"):
                lines[index] = ""


def setup(app):
    app.connect("autodoc-process-docstring", process_docstring)


# Options for: sphinx.ext.extlinks
extlinks = {
    "issue": ("https://github.com/Volue-Public/energy-mesh-python/issues/%s", "[%s]"),
    "pull": ("https://github.com/Volue-Public/energy-mesh-python/pull/%s", "[%s]"),
}

# Options for: sphinx.ext.intersphinx
# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
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
"""


# -- General configuration ---------------------------------------------------

templates_path = ["_templates"]
exclude_patterns = []
source_suffix = [".rst", ".md"]
master_doc = "index"
language = "en"


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
# html_static_path = ['_static']
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "logo_only": True,
    "display_version": False,
}
