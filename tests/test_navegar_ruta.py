from pathlib import Path
from consulta_amigable import ConsultaAmigable
import asyncio

YAML_DIR = Path(__file__).parent / "yamls"
PRODUCTOS_DIR = Path(__file__).parent / "productos"
scraper = ConsultaAmigable(
    timeout=100,
    headless=False,
)

def test_ruta_municipalidades():
    pass
# scraper = ConsultaAmigable(
#     ruta = ROUTE_MUNICIPALIDADES,
#     years = years,
#     timeout = 30,
#     headless = False
#     )


def test_ruta_salud():
    asyncio.run(
        scraper.navegar_ruta(
            route=YAML_DIR / "salud.yaml",
            years=range(2020, 2025),
            output_dir=PRODUCTOS_DIR,
        )
    )

if __name__ == "__main__":
    test_ruta_salud()
