from pathlib import Path
from typing import Any

from playwright.async_api import Page
from playwright.async_api import Error as PlaywrightError

from consulta_amigable.a_config import RouteConfig
from consulta_amigable.f_logger import setup_logger
from consulta_amigable.e_export_yaml import guardar_ruta_yaml


class ClickRecorder:
    def __init__(self, page: Page, grabador_path: Path, main_frame_name: str, table_selector: str):
        self._page = page
        self.GRABADOR_PATH = grabador_path
        self.main_frame_name = main_frame_name
        self.table_selector = table_selector
        self.logger = setup_logger("consulta_amigable")

    async def _inyectar_grabador(self):
        """Inyecta el script de grabación en el iframe"""
        try:
            iframe = self._page.frame(self.main_frame_name)
            if not iframe:
                return
            await iframe.wait_for_selector(self.table_selector, timeout=5000)
            script = self.GRABADOR_PATH.read_text(encoding="utf-8")
            await iframe.evaluate(script)
        except Exception as e:
            self.logger.info(f"Error inyectando grabador: {e}")

    async def grabar_clicks(self, output_file: str | Path) -> RouteConfig:
        """
        Graba clicks y retorna un RouteConfig
        
        Returns
        -------
        RouteConfig
            Configuración de ruta generada a partir de los clicks
        """
        output_file = Path(output_file)
        route_name = output_file.stem
        await self._inyectar_grabador()
        
        async def on_frame_navigated(frame):
            if frame.name == self.main_frame_name:
                await self._inyectar_grabador()
        
        self._page.on("framenavigated", on_frame_navigated)
        
        self.logger.info("\n🎬 GRABANDO CLICKS. Haz tus clicks normalmente y cierra el navegador cuando termines.\n")
        
        clicks_json: dict[str, Any] = {"clicks": []}
        
        while True:
            try:
                iframe = self._page.frame(self.main_frame_name)
                if iframe:
                    clicks_data = await iframe.evaluate("""
                        () => {
                            try {
                                const saved = localStorage.getItem('_macro_clicks');
                                if (saved) return JSON.parse(saved);
                            } catch(e){}
                            return window.clicks || [];
                        }
                    """)
                    clicks_json = {"clicks": clicks_data or []}
                await self._page.wait_for_timeout(500)
            except PlaywrightError as e:
                if "Target page, context or browser has been closed" in str(e):
                    self.logger.info("El navegador se cerró. Grabación terminada.")
                    break
                else:
                    self.logger.error(f"Error inesperado de Playwright: {e}")
                    break

        
        self.logger.info("Convirtiendo clicks a Yaml...")

        # Filtrar solo TD e INPUT
        clicks_filtrados = [
            c for c in clicks_json.get("clicks", []) 
            if c.get("tag") in ("TD", "INPUT")
        ]
        clicks_json["clicks"] = clicks_filtrados
        
        # Convertir a RouteConfig
        route_config = RouteConfig.from_clicks_json(
            clicks_json=clicks_json,
            route_name=route_name,
            output_path=str(output_file.parent)
        )
        
        # Guardar como YAML
        guardar_ruta_yaml(route_config, path=output_file)
        
        self.logger.info(f"Guardado: {output_file}")
        self.logger.info(f"Total de niveles creados: {len(route_config.levels)}")
        
        return route_config