FROM python:3.9.22

# 1. Instalar dependencias del sistema (runtime + build)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    libpq5 && \ 
    rm -rf /var/lib/apt/lists/*

# 2. Configurar entorno
WORKDIR /code
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 3. Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar aplicación
COPY . .

# 5. Limpieza SEGURA (manteniendo libpq5)
RUN apt-get purge -y --auto-remove gcc python3-dev libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 6. Configurar seguridad
RUN groupadd -g 1001 django && \
    useradd -r -u 1001 -g django django && \
    chown -R django:django /code

# 7. Prepara la aplicación
USER django
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "-c", "config/gunicorn/conf.py", "--bind", "0.0.0.0:8000", "--chdir", "commerce", "commerce.wsgi:application"]