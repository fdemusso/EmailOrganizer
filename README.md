# Email Organizer

Un programma Python che automatizza l'organizzazione delle tue email di Gmail utilizzando le API di Google.

## ⚠️ Importante: Credenziali OAuth

Per utilizzare questa applicazione, è necessario ottenere le proprie credenziali OAuth da Google:

1. Vai alla [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona uno esistente
3. Abilita l'API Gmail per il tuo progetto
4. Nella sezione "Credenziali", crea nuove credenziali OAuth 2.0
5. Scarica il file JSON delle credenziali
6. Rinomina il file scaricato in `google_credentials.json` e posizionalo nella directory principale del progetto

**NOTA**: Non utilizzare le credenziali di altri utenti. Ogni utente deve generare le proprie credenziali OAuth per motivi di sicurezza.

## Caratteristiche

- Accesso sicuro all'account Gmail tramite OAuth 2.0
- Categorizzazione automatica delle email in base a parole chiave
- Categorie predefinite: Password e Accessi, Acquisti Online, Pubblicità, Personale
- Configurazione personalizzabile tramite file JSON
- Analisi del contenuto dell'email (oggetto, mittente e corpo)
- Statistiche di elaborazione al termine

## Requisiti

- Python 3.6 o superiore
- Un account Gmail
- Credenziali OAuth 2.0 per le API di Gmail

## Installazione

1. Clona o scarica questo repository
2. Installa le dipendenze richieste:

```bash
pip install -r requirements.txt
```

## Configurazione

Il file `config.json` contiene le regole per la categorizzazione delle email e le impostazioni generali:

```json
{
    "rules": {
        "Password e Accessi": ["password", "login", "..."],
        "Acquisti Online": ["ordine", "acquisto", "..."],
        "Pubblicità": ["offerta", "sconto", "..."],
        "Personale": ["personale", "famiglia", "..."]
    },
    "settings": {
        "max_emails_to_process": 50,
        "check_body": true,
        "body_extract_length": 1000
    }
}
```

Puoi modificare questo file per aggiungere nuove categorie o parole chiave, o per cambiare le impostazioni.

## Utilizzo

Esegui il programma con il comando:

```bash
python email_organizer.py
```

Al primo avvio, ti verrà richiesto di autorizzare l'accesso al tuo account Gmail. Si aprirà una finestra del browser per effettuare l'accesso. Dopo l'autorizzazione, verrà creato un file `token.pickle` che memorizzerà le credenziali per gli avvii successivi.

## Come funziona

1. Il programma si connette alle API di Gmail utilizzando le credenziali OAuth 2.0
2. Recupera un numero specificato di email dalla tua casella di posta
3. Per ogni email, analizza l'oggetto, il mittente e il corpo
4. Verifica se contengono parole chiave corrispondenti alle categorie definite
5. Applica l'etichetta appropriata alle email che corrispondono a una categoria
6. Visualizza statistiche sull'elaborazione al termine

## Personalizzazione

Puoi personalizzare il comportamento del programma modificando il file `config.json`:

- Aggiungere nuove categorie
- Aggiungere o rimuovere parole chiave per ogni categoria
- Modificare il numero di email da elaborare
- Attivare o disattivare l'analisi del corpo dell'email
- Cambiare la lunghezza massima del corpo dell'email da analizzare

## Utilizzo con Docker

Per una maggiore portabilità e facilità di distribuzione, puoi eseguire l'applicazione utilizzando Docker.

### Prerequisiti

- Docker e Docker Compose installati sul tuo sistema

### Passaggi per l'esecuzione

1. **Costruisci il container**:
   ```bash
   docker-compose build
   ```

2. **Esegui l'applicazione**:
   ```bash
   docker-compose up
   ```

3. **Al primo avvio**:
   - Si aprirà un server di autenticazione sulla porta 8080
   - Segui le istruzioni per autorizzare l'applicazione
   - Le credenziali verranno salvate nella directory `./data` per utilizzi futuri

### Note importanti

- Il container monta automaticamente il file di credenziali `google_credentials.json`
- I token di autenticazione vengono salvati nella directory `./data` per persistere tra le esecuzioni
- Per modificare la configurazione, puoi editare il file `config.json` prima di costruire il container

### Variabili d'ambiente

Puoi personalizzare l'esecuzione del container con le seguenti variabili d'ambiente:

- `TOKEN_DIR`: Directory in cui salvare/cercare i token (default: `/app/data`)
- `CONFIG_PATH`: Percorso del file di configurazione (default: `/app/config.json`)
- `CLIENT_SECRET_PATH`: Percorso del file delle credenziali (default: `/app/google_credentials.json`) 