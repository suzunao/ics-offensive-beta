"""
Template Engine — Parametrización de scripts via Jinja2.
Permite crear templates reutilizables para generación de exploits adaptados.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template


class TemplateEngine:
    def __init__(self, template_dirs: Optional[list] = None):
        if template_dirs is None:
            template_dirs = [str(Path(__file__).parent.parent / "scripts" / "templates")]
        self.env = Environment(
            loader=FileSystemLoader(template_dirs),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_name: str, params: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**params)

    def render_string(self, template_string: str, params: Dict[str, Any]) -> str:
        template = self.env.from_string(template_string)
        return template.render(**params)

    def create_template(self, name: str, content: str):
        template_path = Path(self.env.loader.searchpath[0]) / name
        template_path.write_text(content)
