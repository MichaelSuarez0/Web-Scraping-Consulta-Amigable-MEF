import asyncio
from pathlib import Path

from consulta_amigable import ConsultaAmigable

YAML_DIR = Path(__file__).parent / "yamls"

# TODO: El usuario no debería tener que poner asyncio.run para correr, crear un wrapper
if __name__ == "__main__":
    scraper = ConsultaAmigable(
        timeout=100,
        headless=False,
    )

    asyncio.run(scraper.grabar_ruta(route_name="prueba_grabar_ruta", output_dir=YAML_DIR))
