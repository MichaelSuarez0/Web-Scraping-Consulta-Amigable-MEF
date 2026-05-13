from pathlib import Path

from consulta_amigable import ConsultaAmigable

YAML_DIR = Path(__file__).parent / "yamls"
RUTA_FINAL = YAML_DIR / "ruta_personalizada.yaml"

if __name__ == "__main__":
    scraper = ConsultaAmigable(
        timeout=100,
        headless=False,
    )

    scraper.grabar_ruta(path=RUTA_FINAL)
