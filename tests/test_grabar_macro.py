from pathlib import Path
from consulta_amigable import ConsultaAmigable
import asyncio

YAML_DIR = Path(__file__).parent / "yamls"
PRODUCTOS_DIR = Path(__file__).parent / "productos"

scraper = ConsultaAmigable(
    timeout=100,
    headless=False,
)

def test_ruta_salud():
    asyncio.run(
        scraper.grabar_clicks(
            output_file=YAML_DIR / "prueba_grabar_macro.json",
            year=2024,
        )
    )

if __name__ == "__main__":
    test_ruta_salud()
