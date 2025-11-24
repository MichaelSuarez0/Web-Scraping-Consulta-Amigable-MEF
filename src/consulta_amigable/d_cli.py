# =====================
# Funciones de Utilidad
# =====================
import asyncio
from functools import wraps
import questionary
from rich.console import Console
from rich.table import Table
from .a_config import LevelConfig


def handle_keyboard_interrupt(func):
    """Decorador para manejar Ctrl+C en funciones questionary"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        def _bye():
            console = getattr(args[0], "console", None) if args else None
            if console:
                console.print(
                    "\n[yellow]👋 Cancelado por el usuario. Saliendo...[/yellow]"
                )
            else:
                print("\n👋 Cancelado por el usuario. Saliendo...")
            raise SystemExit(0)

        try:
            result = await func(*args, **kwargs)
            # questionary.*.ask() puede devolver None en cancelación (ESC/Ctrl+C)
            if result is None:
                _bye()
            return result

        except (KeyboardInterrupt, EOFError):
            _bye()
        except asyncio.CancelledError:
            # A veces los runners cancelan la tarea: trátalo igual que cancelación del usuario
            _bye()
            raise SystemExit(0)

    return wrapper


class ConsultaCLI:
    GLOBAL_STYLE = questionary.Style(
        [
            ("qmark", "fg:ansiblue bold"),
            ("question", "fg:#888888 bold"),
            ("answer", "fg:#ffffff bold"),
            ("pointer", "fg:#888888 bold"),
            ("highlighted", "fg:#ffffff bg:#444444"),
            ("selected", "fg:#ffffff bg:#666666"),
        ]
    )

    def __init__(self):
        self.console = Console()

    @handle_keyboard_interrupt
    async def confirm(self, message, default=False):
        return await asyncio.to_thread(
            lambda: questionary.confirm(
                message, default=default, style=self.GLOBAL_STYLE
            ).ask()
        )

    @handle_keyboard_interrupt
    async def text(self, message):
        return await asyncio.to_thread(
            lambda: questionary.text(message, style=self.GLOBAL_STYLE).ask()
        )

    @handle_keyboard_interrupt
    async def select(self, message, choices):
        return await asyncio.to_thread(
            lambda: questionary.select(message, choices, style=self.GLOBAL_STYLE).ask()
        )

    async def select_button(self, available_buttons: list[str]) -> str:
        """Prompt to select a button in the first row"""
        return await self.select(
            message="Usa ↑ ↓ para moverte y Enter para seleccionar el botón:",
            choices=available_buttons,
        )

    async def select_row(self, available_rows: list[str]) -> str:
        """Prompt to select a row in the table"""
        return await self.select(
            "Fila a presionar (selecciona ITERAR para entrar a todas una por una o TERMINAR para guardar y salir):",
            choices=available_rows + ["ITERAR"] + ["TERMINAR"],
        )

    async def confirm_table_extraction(self):
        return await self.confirm("¿Scrapear esta tabla?:", False)

    async def confirm_level_and_continue(self)-> bool:
        confirm = await self.select(
            "¿Qué quieres hacer?",
            choices=["Confirmar y continuar", "Reconfigurar este nivel"],
        )
        return False if confirm == "Reconfigurar este nivel" else True

    def show_level_summary_table(self, level: LevelConfig)-> None:
        """Muestra una tabla elegante con el resumen del nivel configurado"""
        table = Table(
            title=f"📋 Resumen del {level.name}",
            show_header=True,
            header_style="bold white",
            border_style="dim white",
            title_style="bold cyan",
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
            "Fila específica",
        )

        table.add_row(
            "🔄 Iterar", "✅ Sí" if level.iterate else "❌ No", "Iterar todas las filas"
        )

        table.add_row(
            "📊 Extraer",
            "✅ Sí" if level.extract_table else "❌ No",
            "Scrapear datos de tabla",
        )

        self.console.print(table)
        self.console.print()
