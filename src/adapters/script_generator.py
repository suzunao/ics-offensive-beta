"""
Script Generator — Genera scripts de explotación adaptados a cualquier target.
Soporta adaptación vía modelo (LLM) para mejora dinámica de scripts.
"""
import importlib
import inspect
import ast
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template


class ScriptGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "scripts" / "templates"
        self.template_dir.mkdir(exist_ok=True)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _load_source_script(self, technique: str) -> str:
        technique_map = {
            "s7_extract": ("plc.siemens_s7", "extract_plc_program"),
            "s7_inject": ("plc.siemens_s7", "inject_malicious_logic"),
            "s7_password_crack": ("plc.siemens_s7", "crack_s7_password"),
            "modbus_write": ("plc.schneider_modicon", "modbus_write"),
            "modbus_read": ("plc.schneider_modicon", "modbus_read"),
            "cip_tag_write": ("plc.allen_bradley", "write_tag"),
            "dnp3_crob": ("rtu.dnp3_crob", "crob_inject"),
            "iec104_mass_trip": ("rtu.iec104_breaker", "mass_trip"),
            "goose_spoof": ("grid.goose_spoof", "goose_spoof"),
            "plc_fw_rootkit": ("persistence.plc_firmware_rootkit", "deploy_firmware_rootkit"),
            "dns_c2": ("c2.dns_tunnel", "start_dns_c2"),
            "modbus_c2": ("c2.modbus_c2", "start_modbus_c2"),
        }

        if technique not in technique_map:
            raise ValueError(f"Technique '{technique}' not found")

        module_path, func_name = technique_map[technique]
        try:
            mod = importlib.import_module(f"src.scripts.{module_path}")
            func = getattr(mod, func_name)
            source = inspect.getsource(func)
            return source
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Cannot load technique '{technique}': {e}")

    def _render_template(self, source_code: str, params: Dict[str, Any]) -> str:
        template_code = source_code

        replacements = {
            "target_ip": params.get("target_ip", "127.0.0.1"),
            "target_port": params.get("target_port", 502),
            "rack": str(params.get("rack", 0)),
            "slot": str(params.get("slot", 1)),
        }

        for old, new in replacements.items():
            template_code = template_code.replace(old, new)

        for key, value in params.get("extra_params", {}).items():
            template_code = template_code.replace(f"{{{{ {key} }}}}", str(value))
            template_code = template_code.replace(key, str(value))

        return template_code

    def generate(
        self,
        target_ip: str,
        technique: str,
        target_vendor: str = "",
        target_model: str = "",
        parameters: Optional[Dict] = None
    ) -> str:
        params = parameters or {}
        params["target_ip"] = target_ip
        params["target_vendor"] = target_vendor
        params["target_model"] = target_model

        source = self._load_source_script(technique)
        script = self._render_template(source, params)

        header = f"""#!/usr/bin/env python3
# ICS Offensive MCP - Generated Script
# Technique: {technique}
# Target: {target_ip} ({target_vendor} {target_model})
# Generated: Auto

"""
        return header + script

    def generate_with_model(
        self,
        base_script: str,
        model_instructions: str,
        target_context: Optional[Dict] = None
    ) -> str:
        """
        Integra mejoras del modelo (LLM) en un script base.
        El modelo analiza el script base y las instrucciones,
        luego produce una versión adaptada y optimizada.

        Args:
            base_script: Script base generado por generate()
            model_instructions: Instrucciones del modelo para adaptar el script
            target_context: Contexto adicional del target (vendor, modelo, fw, etc.)

        Returns:
            Script adaptado con las mejoras del modelo
        """
        ctx = target_context or {}
        ctx_str = "\n".join(f"#   {k}: {v}" for k, v in ctx.items())

        template = """#!/usr/bin/env python3
# ICS Offensive MCP - Model-Adapted Script
# === CONTEXTO DEL TARGET ===
{context}
# === INSTRUCCIONES DEL MODELO ===
# {instructions}
# === SCRIPT BASE ===
{base}
"""
        return template.format(
            context=ctx_str if ctx_str else "#   (sin contexto adicional)",
            instructions=model_instructions.replace("\n", "\n# "),
            base=base_script
        )

    def validate_script(self, script: str) -> Dict[str, Any]:
        """
        Valida sintácticamente un script generado o adaptado.
        Devuelve resultado de validación sin ejecutar el código.
        """
        result = {
            "valid": False,
            "syntax_ok": False,
            "imports": [],
            "functions": [],
            "errors": []
        }

        try:
            tree = ast.parse(script)
            result["syntax_ok"] = True

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        result["imports"].append(f"{module}.{alias.name}")
                elif isinstance(node, ast.FunctionDef):
                    result["functions"].append(node.name)

            result["valid"] = True
        except SyntaxError as e:
            result["errors"].append(f"SyntaxError: {e.msg} at line {e.lineno}")
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")

        return result

    def save_adapted_script(self, script: str, technique: str, target_ip: str) -> str:
        """
        Guarda un script adaptado en el directorio de scripts adaptados.
        """
        adapted_dir = Path(__file__).parent.parent / "scripts" / "adapted"
        adapted_dir.mkdir(exist_ok=True)

        safe_ip = target_ip.replace(".", "_")
        filename = f"{technique}__{safe_ip}__adapted.py"
        filepath = adapted_dir / filename
        filepath.write_text(script)

        return str(filepath)
