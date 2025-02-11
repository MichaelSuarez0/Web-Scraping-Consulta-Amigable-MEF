"""
=====================
Project    : WS CAMRF
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

import os

# 1: Configuración del WebDriver y Navegación

# Directorios
PATH_BASE = os.getcwd()
PATH_DATA_RAW = os.path.join(PATH_BASE, "01_data/01_raw")
PATH_DRIVER = os.path.join(PATH_BASE, "03_config/chromedriver/chromedriver.exe")
# Url
URL = "https://apps5.mineco.gob.pe/transparencia/mensual/"


# 2: Parámetros de Scraping

YEARS = [2024]
# Nombre del archivo de salida
ARCHIVO_SALIDA = "datos_municipalidades.xlsx"
# Encabezados base para el archivo de salida (antes de agregar los de la tabla)
ENCABEZADOS_BASE = ["Año", "Departamento", "Provincia"]
