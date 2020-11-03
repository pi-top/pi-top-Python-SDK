# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
HERE = os.path.abspath(os.path.dirname(__file__))
PARENT = os.path.dirname(HERE)

sys.path.insert(0, PARENT)
import setup as _setup  # noqa

# -- Project information -----------------------------------------------------

project = _setup.__project__
author = _setup.__author__
release = _setup.__version__
copyright = 'pi-top 2020'

# -- General configuration ---------------------------------------------------

master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.intersphinx']

# Extension options
# TODO v2 of sphinx-common: `None` -> `True`
# see https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
autodoc_default_options = {
    'members': None,
    'member-order': 'bysource',
    'undoc-members': None
}

autodoc_warningiserror = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Intersphinx configuration --------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3.7', None),
    'gpiozero': ('https://gpiozero.readthedocs.io/en/latest', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'imageio': ('https://imageio.readthedocs.io/en/stable/', None),
    'Pillow': ('https://pillow.readthedocs.io/en/stable/', None)
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
#html_sidebars = {}

html_theme_options = {
    'canonical_url': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'style_nav_header_background': "#20b6aa",
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': False,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom stuff for project
autodoc_mock_imports = [
    'cv2',
    'numpy',
    'imageio',
    'PyV4L2Camera',
    'PIL',
    # gpiozero dependencies
    'RPi',
    'RPIO',
    'pigpio'
]

exclude_patterns = ['_build']
