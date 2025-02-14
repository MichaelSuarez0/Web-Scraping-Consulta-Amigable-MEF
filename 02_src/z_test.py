# servicios
service = Service(executable_path=a_config.PATH_DRIVER)
options = webdriver.ChromeOptions()

# Configurar el zoom al 90%
# options.add_argument("--force-ui-zoom=0.75")

driver = webdriver.Chrome(service=service, options=options)

# ir a web
driver.get(a_config.URL)


cambiar_frame(driver, "frame0")

# -----------------------------------


# driver.switch_to.default_content()

# Lista de años a iterar
years = [2012, 2013, 2014, 2015]

for year in years:
    select_option(driver, "ctl00_CPH1_DrpYear", 2021)  # Seleccionar el año
    cambiar_frame(driver, "frame0")
    click_element(driver, "ctl00_CPH1_BtnTipoGobierno")  # Tipo de gobierno
    cambiar_frame(driver, "frame0")
    click_element(driver, "tr1")  # Gobierno local
    cambiar_frame(driver, "frame0")
    click_element(
        driver, "ctl00_CPH1_BtnSubTipoGobierno"
    )  # Subtipo de gobierno (Municipalidades)
    cambiar_frame(driver, "frame0")
    click_element(driver, "ctl00_CPH1_RptData_ctl01_TD0")
    cambiar_frame(driver, "frame0")
    click_element(driver, "ctl00_CPH1_BtnDepartamento")  # Departamento
    cambiar_frame(driver, "frame0")

    # Obtener la cantidad de departamentos
    departamentos = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'tr')]")

    for i, depto in enumerate(departamentos):
        click_element(driver, f"tr{i}")  # Seleccionar el departamento
        cambiar_frame(driver, "frame0")
        click_element(driver, "ctl00_CPH1_BtnProvincia")  # Provincia
        cambiar_frame(driver, "frame0")

        # Obtener la cantidad de provincias
        provincias = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'tr')]")

        for j, prov in enumerate(provincias):
            # Seleccionar la provincia
            click_element(driver, f"tr{j}")
            cambiar_frame(driver, "frame0")

            # Municipalidad (distritos)
            click_element(driver, "ctl00_CPH1_BtnMunicipalidad")
            cambiar_frame(driver, "frame0")

            # Extraer los datos de la tabla
            datos_municipalidad = extraer_datos_tabla(driver)

            # Añadir metadatos (año, departamento, provincia) a cada fila de datos
            for fila in datos_municipalidad:
                fila_con_meta = [year, depto.text, prov.text] + fila
                todos_los_datos.append(fila_con_meta)

        # Volver al listado de departamentos
        driver.back()
        cambiar_frame(driver, "frame0")


extraer_datos_tabla(driver)

obtener_encabezados_finales(driver, "ctl00_CPH1_Mt0")

driver.back()

# recorrer por años
select_option(driver, "ctl00_CPH1_DrpYear", 2012)
cambiar_frame(driver, "frame0")

# tipo de gobierno
click_element(driver, "ctl00_CPH1_BtnTipoGobierno")
cambiar_frame(driver, "frame0")

# gobierno local
click_element(driver, "tr1")
cambiar_frame(driver, "frame0")

# seleccion entrar
click_element(driver, "ctl00_CPH1_BtnSubTipoGobierno")
cambiar_frame(driver, "frame0")


# municipalidades
click_element(driver, "ctl00_CPH1_RptData_ctl01_TD0")
cambiar_frame(driver, "frame0")


# seleccion entrar por dpto
click_element(driver, "ctl00_CPH1_BtnDepartamento")
cambiar_frame(driver, "frame0")


# Obtiene la cantidad de departamentos para recorrer
# Selecciona el pirmer departamentoa provincia
click_element(driver, "tr0")
cambiar_frame(driver, "frame0")


# Entra al detalle de proncias del dpto seleccionado
click_element(driver, "ctl00_CPH1_BtnProvincia")
cambiar_frame(driver, "frame0")


# Obtiene la cantidad de provincias para recorrer
# Selecciona la pirmera provincia
click_element(driver, "tr0")
cambiar_frame(driver, "frame0")


# Entra al detalle de disctritos de la prov seleccionada
click_element(driver, "ctl00_CPH1_BtnMunicipalidad")
cambiar_frame(driver, "frame0")


# extrae toda la tabla con todos los distritos de esa prov seleccionada

# regresa y enrtra el la siguiente provincia

# ......

# regresa y ahora con el siguiente departamento y asi
