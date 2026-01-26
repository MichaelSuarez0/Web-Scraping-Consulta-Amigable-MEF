"""
=====================
Project    : WS CAMEF
File       : a_config.py
Description: General configuration settings for the web scraper.
             Includes WebDriver path, target URL, and execution parameters.
Date       : 2025-02-07
Version    : 1.0
Author     : Alex Evanan

Revision History:
    - [2025-02-07] v1.0: Initial version.
    - [2025-02-25] v1.1: Added FILE_CONFIGS and ROUTES.

Usage:
    Run this script from the terminal or interactive environment:
        $ python 02_src/a_config.py
=====================
"""

from dataclasses import dataclass

# =====================
# 0: Importación de librerías
# =====================
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator
import re

# =========================================
# 1: Modelos para guardar configuraciones
# =========================================

GRABADOR_PATH = Path(__file__).parent / "g_grabador.js"


class LevelConfig(BaseModel):
    name: str
    button: Optional[str] = None
    fila: Optional[str] = None
    iterate: Optional[bool] = False
    extract_table: Optional[bool] = False



class RouteConfig(BaseModel):
    route_name: str
    output_path: str
    levels: list[LevelConfig] = Field(default_factory=list)

    
    @classmethod
    def from_script_string(cls, script_code: str, route_name: str, output_path: str) -> "RouteConfig":
        """
        Convierte código de script de Playwright en RouteConfig (sin archivo)
        
        Parameters
        ----------
        script_code : str
            Código Python generado por playwright codegen
        route_name : str
            Nombre de la ruta
        output_path : str
            Directorio de salida
        
        Returns
        -------
        RouteConfig
            Configuración de ruta lista para usar
        """
        levels = []
        level_num = 1
        
        # Regex patterns
        cell_pattern = r'\.get_by_role\("cell",\s*name="([^"]+)"'
        button_pattern = r'\.get_by_role\("button",\s*name="([^"]+)"'
        
        # Extraer todas las líneas de clicks
        lines = [line.strip() for line in script_code.split('\n') if '.click()' in line]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Buscar click en celda (fila)
            cell_match = re.search(cell_pattern, line)
            if cell_match:
                fila = cell_match.group(1)
                button = None
                
                # Buscar el siguiente botón
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    button_match = re.search(button_pattern, next_line)
                    if button_match:
                        button = button_match.group(1)
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
                
                levels.append(LevelConfig(
                    name=f"Nivel {level_num}",
                    fila=fila,
                    button=button,
                    iterate=False,
                    extract_table=False
                ))
                level_num += 1
            
            # Click solo en botón
            else:
                button_match = re.search(button_pattern, line)
                if button_match:
                    levels.append(LevelConfig(
                        name=f"Nivel {level_num}",
                        button=button_match.group(1),
                        iterate=False,
                        extract_table=False
                    ))
                    level_num += 1
                i += 1
        
        return cls(route_name=route_name, output_path=output_path, levels=levels)


# =====================
# 2: Selectores CSS
# =====================
@dataclass
class Locators:
    """
    Locators en CSS presentes en la página de Consulta Amigable para interactuar con botones, filas, etc.
    """

    # Botones
    main_frame = "frame0"
    table_data = "table.Data"
    buttons = "input[type='submit']"
    text_rows = "td[align='left']"
