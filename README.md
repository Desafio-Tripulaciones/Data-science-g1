# README - Calculadora de Precios para Compañías Energéticas
Este proyecto tiene como objetivo desarrollar una calculadora de precios para compañías energéticas, permitiendo a los comerciales generar ofertas para clientes de diferentes compañías y buscar la tarifa más competitiva. A continuación, se detallan los pasos seguidos en el desarrollo del proyecto:

## 1. Creación de la Base de Datos (BBDD)
Escalabilidad y Flexibilidad:
La estructura de la base de datos ha sido diseñada para ser perfectamente escalable a futuros cambios en las tablas de precios.
Se han recopilado la máxima cantidad de datos posible para facilitar análisis futuros y la implementación de modelos de predicción.
La base de datos se encuentra normalizada según el modelo de entidad-relación.
Se ha creado un diagrama de clases para visualizar la estructura de la base de datos.
## 2. Web Scraping
Acceso a Candela mediante Selenium:
Se ha implementado el acceso a la plataforma Candela utilizando Selenium.
Se han generado endpoints para acceder a la base de datos y realizar consultas.
Se ha realizado la extracción de todos los valores generados por el CUPS.
## 3. Creación de Endpoints
Funcionalidad de la Aplicación:
Carga de la página inicial para la tabla de propuestas.
Implementación de rutas de consultas para la generación de filtros necesarios en la elaboración de propuestas.
Extracción de precios de las tablas según los filtros seleccionados.
Los desplegables para los filtros se generan dinámicamente a partir de las tablas, lo que asegura que las modificaciones en las tablas no afectarán al funcionamiento de la aplicación.
## 4. Extracción de Datos de PDF
Procesamiento de Facturas:
Conversión de archivos PDF a texto.
Utilización de expresiones regulares para extraer los datos necesarios.
Alta fiabilidad (100%) en la extracción de datos de las facturas de Endesa.
## 5. Generación de PDF con Propuesta
Diseño del Modelo con Reportlab:
Se ha diseñado el modelo para la generación de propuestas utilizando Reportlab.
Creación de endpoints y asignación de variables para facilitar la generación de documentos.
## 6. Integración con Power BI
Dashboard de Propuestas:
Se ha desarrollado un dashboard en Power BI que permite visualizar las propuestas generadas por el asesor.
(* Los diagramas de clases y el modelo entidad-relación se encuentran en la documentación adjunta).

### Equipo de Data Scientist : Diego Núñez, Manuel Reina, Ana Fernández, July Vargas, Miguel Ruiz 
