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
YEARS = list(range(2024, 2026))  # no incluye el límite superior


# Selectores generales: año y frame principal
GLOBAL_SELECTORS = {"year_dropdown": "ctl00_CPH1_DrpYear", "main_frame": "frame0"}


# Definir múltiples rutas con sus niveles
ROUTES = {
    # Ruta 1
    "MUNICIPALIDADES": {
        "levels": {
            "level_1": {  # Detalle niveles de gobierno
                "button": "ctl00_CPH1_BtnTipoGobierno",  # Botón XPath
                "list_xpath": None,  # Lista para iterar
                "next_level": "level_2",  # Siguiente nivel
            },
            "level_2": {  # Nivel de gobierno: Gob locales
                "button": "ctl00_CPH1_RptData_ctl02_TD0",
                "list_xpath": None,
                "next_level": "level_3",
            },
            "level_3": {  # Subtipo de gobierno locales
                "button": "ctl00_CPH1_BtnSubTipoGobierno",
                "list_xpath": None,
                "next_level": "level_4",
            },
            "level_4": {  # Gobiernos local: Municipalidades
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
            "level_7": {  # Lista Municipalidades (último nivel)
                "button": "ctl00_CPH1_BtnMunicipalidad",
                "list_xpath": None,
                "name_xpath": None,
                "table_id": "ctl00_CPH1_Mt0",  # Se extrae la tabla aquí
                "next_level": None,  # Último nivel
            },
        },
    },
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
