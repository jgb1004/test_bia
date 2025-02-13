FROM python:3.9

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código al contenedor
COPY . .

# Exponer el puerto para comunicación (opcional si la aplicación tiene una API)
EXPOSE 5000

# Comando por defecto para ejecutar la aplicación
CMD ["python", "src/main.py"]
