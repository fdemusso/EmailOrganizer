import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import re
from datetime import datetime

# Se modifichi questi scope, elimina il file token.pickle
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Configurazione percorsi per Docker
TOKEN_DIR = os.environ.get('TOKEN_DIR', '.')
TOKEN_PATH = os.path.join(TOKEN_DIR, 'token.pickle')
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'config.json')
CLIENT_SECRET_PATH = os.environ.get('CLIENT_SECRET_PATH', 'google_credentials.json')

def load_config():
    """Carica la configurazione dal file config.json"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"File di configurazione non trovato: {CONFIG_PATH}. Utilizzo configurazione predefinita.")
        return {
            "rules": {},
            "settings": {
                "max_emails_to_process": 50,
                "check_body": True,
                "body_extract_length": 1000
            }
        }
    except json.JSONDecodeError:
        print("Errore nel file di configurazione. Utilizzo configurazione predefinita.")
        return {
            "rules": {},
            "settings": {
                "max_emails_to_process": 50,
                "check_body": True,
                "body_extract_length": 1000
            }
        }

def get_gmail_service():
    """Crea e restituisce il servizio Gmail autenticato"""
    creds = None
    # Il file token.pickle memorizza i token di accesso e refresh dell'utente
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # Se non ci sono credenziali valide, lascia che l'utente si autentichi
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Verifica che il file delle credenziali esista
            if not os.path.exists(CLIENT_SECRET_PATH):
                raise FileNotFoundError(f"File di credenziali non trovato: {CLIENT_SECRET_PATH}")
                
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_PATH,
                SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Assicurati che la directory per il token esista
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        
        # Salva le credenziali per la prossima esecuzione
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def get_emails(service, max_results=50, include_body=True, body_length=1000):
    """Ottiene le email dalla casella di posta"""
    # Ottieni la lista delle email
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    if not messages:
        print('Nessuna email trovata.')
        return []

    print(f"Recupero dettagli di {len(messages)} email...")
    emails = []
    for i, message in enumerate(messages):
        if i % 10 == 0 and i > 0:
            print(f"Elaborate {i}/{len(messages)} email...")
        
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = msg['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'Nessun oggetto')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Mittente sconosciuto')
        date_str = next((header['value'] for header in headers if header['name'] == 'Date'), '')
        
        # Estrai il corpo dell'email solo se richiesto
        body = ""
        if include_body:
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8', errors='ignore')
            
            # Limita la lunghezza del corpo
            body = body[:body_length] if body else ""
        
        emails.append({
            'id': message['id'],
            'subject': subject,
            'sender': sender,
            'date': date_str,
            'body': body
        })
    
    return emails

def organize_emails(service, emails, rules):
    """Organizza le email in base alle regole definite"""
    if not rules:
        print("Nessuna regola definita per la categorizzazione.")
        return 0

    organized_count = 0
    for email in emails:
        subject = email['subject'].lower()
        sender = email['sender'].lower()
        body = email['body'].lower()
        content_to_check = subject + ' ' + sender + ' ' + body
        assigned_label = None

        # Applica le regole
        for label, keywords in rules.items():
            if any(keyword.lower() in content_to_check for keyword in keywords):
                assigned_label = label
                break

        if assigned_label:
            # Ottieni tutte le etichette esistenti
            labels_response = service.users().labels().list(userId='me').execute()
            labels = labels_response.get('labels', [])
            
            # Cerca l'ID dell'etichetta se esiste già
            label_id = None
            for label_obj in labels:
                if label_obj['name'] == assigned_label:
                    label_id = label_obj['id']
                    break
            
            # Crea l'etichetta se non esiste
            if not label_id:
                created_label = service.users().labels().create(
                    userId='me',
                    body={'name': assigned_label}
                ).execute()
                label_id = created_label['id']

            # Applica l'etichetta all'email
            service.users().messages().modify(
                userId='me',
                id=email['id'],
                body={'addLabelIds': [label_id]}
            ).execute()
            organized_count += 1
            print(f"Email '{email['subject']}' organizzata nella categoria '{assigned_label}'")

    return organized_count

def print_stats(emails, organized):
    """Stampa statistiche sulle email elaborate"""
    print("\n--- Statistiche ---")
    print(f"Email totali elaborate: {len(emails)}")
    print(f"Email categorizzate: {organized}")
    print(f"Percentuale di successo: {(organized/len(emails)*100) if emails else 0:.1f}%")

def main():
    # Carica la configurazione
    config = load_config()
    settings = config.get("settings", {})
    rules = config.get("rules", {})
    
    # Parametri
    max_emails = settings.get("max_emails_to_process", 50)
    check_body = settings.get("check_body", True)
    body_length = settings.get("body_extract_length", 1000)
    
    print(f"Avvio organizzazione email...")
    print(f"Categorie configurate: {', '.join(rules.keys())}")
    
    # Ottieni il servizio Gmail
    service = get_gmail_service()
    
    # Ottieni le email
    print(f"Recupero delle ultime {max_emails} email...")
    emails = get_emails(service, max_results=max_emails, include_body=check_body, body_length=body_length)
    
    # Organizza le email
    if emails:
        print(f"Trovate {len(emails)} email da organizzare.")
        organized = organize_emails(service, emails, rules)
        print(f"Organizzazione completata! {organized} email sono state categorizzate.")
        print_stats(emails, organized)
    else:
        print("Nessuna email da organizzare.")

if __name__ == '__main__':
    main() 