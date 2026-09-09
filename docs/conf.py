from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path("..").resolve()))

html_favicon = "static/images/docs-logo.svg"

project = "vfworks"
ogp_site_name = project
copyright = f"{datetime.now().year}"
author = "vfworks"
release = "0.0.2"

extensions = [
    "myst_parser",
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx_rtd_theme",
    "sphinx_search.extension",
    "sphinx_tabs.tabs",
    "sphinxext.opengraph",
    "sphinxcontrib.mermaid",
    # "sphinxcontrib.drawio",
    "sphinx_toolbox.collapse",
]
# autosectionlabel_prefix_document = True
sphinx_tabs_nowarn = True
templates_path = ["templates"]
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}
source_encoding = "utf-8-sig"
master_doc = "index"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": True,
    "collapse_navigation": False,
}
html_logo = html_favicon
html_static_path = ["static"]
htmlhelp_basename = project
html_extra_path = ["robots.txt"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/custom.js"]
on_rtd = False
html_title = project
html_context = {"conf_py_path": "/"}

notfound_context = {
    "title": "Page not found",
    "body": """
        <h1>Page not found</h1>
        <p>
            Sorry, we couldn't find that page. It may have been renamed or removed
            in the version of the documentation you're currently browsing.
        </p>
        <p>
            If you're currently browsing the
            <em>latest</em> version of the documentation, try browsing the
            <a href="/en/stable/"><em>stable</em> version of the documentation</a>.
        </p>
        <p>
            Alternatively, use the
            <a href="#" onclick="$('#rtd-search-form [name=\\'q\\']').focus()">Search docs</a>
            box on the left or <a href="/">go to the homepage</a>.
        </p>
    """,
}
