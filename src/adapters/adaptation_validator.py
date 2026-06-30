"""
Adaptation Validator — Valida y puntúa adaptaciones de scripts para evitar
modificaciones excesivas que degraden la precisión del MCP.
Cada adaptación pasa por un gate de calidad antes de ser aceptada.
"""
import ast
import difflib
import re
from typing import Dict, Any, List, Optional


BANNED_PATTERNS = [
    r"while\s+True\s*:",
    r"while\s+1\s*:",
    r"os\.system\s*\(\s*['\"]rm\s+-rf",
    r"__import__\s*\(",
    r"eval\s*\(.*input",
    r"exec\s*\(.*input",
    r"subprocess\.call\s*\(\s*['\"](?:rm|format|dd|mkfs)",
]

REQUIRED_MODULES = {
    "asyncio", "socket", "struct", "json", "yaml",
    "typing", "pathlib", "importlib", "logging",
}

OPTIONAL_MODULES = {
    "scapy", "pymodbus", "snap7", "pycomm3", "pydnp3",
    "paramiko", "requests", "jinja2", "pyserial",
    "dnspython", "OpenSSL", "Crypto",
    "pywin32", "pywinrm", "binwalk",
}

SAFE_IMPORTS = REQUIRED_MODULES | OPTIONAL_MODULES | {
    "os", "sys", "re", "math", "random", "time", "datetime",
    "hashlib", "base64", "json", "csv", "copy", "itertools",
    "collections", "functools", "abc", "enum",
    "src.adapters", "src.protocols", "src.utils", "src.scripts",
}


class AdaptationValidator:
    def __init__(self, min_threshold: float = 0.7):
        self.min_threshold = min_threshold

    def validate(self, adapted: str, original: str = "") -> Dict[str, Any]:
        """
        Valida una adaptación y devuelve resultado con puntuación.

        Args:
            adapted: Código adaptado por el modelo
            original: Código original (base) para comparación

        Returns:
            Dict con score (0-1), accepted (bool), report detallado
        """
        scores = {}
        details = []

        syntax_score, syntax_issues = self._check_syntax(adapted)
        scores["syntax"] = syntax_score
        details.append(f"syntax: {syntax_score*100:.0f}%")
        if syntax_issues:
            details.extend([f"  - {i}" for i in syntax_issues])

        structure_score, structure_issues = self._check_structure(adapted)
        scores["structure"] = structure_score
        details.append(f"structure: {structure_score*100:.0f}%")
        if structure_issues:
            details.extend([f"  - {i}" for i in structure_issues])

        if original:
            diff_score, diff_issues = self._check_diff_ratio(adapted, original)
            scores["diff_ratio"] = diff_score
            details.append(f"diff_ratio: {diff_score*100:.0f}%")
            if diff_issues:
                details.extend([f"  - {i}" for i in diff_issues])

        danger_score, danger_issues = self._check_dangerous_patterns(adapted)
        scores["dangerous_patterns"] = danger_score
        details.append(f"dangerous_patterns: {danger_score*100:.0f}%")
        if danger_issues:
            details.extend([f"  - {i}" for i in danger_issues])

        compat_score, compat_issues = self._check_compatibility(adapted)
        scores["compatibility"] = compat_score
        details.append(f"compatibility: {compat_score*100:.0f}%")
        if compat_issues:
            details.extend([f"  - {i}" for i in compat_issues])

        precision_score, precision_issues = self._check_precision(adapted)
        scores["precision"] = precision_score
        details.append(f"precision: {precision_score*100:.0f}%")
        if precision_issues:
            details.extend([f"  - {i}" for i in precision_issues])

        weights = {
            "syntax": 0.20,
            "structure": 0.20,
            "dangerous_patterns": 0.20,
            "compatibility": 0.15,
            "precision": 0.15,
            "diff_ratio": 0.10,
        }

        total_weight = sum(weights.get(k, 0.10) for k in scores)
        weighted_score = sum(
            scores[k] * weights.get(k, 0.10) for k in scores
        ) / total_weight if total_weight > 0 else 0.0

        accepted = weighted_score >= self.min_threshold

        return {
            "score": round(weighted_score, 4),
            "min_threshold": self.min_threshold,
            "accepted": accepted,
            "detail_scores": scores,
            "report": details if details else ["ok"],
            "issues": syntax_issues + structure_issues + danger_issues + compat_issues + precision_issues,
        }

    def _check_syntax(self, code: str) -> tuple:
        try:
            ast.parse(code)
            return 1.0, []
        except SyntaxError as e:
            return 0.0, [f"SyntaxError at line {e.lineno}: {e.msg}"]

    def _check_structure(self, code: str) -> tuple:
        issues = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0, ["cannot parse (syntax error)"]

        func_count = 0
        class_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_count += 1
            elif isinstance(node, ast.ClassDef):
                class_count += 1

        if func_count == 0 and class_count == 0:
            issues.append("no functions or classes defined")

        has_main = False
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                has_main = True
            if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                has_main = True

        score = 1.0
        if issues:
            score = 0.5
        return score, issues

    def _check_diff_ratio(self, adapted: str, original: str) -> tuple:
        if not original:
            return 1.0, []

        orig_lines = original.strip().splitlines()
        adapt_lines = adapted.strip().splitlines()

        matcher = difflib.SequenceMatcher(None, orig_lines, adapt_lines)
        ratio = matcher.ratio()

        if ratio < 0.3:
            return 0.3, [f"adaptation changes too much (dice: {ratio:.2f}), risky"]
        elif ratio < 0.5:
            return 0.6, [f"high modification rate (dice: {ratio:.2f})"]
        elif ratio < 0.7:
            return 0.8, [f"moderate changes (dice: {ratio:.2f})"]

        return 1.0, []

    def _check_dangerous_patterns(self, code: str) -> tuple:
        issues = []
        score = 1.0

        for pattern in BANNED_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                issues.append(f"banned pattern detected: {pattern}")
                score = 0.0

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0, issues

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"system", "popen", "call", "run"}:
                        func_name = f"{node.func.attr}"
                        issues.append(f"subprocess call: {func_name}")
                        score = min(score, 0.5)
                elif isinstance(node.func, ast.Name):
                    if node.func.id in {"eval", "exec", "compile", "__import__"}:
                        issues.append(f"dynamic execution: {node.func.id}")
                        score = min(score, 0.3)
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr == "send" and isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                        pass

            if isinstance(node, ast.While):
                if node.orelse:
                    pass

            if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
                if isinstance(node.iter.func, ast.Attribute) and node.iter.func.attr == "repeat":
                    issues.append("potential infinite loop with itertools.repeat")

        return score, issues

    def _check_compatibility(self, code: str) -> tuple:
        issues = []
        score = 1.0

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0, ["cannot parse"]

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                else:
                    names = [f"{node.module}.{alias.name}" if node.module else alias.name for alias in node.names]

                for name in names:
                    base = name.split(".")[0]
                    if base not in SAFE_IMPORTS and not base.startswith("src."):
                        issues.append(f"unknown import: {name}")
                        score = min(score, 0.6)

        return score, issues

    def _check_precision(self, code: str) -> tuple:
        issues = []
        score = 1.0

        placeholders = re.findall(r'127\.0\.0\.1|0\.0\.0\.0|__FILL__|__CHANGE__|__TODO__|TODO:|FIXME:|placeholder|example\.com', code, re.IGNORECASE)
        if placeholders:
            issues.append(f"placeholder values remain: {set(placeholders)}")
            score = min(score, 0.4)

        bare_excepts = 0
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    bare_excepts += 1
        except:
            pass

        if bare_excepts > 3:
            issues.append(f"excessive bare excepts ({bare_excepts}), reduces debuggability")
            score = min(score, 0.7)

        return score, issues
