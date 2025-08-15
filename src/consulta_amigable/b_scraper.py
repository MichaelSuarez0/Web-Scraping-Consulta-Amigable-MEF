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
import warnings
from pathlib import Path
from typing import Iterable
from playwright.async_api import async_playwright, TimeoutError
from rich.console import Console
from .a_config import LevelConfig, RouteConfig, Locators
from .c_cleaner import CCleaner
from .f_logger import setup_logger
from .e_export_yaml import guardar_ruta_yaml, cargar_ruta_yaml
from .d_cli import ConsultaCLI

logger = setup_logger()

# =====================
# Funciones de Utilidad
# =====================
class ConsultaAmigable:
    URL_MENSUAL = "https://apps5.mineco.gob.pe/transparencia/mensual/"
    URL_ANUAL = "https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx?y={}&ap=ActProy"

    def __init__(self, timeout: int = 100, headless: bool = False):
        self._headless = headless
        self._timeout = timeout
        self._playwright = None
        self._browser = None
        self._page = None
        self._cleaner = None
        self.logger = logger

        self.route_config: RouteConfig = None
        self.years = None
        self._year = 0

        self._extracted_data = []
        self._headers = []
        self._context = {}
        self._clicks_number = 0
        self.level_index = 0

        self.console = Console()
        if timeout < 50:
            warnings.warn(
                "Un timeout menor a 50 puede llevar a inconsistencias con la interacción de la página"
            )

    async def _initialize_driver(self):
        """
        Inicializa el driver de Playwright.
        """
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self._headless, slow_mo=self._timeout
        )
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        self._page = await context.new_page()
        self._page.set_default_timeout(15_000)
        self._page.set_default_navigation_timeout(20_000)

    async def _cerrar_navegador(self):
        """
        Cierra el navegador y libera los recursos.
        """
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def _navigate_to_url(self, year: str | int, mensual: bool = False):
        """
        Navega a la URL especificada utilizando el driver proporcionado.
        """
        if not mensual:
            await self._page.goto(self.URL_ANUAL.format(str(year)))
        else:
            await self._page.goto(self.URL_MENSUAL)

    async def _click_on_element(self, element_text: str | Locators, row: bool = True):
        """
        Hace clic en un elemento de la página utilizando su ID.
        """
        iframe = self._page.frame(Locators.main_frame)
        if row:
            await iframe.locator(Locators.table_data).locator(Locators.text_rows).filter(
                has_text=element_text
            ).click()
        else:
            button = iframe.locator(Locators.buttons).filter(has_text=element_text)
            await button.first.click()
        # if isinstance(element, str):
        #     await iframe.locator(element).click()
        # elif isinstance(element, Locator):
        #     await element.click()
        self._clicks_number += 1

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
        iframe = self._page.frame(Locators.main_frame)
        filas = await iframe.locator(Locators.table_data).locator("tr").all()

        # Extraer los datos de cada fila
        for i, fila in enumerate(filas):
            datos = await fila.locator("td").all_inner_texts()
            datos = [dato.replace(",", "").strip() for dato in datos]

            # Agregar datos solo si la fila tiene contenido
            if datos:
                datos_tabla.append(datos)
        self.logger.info(f"Se extrajeron datos de {int(len(filas))} filas.")

        return datos_tabla

    async def _get_final_headers(self) -> list:
        """
        Extrae encabezados manteniendo el orden de la tabla, omitiendo la primera columna
        vacía (botón) y obteniendo los niveles inferiores cuando hay agrupación.

        Returns
        -------
        list
            Lista de encabezados extraídos de la tabla.
        """
        if not self._headers:
            try:
                iframe = self._page.frame(Locators.main_frame)
                primer_encabezado = iframe.locator("tr[id='ctl00_CPH1_Mt0_Row0']")
                segundo_encabezado = iframe.locator("tr[id='ctl00_CPH1_Mt0_Row1']")
                tds = await primer_encabezado.locator("td").all()

                idx_inferior = (
                    0  # Índice para recorrer fila_inferior cuando haya agrupación
                )

                for i, td in enumerate(tds):
                    # Omitir la primera celda si está vacía (botón)
                    if i == 0:
                        continue

                    colspan = await td.get_attribute("colspan")

                    if (
                        colspan
                    ):  # Si hay agrupación, tomar encabezados del nivel inferior
                        for _ in range(int(colspan)):
                            encabezado = (
                                await segundo_encabezado.locator("td")
                                .nth(idx_inferior)
                                .inner_text()
                            )
                            self._headers.append(encabezado.strip())
                            idx_inferior += 1
                    else:  # Si no hay agrupación, tomar el texto directamente
                        encabezado = await td.inner_text()
                        self._headers.append(encabezado.strip())

                self.logger.info(f"Encabezados extraídos: {self._headers}")

            except Exception as e:
                print(f"Error al obtener encabezados: {e}")

    async def _assert_extraction(self) -> None:
        """
        Verifica y realiza la extracción de datos de la tabla según el nivel actual.
        """
        level = self.route_config.levels[self.level_index]
        iframe = self._page.frame(Locators.main_frame)
        await iframe.wait_for_selector(Locators.table_data)
        if level.extract_table:
            if not self._headers:
                await self._get_final_headers()

            # self.logger.info(f"📊 Extrayendo datos de la tabla: {self.route_config.levels[self.level_index].name}")
            table_data = await self._extract_table_data()

            # Construir cada fila incluyendo los niveles donde hubo iteración
            for row in table_data:
                formatted_row = (
                    [self._year]
                    + [self._context[level] for level in self._context.keys()]
                    + row
                )
                self._extracted_data.append(formatted_row)

    async def _navigate_levels(self) -> None:
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
            elif level.iterate:
                await self._iterate_over_levels(level.button)

    async def _navigate_level_simple(self, row_text: str, button_text: str) -> None:
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

    async def _iterate_over_levels(self, button_text: str) -> list:
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
        iframe = self._page.frame(Locators.main_frame)
        await iframe.wait_for_selector(Locators.table_data)
        filas = (
            await iframe.locator(Locators.table_data).locator(Locators.text_rows).all()
        )
        self.logger.info(
            f"📋 Se encontraron {len(filas)} filas para iterar en {level.name}"
        )

        for i in range(len(filas)):
            fila = filas[i]
            element_name = await fila.locator("td").nth(1).inner_text()
            self._context[level.name] = element_name  # Guardar el nombre en el contexto
            self.logger.info(f"➡️ Entrando en: {element_name}")

            await self._navigate_level_simple(fila, button_text)
            levels_left = len(self.route_config.levels) - (self.level_index + 1)
            if levels_left > 0:
                for _ in range(levels_left):
                    await self._navigate_levels()
                for _ in range(levels_left):  # TODO: Evaluar descomentar
                    await iframe.wait_for_selector(Locators.table_data)
                    try:
                        await self._page.go_back(timeout=100)
                    except TimeoutError:
                        pass

                    self.level_index -= 1
                    self._clicks_number += 1
                self.level_index -= levels_left
            else:
                try:
                    await self._page.go_back(timeout=100)
                except TimeoutError:
                    pass
                self.level_index -= 1
                self._clicks_number += 1

        # Al terminar la iteración, se avanza de nivel
        self.level_index += 1

    # TODO: Save data every year (?)
    async def _extract_data_by_year(self) -> None:
        """
        Extrae los datos de la página para cada año especificado basado en la
        configuración de ruta establecida.
        """
        for year in self.years:
            self._year = year
            self.logger.info(
                f"🗓️  Iniciando extracción para el año {year}, ruta: {self.route_config.route_name}"
            )
            await self._navigate_to_url(year)

            iframe = self._page.frame(Locators.main_frame)
            await iframe.wait_for_selector(Locators.table_data)

            # Navegar a través de los niveles desde el primer nivel
            for _ in self.route_config.levels:
                await self._navigate_levels()

            # Agregar metadatos: Año...
            self.level_index = 0

    def _save_data(self, output_dir: Path) -> None:
        """
        Guarda los datos extraídos en un archivo Excel.
        """
        import pandas as pd

        df = pd.DataFrame(self._extracted_data, columns=self._headers)
        self._cleaner = CCleaner(
            df, output_path=output_dir / f"{self.route_config.route_name}.xlsx"
        )
        return self._cleaner.clean()

    async def crear_ruta(self, route_name: str, output_dir: str = ".") -> None:
        """
        Interfaz interactiva en la terminal para construir y guardar una ruta de scraping.

        Esta función guía al usuario, mediante un CLI interactivo, en la creación
        de una configuración de ruta (`RouteConfig`) que describe los niveles de
        navegación dentro de la interfaz de "Consulta Amigable". El flujo inicia
        cargando la página principal, pidiendo al usuario las filas y botones que
        desea dar click, y avanzando nivel por nivel hasta se indique que no hay
        más niveles que configurar. La ruta resultante se guarda en un archivo YAML
        que luego se puede utilizar en la función run() para scrapear múltiples años.

        Parameters
        ----------
        route_name : str
            Nombre de la ruta a crear. Este nombre se utilizará tanto para
            etiquetar la configuración como para el nombre del archivo
            de salida.
        output_dir : str, optional
            Ruta al directorio donde se guardará el archivo YAML con la configuración
            de la ruta. Por defecto se guardará en el directorio actual.

        Returns
        -------
        None
            No devuelve ningún valor, pero genera como efecto secundario un archivo
            `<route_name>.yaml` en el directorio especificado.

        Notes
        -----
        - Establece por defecto el año 2024 como año de referencia inicial para la
        navegación.
        - Utiliza `ConsultaCLI` para solicitar al usuario la configuración de cada
        nivel (`LevelConfig`), incluyendo parámetros de fila y botón.
        - Si un nivel no contiene valores de `button` ni `fila`, se considera el
        final de la ruta y se guarda la configuración en disco.
        - El archivo YAML generado incluye valores por defecto definidos en
        `save_route_with_defaults`.

        See Also
        --------
        ConsultaCLI : CLI interactivo para definir niveles de navegación.
        RouteConfig : Clase que representa la configuración completa de una ruta.
        save_route_with_defaults : Guarda un `RouteConfig` en un archivo YAML con
            parámetros por defecto.
        """
        cli = ConsultaCLI()
        output_dir = Path(output_dir)
        self.years = [2024]
        await self._initialize_driver()
        await self._navigate_to_url(self.years[0])

        iframe = self._page.frame(Locators.main_frame)
        await iframe.wait_for_selector(Locators.table_data)

        route_config = RouteConfig(route_name=route_name, output_path=str(output_dir))
        self.level_index = 1
        while True:
            iframe = self._page.frame(Locators.main_frame)
            await iframe.wait_for_selector(Locators.table_data)
            buttons_locator = iframe.locator(Locators.buttons)
            filas_locator = iframe.locator(Locators.table_data).locator(
                Locators.text_rows
            )
            buttons = await buttons_locator.evaluate_all(
                "elements => elements.map(el => el.value)"
            )
            filas = await filas_locator.all_inner_texts()
            level_config = await cli.create_level_config(
                name=f"Nivel {self.level_index}", buttons=buttons, filas=filas
            )
            route_config.levels.append(level_config)

            if not level_config.button and not level_config.fila:
                await self._cerrar_navegador()
                route_path = output_dir / f"{route_name}.yaml"
                guardar_ruta_yaml(route_config, path=route_path)
                logger.info(f"Se guardó la ruta en {route_path}")
                break
            else:
                await self._navigate_level_simple(
                    level_config.fila, level_config.button
                )

    # TODO: VERIFICAR TYPE DE LOS AÑOS
    # TODO: Modificar see also según sphinx
    async def navegar_ruta(
        self,
        route: str | Path | RouteConfig,
        years: list[int] | int,
        output_dir: str | Path,
    ):
        """
        Ejecuta el proceso de scraping siguiendo una ruta de navegación predefinida.

        Esta función carga una configuración de ruta (`RouteConfig`) previamente creada,
        navega por la interfaz de "Consulta Amigable" para cada año especificado y
        extrae los datos correspondientes. La información recolectada se guarda en
        disco incluso si ocurre un error durante la ejecución.

        Parameters
        ----------
        route : Path or RouteConfig
            Configuración de la ruta a seguir durante el scraping. Puede ser una ruta 
            (str o Path) a un archivo YAML creado a partir de `crear_ruta()` o un
            objeto `RouteConfig` ya instanciado.
        years : list[int] or int
            Año o lista de años para los que se ejecutará el scraping.
        output_dir : str or Path
            Ruta al directorio donde se guardarán los archivos de salida con los
            datos extraídos.

        Returns
        -------
        output_path : str | None
            Retorna el path del excel con los datos recolectados. También imprime
            el path en la consola.

        Notes
        -----
        - Asegura el cierre del navegador al final de la ejecución, incluso si
          ocurre una excepción.

        See Also
        --------
        crear_ruta : Función interactiva para construir y guardar una configuración
            de ruta desde cero.
        cargar_ruta_yaml : Carga una configuración de ruta desde un archivo YAML.
        _extract_data_by_year : Lógica de extracción de datos para cada año.
        _save_data : Guarda los datos recolectados en disco.
        """

        if isinstance(route, (str, Path)):
            path = Path(route)
            route = cargar_ruta_yaml(path)
        self.route_config = route

        self.years = list(years) if isinstance(years, Iterable) else [years]
        await self._initialize_driver()

        try:
            # print(f"\n🔍 Iniciando scraping para la ruta: {ruta_seleccionada}")

            # Iterar sobre los años y extraer datos
            await self._extract_data_by_year()

        finally:
            output_path = None
            # Guardar los datos finales si se obtuvieron datos completos
            if self._extracted_data:
                self.logger.info("💾 Guardando datos...")
                self._headers = ["Año", ""] + self._headers
                output_path = self._save_data(output_dir=output_dir)

            await self._cerrar_navegador()
            self.logger.info("✅ Proceso finalizado, driver cerrado.")
            self.logger.info(f"Se dieron {self._clicks_number} clicks")

            return str(output_path)

    # def select_route(self)-> str:
    #     """
    #     Muestra las rutas disponibles y permite al usuario seleccionar una.
    #     """
    #     self.logger.info("\n--- Rutas disponibles ---")
    #     rutas_disponibles = list(self.years)

    #     for i, ruta in enumerate(rutas_disponibles, start=1):
    #         self.logger.info(f"{i}: {ruta}")

    #     while True:
    #         try:
    #             opcion = int(input("\nElige una ruta (número): "))
    #             if 1 <= opcion <= len(rutas_disponibles):
    #                 return rutas_disponibles[opcion - 1]
    #             else:
    #                 self.logger.error("⚠️ Opción inválida, ingresa un número de la lista.")
    #         except ValueError:
    #             self.logger.error("⚠️ Entrada inválida, ingresa un número.")
