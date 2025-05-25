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
    - [2025-02-10]  v1.1: function implementation.
    - [2025-02-24]  v1.2: Added generalized functions for navigation and data extraction.
    - [2025-02-25]  v1.3: Tested escalability new ROUTES and FILE_CONFIGS.

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
import os
import pandas as pd
from playwright.async_api import async_playwright, TimeoutError, Locator
import logging
from .a_config import RouteConfig, LevelConfig

# =====================
# # Configuración básica del logging
# =====================

PATH_BASE = os.path.join(os.path.dirname(__file__))
PATH_DATA_RAW = os.path.join(PATH_BASE, "01_data/01_raw")
PATH_DATA_PRO = os.path.join(PATH_BASE, "01_data/02_processed")

LOG_DIR = os.path.join(PATH_BASE, "..", "05_logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "obtener_metadata.log")

logging.basicConfig(
    level=logging.INFO,  # Nivel de registro (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='[%(levelname)s] - %(message)s',  
    handlers=[
    logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'),  # Archivo en UTF-8
    logging.StreamHandler()  # También mostrar logs en la consola
    ]
)

# Selectores generales: año y frame principal
GLOBAL_SELECTORS = {
    "year_dropdown": "ctl00_CPH1_DrpYear", 
    "main_frame": "frame0"
    }


# =====================
# Funciones de Utilidad
# =====================
class ConsultaAmigable():
    def __init__(self, ruta: RouteConfig, years: list[int], timeout: int = 100, headless=False):
        self.headless = headless
        self.timeout = timeout
        self.URL_MENSUAL = "https://apps5.mineco.gob.pe/transparencia/mensual/"
        self.URL_ANUAL = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx?y={}&ap=ActProy"
        self.route_config = ruta
        self.years = years
        self.extracted_data = []
        self.headers = []
        self.context = {}
        self.click_number = 0
        self.level_index = 0
        self.playwright = None
        self.browser = None
        self.page = None

    async def initialize_driver(self):
        """
        Inicializa el driver de Playwright.
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless, slow_mo=self.timeout)
        context = await self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = await context.new_page()
        self.page.set_default_timeout(15_000)
        self.page.set_default_navigation_timeout(20_000)
        

    async def cerrar_navegador(self):
        """
        Cierra el navegador y libera los recursos.
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


    async def navigate_to_url(self, year: str | int,  mensual: bool = False):
        """
        Navega a la URL especificada utilizando el driver proporcionado.
        """
        if not mensual:
            await self.page.goto(self.URL_ANUAL.format(str(year)))
        else:
            await self.page.goto(self.URL_MENSUAL)


    def select_route(self)-> str:
        """
        Muestra las rutas disponibles y permite al usuario seleccionar una.
        """
        print("\n--- Rutas disponibles ---")
        rutas_disponibles = list(self.years)

        for i, ruta in enumerate(rutas_disponibles, start=1):
            print(f"{i}: {ruta}")

        while True:
            try:
                opcion = int(input("\nElige una ruta (número): "))
                if 1 <= opcion <= len(rutas_disponibles):
                    return rutas_disponibles[opcion - 1]
                else:
                    print("⚠️ Opción inválida, ingresa un número de la lista.")
            except ValueError:
                print("⚠️ Entrada inválida, ingresa un número.")


    async def click_on_element(self, element):
        """
        Hace clic en un elemento de la página utilizando su ID.
        """
        iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
        if isinstance(element, str):
            await iframe.locator(element).click()
        elif isinstance(element, Locator):
            await element.click()
        self.click_number += 1


    async def _extract_table_data(self):
        """
        Extrae los datos de una tabla con clase 'Data' y retorna una lista de listas
        """
        # Lista para almacenar los datos extraídos
        datos_tabla = []

        # Seleccionar todas las filas de la tabla con clase 'Data'
        iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
        # filas = await iframe.locator("table.Data").locator("tr").all()
        filas = await iframe.locator("table.Data").all()

        # Extraer los datos de cada fila
        for i, fila in enumerate(filas):
            datos = await fila.locator("td").all_inner_texts()
            datos = [dato.replace(",", "").strip() for dato in datos]

            # Agregar datos solo si la fila tiene contenido
            if datos:
                datos_tabla.append(datos)
            logging.info(f"Se extrayeron datos de {int(len(datos) / 10)} filas.")

        return datos_tabla


    async def get_final_headers(self, tabla_id)-> list:
        """
        Extrae encabezados manteniendo el orden de la tabla,
        omitiendo la primera columna vacía (botón) y obteniendo
        los niveles inferiores cuando hay agrupación.
        """
        if not self.headers:
            try:
                iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
                tabla = iframe.locator(tabla_id)
                primer_encabezado = iframe.locator("tr[id='ctl00_CPH1_Mt0_Row0']")
                segundo_encabezado = iframe.locator("tr[id='ctl00_CPH1_Mt0_Row1']")
                tds = await primer_encabezado.locator("td").all()

                idx_inferior = 0  # Índice para recorrer fila_inferior cuando haya agrupación

                for i, td in enumerate(tds):
                    # Omitir la primera celda si está vacía (botón)
                    if i == 0:
                        continue

                    colspan = await td.get_attribute("colspan")

                    if colspan:  # Si hay agrupación, tomar encabezados del nivel inferior
                        for _ in range(int(colspan)):
                            encabezado = await segundo_encabezado.locator("td").nth(idx_inferior).inner_text()
                            self.headers.append(encabezado.strip())
                            idx_inferior += 1
                    else:  # Si no hay agrupación, tomar el texto directamente
                        encabezado = await td.inner_text()
                        self.headers.append(encabezado.strip())

                logging.info(f"Encabezados extraídos: {self.headers}")

            except Exception as e:
                print(f"Error al obtener encabezados: {e}")
            
            

    async def navigate_levels(self, custom_row: str = "")-> None:
        """
        Navega a través de los niveles definidos en la configuración.

        :param route_config: Configuración de la ruta (ROUTES en a_config.py).
        :param current_level: Nivel actual en la navegación.
        :param self.table_headers: Lista donde se almacenarán los encabezados solo una vez.
        :param context: Diccionario para almacenar la jerarquía para iterar.
        :return: Lista con los datos extraídos.
        """
        level = self.route_config.levels[self.level_index]
                    
        if level.button:
            if level.row:
                await self.navigate_level_simple(level.row, level.button)
            elif custom_row:
                await self.navigate_level_simple(custom_row, level.button)
            elif level.table_rows:
                await self.iterate_over_levels(level.button)


    async def assert_extraction(self):
        level = self.route_config.levels[self.level_index]
        iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
        await iframe.wait_for_selector("table.Data")
        if level.table:
            #await self._extract_table_data()
            if not self.table_headers:
                await self.get_final_headers(level.table)
                #logging.info(f"📊 Extrayendo datos de la tabla: {self.route_config.levels[self.level_index].name}")
                table_data = await self._extract_table_data()

                # Construir cada fila incluyendo los niveles donde hubo iteración
                for row in table_data:
                    formatted_row = [self.context[level] for level in self.context.keys()] + row
                    self.extracted_data.append(formatted_row)
                
    
    async def navigate_level_simple(self, row: str, button: str)-> None:
        await self.click_on_element(row)
        await self.click_on_element(button)
        self.level_index += 1
    
    
    async def iterate_over_levels(self, button: str)-> list:
        """
        Navega a través de cada fila en el nivel actual, guardando el contexto,
        extrayendo datos y manejando la navegación hacia adelante y atrás para
        mantener la consistencia durante la exploración jerárquica.
        """
        level = self.route_config.levels[self.level_index]
        iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
        await iframe.wait_for_selector("table.Data")
        filas = await iframe.locator("table.Data > tbody > tr").all()
        logging.info(f"📋 Se encontraron {len(filas)} filas para iterar en {level.name}")

        for i in range(len(filas)):
            fila = filas[i]
            element_name = await fila.locator("td").nth(1).inner_text()
            self.context[level.name] = element_name  # Guardar el nombre en el contexto
            logging.info(f"➡️ Entrando en: {element_name}")
            
            await self.navigate_level_simple(fila, button)
            await self.assert_extraction()
            levels_left = len(self.route_config.levels) - (self.level_index + 1)
            if levels_left > 0:
                for _ in range(levels_left):
                    await self.navigate_levels()
                for _ in range(levels_left):
                    await iframe.wait_for_selector("table.Data")
                    try:
                        await self.page.go_back(timeout=100)
                    except TimeoutError:
                        pass
                    
                    self.level_index -= 1
                    self.click_number += 1
            else:
                try:
                    await self.page.go_back(timeout=100)
                except TimeoutError:
                        pass
                self.level_index -= 1
                self.click_number += 1   


    async def extract_data_by_year(self):
        """
        Extrae los datos de la página para un año específico basado en la ruta configurada.

        :param year: Año para el cual se extraen los datos.
        :param route_name: Nombre de la ruta en ROUTES.
        :param self.table_headers: Lista compartida para almacenar los encabezados una sola vez.
        :return: Datos extraídos.
        """
        for year in self.years:
            logging.info(f"🗓️ Iniciando extracción para el año {year}, ruta: {self.route_config.name}")
            datos_anio = []
            await self.navigate_to_url(year)
            
            iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
            await iframe.wait_for_selector("table.Data")

            # Navegar a través de los niveles desde el primer nivel
            for level in self.route_config.levels:
                await self.navigate_levels()

            # Agregar metadatos: Año...
            for fila in self.extracted_data:
                fila_con_meta = [year] + fila
                datos_anio.append(fila_con_meta)
            self.level_index = 0


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


    # TODO: Modularizar años
    async def main(self):
        """
        Función principal para iniciar el proceso de scraping con selección de ruta.
        Guarda los datos recolectados incluso si ocurre un error.
        """
        #ruta_seleccionada = ConsultaAmigable.select_route()
        # ruta_seleccionada = "MUNICIPALIDADES"
        # session = ConsultaAmigable(ruta_seleccionada, timeout=100, headless=False)
        await self.initialize_driver()
        todos_los_datos = []
        self.table_headers = []
        

        try:
            #print(f"\n🔍 Iniciando scraping para la ruta: {ruta_seleccionada}")

            # Obtener configuración de la ruta seleccionada
            encabezados_base = self.route_config.file.get("ENCABEZADOS_BASE", [])
            # archivo_scraping = file_conf.get("ARCHIVO_SCRAPING", [])

            # Iterar sobre los años y extraer datos
            datos_anio = await self.extract_data_by_year()
            todos_los_datos.extend(datos_anio)

        # except Exception as e:
        #     print(f"Se produjo un error inesperado: {e}")
        #     logging.info("💾 Guardando datos parciales antes de cerrar...")

        finally:
            # Guardar los datos finales si se obtuvieron datos completos
            if todos_los_datos:
                logging.info("💾 Guardando datos...")
                encabezados_completos = encabezados_base + self.table_headers
                self.save_data(
                    os.path.join(PATH_DATA_RAW, self.route_config.file["FILE_NAME"]),
                    todos_los_datos,
                    encabezados_completos,
                )

            await self.cerrar_navegador()
            logging.info("✅ Proceso finalizado, driver cerrado.")
            logging.info(f"Se dieron {self.click_number} clicks")

