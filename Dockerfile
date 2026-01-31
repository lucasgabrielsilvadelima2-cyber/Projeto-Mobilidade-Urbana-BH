# Dockerfile para BH Mobilidade Pipeline
# Python 3.11 slim para imagem otimizada

FROM python:3.11-slim

# Metadados
LABEL description="Pipeline de Dados de Mobilidade Urbana - Belo Horizonte"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY src/ ./src/
COPY config/ ./config/
COPY notebooks/ ./notebooks/
COPY tests/ ./tests/
COPY setup.py .
COPY README.md .

# Criar diretórios de dados e logs
RUN mkdir -p /app/data/bronze /app/data/silver /app/data/gold /app/logs

# Instalar o pacote
RUN pip install -e .

# Expor porta (para futura API REST)
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Volume para dados persistentes
VOLUME ["/app/data", "/app/logs"]

# Usuário não-root para segurança
RUN useradd -m -u 1000 dataeng && \
    chown -R dataeng:dataeng /app
USER dataeng

# Comando padrão
CMD ["python", "src/pipeline.py"]
