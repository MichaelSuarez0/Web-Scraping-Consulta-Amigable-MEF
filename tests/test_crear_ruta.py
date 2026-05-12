from pathlib import Path

from consulta_amigable import ConsultaAmigable

YAML_DIR = Path(__file__).parent / "yamls"

if __name__ == "__main__":
    scraper = ConsultaAmigable(
        timeout=100,
        headless=False,
    )

    scraper.crear_ruta(route_name="prueba2", output_dir=YAML_DIR)
