from pymongo import MongoClient, errors
import pandas as pd
import os
from log_handler.logger import setup_logger

# Configurar logger
logger = setup_logger()

# def connect_to_mongo(uri="mongodb://localhost:27017/", db_name="local"):
def connect_to_mongo():
    """ Conecta a MongoDB y devuelve la base de datos. """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/local")
    try:
        # client = MongoClient(uri)
        # db = client[db_name]
        client = MongoClient(mongo_uri)
        db = client.get_database()
        print("✅ Conexión exitosa a MongoDB")
        return db
    except errors.ConnectionFailure as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return None

def store_data_in_mongo(db, postcodes_collection="postcodes", df=None):
    """
    Almacena los datos en MongoDB en la colección `postcodes`.
    """
    if df is None or df.empty:
        print("⚠️ DataFrame vacío. No se almacenará en MongoDB.")
        return False

    postcodes_col = db[postcodes_collection]

    #Vaciar la colección antes de insertar nuevos datos
    postcodes_col.delete_many({})
    print("Colección 'postcodes' vaciada antes de la inserción.")

    for _, row in df.iterrows():
        lat, lon, data = row["latitude"], row["longitude"], row["data"]

        if data is None or not isinstance(data, dict):  
            continue  # Saltamos registros sin información

        postcode = data.get("postcode", None)
        if not postcode:
            continue  # No hay código postal, no se almacena

        # 📌 Asegurar que el campo `location` tenga el formato correcto para índice geoespacial
        location_data = {
            "type": "Point",
            "coordinates": [lon, lat]  # Orden correcto: [longitude, latitude]
        }

        # Insertar en la colección `postcodes`
        postcodes_col.insert_one({
            "latitude": lat,
            "longitude": lon,
            "location": location_data,
            "postcode": postcode,
            "data": data  # Ahora será un diccionario correcto
        })

    print("✅ Datos almacenados correctamente en MongoDB.")
    return True


def fetch_data(db, collection="postcodes"):
    """ Extrae los datos desde MongoDB. """
    collection = db[collection]
    data = list(collection.find({}, {"_id": 0}))  # Excluir `_id`
    return pd.DataFrame(data)

def create_indexes(mongo_db):
    """
    Crea índices en la colección `postcodes` para mejorar la eficiencia de las consultas.
    """
    logger.info("✅ Creando índices automáticamente")

    postcodes_col = mongo_db["postcodes"]

    # Obtener índices existentes en la colección de postcodes
    existing_postcodes_indexes = [idx["name"] for idx in postcodes_col.list_indexes()]

    # Crear índice compuesto para búsquedas por coordenadas
    if "latitude_1_longitude_1" not in existing_postcodes_indexes:
        postcodes_col.create_index([("latitude", 1), ("longitude", 1)], name="latitude_longitude_idx")

    # Crear índice geoespacial para consultas de proximidad
    if "location_2dsphere" not in existing_postcodes_indexes:
        postcodes_col.create_index([("location", "2dsphere")], name="location_2dsphere")

    logger.info("✅ Índices creados o ya existentes en MongoDB.")
