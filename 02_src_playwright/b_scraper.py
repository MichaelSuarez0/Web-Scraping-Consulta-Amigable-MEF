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
import asyncio

from playwright.async_api import async_playwright, TimeoutError, Locator
import logging
import a_config

# =====================
# # Configuración básica del logging
# =====================

PATH_BASE = os.path.join(os.path.dirname(__file__))
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

# Años de consulta
YEARS = list(range(2024, 2026))  # no incluye el límite superior


# Selectores generales: año y frame principal
GLOBAL_SELECTORS = {
    "year_dropdown": "ctl00_CPH1_DrpYear", 
    "main_frame": "frame0"
    }


# =====================
# Funciones de Utilidad
# =====================
class ConsultaAmigable():
    def __init__(self, ruta: str, timeout: int = 100, headless=False):
        self.headless = headless
        self.timeout = timeout
        self.URL_MENSUAL = "https://apps5.mineco.gob.pe/transparencia/mensual/"
        self.URL_ANUAL = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx?y={}&ap=ActProy"
        self.playwright = None
        self.browser = None
        self.page = None
        self.datos = []
        self.headers = []
        self.route_config = a_config.ROUTES[ruta]
        self.iframe = None

    async def initialize_driver(self):
        """
        Inicializa el driver de Playwright.
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless, slow_mo=self.timeout)
        context = await self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = await context.new_page()
        self.page.set_default_timeout(10_000)

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

    @staticmethod
    def select_route()-> str:
        """
        Muestra las rutas disponibles y permite al usuario seleccionar una.
        """
        print("\n--- Rutas disponibles ---")
        rutas_disponibles = list(a_config.ROUTES.keys())

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


    async def click_on_element(self, element_id):
        """
        Hace clic en un elemento de la página utilizando su ID.
        """
        if self.iframe:
            try:
                await self.iframe.locator(element_id).click()
            except Exception:
                logging.error("No se pudo presionar en el botón a partir de iframe guardado")
                pass
        else:
            try:
                iframe = self.page.frame(a_config.GLOBAL_SELECTORS["main_frame"])
                if iframe is not None:
                    self.iframe = iframe
                    await iframe.locator(element_id).click()
                else:
                    iframe = self.page.frame(name="frame0") 
                    await self.iframe.locator(element_id).click()
            except TimeoutError:
                await self.page.locator(element_id).click()
                logging.info("No se encontró el botón")
            except Exception:
                await self.page.locator(element_id).click()

    # async def select_dropdown_option(self, element_id, option_text):
    #     """
    #     Selecciona una opción de un elemento <select> utilizando el texto de la opción
    #     """
    #     try:
    #         await self.page.wait_for_timeout(3000)
    #         iframe = self.page.frame(a_config.GLOBAL_SELECTORS["main_frame"])
    #         if iframe is not None:
    #             self.iframe = iframe
    #             await self.iframe.locator(f'select[id={element_id}]').select_option(str(option_text))
    #         else:
    #             iframe = self.page.frame(name="frame0") 
    #             await iframe.locator(f'select[id={element_id}]').select_option(str(option_text))
    #     except TimeoutError:
    #         logging.error("No funcionó select dropdown")


    async def extract_table_data(self):
        """
        Extrae los datos de una tabla con clase 'Data' y retorna una lista de listas
        """
        # Lista para almacenar los datos extraídos
        datos_tabla = []

        # Seleccionar todas las filas de la tabla con clase 'Data'
        filas = await self.page.locator("table['class=Data']").locator("tr").all()
        logging.info(f"Se encontraron {len(filas)} filas.")

        # Extraer los datos de cada fila
        for i, fila in enumerate(filas):
            datos = await fila.locator("td").all_inner_texts()
            datos = [dato.replace(",", "").strip() for dato in datos]
        
            print(f"Fila {i + 1}: {datos}")

            # Agregar datos solo si la fila tiene contenido
            if datos:
                datos_tabla.append(datos)

        return datos_tabla


    async def get_final_headers(self, tabla_id)-> list:
        """
        Extrae encabezados manteniendo el orden de la tabla,
        omitiendo la primera columna vacía (botón) y obteniendo
        los niveles inferiores cuando hay agrupación.
        """
        try:
            tabla = self.page.locator(tabla_id)
            primer_encabezado = self.page.locator("tr[id='ctl00_CPH1_Mt0_Row0']")
            segundo_encabezado = self.page.locator("tr[id='ctl00_CPH1_Mt0_Row1']")
            tds = primer_encabezado.locator("td").all()

            encabezados = []
            idx_inferior = 0  # Índice para recorrer fila_inferior cuando haya agrupación

            for i, td in enumerate(tds):
                # Omitir la primera celda si está vacía (botón)
                td: Locator
                if i == 0:
                    continue

                colspan = td.get_attribute("colspan")

                if colspan:  # Si hay agrupación, tomar encabezados del nivel inferior
                    for _ in range(int(colspan)):
                        encabezado = await segundo_encabezado[idx_inferior].inner_text()
                        encabezados.append(encabezado.strip())
                        idx_inferior += 1
                else:  # Si no hay agrupación, tomar el texto directamente
                    encabezado = await td.inner_text()
                    encabezados.append(encabezado.strip())

            logging.info(f"Encabezados extraídos: {encabezados}")
            return encabezados

        except Exception as e:
            print(f"Error al obtener encabezados: {e}")
            return []


    async def navigate_levels(self, current_level, table_headers, context=None)-> list:
        """
        Navega a través de los niveles definidos en la configuración.

        :param route_config: Configuración de la ruta (ROUTES en a_config.py).
        :param current_level: Nivel actual en la navegación.
        :param table_headers: Lista donde se almacenarán los encabezados solo una vez.
        :param context: Diccionario para almacenar la jerarquía para iterar.
        :return: Lista con los datos extraídos.
        """

        extracted_data = []  # Lista para almacenar los datos extraídos en este nivel

        if context is None:
            context = {}

        logging.info(f"\n📌 Entrando a nivel: {current_level}")

        level_config = self.route_config["levels"][current_level]
        button = f"button[{level_config.get('button')}]"
        td = f"td[{level_config.get("td")}]"
        list_xpath = level_config.get("list_xpath")
        name_xpath = level_config.get("name_xpath")
        next_level = level_config.get("next_level")
        table_id = level_config.get("table_id")

        # Hacer clic en el botón del nivel si existe
        if button:
            logging.info(f"🔘 Haciendo clic en botón: {button}")
            #button = self.page.locator("input[id='ctl00_CPH1_BtnTipoGobierno']")
            await self.click_on_element(button)

        # Si el nivel tiene una lista definida, iterar sobre los elementos
        if list_xpath:
            elements = await self.page.locator(list_xpath).all()
            logging.info(f"📋 Se encontraron {len(elements)} elementos en {current_level}")

            for i in range(len(elements)):
                element = elements[i]
                element_name = element.inner_text()
                context[current_level] = element_name  # Guardar el nombre en el contexto
                logging.info(f"➡️ Entrando en: {element_name}")

                # Hacer clic en el elemento actual
                await self.page.locator(f"tr{i}").click()

                # Navegar al siguiente nivel (si existe)
                if next_level:
                    print(f"🔽 Navegando al siguiente nivel: {next_level}")
                    extracted_data.extend(
                        await self.navigate_levels(
                            next_level, table_headers, context
                        )
                    )

                # Regresar al nivel anterior
                logging.info(f"⬅️ Regresando a {current_level}")
                await self.page.go_back()
                await self.page.wait_for_load_state('networkidle')

        else:
            # Si no hay lista, navegar directamente al siguiente nivel
            if next_level:
                print(f"⏭️ Saltando a siguiente nivel: {next_level}")
                extracted_data.extend(
                    await self.navigate_levels(
                        next_level, table_headers, context
                    )
                )
            else:
                if table_id:
                    if not table_headers:
                        logging.info("📌 Extrayendo encabezados de la tabla...")
                        table_headers.extend(self.get_final_headers(table_id))

                    logging.info(f"📊 Extrayendo datos de la tabla: {table_id}")
                    table_data = self.extract_table_data()

                    # Construir cada fila incluyendo los niveles donde hubo iteración
                    for row in table_data:
                        formatted_row = [context[level] for level in context.keys()] + row
                        extracted_data.append(formatted_row)

        logging.info(f"✅ Saliendo de nivel: {current_level}")
        return extracted_data


    async def extract_data_by_year(self, year, route_name, table_headers):
        """
        Extrae los datos de la página para un año específico basado en la ruta configurada.

        :param year: Año para el cual se extraen los datos.
        :param route_name: Nombre de la ruta en ROUTES.
        :param table_headers: Lista compartida para almacenar los encabezados una sola vez.
        :return: Datos extraídos.
        """
        print(f"\n🗓️ Iniciando extracción para el año {year}, ruta: {route_name}")
        datos_anio = []
    
        # Obtener la configuración de la ruta
        route_config = a_config.ROUTES[route_name]

        # Determinar el primer nivel dinámicamente
        first_level = min(
            route_config["levels"].keys(), key=lambda lvl: int(lvl.split("_")[1])
        )

        # Navegar a través de los niveles desde el primer nivel
        datos_extraidos = await self.navigate_levels(first_level, table_headers)

        # Agregar metadatos: Año...
        for fila in datos_extraidos:
            fila_con_meta = [year] + fila
            datos_anio.append(fila_con_meta)

        print("✅ Extracción completada")
        return datos_anio


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
async def main():
    """
    Función principal para iniciar el proceso de scraping con selección de ruta.
    Guarda los datos recolectados incluso si ocurre un error.
    """
    #ruta_seleccionada = ConsultaAmigable.select_route()
    ruta_seleccionada = "MUNICIPALIDADES"
    session = ConsultaAmigable(ruta_seleccionada, timeout=100, headless=False)
    await session.initialize_driver()
    todos_los_datos = []
    table_headers = []

    for year in a_config.YEARS:
        try:
            await session.navigate_to_url(year)
            #await session.navigate_levels()

            print(f"\n🔍 Iniciando scraping para la ruta: {ruta_seleccionada}")

            # Obtener configuración de la ruta seleccionada
            file_conf = a_config.FILE_CONFIGS.get(ruta_seleccionada, {})
            encabezados_base = file_conf.get("ENCABEZADOS_BASE", [])
            archivo_scraping = file_conf.get("ARCHIVO_SCRAPING", [])

            # Iterar sobre los años y extraer datos
            for year in a_config.YEARS:
                datos_anio = await session.extract_data_by_year(
                    year, ruta_seleccionada, table_headers
                )

                todos_los_datos.extend(datos_anio)

        except Exception as e:
            print(f"Se produjo un error inesperado: {e}")

            # Guardar datos parciales si hubo un error
            if todos_los_datos:
                print("💾 Guardando datos parciales antes de cerrar...")
                encabezados_completos = encabezados_base + table_headers
                session.save_data(
                    os.path.join(a_config.PATH_DATA_RAW, "parcial_" + archivo_scraping),
                    todos_los_datos,
                    encabezados_completos,
                )

        finally:
            # Guardar los datos finales si se obtuvieron datos completos
            if todos_los_datos:
                logging.info("💾 Guardando datos finales...")
                encabezados_completos = encabezados_base + table_headers
                session.save_data(
                    os.path.join(a_config.PATH_DATA_RAW, archivo_scraping),
                    todos_los_datos,
                    encabezados_completos,
                )

            await session.cerrar_navegador()
            print("✅ Proceso finalizado, driver cerrado.")


if __name__ == "__main__":
    asyncio.run(main())