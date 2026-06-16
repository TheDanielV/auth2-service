# ─────────────────────────────────────────────
# Etapa 1: builder – instala dependencias
# ─────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

# Evita que Python escriba archivos .pyc y activa unbuffered para logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala herramientas de compilación mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias en un virtualenv aislado
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
# Etapa 2: runtime – imagen final ligera
# ─────────────────────────────────────────────
FROM python:3.13-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copia las dependencias instaladas desde el builder
COPY --from=builder /install /usr/local

# Copia el código fuente del proyecto
COPY app/ ./app/

# Crea el directorio de logs para que el contenedor pueda escribir en él
RUN mkdir -p /app/logs

# Puerto expuesto por uvicorn
EXPOSE 8000

# Usuario no-root por seguridad
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

