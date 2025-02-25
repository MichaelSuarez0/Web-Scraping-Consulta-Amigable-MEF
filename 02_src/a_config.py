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

Usage:
    Run this script from the terminal or interactive environment:
        $ python 02_src/a_config.py
=====================
"""

# =====================
# Importación de librerías
# =====================

import os

# =====================
# 1: Configuración del WebDriver y Navegación
# =====================

# Directorios
PATH_BASE = os.getcwd()
PATH_DATA_RAW = os.path.join(PATH_BASE, "01_data/01_raw")
PATH_DATA_PRO = os.path.join(PATH_BASE, "01_data/02_processed")
PATH_DRIVER = os.path.join(PATH_BASE, "03_config/chromedriver/chromedriver.exe")
# Url
URL = "https://apps5.mineco.gob.pe/transparencia/mensual/"


# =====================
# 2: Parámetros de Scraping
# =====================

# Años de consulta
YEARS = list(range(2022, 2023))  # no incluye el límite superior
# Nombre del archivo de salida
ARCHIVO_SALIDA = "EJECUCION_GASTO_MUNICI.xlsx"
# Nombre del archivo de salida parcial (en caso de error)
ARCHIVO_SALIDA_PARCIAL = "EJECUCION_GASTO_MUNICI_parcial.xlsx"
# Encabezados base
ENCABEZADOS_BASE = ["Año", "Departamento", "Provincia"]

# =====================
# 3: Parámetros de Procesamiento
# =====================

ARCHIVO_PROCESADO = "EJECUCION_GASTO_MUNICI_procesado.xlsx"


# Selectores generales
GLOBAL_SELECTORS = {"year_dropdown": "ctl00_CPH1_DrpYear", "main_frame": "frame0"}


# Definir múltiples rutas con sus niveles
ROUTES = {
    "municipalidades": {
        "levels": {
            "level_1": {  # Primer nivel: Tab inicial
                "button": "ctl00_CPH1_BtnTipoGobierno",
                "list_xpath": None,  # No hay lista, solo clic
                "next_level": "level_2",
            },
            "level_2": {  # Segundo nivel: Tipo de gobierno
                "button": "tr1",
                "list_xpath": None,
                "next_level": "level_3",
            },
            "level_3": {  # Subtipo de gobierno
                "button": "ctl00_CPH1_BtnSubTipoGobierno",
                "list_xpath": None,
                "next_level": "level_4",
            },
            "level_4": {  # Gobiernos locales
                "button": "ctl00_CPH1_RptData_ctl01_TD0",
                "list_xpath": None,
                "next_level": "level_5",
            },
            "level_5": {  # Departamentos
                "button": "ctl00_CPH1_BtnDepartamento",
                "list_xpath": "//tr[starts-with(@id, 'tr')]",
                "name_xpath": "./td[2]",
                "next_level": "level_6",
            },
            "level_6": {  # Provincias
                "button": "ctl00_CPH1_BtnProvincia",
                "list_xpath": "//tr[starts-with(@id, 'tr')]",
                "name_xpath": "./td[2]",
                "next_level": "level_7",
            },
            "level_7": {  # Municipalidades (último nivel)
                "button": "ctl00_CPH1_BtnMunicipalidad",
                "list_xpath": None,
                "name_xpath": None,
                "table_id": "ctl00_CPH1_Mt0",  # Se extrae la tabla aquí
                "next_level": None,  # Último nivel
            },
        },
    }
}
