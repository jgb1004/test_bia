import pandas as pd
from database.mongo_db import connect_to_mongo,fetch_data  # ✅ Importamos la conexión

# 📌 Guardar en CSV y Excel
def save_to_csv(df_data, output_csv="data/processed/postcodes_api.csv"):
    df_data.to_csv(output_csv, index=False)
    print(f"✅ Datos guardados en '{output_csv}'.")

# 📌 Ejecución del script
if __name__ == "__main__":
    mongo_db = connect_to_mongo()  # ✅ Reutilizamos la conexión
    
    if mongo_db:
        df_data = fetch_data(mongo_db)
        save_to_csv(df_data)
