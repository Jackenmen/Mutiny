# Copyright 2021 Jakub Kuczys (https://github.com/jack1142)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib
import inspect
import sys
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from typing import Any, Iterator, NewType, Optional

from sphinx.application import Sphinx
from sphinx.ext.autodoc import Options

import mutiny

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.join(os.path.abspath(".."), "src"))

# -- Project information -----------------------------------------------------

project = "Mutiny"
copyright = "2021, Jakub Kuczys (jack1142)"
author = "Jakub Kuczys (jack1142)"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

# The short X.Y version.
version = mutiny.__version__

# The full version, including alpha/beta/rc tags.
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # built-in extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    # 3rd-party extensions
    "furo",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx-prompt",
    "sphinxcontrib.jinja",
    "sphinxcontrib_trio",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Role which is assigned when you make a simple reference within backticks
default_role = "any"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#
# html_static_path = ["_static"]

# this variable will be replaced RTD
context = {"version_slug": "latest"}


# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
napoleon_attr_annotations = True

modules: dict[str, Any] = {"mutiny": mutiny}
for name in mutiny.__all__:
    obj = getattr(mutiny, name)
    if inspect.ismodule(obj):
        modules[obj.__name__] = obj

autodoc_type_aliases = {
    name: f"{module_name}.{name}"
    for module_name, module in modules.items()
    for name in module.__all__
}
# this fixes very long overload signature for this internal type
autodoc_type_aliases["EventListener"] = "EventListener"


def fixup_base_reprs(
    app: Sphinx, name: str, obj: type, options: Options, bases: list[type]
) -> None:
    for idx, base in enumerate(bases):
        alias = autodoc_type_aliases.get(base.__name__)
        if alias is not None:
            bases[idx] = NewType(alias, int)


# -- Options for sphinx-jinja extension --------------------------------------


def classes(module_name: str, /) -> Iterator[type]:
    module = modules[module_name]
    for name in module.__all__:
        obj = getattr(module, name)
        if inspect.isclass(obj):
            yield obj


def grouped_classes(module_name: str, /) -> Iterator[tuple[ModuleType, list[type]]]:
    groups = defaultdict(list)
    module = modules[module_name]
    for name in module.__all__:
        obj = getattr(module, name)
        if inspect.isclass(obj):
            groups[obj.__module__].append(obj)

    for module_name, classes in groups.items():
        internal_module = importlib.import_module(module_name)
        yield internal_module, classes


jinja_contexts = {
    "autodoc": {
        "classes": classes,
        "grouped_classes": grouped_classes,
    },
}

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for linkcode extension ------------------------------------------

GITHUB_URL = "https://github.com/jack1142/Mutiny"
SRC_PATH = Path(inspect.getsourcefile(mutiny)).parent.parent  # type: ignore[arg-type]


def linkcode_resolve(domain: str, info: dict[str, Any]) -> Optional[str]:
    if domain != "py":
        return None
    module_name = info["module"]
    full_name = info["fullname"]
    module = sys.modules.get(module_name)
    if module is None:
        return None
    obj = module
    for part in full_name.split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            return None
    try:
        file_name = inspect.getsourcefile(obj)
    except TypeError:
        return None
    if file_name is None:
        return None

    source_lines: list[str] = []
    first_line_number: Optional[int]
    try:
        source_lines, first_line_number = inspect.getsourcelines(obj)
    except OSError:
        first_line_number = None

    if first_line_number is None:
        line_anchor = ""
    else:
        last_line_number = first_line_number + len(source_lines) - 1
        line_anchor = f"#L{first_line_number}-L{last_line_number}"

    file_name = Path(file_name).relative_to(SRC_PATH).as_posix()

    branch = "main" if context.get("version_slug") == "latest" else version
    return f"{GITHUB_URL}/blob/{branch}/src/{file_name}{line_anchor}"


def setup(app: Sphinx) -> None:
    app.connect("autodoc-process-bases", fixup_base_reprs)
