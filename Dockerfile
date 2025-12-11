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
#  EXPOSE: Decimos a Docker que este contenedor usará el puerto 8501
EXPOSE 8501
#  HEALTHCHECK Para saber si Streamlit arrancó bien
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
#  CMD: Usamos 'streamlit run' y configuramos la IP a 0.0.0.0 
# (esto es vital en Docker para que sea accesible desde fuera)
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

