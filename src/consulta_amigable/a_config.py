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

# =====================
# 0: Importación de librerías
# =====================
from pydantic import BaseModel, Field
from typing import Optional
from dataclasses import dataclass

# =========================================
# 1: Modelos para guardar configuraciones
# =========================================

class LevelConfig(BaseModel):
    name: str
    button: Optional[str] = None
    fila: Optional[str] = None
    iterate: Optional[bool] = False
    extract_table: Optional[bool] = False
    
class RouteConfig(BaseModel):
    route_name: str
    output_path: str
    levels: Optional[list[LevelConfig]] = Field(default_factory=list)

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
    