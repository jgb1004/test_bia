import requests
import logging
import pandas as pd
import json
from log_handler.logger import setup_logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = setup_logger()

POSTCODES_BATCH_URL = "https://api.postcodes.io/postcodes"
MAX_WORKERS = 10  
MISSING_POSTCODES_LOG = "logs/missing_postcodes.log"

RETRY_STRATEGY = Retry(
    total=3,  
    backoff_factor=1,  
    status_forcelist=[500, 502, 503, 504],  
    allowed_methods=["POST"]  
)

# Configurar sesión global con reintentos
session = requests.Session()
adapter = HTTPAdapter(max_retries=RETRY_STRATEGY)
session.mount("https://", adapter)

def log_missing_postcode(lat, lon, reason):
    """ Guarda coordenadas sin código postal en un log estructurado (JSON). """
    error_data = {"latitude": lat, "longitude": lon, "reason": reason}
    with open(MISSING_POSTCODES_LOG, "a") as log_file:
        log_file.write(json.dumps(error_data) + "\n")
    logger.warning(f"⚠️ Coordenada ({lat}, {lon}) sin código postal. Razón: {reason}")

def fetch_postcodes(batch, batch_index, start_idx, end_idx):
    """ Realiza la petición a la API de postcodes.io para un lote de coordenadas con manejo de errores. """
    payload = {"geolocations": [{"longitude": lon, "latitude": lat} for lat, lon in zip(batch["lat"], batch["lon"])]}

    try:
        response = session.post(POSTCODES_BATCH_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()

        results = []
        if data.get("status") == 200 and isinstance(data.get("result"), list):
            for idx, item in enumerate(data["result"]):
                lat, lon = batch.iloc[idx]["lat"], batch.iloc[idx]["lon"]
                if item and "result" in item and item["result"]:
                    results.append({"latitude": lat, "longitude": lon, "data": item["result"]})  # Guardamos el JSON completo
                else:
                    log_missing_postcode(lat, lon, "No data returned")
                    results.append({"latitude": lat, "longitude": lon, "data": None})  # Agregar un valor vacío

            logger.info(f"✅ Lote {batch_index + 1}: Procesado ({start_idx} a {end_idx}) con {len(batch)} registros.")
        else:
            logger.warning(f"⚠️ Lote {batch_index + 1}: Respuesta vacía o inválida. ({start_idx} a {end_idx})")
            for idx in range(len(batch)):
                lat, lon = batch.iloc[idx]["lat"], batch.iloc[idx]["lon"]
                log_missing_postcode(lat, lon, "API returned empty data")
                results.append({"latitude": lat, "longitude": lon, "data": None})

    except requests.Timeout:
        logger.error(f"❌ Lote {batch_index + 1}: Timeout al consultar la API. ({start_idx} a {end_idx})")
        results = [{"latitude": batch.iloc[idx]["lat"], "longitude": batch.iloc[idx]["lon"], "data": None} for idx in range(len(batch))]
    
    except requests.ConnectionError:
        logger.error(f"❌ Lote {batch_index + 1}: Fallo en la conexión con la API. ({start_idx} a {end_idx})")
        results = [{"latitude": batch.iloc[idx]["lat"], "longitude": batch.iloc[idx]["lon"], "data": None} for idx in range(len(batch))]

    except requests.HTTPError as e:
        logger.error(f"❌ Lote {batch_index + 1}: Error HTTP ({response.status_code}). ({start_idx} a {end_idx}) - {e}")
        results = [{"latitude": batch.iloc[idx]["lat"], "longitude": batch.iloc[idx]["lon"], "data": None} for idx in range(len(batch))]

    except Exception as e:
        logger.error(f"❌ Lote {batch_index + 1}: Error inesperado. ({start_idx} a {end_idx}) - {e}")
        results = [{"latitude": batch.iloc[idx]["lat"], "longitude": batch.iloc[idx]["lon"], "data": None} for idx in range(len(batch))]

    return results

def get_postcodes_batch(df, batch_size=100):
    """ Obtiene información de los códigos postales más cercanos para un DataFrame en lotes, devolviendo un DataFrame con JSON completo. """
    if df.empty:
        logger.warning("⚠️ El DataFrame está vacío. No hay coordenadas para procesar.")
        return pd.DataFrame()
    # subset_size = len(df)//1000
    # df = df.iloc[:subset_size]
    total_records = len(df)
    logger.info(f"📊 Se procesarán {total_records} registros en lotes de {batch_size}.")

    results = []
    batch_size = min(batch_size, total_records)
    batches = [df.iloc[i:i + batch_size] for i in range(0, total_records, batch_size)]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_postcodes, batch, i, i * batch_size, min((i + 1) * batch_size, total_records)): i
            for i, batch in enumerate(batches)
        }

        for future in as_completed(futures):
            batch_index = futures[future]
            try:
                results.extend(future.result())
            except Exception as e:
                logger.error(f"❌ Error procesando el lote {batch_index + 1}: {e}")
                results.extend([{"latitude": None, "longitude": None, "data": None}] * len(batches[batch_index]))

    df_results = pd.DataFrame(results)

    if df_results.empty:
        logger.warning("⚠️ No se obtuvieron datos de la API.")
    else:
        logger.info(f"📊 Datos obtenidos correctamente: {len(df_results)} registros.")

    return df_results
