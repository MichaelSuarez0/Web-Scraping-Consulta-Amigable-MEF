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
    def from_clicks_json(cls, clicks_json: dict, route_name: str, output_path: str) -> "RouteConfig":
        """
        Convierte el JSON de clicks directamente en RouteConfig
        
        Parameters
        ----------
        clicks_json : dict
            Diccionario con formato {"clicks": [{"tag": "TD", "valor": "...", ...}, ...]}
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
        clicks = clicks_json.get("clicks", [])
        i = 0
        level_num = 1
        
        while i < len(clicks):
            click = clicks[i]
            
            # Si es TD (fila)
            if click["tag"] == "TD":
                fila = click["valor"]
                button = None
                
                # Buscar el siguiente INPUT (botón)
                if i + 1 < len(clicks) and clicks[i + 1]["tag"] == "INPUT":
                    button = clicks[i + 1]["valor"]
                    i += 2  # Saltar ambos clicks
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
            
            # Si es INPUT solo (sin fila previa)
            elif click["tag"] == "INPUT":
                levels.append(LevelConfig(
                    name=f"Nivel {level_num}",
                    button=click["valor"],
                    iterate=False,
                    extract_table=False
                ))
                level_num += 1
                i += 1
            else:
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
