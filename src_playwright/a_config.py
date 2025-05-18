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
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import os
# =====================
# 1: Parámetros de Scraping
# =====================

# Años de consulta
YEARS = list(range(2024, 2026))  # no incluye el límite superior
PATH_BASE = os.getcwd()

# Selectores generales: año y frame principal
GLOBAL_SELECTORS = {"year_dropdown": "ctl00_CPH1_DrpYear", "main_frame": "frame0"}


@dataclass
class LevelConfig:
    name: str
    button: Optional[str] = None
    row: Optional[str] = None
    table_rows: Optional[str] = None
    list_xpath: Optional[str] = None
    name_xpath: Optional[str] = None
    table: Optional[str] = None
    is_final: bool = False

@dataclass
class RouteConfig:
    name: str
    file: dict[Any]
    cleaning: dict[Any]
    levels: List[LevelConfig]

# Creación de configuraciones
ROUTE_MUNICIPALIDADES = RouteConfig(
    name="MUNICIPALIDADES",
    file = {
        "ENCABEZADOS_BASE": ["Año", "Departamento", "Provincia"],  # Encabezados base
        "FILE_NAME": "EJECUCION_GASTO_GL_X_MUNICIPALIDADES.xlsx",  # Nombre del archivo de salida
    },
    cleaning = {
        "ENCABEZADOS_PROCESADOS": [
            ["Departamento", ["UBI_DPTO", "Departamento"], ":"],
            ["Provincia", ["UBI_PROV", "Provincia"], ":"],
            ["Municipalidad", ["UBI_DIST", "COD_SIAF", "Municipalidad"], "-|:"],
        ],
    },
    levels=[
        LevelConfig(
            name="Tipos de Gobierno",
            row='td:has-text("TOTAL")',
            button='input[value="Nivel de Gobierno"]'
        ),
        LevelConfig(
            name="Subtipos de Gobierno",
            row='td:has-text("GOBIERNOS LOCALES")',
            button='input[id="ctl00_CPH1_BtnSubTipoGobierno"]'
        ),
        LevelConfig(
            name="Municipalidades",
            row='td:has-text("MUNICIPALIDADES")',
            button='input[id="ctl00_CPH1_BtnDepartamento"]'
        ),
        LevelConfig(
            name="Departamentos",
            table_rows= True,
            button='input.Button[value="Provincia"]'
        ),
        LevelConfig(
            name="Provincias",
            table_rows=True,
            button='input[value="Municipalidad"]',
        ),
        LevelConfig(
            name="Municipalidades",
            table="table.MapTable",
            is_final=True
        )
    ]
)
"""
    # Ruta 2
    "SECTORES": {
        "levels": {
            "level_1": {  # Detalle niveles de gobierno
                "button": "ctl00_CPH1_BtnTipoGobierno",
                "list_xpath": None,
                "next_level": "level_2",
            },
            "level_2": {  # Nivel de gobierno: Nacional
                "button": "ctl00_CPH1_RptData_ctl01_TD0",
                "list_xpath": None,
                "next_level": "level_3",
            },
            "level_3": {  # Sectores
                "button": "ctl00_CPH1_BtnSector",
                "list_xpath": "//tr[starts-with(@id, 'tr')]",
                "name_xpath": "./td[2]",
                "next_level": "level_4",
            },
            "level_4": {  # Pliegos
                "button": "ctl00_CPH1_BtnPliego",
                "list_xpath": "//tr[starts-with(@id, 'tr')]",
                "name_xpath": "./td[2]",
                "next_level": "level_5",
            },
            "level_5": {  # Ejecutoras
                "button": "ctl00_CPH1_BtnEjecutora",
                "list_xpath": None,
                "name_xpath": None,
                "table_id": "ctl00_CPH1_Mt0",
                "next_level": None,  # Último nivel
            },
        },
    },
}
"""

# =====================
# 3: Parámetros de Procesamiento
# =====================

# Configuración columnas base y archivos de salida
FILE_CONFIGS = {
    "MUNICIPALIDADES": {
        "ENCABEZADOS_BASE": ["Año", "Departamento", "Provincia"],  # Encabezados base
        "ARCHIVO_SCRAPING": "EJECUCION_GASTO_GL_X_MUNICIPALIDADES.xlsx",  # Nombre del archivo de salida
    },
    "SECTORES": {
        "ENCABEZADOS_BASE": ["Año", "Sector", "Pliego"],
        "ARCHIVO_SCRAPING": "EJECUCION_GASTO_GN_X_SECTORES.xlsx",
    },
}


# Configuración de limpieza: split, renombrado de columnas y delimitadores
CLEANING_CONFIGS = {
    "MUNICIPALIDADES": {
        "ENCABEZADOS_PROCESADOS": [
            ["Departamento", ["UBI_DPTO", "Departamento"], ":"],
            ["Provincia", ["UBI_PROV", "Provincia"], ":"],
            ["Municipalidad", ["UBI_DIST", "COD_SIAF", "Municipalidad"], "-|:"],
        ],
    },
    "SECTORES": {
        "ENCABEZADOS_PROCESADOS": [
            ["Sector", ["COD_SEC", "Sector"], ":"],
            ["Pliego", ["COD_PLI", "Pliego"], ":"],
            ["Unidad Ejecutora", ["UE", "SEC_EJEC", "Unidad Ejecutora"], "-|:"],
        ],
    },
}
