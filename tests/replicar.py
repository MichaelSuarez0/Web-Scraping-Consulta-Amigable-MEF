

# Selectores generales: año y frame principal
GLOBAL_SELECTORS = {"year_dropdown": "ctl00_CPH1_DrpYear", "main_frame": "frame0"}


# Definir múltiples rutas con sus niveles
ROUTES = {
    # Ruta 1
    "MUNICIPALIDADES": {
        "levels": {
            "level_1": {  # Detalle niveles de gobierno
                "button": "ctl00_CPH1_BtnTipoGobierno",  # Botón XPath
                "list_xpath": None,  # Lista para iterar
                "next_level": "level_2",  # Siguiente nivel
            },
            "level_2": {  # Nivel de gobierno: Gob locales
                "button": "ctl00_CPH1_RptData_ctl02_TD0",
                "list_xpath": None,
                "next_level": "level_3",
            },
            "level_3": {  # Subtipo de gobierno locales
                "button": "ctl00_CPH1_BtnSubTipoGobierno",
                "list_xpath": None,
                "next_level": "level_4",
            },
            "level_4": {  # Gobiernos local: Municipalidades
                "button": "ctl00_CPH1_RptData_ctl01_TD0",
                "list_xpath": None,
                "next_level": "level_5",
            },
            "level_5": {  # Departamentos
                "button": "ctl00_CPH1_BtnDepartamento",
                "list_xpath": "//tr[starts-with(@id, 'tr')]",
                "name_xpath": "./td[2]",
                "next_level": "level_6",
            },
            "level_6": {  # Provincias
                "button": "ctl00_CPH1_BtnProvincia",
                "list_xpath": "//tr[starts-with(@id, 'tr')]",
                "name_xpath": "./td[2]",
                "next_level": "level_7",
            },
            "level_7": {  # Lista Municipalidades (último nivel)
                "button": "ctl00_CPH1_BtnMunicipalidad",
                "list_xpath": None,
                "name_xpath": None,
                "table_id": "ctl00_CPH1_Mt0",  # Se extrae la tabla aquí
                "next_level": None,  # Último nivel
            },
        },
    },
    # Ruta 2
    "SECTORES": {
        "levels": {
            "level_1": {  # Detalle niveles de gobierno
                "button": "ctl00_CPH1_BtnTipoGobierno",
                "list_xpath": None,
                "next_level": "level_2",
            },
            "level_2": {  # Nivel de gobierno: Nacional
                "button": "ctl00_CPH1_RptData_ctl01_TD0",
                "list_xpath": None,
                "next_level": "level_3",
            },
            "level_3": {  # Sectores
                "button": "ctl00_CPH1_BtnSector",
                "list_xpath": "//tr[starts-with(@id, 'tr')]",
                "name_xpath": "./td[2]",
                "next_level": "level_4",
            },
            "level_4": {  # Pliegos
                "button": "ctl00_CPH1_BtnPliego",
                "list_xpath": "//tr[starts-with(@id, 'tr')]",
                "name_xpath": "./td[2]",
                "next_level": "level_5",
            },
            "level_5": {  # Ejecutoras
                "button": "ctl00_CPH1_BtnEjecutora",
                "list_xpath": None,
                "name_xpath": None,
                "table_id": "ctl00_CPH1_Mt0",
                "next_level": None,  # Último nivel
            },
        },
    },
}
