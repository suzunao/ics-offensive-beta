"""Registro automático de tools MCP desde los scripts de src/scripts/"""

import ast
import inspect
from pathlib import Path
from typing import Callable
import yaml

TOOL_METADATA_PATH = Path(__file__).parent / "metadata.yaml"

def load_metadata():
    with open(TOOL_METADATA_PATH) as f:
        return yaml.safe_load(f) or {}

def generate_tool_wrapper(script_path: str, function_name: str, metadata: dict) -> Callable:
    import importlib.util

    spec = importlib.util.spec_from_file_location(f"src.scripts.{script_path.replace('/', '.')}",
                                                   Path(f"src/scripts/{script_path}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    func = getattr(module, function_name)

    return func
