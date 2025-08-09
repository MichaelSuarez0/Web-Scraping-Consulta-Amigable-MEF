
# =====================
# Funciones de Utilidad
# =====================
import asyncio
from functools import wraps
import sys
from rich.console import Console
from rich.table import Table
import questionary
from .a_config import LevelConfig

def handle_keyboard_interrupt(func):
    """Decorador para manejar Ctrl+C en funciones questionary"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except KeyboardInterrupt:
            if args and hasattr(args[0], 'console'):
                args[0].console.print("\n[yellow]👋 ¡Adiós![/yellow]")
            else:
                print("\n👋 ¡Adiós!")
            sys.exit(0)
    return wrapper

class ConsultaCLI:    
    GLOBAL_STYLE = questionary.Style(
        [
            ("qmark", f"fg:ansiblue bold"),  # question mark in gray
            ("question", "fg:#888888 bold"),  # question text in gray
            ("answer", "fg:#ffffff bold"),  # submitted answer in white
            ("pointer", "fg:#888888 bold"),  # pointer in gray
            ("highlighted", "fg:#ffffff bg:#444444"),  # highlighted choice
            ("selected", "fg:#ffffff bg:#666666"),  # style for selected item
        ]
    )

    def __init__(self):
        self.console = Console()

    # WRAPPERS DE STYLE
    @handle_keyboard_interrupt
    async def confirm(self, message, default=False):
        return await asyncio.to_thread(lambda: questionary.confirm(message, default=default, style=self.GLOBAL_STYLE).ask())

    @handle_keyboard_interrupt
    async def text(self, message):
        return await asyncio.to_thread(lambda: questionary.text(message, style=self.GLOBAL_STYLE).ask())


    async def create_level_config(self, name = str) -> LevelConfig:
        if name == "Nivel 1":
            extract_table = False
        else:
            extract_table = await self.confirm("¿Extraer datos de esta tabla?:", False)
        
        button = await self.text("Texto del botón que quieres presionar (si quieres terminar aquí, déjalo en blanco):")
        if button:
            fila = await self.text("Texto de la fila que quieres presionar (si quieres iterar, déjalo en blanco):")
            iterate = True if not fila else False

            level = LevelConfig(
                name=name,
                button=button,
                fila=fila,
                iterate=iterate,
                extract_table=extract_table,
            )
            self.show_level_summary_table(level)
            respuesta = await asyncio.to_thread(
                lambda: questionary.select(
                    "¿Qué quieres hacer?",
                    choices=[
                        "Confirmar y continuar",
                        "Reconfigurar este nivel"
                    ],
                ).ask())
            print()
            if respuesta == "Reconfigurar este nivel":
                print()
                return await self.create_level_config(name=name)

        else:
            level = LevelConfig(
                name=name,
                button="",
                fila="",
                iterate=False,
                extract_table=extract_table,
            )

        return level

    def show_level_summary_table(self, level: LevelConfig):
        """Muestra una tabla elegante con el resumen del nivel configurado"""
        table = Table(
            title=f"📋 Resumen del {level.name}",
            show_header=True,
            header_style="bold white",
            border_style="dim white",
            title_style="bold cyan"
        )
        # Columnas
        table.add_column("Campo", style="white", width=20)
        table.add_column("Valor", style="bright_white", width=30)
        table.add_column("Descripción", style="dim white", width=25)
        
        # Filas
        table.add_row("🏷️  Nombre", level.name, f"{level.name}")

        table.add_row(
            "🔘 Botón", level.button or "[dim]ninguno[/dim]", "Botón a presionar"
        )

        table.add_row(
            "📄 Fila",
            level.fila or "[dim]ninguna[/dim]",
            "Fila específica" if level.fila else "Iterará todas",
        )

        table.add_row(
            "🔄 Iterar", "✅ Sí" if level.iterate else "❌ No", "Por todas las filas"
        )

        table.add_row(
            "📊 Extraer", "✅ Sí" if level.extract_table else "❌ No", "Datos de tabla"
        )

        self.console.print("\n")
        self.console.print(table)
        self.console.print()
