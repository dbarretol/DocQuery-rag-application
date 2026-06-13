# Usar una imagen base slim de Python
FROM python:3.12-slim

# Evitar prompts de configuración interactiva
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Crear un usuario no root
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

# Configurar directorio de trabajo
WORKDIR /app

# Asegurar que el usuario appuser tenga permisos sobre el directorio
RUN chown -R appuser:appuser /app

# Cambiar a usuario no root
USER appuser

# Copiar archivos de dependencias primero para aprovechar caché de Docker
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Instalar dependencias explícitamente y mostrar logs
RUN echo "--- Installing dependencies ---" && \
    uv sync --frozen --no-cache && \
    echo "--- Dependencies installed successfully ---"

# Copiar el código fuente
COPY --chown=appuser:appuser . .

# Crear directorio de logs
RUN mkdir -p /app/logs && chmod -R 777 /app/logs

# Exponer el puerto
EXPOSE 8000

# Comando para arrancar
CMD ["uv", "run", "uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
