from dataclasses import dataclass

@dataclass
class Locator:
    """
    Locators en CSS para interactuar con botones, filas, etc.
    """
    # Botones
    main_frame = "frame0"
    table_data = "table.Data"
    buttons = "input[type='submit']"
    text_rows = "td[align='left']"
    