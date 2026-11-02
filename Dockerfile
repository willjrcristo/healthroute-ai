FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria diretório de output
RUN mkdir -p output

# Variáveis de ambiente padrão
ENV LLM_PROVIDER=local
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py", "--no-gui", "--no-qa"]
