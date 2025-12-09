# Imagen base con Python
FROM python:3.11-slim
#carpeta de trabajo dentro del contenedor
WORKDIR /app
#copiamos las dependencias
COPY requirements.txt .
#instalamos las dependencias dentro del contenedor
RUN pip install --no-cache-dir -r requirements.txt
#copiamos todo el proyecto al contendor
COPY . .
# 6. lo que vamos a ejecutar en este caso mi archivo que he hecho para consola
CMD ["python", "src/main.py"]
