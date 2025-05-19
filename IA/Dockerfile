FROM python:3.9-slim

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installa Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Crea e imposta la directory di lavoro
WORKDIR /app

# Copia i file dei requisiti
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Imposta le variabili d'ambiente
ENV TOKEN_DIR=/app/tokens
ENV CONFIG_PATH=/app/config.json

# Crea la directory per i token
RUN mkdir -p ${TOKEN_DIR}

# Comando di avvio
CMD ["python", "Email_IA.py"] 