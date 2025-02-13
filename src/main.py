import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.log_handler.logger import setup_logger
from src.data_processing.clean_data import load_csv, validate_data, clean_data
from src.database.mongo_db import connect_to_mongo, store_data_in_mongo, create_indexes
from src.api_client.postcodes_api import get_postcodes_batch
from src.scripts.calculate_statistics import calculate_statistics, save_statistics
from src.scripts.export_data import save_to_csv
import pandas as pd

# Configurar logger
logger = setup_logger()

def main():
    logger.info("🟢 Iniciando el proceso de carga de datos.")

    # Cargar datos desde CSV
    file_path = "data/raw/postcodesgeo.csv"
    df = load_csv(file_path)

    if df is None or df.empty:
        logger.error("🔴 No se pudo cargar el archivo CSV. Terminando ejecución.")
        return

    validate_data(df)
    df_cleaned = clean_data(df)

    # Obtener datos de códigos postales desde la API
    df_postcodes = get_postcodes_batch(df_cleaned)

    # Unir datos limpios con datos de la API
    # df_cleaned = df_cleaned.reset_index(drop=True)
    df_final = df_postcodes.reset_index(drop=True)
    # df_final = df_cleaned.join(df_postcodes)

    # Guardar datos  en CSV
    output_path = "data/processed/postcodesgeo_api.csv"
    save_to_csv(df_final,output_path)
    df_final["data"] = df_final["data"].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else {})
    df_final["postcode"] = df_final["data"].apply(lambda x: x.get("postcode", None))

    # Conectar a MongoDB y almacenar datos con el nuevo esquema
    mongo_db = connect_to_mongo()
    if mongo_db is not None:
        create_indexes(mongo_db)  # ✅ Crear índices automáticamente
        if store_data_in_mongo(mongo_db, "postcodes", df_final):
            logger.info("✅ Datos almacenados correctamente en MongoDB.")
        else:
            logger.error("🔴 Hubo un error almacenando los datos en MongoDB.")

    # 📌 Calcular estadísticas de calidad de datos y guardarlas
    logger.info(f"🔍 Columnas disponibles en el DataFrame final: {df_final.columns.tolist()}")

    if "postcode" not in df_final.columns:
        logger.warning("⚠️ La columna 'postcode' no está en df_final. Verifica la API o la transformación de datos.")

    logger.info("📊 Calculando estadísticas de calidad de datos...")
    stats = calculate_statistics(df_final)
    save_statistics(stats)
    logger.info("✅ Estadísticas generadas y guardadas.")

    # 📌 Generar archivos de exportación
    logger.info("📂 Exportando datos de la API...")
    save_to_csv(df_final)
    logger.info("✅ Datos exportados correctamente.")

    logger.info("🚀 Proceso finalizado exitosamente.")

if __name__ == "__main__":
    main()
