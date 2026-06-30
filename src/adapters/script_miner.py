"""
Script Miner — Extrae scripts y parámetros de los archivos .md de las lecciones.
Permite que el MCP aprenda nuevas técnicas automáticamente desde los markdowns.
"""
import re
from pathlib import Path
from typing import List, Dict

class ScriptMiner:
    def __init__(self, lessons_dir: Path):
        self.lessons_dir = lessons_dir
        self.scripts_index = {}

    def mine_all(self) -> Dict[str, List[Dict]]:
        for md_file in sorted(self.lessons_dir.glob("Lesson *.md")):
            lesson_name = md_file.stem
            lesson_scripts = self.mine_file(md_file)
            self.scripts_index[lesson_name] = lesson_scripts
        return self.scripts_index

    def mine_file(self, md_path: Path) -> List[Dict]:
        content = md_path.read_text()
        scripts = []

        python_blocks = re.finditer(
            r'```python\n(.*?)```',
            content,
            re.DOTALL
        )

        for i, block in enumerate(python_blocks):
            code = block.group(1).strip()
            if not code or len(code) < 50:
                continue

            block_start = block.start()
            context_start = max(0, block_start - 500)
            context = content[context_start:block_start]

            params = self._extract_parameters(code)

            script_info = {
                "source_file": str(md_path),
                "block_index": i,
                "language": "python",
                "code": code,
                "parameters": params,
                "context": context.strip()[:200],
                "title": self._extract_section_title(content, block_start),
            }
            scripts.append(script_info)

        bash_blocks = re.finditer(
            r'```(?:bash|shell|sh|powershell)\n(.*?)```',
            content,
            re.DOTALL
        )

        for i, block in enumerate(bash_blocks):
            code = block.group(1).strip()
            if not code:
                continue

            script_info = {
                "source_file": str(md_path),
                "block_index": i,
                "language": "bash",
                "code": code,
                "parameters": {},
                "context": "",
                "title": self._extract_section_title(content, block.start()),
            }
            scripts.append(script_info)

        return scripts

    def _extract_section_title(self, content: str, position: int) -> str:
        before = content[:position]
        headings = list(re.finditer(r'^#{1,3}\s+(.+)$', before, re.MULTILINE))
        if headings:
            return headings[-1].group(1).strip()
        return ""

    def _extract_parameters(self, code: str) -> List[Dict]:
        params = []

        func_matches = re.finditer(
            r'def\s+\w+\s*\((.*?)\)(?:\s*->.*?)?:',
            code,
            re.DOTALL
        )

        for func_match in func_matches:
            args_str = func_match.group(1)
            args = re.findall(
                r'(\w+)\s*(?::\s*(\w+(?:\[.*?\])?))?\s*(?:=\s*([^,]+))?',
                args_str
            )
            for name, type_hint, default in args:
                param = {
                    "name": name,
                    "type": type_hint if type_hint else "str",
                    "default": default.strip() if default else None,
                    "required": default is None,
                }
                params.append(param)

        ip_vars = re.findall(r'(?:target_ip|ip|host|server)\s*[:=]\s*["\']([^"\']+)["\']', code)
        port_vars = re.findall(r'(?:port|tcp_port)\s*[:=]\s*(\d+)', code)

        return params

    def discover_techniques(self) -> Dict[str, List[str]]:
        if not self.scripts_index:
            self.mine_all()

        lesson_domain = {
            "Lesson 01": "plc",
            "Lesson 02": "scada",
            "Lesson 03": "mitm",
            "Lesson 04": "plc",
            "Lesson 05": "grid",
            "Lesson 06": "firmware",
            "Lesson 07": "supply_chain",
            "Lesson 08": "persistence",
            "Lesson 09": "c2",
            "Lesson 10": "full_operation",
        }

        techniques = {}
        for lesson, scripts in self.scripts_index.items():
            for key in lesson_domain:
                if key in lesson:
                    domain = lesson_domain[key]
                    if domain not in techniques:
                        techniques[domain] = []
                    for s in scripts:
                        if s["title"]:
                            techniques[domain].append(s["title"])
                    break

        return techniques
