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
import pandas as pd
from playwright.async_api import async_playwright, TimeoutError, Locator
from .a_config import RouteConfig
from .c_cleaner import Cleaner

# =====================
# # Configuraciones básicas
# =====================
import logging
from pathlib import Path

logger = logging.getLogger('consulta_amigable')
logger.setLevel(logging.INFO)

PATH_BASE = Path(__file__).parent
LOG_PATH = PATH_BASE.parent / "logs" / "consulta_amigable.log"

# Formateadores
file_formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler = logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8')
file_handler.setFormatter(file_formatter)

console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

# Evitar duplicados
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Selectores generales: año y frame principal
GLOBAL_SELECTORS = {
    "year_dropdown": "ctl00_CPH1_DrpYear", 
    "main_frame": "frame0"
    }


# =====================
# Funciones de Utilidad
# =====================
class ConsultaAmigable():
    URL_MENSUAL = "https://apps5.mineco.gob.pe/transparencia/mensual/"
    URL_ANUAL = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx?y={}&ap=ActProy"

    def __init__(self, ruta: RouteConfig, years: list[int] | int, output_path: str, timeout: int = 100, headless=False):
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.page = None
        self.cleaner = None
        self.logger = logger

        self.route_config = ruta
        self.years = years if isinstance(years, list) else [years]
        self.year = 0
        self.output_path = output_path

        self.extracted_data = []
        self.headers = []
        self.context = {}
        self.click_number = 0
        self.level_index = 0

    async def _initialize_driver(self):
        """
        Inicializa el driver de Playwright.
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless, slow_mo=self.timeout)
        context = await self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = await context.new_page()
        self.page.set_default_timeout(15_000)
        self.page.set_default_navigation_timeout(20_000)
        

    async def _cerrar_navegador(self):
        """
        Cierra el navegador y libera los recursos.
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


    async def _navigate_to_url(self, year: str | int,  mensual: bool = False):
        """
        Navega a la URL especificada utilizando el driver proporcionado.
        """
        if not mensual:
            await self.page.goto(self.URL_ANUAL.format(str(year)))
        else:
            await self.page.goto(self.URL_MENSUAL)


    async def _click_on_element(self, element_text: str | Locator, row: True):
        """
        Hace clic en un elemento de la página utilizando su ID.
        """
        iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
        if row:
            await iframe.locator("td").filter(has_text=element_text).click()
        else:
            button = iframe.locator("input").filter(has_text=element_text)
            await button.first.click()
        # if isinstance(element, str):
        #     await iframe.locator(element).click()
        # elif isinstance(element, Locator):
        #     await element.click()
        self.click_number += 1


    async def _extract_table_data(self):
        """
        Extrae los datos de una tabla con clase 'Data' y retorna una lista de listas.
        
        Returns
        -------
        list
            Lista de listas donde cada sublista contiene los datos de una fila de la tabla.
        """
        # Lista para almacenar los datos extraídos
        datos_tabla = []

        # Seleccionar todas las filas de la tabla con clase 'Data'
        iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
        filas = await iframe.locator("table.Data").locator("tr").all()

        # Extraer los datos de cada fila
        for i, fila in enumerate(filas):
            datos = await fila.locator("td").all_inner_texts()
            datos = [dato.replace(",", "").strip() for dato in datos]

            # Agregar datos solo si la fila tiene contenido
            if datos:
                datos_tabla.append(datos)
        self.logger.info(f"Se extrajeron datos de {int(len(filas))} filas.")

        return datos_tabla


    async def _get_final_headers(self)-> list:
        """
        Extrae encabezados manteniendo el orden de la tabla, omitiendo la primera columna 
        vacía (botón) y obteniendo los niveles inferiores cuando hay agrupación.
        
        Returns
        -------
        list
            Lista de encabezados extraídos de la tabla.
        """
        if not self.headers:
            try:
                iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
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

                self.logger.info(f"Encabezados extraídos: {self.headers}")

            except Exception as e:
                print(f"Error al obtener encabezados: {e}")
            

    async def _assert_extraction(self)-> None:
        """
        Verifica y realiza la extracción de datos de la tabla según el nivel actual.
        """
        level = self.route_config.levels[self.level_index]
        iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
        await iframe.wait_for_selector("table.Data")
        if level.extract_table:
            if not self.headers:
                await self._get_final_headers()

            #self.logger.info(f"📊 Extrayendo datos de la tabla: {self.route_config.levels[self.level_index].name}")
            table_data = await self._extract_table_data()

            # Construir cada fila incluyendo los niveles donde hubo iteración
            for row in table_data:
                formatted_row = [self.year] + [self.context[level] for level in self.context.keys()] + row
                self.extracted_data.append(formatted_row)
            

    async def _navigate_levels(self, custom_row: str = "")-> None:
        """
        Navega a través de los niveles definidos en la configuración.

        Parameters
        ----------
        custom_row : str, optional
            Fila personalizada para navegar, por defecto es cadena vacía.
        """
        level = self.route_config.levels[self.level_index]

        await self._assert_extraction() 
        if level.button:
            if level.fila:
                await self._navigate_level_simple(level.fila, level.button)
            elif custom_row:
                await self._navigate_level_simple(custom_row, level.button)
            elif level.iterate:
                await self._iterate_over_levels(level.button)

    
    async def _navigate_level_simple(self, row_text: str, button_text: str)-> None:
        """
        Navega a un nivel específico haciendo clic en una fila y luego en un botón.

        Parameters
        ----------
        row : str
            Selector o identificador de la fila a hacer clic.
        button_xpath : str
            XPath del botón a hacer clic después de seleccionar la fila.
        """
        await self._click_on_element(row_text, row=True)
        await self._click_on_element(button_text, row=False)
        self.level_index += 1
    
    
    async def _iterate_over_levels(self, button_text: str)-> list:
        """
        Navega a través de cada fila en el nivel actual, guardando el contexto,
        extrayendo datos y manejando la navegación hacia adelante y atrás para
        mantener la consistencia durante la exploración jerárquica.

        Parameters
        ----------
        button_xpath : str
            XPath del botón utilizado para la navegación.

        Returns
        -------
        list
            Lista con los datos extraídos durante la iteración.
        """
        level = self.route_config.levels[self.level_index]
        iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
        await iframe.wait_for_selector("table.Data")
        filas = await iframe.locator("table.Data > tbody > tr").all()
        self.logger.info(f"📋 Se encontraron {len(filas)} filas para iterar en {level.name}")

        for i in range(len(filas)):
            fila = filas[i]
            element_name = await fila.locator("td").nth(1).inner_text()
            self.context[level.name] = element_name  # Guardar el nombre en el contexto
            self.logger.info(f"➡️ Entrando en: {element_name}")
            
            await self._navigate_level_simple(fila, button_text)
            levels_left = len(self.route_config.levels) - (self.level_index + 1)
            if levels_left > 0:
                for _ in range(levels_left):
                    await self._navigate_levels()
                for _ in range(levels_left):  # TODO: Evaluar descomentar
                    await iframe.wait_for_selector("table.Data")
                    try:
                        await self.page.go_back(timeout=100)
                    except TimeoutError:
                        pass
                    
                    self.level_index -= 1
                    self.click_number += 1
                self.level_index -= levels_left
            else:
                try:
                    await self.page.go_back(timeout=100)
                except TimeoutError:
                        pass
                self.level_index -= 1
                self.click_number += 1

        # Al terminar la iteración, se avanza de nivel        
        self.level_index += 1

    # TODO: Save data every year
    async def _extract_data_by_year(self) -> None:
        """
        Extrae los datos de la página para cada año especificado basado en la 
        configuración de ruta establecida.
        """
        for year in self.years:
            self.year = year
            self.logger.info(f"🗓️ Iniciando extracción para el año {year}, ruta: {self.route_config.name}")
            await self._navigate_to_url(year)
            
            iframe = self.page.frame(GLOBAL_SELECTORS["main_frame"])
            await iframe.wait_for_selector("table.Data")

            # Navegar a través de los niveles desde el primer nivel
            for level in self.route_config.levels:
                await self._navigate_levels()

            # Agregar metadatos: Año...
            self.level_index = 0


    # TODO: Path should be inputted by the user, else it will write inside lib
    def clean(self):
        self.cleaner = Cleaner()

    def _save_data(self)-> None:
        """
        Guarda los datos extraídos en un archivo Excel.
        """
    
        df = pd.DataFrame(self.extracted_data, columns=self.headers)
        self.cleaner = Cleaner(df, output_name=self.output_path)
        self.cleaner.clean()

    def create_route(self)-> None:
        pass


    def select_route(self)-> str:
        """
        Muestra las rutas disponibles y permite al usuario seleccionar una.
        """
        self.logger.info("\n--- Rutas disponibles ---")
        rutas_disponibles = list(self.years)

        for i, ruta in enumerate(rutas_disponibles, start=1):
            self.logger.info(f"{i}: {ruta}")

        while True:
            try:
                opcion = int(input("\nElige una ruta (número): "))
                if 1 <= opcion <= len(rutas_disponibles):
                    return rutas_disponibles[opcion - 1]
                else:
                    self.logger.error("⚠️ Opción inválida, ingresa un número de la lista.")
            except ValueError:
                self.logger.error("⚠️ Entrada inválida, ingresa un número.")


    # TODO: Modularizar años
    async def run(self):
        """
        Función principal para iniciar el proceso de scraping con selección de ruta.
        Guarda los datos recolectados incluso si ocurre un error.
        """
        await self._initialize_driver()

        try:
            #print(f"\n🔍 Iniciando scraping para la ruta: {ruta_seleccionada}")

            # Iterar sobre los años y extraer datos
            await self._extract_data_by_year()

        # except Exception as e:
        #     print(f"Se produjo un error inesperado: {e}")
        #     self.logger.info("💾 Guardando datos parciales antes de cerrar...")

        finally:
            # Guardar los datos finales si se obtuvieron datos completos
            if self.extracted_data:
                self.logger.info("💾 Guardando datos...")
                self.headers = ["Año", ""] + self.headers
                self.logger.info(self.headers)
                self._save_data()

            await self._cerrar_navegador()
            self.logger.info("✅ Proceso finalizado, driver cerrado.")
            self.logger.info(f"Se dieron {self.click_number} clicks")

