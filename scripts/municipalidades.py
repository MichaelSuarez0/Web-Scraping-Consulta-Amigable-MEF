from src_playwright import ConsultaAmigable, ROUTE_MUNICIPALIDADES, RouteConfig
import asyncio

if __name__ == "__main__":
    years = list(range(2024, 2026))
    scraper = ConsultaAmigable(ROUTE_MUNICIPALIDADES, years, timeout=120, headless = False)
    asyncio.run(scraper.main())