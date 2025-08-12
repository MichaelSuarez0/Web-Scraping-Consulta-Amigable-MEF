
import yaml
from pathlib import Path
from .a_config import RouteConfig


def guardar_ruta_yaml(
    route: RouteConfig,
    path: Path,
    spacing_between_levels: bool = True
) -> None:
    """
    Guarda un objeto RouteConfig como YAML incluyendo todas sus claves,
    y con salto entre niveles para mejor legibilidad.

    Args:
        route: Instancia de RouteConfig o similar.
        path: Ruta del archivo .yml
        spacing_between_levels: Inserta líneas en blanco entre niveles si True.
    """
    # Extrae el dict completo, con defaults y claves vacías
    full_dict = route.model_dump(mode="python")

    if spacing_between_levels and "levels" in full_dict:
        # Serializa todo menos levels
        base_yaml = yaml.safe_dump(
            {k: v for k, v in full_dict.items() if k != "levels"},
            allow_unicode=True,
            sort_keys=False
        )

        # Serializa cada level por separado (para insertar salto de línea entre ellos)
        levels_yaml = [
            yaml.safe_dump([level], allow_unicode=True, sort_keys=False).strip("- ").rstrip()
            for level in full_dict["levels"]
        ]
        levels_yaml_block = "\n\n".join(f"- {block}" for block in levels_yaml)

        final_yaml = base_yaml + "levels:\n" + levels_yaml_block + "\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(final_yaml, encoding="utf-8")
        path.write_text

    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path = str(path)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(full_dict, f, allow_unicode=True, sort_keys=False)



def cargar_ruta_yaml(
    path: Path,
) -> RouteConfig:
    """
    Carga un archivo YAML y lo convierte en una instancia de RouteConfig usando Pydantic.

    Args:
        path: Ruta del archivo .yml

    Returns:
        RouteConfig: Instancia validada de RouteConfig con los datos cargados

    Raises:
        ValidationError: Si los datos del YAML no coinciden con el modelo
    """
    with path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return RouteConfig.model_validate(data)