import datetime
import pathlib

import toml

with open(pathlib.Path(__file__).parents[1] / "pyproject.toml", "r") as file:
    pyproject_toml = toml.load(file)

copyright = str(datetime.date.today().year)  # noqa: A001
project = pyproject_toml["tool"]["poetry"]["name"]
version = pyproject_toml["tool"]["poetry"]["version"]
authors = pyproject_toml["tool"]["poetry"]["authors"]
names = [name.split("<")[0].strip() for name in authors]  # Remove emails
author = " & ".join([", ".join(names[:-1]), names[-1]])
master_doc = project

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
]

html_theme = "furo"
pygments_style = "vs"
autodoc_member_order = "groupwise"
autodoc_default_options = {"output_path": "./something"}
exclude_patterns = ["_build", "modules.rst"]
