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
    - [2025-02-25]  v1.1: Add support for multiple files.

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
import os
import pandas as pd
import a_config

# =====================
# Importación de data
# =====================

# TODO: Convertir a clase tmb

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
    """
    Función principal para procesar los archivos extraídos.
    - Lee los archivos extraídos.
    - Divide columnas según la configuración.
    - Convierte las últimas 8 columnas a numéricas.
    - Guarda los datos procesados en un nuevo archivo.
    """
    for file_key, config_file in a_config.FILE_CONFIGS.items():
        print(f"🔹 Procesando data: {file_key}")

        archivo_entrada = os.path.join(
            a_config.PATH_DATA_RAW, config_file.get("ARCHIVO_SCRAPING", "")
        )
        if not os.path.exists(archivo_entrada):
            print(f"Archivo no encontrado: {archivo_entrada}. Se omite.")
            continue

        # Leer archivo
        df = read_files(archivo_entrada)

        # Obtener configuración de limpieza
        config_clean = a_config.CLEANING_CONFIGS.get(file_key, {})
        encabezados = config_clean.get("ENCABEZADOS_PROCESADOS", [])

        # Identificar la primera columna original
        primera_columna = [df.columns[0]] if not df.empty else []

        # Aplicar split de columnas y mantener el orden
        columnas_nuevas = []
        for source_col, new_cols, delimiter in encabezados:
            if source_col in df.columns:
                df = split_column(df, source_col, new_cols, delimiter)
                columnas_nuevas.extend(new_cols)

        # Obtener columnas restantes (las que no fueron afectadas por el split)
        columnas_restantes = [
            col for col in df.columns if col not in primera_columna + columnas_nuevas
        ]

        # Reordenar: Primera columna original → columnas del split → otras columnas
        df = df[primera_columna + columnas_nuevas + columnas_restantes]

        # Convertir las últimas 8 columnas a numéricas (si existen)
        df = numeric_columns(df, df.columns[-8:])

        # Guardar archivo procesado
        archivo_salida = os.path.join(
            a_config.PATH_DATA_PRO,
            f"PROCESADO_{config_file.get('ARCHIVO_SCRAPING', '')}",
        )
        save_data(archivo_salida, df)


if __name__ == "__main__":
    """
    Verifica si el script se ejecuta directamente.
    Si es así, llama a la función main().
    """
    main()
