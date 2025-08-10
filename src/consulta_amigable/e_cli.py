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
            ("qmark", f"fg:ansiblue bold"),
            ("question", "fg:#888888 bold"),
            ("answer", "fg:#ffffff bold"),
            ("pointer", "fg:#888888 bold"),
            ("highlighted", "fg:#ffffff bg:#444444"),
            ("selected", "fg:#ffffff bg:#666666"),
        ]
    )

    def __init__(self):
        self.console = Console()

    # WRAPPERS DE STYLE
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

    async def create_level_config(
        self, name: str, buttons: list[str], filas: list[str]
    ) -> LevelConfig:
        if name == "Nivel 1":
            extract_table = False
        else:
            extract_table = await self.confirm("¿Extraer datos de esta tabla?:", False)

        button = await self.select(
            message="Botón a presionar (selecciona NINGUNO para terminar aquí):",
            choices=buttons + ["NINGUNO"],
        )
        if button != "NINGUNO":
            fila = await self.select(
                "Fila a presionar (selecciona ITERAR para entrar a todas una por una):",
                choices=filas + ["ITERAR"],
            )
            iterate = True if fila == "ITERAR" else False

            level = LevelConfig(
                name=name,
                button=button,
                fila=fila,
                iterate=iterate,
                extract_table=extract_table,
            )
            self.show_level_summary_table(level)
            respuesta = await self.select(
                "¿Qué quieres hacer?",
                choices=["Confirmar y continuar", "Reconfigurar este nivel"],
            )
            print()
            if respuesta == "Reconfigurar este nivel":
                print()
                return await self.create_level_config(
                    name=name, buttons=buttons, filas=filas
                )

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

        self.console.print("\n")
        self.console.print(table)
        self.console.print()
