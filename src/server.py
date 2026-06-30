"""
ICS Offensive MCP Server
FastMCP server that exposes OT/ICS/SCADA offensive tools.
"""
import importlib
import pkgutil
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ics-offensive-mcp")

def _discover_and_register_tools():
    import src.tools
    tool_modules = []
    for finder, name, ispkg in pkgutil.iter_modules(src.tools.__path__):
        if not ispkg and name != "registry":
            tool_modules.append(name)

    for name in tool_modules:
        mod = importlib.import_module(f"src.tools.{name}")
        if hasattr(mod, "register_tools"):
            mod.register_tools(mcp)

    _register_manual_tools()

def _register_manual_tools():
    @mcp.tool()
    async def generate_exploit_script(
        target_ip: str,
        technique: str,
        target_vendor: str = "",
        target_model: str = "",
        parameters: dict = {}
    ) -> str:
        """
        Genera un script de explotación adaptado a un objetivo específico.

        Args:
            target_ip: IP del dispositivo objetivo
            technique: Técnica a usar (ej: s7_extract, modbus_write, dnp3_crob)
            target_vendor: Vendor detectado (siemens, rockwell, schneider, etc.)
            target_model: Modelo específico (S7-1200, MicroLogix, M340, etc.)
            parameters: Parámetros adicionales específicos de la técnica

        Returns:
            Código Python del script generado
        """
        from src.adapters.script_generator import ScriptGenerator
        gen = ScriptGenerator()
        return gen.generate(target_ip, technique, target_vendor, target_model, parameters)

    @mcp.tool()
    async def adapt_script_with_model(
        base_script: str,
        model_instructions: str,
        target_ip: str = "",
        target_vendor: str = "",
        target_model: str = ""
    ) -> str:
        """
        Integra mejoras del modelo (LLM) en un script base para adaptarlo dinámicamente.
        El agente (modelo) analiza el script base, lo adapta al target específico
        y devuelve una versión mejorada.

        Args:
            base_script: Script base generado por generate_exploit_script
            model_instructions: Instrucciones del modelo para adaptar el script
            target_ip: IP del target (opcional, para contexto)
            target_vendor: Vendor del target (opcional, para contexto)
            target_model: Modelo del target (opcional, para contexto)

        Returns:
            Script adaptado con las mejoras del modelo
        """
        from src.adapters.script_generator import ScriptGenerator
        gen = ScriptGenerator()
        ctx = {
            "target_ip": target_ip,
            "target_vendor": target_vendor,
            "target_model": target_model,
        }
        return gen.generate_with_model(base_script, model_instructions, ctx)

    @mcp.tool()
    async def validate_script_code(script: str) -> dict:
        """
        Valida sintácticamente un script sin ejecutarlo.
        Útil para verificar que el código adaptado por el modelo es válido.

        Args:
            script: Código Python a validar

        Returns:
            Resultado de validación (syntax_ok, imports, functions, errors)
        """
        from src.adapters.script_generator import ScriptGenerator
        gen = ScriptGenerator()
        return gen.validate_script(script)

    @mcp.tool()
    async def validate_adaptation(
        adapted_script: str,
        original_script: str = "",
        min_threshold: float = 0.7
    ) -> dict:
        """
        Valida y puntúa una adaptación de script antes de aceptarla.
        Cada adaptación pasa por un quality gate: sintaxis, estructura,
        patrones peligrosos, compatibilidad, precisión y ratio de cambio.
        Si el score < threshold, la adaptación es RECHAZADA.

        Args:
            adapted_script: Código adaptado por el modelo
            original_script: Código original para comparar cambios
            min_threshold: Umbral mínimo de aceptación (0.0 - 1.0, default 0.7)

        Returns:
            Dict con score, accepted, detail_scores y report de issues
        """
        from src.adapters.adaptation_validator import AdaptationValidator
        validator = AdaptationValidator(min_threshold=min_threshold)
        return validator.validate(adapted_script, original_script)

    @mcp.tool()
    async def save_adapted_script(
        script: str,
        technique: str,
        target_ip: str
    ) -> str:
        """
        Guarda un script adaptado por el modelo para reuso futuro.

        Args:
            script: Código adaptado a guardar
            technique: Técnica asociada
            target_ip: IP del target

        Returns:
            Ruta del archivo guardado
        """
        from src.adapters.script_generator import ScriptGenerator
        gen = ScriptGenerator()
        return gen.save_adapted_script(script, technique, target_ip)

    @mcp.tool()
    async def analyze_target(target_ip: str, ports: str = "102,502,20000,44818") -> str:
        """
        Analiza un dispositivo OT/ICS para identificar vendor, modelo y servicios.

        Args:
            target_ip: IP del dispositivo
            ports: Puertos a escanear (separados por coma)

        Returns:
            Perfil del target en YAML
        """
        from src.adapters.target_analyzer import TargetAnalyzer
        analyzer = TargetAnalyzer()
        return await analyzer.analyze(target_ip, ports)

    @mcp.tool()
    async def select_techniques(target_profile: str, goal: str = "initial_access") -> list:
        """
        Selecciona las mejores técnicas para un perfil de target.

        Args:
            target_profile: Perfil YAML del target (output de analyze_target)
            goal: Objetivo (initial_access, persistence, c2, etc.)

        Returns:
            Lista de técnicas recomendadas con descripción
        """
        from src.adapters.technique_selector import TechniqueSelector
        selector = TechniqueSelector()
        return selector.select(target_profile, goal)

def main():
    _discover_and_register_tools()
    mcp.run()

if __name__ == "__main__":
    main()
