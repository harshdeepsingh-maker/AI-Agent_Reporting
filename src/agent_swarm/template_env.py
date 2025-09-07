from __future__ import annotations
import pathlib
from jinja2 import Environment, FileSystemLoader, select_autoescape

templates_dir = pathlib.Path(__file__).resolve().parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"])
)
