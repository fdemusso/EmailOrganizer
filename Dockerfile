FROM python:3.9-slim

WORKDIR /app

# Copia file dei requisiti
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY email_organizer.py .
COPY config.json .

# Crea una directory per i segreti
RUN mkdir -p /app/secrets

# Istruzioni per l'utente
RUN echo "IMPORTANTE: Prima di eseguire il container, montare il volume con il file delle credenziali!" > /app/README.docker

# Imposta le variabili d'ambiente
ENV PYTHONUNBUFFERED=1

# Comando predefinito
CMD ["python", "email_organizer.py"] 