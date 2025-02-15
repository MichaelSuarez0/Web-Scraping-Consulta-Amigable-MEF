# Web Scraping: Consulta Amigable MEF
Este proyecto utiliza Selenium para automatizar la navegación web y extraer datos del portal [Consulta Amigable](https://apps5.mineco.gob.pe/transparencia/Mensual/default.aspx) del MEF. Los datos extraídos se guardan en un archivo XLSX/CSV para su posterior análisis y procesamiento.

El scraper está optimizado para extraer la ejecución del gasto con frecuencia mensual según la desagregación "¿Quién gasta?", iterando por año, departamento, provincia y municipalidad, siendo este último el nivel donde se obtienen los datos.


## 1. Requisitos

Este proyecto se desarrolló en:
* Python 3.11
* ChromeDriver

Para ejecutar se necesitas tener instaladas las siguientes dependencias con ```pip```:

```cmd
pandas==2.2.3
numpy==2.2.2
openpyxl==3.1.5
selenium==4.28.1
requests==2.32.3
```

## 2. Instalación

### 2.1. Clonar el repositorio
Clona este repositorio en tu máquina local utilizando el siguiente comando:
```bash
git clone https://github.com/AlexEvanan/Web-Scraping-Consulta-Amigable-MEF.git
```

Se establece como directorio de trabajo la carpeta clonada.
```bash
cd "nombre de la carpeta"
```

### 2.2. Crear y activar el entorno virtual

```bash
python -m venv .venvWS
```

```bash
.venvWS\Scripts\activate
```

> [!NOTE]
> Verificar que el terminal muestre el entorno virtual activo.

### 2.3. Instalar las dependencias
```cmd
pip install -r requirements.txt
```

### 2.4 Descargar ChromeDriver
Desde la web oficial  [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/#stable) descargar la version estable del binario en formato ```.zip```.

Los archivos extraidos del  ```.zip``` guardar y/o reemplazar en la carpeta ```03_config\chromedriver```

> [!IMPORTANT] 
> La versión del Chrome (el navegador regular) debe estar actualizado. 

## 3. Estructura del Proyecto

```
/WS CAMEF/
│
├── 01_data/                # Datos extraídos y procesados
│   ├── raw/                
│   └── processed/          
│
├── 02_src/                 # Código fuente
│   ├── a_config.py         # Configuracion url, driver y otros
│   ├── b_scraper.py        # Código relacionado con el scraping web
│   ├── c_cleaner.py        # Código para limpiar y procesar los datos
│   └── d_analysis.ipnb     # Scripts de análisis de los datos
│
├── 03_config/              # Driver para simular navegación
│   └── chromedriver/
│       ├── chromedriver.exe
│       ├── LICENSE.chromedriver
│       └── THIRD_PARTY_NOTICES.chromedriver
│           
├── 04_results/             # Resultados y reportes
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Documentación
└── .venvWS/                # Entorno virtual
```

## 4. Uso

### 4.1. Activar el entorno virtual

```cmd
.venvWS\Scripts\activate
```

### 4.2. Ejecutar el Script de Scraping
Para ejecutar el scraper y extraer los datos, simplemente corre el siguiente comando:

```cmd
python 02_src\b_scraper.py
```

### 4.3. Ejecutar el Script de Limpieza y Procesamiento

```cmd
python 02_src\c_cleaner.py
```

## 5. Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

## 6. Contactos
Correo:
LinkedIn: 