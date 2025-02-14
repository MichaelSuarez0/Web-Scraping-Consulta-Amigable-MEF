"""
=====================
Project     : WS CAMEF
File        : c_cleaner.py
Description : Cleaning and preprocessing data extracted via web scraping.
Date        : 2025-02-11
Version     : 1.0
Author      : Alex Evanan

Revision History:
    - [2025-02-07]  v1.0: Initial version.

Notes:
    - Developed with Python 3.11.9.
    - Compatible with JupyterLab, Notebook, and Google Colab.
    - Dependencies are listed in 'requirements.txt'.

Usage:
    Run this script from the terminal or interactive environment:
        $ python 02_src/c_cleaner.py
=====================
"""

# =====================
# Importación de librerías
# =====================
import sys
import os

import pandas as pd
import numpy as np

# Configuración desde 02_src/0_config.py
sys.path.append(os.path.join(os.getcwd(), "02_src"))
import a_config

# =====================
# Importacion de data
# =====================


def read_files(ruta_archivo, hoja=0):
    """
    Lee un archivo Excel (.xlsx, .xls) o CSV (.csv) y devuelve un DataFrame.
    """
    try:
        if ruta_archivo.endswith((".xlsx", ".xls")):
            return pd.read_excel(ruta_archivo, sheet_name=hoja)
        elif ruta_archivo.endswith(".csv"):
            print(f"{ruta_archivo} leido.")
            return pd.read_csv(ruta_archivo)
        else:
            raise ValueError("Formato no soportado. Usa .xlsx, .xls o .csv.")
    except Exception as e:
        print(f"Error al leer el archivo '{ruta_archivo}': {e}")
        return None


def split_column(df, source_col, new_cols, delimiter, max_splits=None):
    """
    Divide una columna en dos nuevas columnas eliminando la original.
    """
    if len(new_cols) < 2:
        raise ValueError(
            "Debes proporcionar al menos dos nombres para las nuevas columnas."
        )

    if source_col not in df.columns:
        raise ValueError(f"La columna '{source_col}' no existe en el DataFrame.")

    if max_splits is None:
        max_splits = len(new_cols) - 1

    # Dividir la columna y asignar a las nuevas columnas
    df[new_cols] = (
        df.pop(source_col)
        .str.split(delimiter, n=max_splits, expand=True)
        .apply(lambda x: x.str.strip())
        .astype(str)
    )

    return df


def numeric_columns(df, columns):
    """
    Limpia múltiples columnas numéricas eliminando comas y convierte a tipo numérico.
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ""), errors="coerce"
            )
        else:
            print(f"Advertencia: La columna '{col}' no existe en el DataFrame.")
    return df


def save_data(nombre_archivo, datos):
    """
    Guarda los datos extraídos en un archivo Excel.
    """
    try:
        df = pd.DataFrame(datos)
        df.to_excel(nombre_archivo, index=False)
        print(f"Datos guardados correctamente en {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar en Excel: {e}")


def main():
    # Leer el archivo de salida
    df = read_files(os.path.join(a_config.PATH_DATA_RAW, a_config.ARCHIVO_SALIDA))

    # Limpiar y procesar los datos
    df = split_column(
        df,
        source_col="Departamento",
        new_cols=["UBI_DPTO", "Departamento"],
        delimiter=":",
    )

    df = split_column(
        df, source_col="Provincia", new_cols=["UBI_PROV", "Provincia"], delimiter=":"
    )

    df = split_column(
        df,
        source_col="Municipalidad",
        new_cols=["UBI_DIST", "COD_SIAF", "Municipalidad"],
        delimiter="-|:",
    )

    # Convertir columnas numéricas
    cols = [
        "PIA",
        "PIM",
        "Certificación",
        "Compromiso Anual",
        "Atención de Compromiso Mensual",
        "Devengado",
        "Girado",
    ]
    df = numeric_columns(df, cols)

    # Ordenar y exportar los datos
    cols_orden = [
        "Año",
        "UBI_DPTO",
        "Departamento",
        "UBI_PROV",
        "Provincia",
        "UBI_DIST",
        "COD_SIAF",
        "Municipalidad",
        "PIA",
        "PIM",
        "Certificación",
        "Compromiso Anual",
        "Atención de Compromiso Mensual",
        "Devengado",
        "Girado",
        "Avance %",
    ]

    df = df[cols_orden]

    save_data(os.path.join(a_config.PATH_DATA_PRO, a_config.ARCHIVO_PROCESADO), df)


if __name__ == "__main__":
    """
    Verifica si el script se ejecuta directamente.
    Si es así, llama a la función main().
    """
    main()
