from pathlib import Path
from consulta_amigable import ConsultaAmigable
import asyncio

YAML_DIR = Path(__file__).parent / "yamls"

if __name__ == "__main__":
    scraper = ConsultaAmigable(
        timeout = 100, 
        headless = False,
        )
    
    asyncio.run(scraper.crear_ruta(route_name="salud", output_dir=YAML_DIR))
