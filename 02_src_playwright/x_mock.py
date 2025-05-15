
def main():
    """
    Función principal para iniciar el proceso de scraping con selección de ruta.
    Guarda los datos recolectados incluso si ocurre un error.
    """
    driver = initialize_driver()
    todos_los_datos = []
    table_headers = []

    try:
        navigate_to_url(driver, a_config.URL_MENSUAL)

        ruta_seleccionada = select_route()
        print(f"\n🔍 Iniciando scraping para la ruta: {ruta_seleccionada}")

        # Obtener configuración de la ruta seleccionada
        file_conf = a_config.FILE_CONFIGS.get(ruta_seleccionada, {})
        encabezados_base = file_conf.get("ENCABEZADOS_BASE", [])
        archivo_scraping = file_conf.get("ARCHIVO_SCRAPING", [])

        # Iterar sobre los años y extraer datos
        for year in a_config.YEARS:
            datos_anio = extract_data_by_year(
                driver, year, ruta_seleccionada, table_headers
            )

            todos_los_datos.extend(datos_anio)

    except Exception as e:
        print(f"Se produjo un error inesperado: {e}")

        # Guardar datos parciales si hubo un error
        if todos_los_datos:
            print("💾 Guardando datos parciales antes de cerrar...")
            encabezados_completos = encabezados_base + table_headers
            save_data(
                os.path.join(a_config.PATH_DATA_RAW, "parcial_" + archivo_scraping),
                todos_los_datos,
                encabezados_completos,
            )

    finally:
        # Guardar los datos finales si se obtuvieron datos completos
        if todos_los_datos:
            print("💾 Guardando datos finales...")
            encabezados_completos = encabezados_base + table_headers
            save_data(
                os.path.join(a_config.PATH_DATA_RAW, archivo_scraping),
                todos_los_datos,
                encabezados_completos,
            )

        driver.quit()
        print("✅ Proceso finalizado, driver cerrado.")

