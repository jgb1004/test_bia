import pandas as pd
import json
from database.mongo_db import connect_to_mongo, fetch_data # ✅ Importamos la conexión



# 📌 Calcular estadísticas de calidad de datos
def calculate_statistics(df):
    total_records = len(df)

    # 📌 Validar que la columna 'postcode' exista antes de usarla
    if "postcode" not in df.columns:
        print("⚠️ La columna 'postcode' no está en el DataFrame. Verifica los datos.")
        return {
            "Total registros": total_records,
            "Coordenadas sin codigo postal": "N/A",
            "Porcentaje sin codigo postal": "N/A",
            "Registros duplicados": "N/A",

            "Porcentaje duplicados": "N/A",
        }

    missing_postcodes = df["postcode"].isna().sum()
    duplicate_coords = df.duplicated(subset=["latitude", "longitude"]).sum()

    stats = {
        "Total registros": total_records,
        "Coordenadas sin codigo postal": missing_postcodes,
        "Porcentaje sin codigo postal": round((missing_postcodes / total_records) * 100, 2),
        "Registros duplicados": duplicate_coords,
        "Porcentaje duplicados": round((duplicate_coords / total_records) * 100, 2),
    }
    
    return stats

# 📌 Guardar estadísticas en CSV y JSON
def save_statistics(stats, output_csv="data/reports/statistics.csv", output_json="data/reports/statistics.json"):
    df_stats = pd.DataFrame([stats])
    df_stats.to_csv(output_csv, index=False)
    
    with open(output_json, "w") as json_file:
        json.dump(stats, json_file, indent=4, default=str)


    print(f"✅ Estadísticas guardadas en '{output_csv}' y '{output_json}'.")

# 📌 Ejecución del script
if __name__ == "__main__":
    mongo_db = connect_to_mongo()

    if mongo_db:
        df_data = fetch_data(mongo_db)
        stats = calculate_statistics(df_data)
        save_statistics(stats)