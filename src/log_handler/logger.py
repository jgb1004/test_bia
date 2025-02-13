import logging
import os

def setup_logger():
    """
    Configura el logger para escribir en logs/app.log y mostrar mensajes en la consola.
    """
    log_file = "logs/app.log"

    # Crear la carpeta de logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a",  # "a" para añadir al log sin sobrescribir
        encoding="utf-8"  # <-- Agregar encoding UTF-8
    )

    # Crear un manejador de consola para mostrar logs en la terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # Obtener el logger principal y evitar duplicados
    logger = logging.getLogger()
    if not logger.hasHandlers():
        logger.addHandler(console_handler)

    return logger
