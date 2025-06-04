from src_playwright import ConsultaAmigable, ROUTE_MUNICIPALIDADES, ROUTE_SALUD
import asyncio

if __name__ == "__main__":
    years = list(range(2024, 2026))

    # scraper = ConsultaAmigable(
    #     ruta = ROUTE_MUNICIPALIDADES, 
    #     years = years, 
    #     timeout = 30, 
    #     headless = False
    #     )
    
    scraper = ConsultaAmigable(
        ruta = ROUTE_SALUD,
        years = years, 
        timeout = 50, 
        headless = False
        )
    
    asyncio.run(scraper.main())