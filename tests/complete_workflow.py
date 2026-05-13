from pathlib import Path
from consulta_amigable import ConsultaAmigable

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "productos"
YAML_DIR = ROOT / "yamls"
RUTA_FINAL = YAML_DIR / "ruta_personalizadaaa.yaml"

scraper = ConsultaAmigable(
    timeout=150,
    headless=False,
)

if __name__ == "__main__":
    scraper.grabar_ruta(path=RUTA_FINAL) 
    # scraper.navegar_ruta(
    #     route=RUTA_FINAL,
    #     years=range(2020, 2023),
    #     output_dir=OUTPUT_DIR,
    # )
