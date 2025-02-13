import pandas as pd
from log_handler.logger import setup_logger

# Configurar el logger desde log_handler
logger = setup_logger()

def load_csv(file_path):
    """
    Carga un archivo CSV y maneja errores de carga.
    """
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
        logger.info(f"Archivo '{file_path}' cargado correctamente con {len(df)} registros.")
        return df
    except Exception as e:
        logger.error(f"Error al cargar el archivo '{file_path}': {e}")
        return None

def validate_data(df):
    """
    Valida los datos, revisa valores nulos, tipos de datos y registros duplicados.
    """
    if df is None:
        logger.error("El DataFrame está vacío. No se puede validar.")
        return None

    missing_values = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()

    logger.info(f"Validación de datos: {missing_values} valores nulos, {duplicates} duplicados.")

    return {"missing_values": missing_values, "duplicates": duplicates}

def clean_data(df):
    """
    Elimina duplicados y asegura que los datos sean consistentes.
    """
    if df is None:
        logger.error("El DataFrame está vacío. No se puede limpiar.")
        return None

    initial_count = len(df)
    df_cleaned = df.drop_duplicates()
    final_count = len(df_cleaned)

    logger.info(f"Limpieza de datos: {initial_count} registros antes, {final_count} después.")

    return df_cleaned
