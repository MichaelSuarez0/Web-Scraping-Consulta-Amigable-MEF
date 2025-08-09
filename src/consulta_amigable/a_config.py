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
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List

# =====================
# 1: Modelos de Scraping
# =====================

class LevelConfig(BaseModel):
    name: str
    button: Optional[str] = None
    fila: Optional[str] = None
    iterate: Optional[bool] = False
    extract_table: Optional[bool] = False

    # @property
    # def button_xpath(self):
    #     if self.button is not None:
    #         return f'//input[contains(translate(@value, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{self.button.lower()}")]'
    #     else:
    #         return None
    
    # @property
    # def row_xpath(self):
    #     if self.row is not None:
    #         return f'//td[contains(translate(@value, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{self.row.lower()}")]'
    #     else:
    #         return None

    # @property
    # def table_xpath(self):
    #     if self.table is not False:
    #         return f'table.MapTable'
    #     else:
    #         return None


# TODO: Obtener nombres de niveles dinámicamente (a partir de la primera columna de la tabla)
class RouteConfig(BaseModel):
    route_name: str
    output_path: str
    levels: Optional[list[LevelConfig]] = Field(default_factory=list)
