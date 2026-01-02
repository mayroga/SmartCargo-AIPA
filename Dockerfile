# Usamos Python 3.13 como base
FROM python:3.13-slim

# Variables de entorno para no generar caches de pip y logs de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos dependencias del sistema necesarias para Pillow y tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    poppler-utils \
    git \
    && rm -rf /var/lib/apt/lists/*

# Creamos el directorio de la app
WORKDIR /app

# Copiamos los archivos de la app
COPY . /app

# Instalamos dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponemos el puerto que usa Render para web services
EXPOSE 10000

# Comando para iniciar la app con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
