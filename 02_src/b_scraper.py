"""
=====================
Project     : WS CAMEF
File        : b_scraper.py
Description : Web data extraction using Selenium.
Date        : 2025-02-07
Version     : 1.0
Author      : Alex Evanan

Revision History:
    - [2025-02-07]  v1.0: Initial version.
    - [2025-02-010] v1.1: function implementation.

Notes:
    - Developed with Python 3.11.9.
    - Compatible with JupyterLab, Notebook, and Google Colab.
    - Dependencies are listed in 'requirements.txt'.

Usage:
    Run this script from the terminal or interactive environment:
        $ python 02_src/b_scraper.py
=====================
"""

# =====================
# Importación de librerías
# =====================
import sys
import os

import time
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select

# Configuración desde 02_src/0_config.py
sys.path.append(os.path.join(os.getcwd(), "02_src"))
import a_config


# =====================
# Funciones de Utilidad
# =====================


def initialize_driver():
    """
    Inicializa el driver de Selenium.
    """
    try:
        # Configurar el servicio del WebDriver
        service = Service(executable_path=a_config.PATH_DRIVER)
        options = webdriver.ChromeOptions()

        # Opciones adicionales para estabilidad
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option(
            "excludeSwitches", ["enable-logging"]
        )  # Oculta notificaciones

        # Inicializar el driver
        driver = webdriver.Chrome(service=service, options=options)

        # Log para confirmar que se inició correctamente
        print("Driver iniciado.")

        return driver  # Devuelve la instancia del driver

    except Exception as e:
        print(f"Error al iniciar el driver de Selenium: {e}")
        raise


def switch_to_frame(driver, nombre_frame, tiempo=10):
    """
    Cambia al frame especificado y verifica que el <body> esté presente
    """
    try:
        # primero cambiar contenido por defecto
        driver.switch_to.default_content()

        # Camviar de frame
        WebDriverWait(driver, tiempo).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, nombre_frame))
        )
        print(f"Cambiado a '{nombre_frame}'.")

        # Verificar que el <body> del frame esté presente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Body cargado y verificado.")

    except Exception as e:
        print(f"Error: No se pudo cargar el <body> del'{nombre_frame}'. {e}")


def navigate_to_url(driver, url):
    """
    Navega a la URL especificada utilizando el driver proporcionado.
    """
    try:
        driver.get(url)
        print(f"Navegando a: {url}")

        # cambio de frame
        switch_to_frame(driver, "frame0")

    except Exception as e:
        print(f"Error al navegar a {url}: {e}")
        raise


def click_on_element(driver, element_id):
    """
    Hace clic en un elemento de la página utilizando su ID.
    """
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        element.click()
    except StaleElementReferenceException:
        click_on_element(driver, element_id)


def select_dropdown_option(driver, element_id, option_text):
    """
    Selecciona una opción de un elemento <select> utilizando el texto de la opción
    """
    try:
        # Esperar a que el elemento <select> sea clickeable
        select_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )

        # Crear instancia de Select
        select = Select(select_element)
        select.select_by_value(str(option_text))

    except StaleElementReferenceException:
        select_dropdown_option(driver, element_id, option_text)


def extract_table_data(driver):
    """
    Extrae los datos de una tabla con clase 'Data' y retorna una lista de listas
    """
    # Lista para almacenar los datos extraídos
    datos_tabla = []

    # Seleccionar todas las filas de la tabla con clase 'Data'
    filas = driver.find_elements(By.CSS_SELECTOR, "table.Data tr[id^='tr']")
    print(f"Se encontraron {len(filas)} filas.")

    # Extraer los datos de cada fila
    for i, fila in enumerate(filas):
        # Extraer desde la segunda celda para omitir el botón (primer <td>)
        datos = [td.text.strip() for td in fila.find_elements(By.TAG_NAME, "td")[1:]]

        print(f"Fila {i + 1}: {datos}")

        # Agregar datos solo si la fila tiene contenido
        if datos:
            datos_tabla.append(datos)

    return datos_tabla


def get_final_headers(driver, tabla_id):
    """
    Extrae encabezados manteniendo el orden de la tabla,
    omitiendo la primera columna vacía (botón) y obteniendo
    los niveles inferiores cuando hay agrupación.
    """
    try:
        tabla = driver.find_element(By.ID, tabla_id)
        fila_superior = tabla.find_elements(By.XPATH, ".//tr[1]/td | .//tr[1]/th")
        fila_inferior = tabla.find_elements(By.XPATH, ".//tr[2]/td | .//tr[2]/th")

        encabezados = []
        idx_inferior = 0  # Índice para recorrer fila_inferior cuando haya agrupación

        for i, celda in enumerate(fila_superior):
            # Omitir la primera celda si está vacía (botón)
            if i == 0 and not celda.text.strip():
                continue

            colspan = celda.get_attribute("colspan")

            if colspan:  # Si hay agrupación, tomar encabezados del nivel inferior
                for _ in range(int(colspan)):
                    encabezados.append(fila_inferior[idx_inferior].text.strip())
                    idx_inferior += 1
            else:  # Si no hay agrupación, tomar el texto directamente
                encabezados.append(celda.text.strip())

        print(f"Encabezados extraídos: {encabezados}")
        return encabezados

    except Exception as e:
        print(f"Error al obtener encabezados: {e}")
        return []


def extract_data_by_year(driver, year):
    """
    Extrae los datos de la página para un año/s específicado/s.
    Itera sobre departamentos, provincias y municipalidades.
    """
    datos_anio = []
    encabezados_extraidos = []  # Para almacenar los encabezados

    select_dropdown_option(driver, "ctl00_CPH1_DrpYear", year)
    switch_to_frame(driver, "frame0")
    click_on_element(driver, "ctl00_CPH1_BtnTipoGobierno")
    switch_to_frame(driver, "frame0")
    print("Nivel de Gob detalle")
    click_on_element(driver, "tr1")
    switch_to_frame(driver, "frame0")
    print("Gob. locales")
    click_on_element(driver, "ctl00_CPH1_BtnSubTipoGobierno")
    switch_to_frame(driver, "frame0")
    print("Gob. locales detalle")
    click_on_element(driver, "ctl00_CPH1_RptData_ctl01_TD0")
    switch_to_frame(driver, "frame0")
    print("Municipalidades.")
    click_on_element(driver, "ctl00_CPH1_BtnDepartamento")
    switch_to_frame(driver, "frame0")
    print("Dept. detalle")

    departamentos = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'tr')]")

    for i, depto in enumerate(departamentos):
        departamentos = driver.find_elements(
            By.XPATH, "//tr[starts-with(@id, 'tr')]"
        )  # Refrescar la lista
        depto = departamentos[i]  # Usar el elemento actualizado
        depto_nombre = depto.find_element(By.XPATH, "./td[2]").text.strip()

        click_on_element(driver, f"tr{i}")
        switch_to_frame(driver, "frame0")
        click_on_element(driver, "ctl00_CPH1_BtnProvincia")
        switch_to_frame(driver, "frame0")
        print(f"{depto_nombre} seleccionado")

        provincias = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'tr')]")

        for j, prov in enumerate(provincias):
            provincias = driver.find_elements(
                By.XPATH, "//tr[starts-with(@id, 'tr')]"
            )  # Refrescar la lista
            prov = provincias[j]  # Usar el elemento actualizado
            prov_nombre = prov.find_element(By.XPATH, "./td[2]").text.strip()

            click_on_element(driver, f"tr{j}")
            switch_to_frame(driver, "frame0")
            click_on_element(driver, "ctl00_CPH1_BtnMunicipalidad")
            switch_to_frame(driver, "frame0")
            print(f"{prov_nombre} seleccionado")

            # Obtener los encabezados solo la primera vez
            if not encabezados_extraidos:
                encabezados_extraidos = get_final_headers(driver, "ctl00_CPH1_Mt0")

            # Extraer los datos de la tabla de municipalidades
            datos_municipalidad = extract_table_data(driver)

            # Agregar metadatos: Año, Departamento, Provincia
            for fila in datos_municipalidad:
                fila_con_meta = [year, depto_nombre, prov_nombre] + fila
                datos_anio.append(fila_con_meta)

            # Volver a la lista de provincias
            driver.back()
            switch_to_frame(driver, "frame0")

        # Volver a la lista de departamentos
        driver.back()
        switch_to_frame(driver, "frame0")

    # Retornar los datos y los encabezados extraídos
    return datos_anio, encabezados_extraidos


def save_data(nombre_archivo, datos, encabezados):
    """
    Guarda los datos extraídos en un archivo Excel.
    """
    try:
        df = pd.DataFrame(datos, columns=encabezados)
        df.to_excel(nombre_archivo, index=False)
        print(f"Datos guardados correctamente en {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar en Excel: {e}")


def main():
    """
    Función principal para iniciar el proceso de scraping.
    """
    driver = initialize_driver()
    todos_los_datos = []
    encabezados_municipalidad = []

    try:
        navigate_to_url(driver, a_config.URL)

        for year in a_config.YEARS:
            print(f"Extrayendo datos para el año {year}...")
            datos_anio, encabezados_tabla = extract_data_by_year(driver, year)

            # Guardar los encabezados solo si aún no se han extraído
            if not encabezados_municipalidad and encabezados_tabla:
                encabezados_municipalidad = encabezados_tabla

            todos_los_datos.extend(datos_anio)

    except Exception as e:
        print(f"Se produjo un error en el proceso: {e}")
        # Guardar los datos recolectados hasta el momento del error
        if todos_los_datos:
            print("Guardando los datos recolectados hasta el momento...")
            encabezados_completos = (
                a_config.ENCABEZADOS_BASE + encabezados_municipalidad
            )
            save_data(
                os.path.join(a_config.PATH_DATA_RAW, a_config.ARCHIVO_SALIDA_PARCIAL),
                todos_los_datos,
                encabezados_completos,
            )
        else:
            print("No hay datos para guardar.")

    finally:
        # Guardar los datos recolectados en un archivo Excel
        if todos_los_datos:
            encabezados_completos = (
                a_config.ENCABEZADOS_BASE + encabezados_municipalidad
            )
            save_data(
                os.path.join(a_config.PATH_DATA_RAW, a_config.ARCHIVO_SALIDA),
                todos_los_datos,
                encabezados_completos,
            )
        driver.quit()
        print("Driver cerrado correctamente.")


if __name__ == "__main__":
    """
    Verifica si el script se ejecuta directamente.
    Si es así, llama a la función main().
    """
    main()
