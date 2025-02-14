# Proyecto: TEST BIA DATOS GEOESPACIALES

## Descripción 📌
Este proyecto realiza la extracción de datos geoespaciales mediante la integración de coordenadas de latitud y longitud con información detallada de códigos postales obtenida desde una API externa. Los datos procesados se almacenan en MongoDB para su posterior análisis y consultas optimizadas.

## Arquitectura 🏗️
La solución está compuesta por los siguientes componentes:

1. **Extracción de datos**: Carga de datos en formato CSV.
2. **Limpieza y validación**: Se validan y limpian los datos para asegurar su integridad.
3. **Consulta de datos en API**: Se realiza la consulta de códigos postales en la API externa en lotes para mejorar la eficiencia.
4. **Almacenamiento en MongoDB**: Se almacena la información en una colección optimizada con índices geoespaciales.
5. **Generación de reportes**: Cálculo de estadísticas de calidad de datos y exportación a formatos CSV y JSON.

![Diagrama de Arquitectura]("docs/ArquitecturaTestBIA.png")

## Tecnologías utilizadas 🛠️
- **Python**: Procesamiento de datos y consumo de API.
- **MongoDB**: Almacenamiento de datos con optimización geoespacial.
- **Docker & Docker Compose**: Contenerización del proyecto.
- **Pandas**: Manipulación de datos.
- **Requests**: Integración con la API de códigos postales.
- **Logging**: Registro de eventos y errores.

## Requisitos 📋
- Tener instalado **Docker** y **Docker Compose**.
- Tener configurado **MongoDB** en local o en un contenedor Docker.

## Instalación y ejecución 🚀

### Opción 1: Ejecutar en entorno local
```sh
# Clonar el repositorio
git clone https://github.com/jgb1004/test_bia.git
cd bia

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el script principal
python src/main.py
```

### Opción 2: Ejecutar con Docker
```sh
# Construir y levantar los contenedores
docker-compose up --build
```

Este comando iniciará los servicios definidos en el archivo `docker-compose.yml`, incluyendo la aplicación y MongoDB.

## Estructura del repositorio 📂
```
📦 proyecto
 ┣ 📂 bia
 ┃ ┣ 📂 data_processing   # Procesamiento y validación de datos
 ┃ ┣ 📂 api_client        # Módulo para consumir la API de códigos postales
 ┃ ┣ 📂 database         # Conexión y almacenamiento en MongoDB
 ┃ ┣ 📂 scripts         # Generación de reportes y estadísticas
 ┃ ┣ 📂 tests           # Pruebas unitarias
 ┃ ┣ 📜 main.py         # Script principal
 ┣ 📜 Dockerfile        # Definición de imagen Docker
 ┣ 📜 docker-compose.yml # Orquestación de contenedores
 ┣ 📜 requirements.txt   # Dependencias del proyecto
 ┣ 📜 README.md         # Documentación del proyecto
```

## Consultas en MongoDB 🗄️

### Obtener los códigos postales más comunes
```js
db.postcodes.aggregate([
  { $group: { _id: "$postcode", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```

### Contar coordenadas sin código postal
```js
db.postcodes.countDocuments({ postcode: null })
```

## Contribución 🤝
Si deseas contribuir, por favor sigue los siguientes pasos:
1. **Fork** el repositorio.
2. Crea una nueva rama con la funcionalidad o corrección.
3. Realiza un **Pull Request** con una descripción detallada.
