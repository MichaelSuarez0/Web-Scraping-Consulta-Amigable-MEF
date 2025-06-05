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
import logging
from ubigeos_peru import Ubigeo as ubg
from .a_config import PATH_DATA_PRO, PATH_DATA_RAW

logging.getLogger('consulta_amigable')

# =====================
# Importación de data
# =====================

# TODO: Convertir a clase tmb, un argumento para leer un excel y otro un df (integrar con consultaamigable)

class Cleaner:
    encabezados = [
        ("Departamento", ["UBI_DPTO", "Departamento"], ":"),
        ("Provincia", ["UBI_PROV", "Provincia"], ":"),
        ("Municipalidad", ["UBI_DIST", "COD_SIAF", "Municipalidad"], "-|:"),
        ("Sector", ["COD_SEC", "Sector"], ":"),
        ("Pliego", ["COD_PLI", "Pliego"], ":"),
        ("Unidad Ejecutora", ["UE", "SEC_EJEC", "Unidad Ejecutora"], "-|:"),
    ]

    def __init__(self, input: pd.DataFrame | str):
        self.input = input
        self.df = None
        self._obtain_df()

    def _obtain_df(self):
        if isinstance(self.input, pd.DataFrame):
            self.df = self.input
        elif isinstance(self.input, str):
            self.df = self.read_files()
        else:
            raise TypeError("Not a valid input type, should be either DataFrame or path (str)")
        
    def read_files(self):
        """
        Lee un archivo Excel (.xlsx, .xls) o CSV (.csv) y devuelve un DataFrame.
        """
        try:
            if self.input.endswith((".xlsx", ".xls")):
                return pd.read_excel(self.input)
            elif self.input.endswith(".csv"):
                return pd.read_csv(self.input)
            else:
                raise ValueError("Formato no soportado. Usa .xlsx, .xls o .csv.")
        except Exception as e:
            print(f"Error al leer el archivo '{self.input}': {e}")
            return None


    def split_column(self, source_col: str, new_cols: list[str], delimiter: str, max_splits=None):
        """
        Divide una columna en dos nuevas columnas eliminando la original.
        """
        if len(new_cols) < 2:
            raise ValueError(
                "Debes proporcionar al menos dos nombres para las nuevas columnas."
            )

        if source_col not in self.df.columns:
            raise ValueError(f"La columna '{source_col}' no existe en el DataFrame.")

        if max_splits is None:
            max_splits = len(new_cols) - 1

        # Dividir la columna y asignar a las nuevas columnas
        self.df[new_cols] = (
            self.df.pop(source_col)
            .str.split(delimiter, n=max_splits, expand=True)
            .apply(lambda x: x.str.strip())
            .astype(str)
        )

        return self.df

    @staticmethod
    def convert_to_numeric(df: pd.DataFrame):
        """
        Limpia múltiples columnas numéricas eliminando comas y convierte a tipo numérico.
        """
        df = df.apply(lambda col: pd.to_numeric(col.astype(str).str.replace(",", ""), errors="coerce"))
        return df
    
    def normalize_dep_column(self):
        for col in self.df.columns:
            if col.lower() in "departamento" or "departamento" in col.lower():
                self.df[col] = self.df[col].apply(lambda x: x.split(" ")[-1])
                self.df[col] = self.df[col].apply(lambda x: ubg.validate_departamento(x, on_error="capitalize"))
                self.df = self.df.rename(columns={col: "Departamento"})
            elif col.lower() in "provincia" or "provincia" in col.lower():
                self.df[col] = self.df[col].apply(lambda x: x.split(" ")[-1])
                self.df[col] = self.df[col].apply(lambda x: ubg.validate_ubicacion(x, on_error="capitalize"))
                self.df = self.df.rename(columns={col: "Provincia"})
    

    def save_data(self, nombre_archivo: str, datos):
        """
        Guarda los datos extraídos en un archivo Excel.
        """
        try:
            df = pd.DataFrame(datos)
            df.to_excel(nombre_archivo, index=False)
            print(f"Datos guardados correctamente en {nombre_archivo}")
        except Exception as e:
            print(f"Error al guardar en Excel: {e}")


    def main(self):
        """
        Función principal para procesar los archivos extraídos.
        - Lee los archivos extraídos si es necesario.
        - Convierte las últimas 8 columnas a numéricas.
        - Guarda los datos procesados en un nuevo archivo.
        """
        
        # for file_key, config_file in FILE_CONFIGS.items():
        #     logging.info(f"🔹 Procesando data: {file_key}")

        # Convertir las últimas 8 columnas a numéricas (si existen)
        self.df.iloc[-8:] = self.convert_to_numeric(self.df, self.df.columns[-8:])
        self.normalize_dep_column()

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

        

        # Guardar archivo procesado
        archivo_salida = os.path.join(
            PATH_DATA_PRO,
            f"PROCESADO_{config_file.get('ARCHIVO_SCRAPING', '')}",
        )
        save_data(archivo_salida, df)


if __name__ == "__main__":
    """
    Verifica si el script se ejecuta directamente.
    Si es así, llama a la función main().
    """
    main()
