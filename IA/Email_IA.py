import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path
import tempfile
from datetime import datetime
import base64
import ollama
import psutil
import subprocess
from tqdm import tqdm
import logging

# Configurazione del logging
logging.basicConfig(
    filename='email_organizer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurazione degli scope per l'API Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class AICategorizer:
    def __init__(self):
        self.categories_file = os.path.join(os.path.dirname(__file__), 'categories.json')
        ram = psutil.virtual_memory()

        self.model_name = "gemma3:12b"


        if ram.available < 9 * 1024**3:
            print(f"There isn't enough ram to use {self.model_name}")
            print(f"You got: {ram.available / 1024**3:.2f} GB of {ram.total / 1024**3:.2f} GB free and you'll need at least 8.3 GB free")
            rs = input("Did you wanna force the Email_IA.py run anyway? (y/n): ")
            if rs != 'y':
                return
            
            
        self.categories = self._load_categories()
        self.max_iterations = 5
        self.tool_commands = {
            "GET_CATEGORIES": self.get_categories,
            "ADD_CATEGORY": self._add_category_tool,
            "GET_CATEGORY_INFO": self._get_category_info
        }

    def _load_categories(self):
        """Carica le categorie dal file JSON"""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Errore nel caricamento delle categorie: {e}")
            return {}

    def _save_categories(self):
        """Salva le categorie nel file JSON"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, indent=4)
        except Exception as e:
            logging.error(f"Errore nel salvataggio delle categorie: {e}")

    def get_categories(self):
        """Restituisce tutte le categorie esistenti"""
        return list(self.categories.keys())

    def add_category(self, category_name, description=""):
        """Aggiunge una nuova categoria"""
        if category_name not in self.categories:
            self.categories[category_name] = {
                "description": description,
                "created_at": datetime.now().isoformat()
            }
            self._save_categories()
            return True
        return False

    def _add_category_tool(self, *args):
        """Strumento per aggiungere una categoria"""
        if len(args) < 1:
            return "Errore: nome categoria mancante"
        category_name = args[0]
        description = args[1] if len(args) > 1 else ""
        if self.add_category(category_name, description):
            return f"Categoria '{category_name}' aggiunta con successo"
        return f"La categoria '{category_name}' esiste già"

    def _get_category_info(self, *args):
        """Strumento per ottenere informazioni su una categoria"""
        if len(args) < 1:
            return "Errore: nome categoria mancante"
        category_name = args[0]
        if category_name in self.categories:
            return self.categories[category_name]
        return f"La categoria '{category_name}' non esiste"

    def _run_model(self, prompt):
        """Esegue il modello con il prompt fornito e gestisce la risposta"""
        try:
            # Esegui il modello usando la libreria
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt
            )
            
            if not response or 'response' not in response:
                logging.error("Nessuna risposta valida dal modello")
                return None

            # Estrai la risposta effettiva
            response_text = response['response'].strip()
            
            # Rimuovi eventuali prefissi o suffissi non necessari
            response_text = response_text.replace("Risposta:", "").strip()
            
            return response_text

        except Exception as e:
            logging.error(f"Errore nell'esecuzione del modello: {e}")
            return None

    def categorize_email(self, email_data):
        """Categorizza un'email usando il modello in un loop interattivo"""
        conversation_history = []
        current_iteration = 0
        last_tool_result = None

        while current_iteration < self.max_iterations:
            # Prepara il prompt per il modello
            prompt = self._create_categorization_prompt(email_data, conversation_history, last_tool_result)
            
            # Esegui il modello e ottieni la risposta
            response = self._run_model(prompt)
            
            if not response:
                logging.error("Nessuna risposta dal modello")
                return None

            conversation_history.append({"role": "assistant", "content": response})

            # Verifica se la risposta è una chiamata a uno strumento
            if self._is_tool_call(response):
                tool_result = self._execute_tool_call(response)
                last_tool_result = tool_result
                conversation_history.append({
                    "role": "system", 
                    "content": f"Risultato dello strumento: {tool_result}"
                })
            else:
                # Verifica se è una categoria valida
                category = self._parse_model_response(response)
                if category:
                    if category not in self.categories:
                        self.add_category(category)
                    return category
                else:
                    # Se non è una categoria valida, informa il modello
                    conversation_history.append({
                        "role": "system",
                        "content": "La risposta non è una categoria valida. Per favore, fornisci SOLO il nome della categoria."
                    })

            current_iteration += 1

        logging.info("Raggiunto il numero massimo di iterazioni senza una categorizzazione definitiva")
        return None

    def _is_tool_call(self, response):
        """Verifica se la risposta è una chiamata a uno strumento"""
        return response.startswith("TOOL:")

    def _execute_tool_call(self, tool_call):
        """Esegue una chiamata a uno strumento"""
        try:
            # Rimuovi il prefisso "TOOL:"
            tool_call = tool_call[5:].strip()
            
            # Analizza la chiamata allo strumento
            parts = tool_call.split(":")
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if command in self.tool_commands:
                return self.tool_commands[command](*args)
            else:
                return f"Strumento sconosciuto: {command}. Strumenti disponibili: {', '.join(self.tool_commands.keys())}"
        except Exception as e:
            return f"Errore nell'esecuzione dello strumento: {e}"

    def _create_categorization_prompt(self, email_data, conversation_history, last_tool_result=None):
        """Creates the prompt for the model with tool support and few-shot examples"""
        categories = self.get_categories()
        
        # Build conversation history
        conversation_text = ""
        for msg in conversation_history:
            role = "Assistant" if msg["role"] == "assistant" else "System"
            conversation_text += f"{role}: {msg['content']}\n\n"

        # Few-shot examples
        few_shot_examples = """
Example 1:
System: Email to categorize:
From: amazon@orders.com
Subject: Your order #12345 has been shipped
Date: 2024-03-20
Content: Dear customer, your order #12345 has been shipped and will arrive in 2-3 business days.

Assistant: TOOL:GET_CATEGORIES
System: Tool result: ['Shopping', 'Work', 'Personal', 'Travel']

Assistant: TOOL:ADD_CATEGORY:Purchases:Emails related to online purchases
System: Tool result: Category 'Purchases' added successfully

Assistant: Purchases

Example 2:
System: Email to categorize:
From: meeting@company.com
Subject: Project meeting - 15:00
Date: 2024-03-20
Content: Hello team, reminder for today's project meeting at 15:00.

Assistant: TOOL:GET_CATEGORIES
System: Tool result: ['Shopping', 'Work', 'Personal', 'Travel', 'Purchases']

Assistant: Work
"""

        prompt = f"""You are an assistant specialized in email categorization.
Your task is to analyze emails and assign them the most appropriate category.

IMPORTANT: 
- The final response must be ONLY the category name
- Example of correct response: "Work"
- Do not include explanations or additional text
- Use the category "Other" if you are not sure about the category and you can't create a more specific one

AVAILABLE TOOLS:
1. GET_CATEGORIES
   - Description: Get all existing categories
   - Usage: TOOL:GET_CATEGORIES
   - Example: TOOL:GET_CATEGORIES

2. ADD_CATEGORY
   - Description: Add a new category
   - Usage: TOOL:ADD_CATEGORY:category_name:description
   - Example: TOOL:ADD_CATEGORY:Purchases:Emails related to online purchases

3. GET_CATEGORY_INFO
   - Description: Get information about a specific category
   - Usage: TOOL:GET_CATEGORY_INFO:category_name
   - Example: TOOL:GET_CATEGORY_INFO:Work

INTERACTION RULES:
1. To use a tool, start your response with "TOOL:" followed by the command
2. After using a tool, analyze the result and decide the next step
3. When you are sure about the category, respond ONLY with the category name

INTERACTION EXAMPLES:
{few_shot_examples}

EMAIL TO CATEGORIZE:
From: {email_data['sender']}
Subject: {email_data['subject']}
Date: {email_data['date']}
Content: {email_data['body']}

EXISTING CATEGORIES:
{', '.join(categories)}

CONVERSATION HISTORY:
{conversation_text}

{last_tool_result if last_tool_result else ''}

CATEGORIZATION PROCEDURE:
1. Analyze the email content
2. If needed, use GET_CATEGORIES to see available categories
3. If needed, use GET_CATEGORY_INFO for category details
4. If needed, use ADD_CATEGORY to create a new category
5. When sure, provide ONLY the category name

REMEMBER:
- Use tools when you need information
- The final response must be ONLY the category name
- If the category doesn't exist, it will be created automatically
"""
        return prompt

    def _parse_model_response(self, response):
        """Analizza la risposta del modello per estrarre la categoria"""
        # Se la risposta è una chiamata a uno strumento, non è una categoria
        if self._is_tool_call(response):
            return None
            
        # Rimuovi spazi e caratteri speciali
        category = response.strip()
        
        # Verifica che la categoria non sia vuota o troppo lunga
        if not category or len(category) > 100:
            return None
            
        # Verifica che la categoria non contenga caratteri speciali
        if not all(c.isalnum() or c.isspace() or c in '-_' for c in category):
            return None
            
        # Verifica che la categoria non sia una risposta generica
        generic_responses = ['ok', 'si', 'no', 'grazie', 'thanks', 'thank you', 'okay']
        if category.lower() in generic_responses:
            return None
            
        return category

    def close(self):
        """Chiude la connessione con il modello"""
        try:
            # Ferma il modello usando il comando da terminale
            subprocess.run(['ollama', 'stop', self.model_name], check=True)
            logging.info("Connessione con il modello chiusa correttamente")
        except Exception as e:
            logging.error(f"Errore durante la chiusura della connessione con il modello: {e}")

class GmailAuthenticator:
    def __init__(self):
        self.token_dir = os.environ.get('TOKEN_DIR', '.')
        self.token_path = os.path.join(self.token_dir, 'token.pickle')
        self.client_secret_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'google_credentials.json')

    def get_credentials(self):
        """Gestisce l'autenticazione e restituisce le credenziali Gmail"""
        creds = None
        
        # Controlla se esiste un token salvato
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # Se non ci sono credenziali valide, procedi con l'autenticazione
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.client_secret_path):
                    raise FileNotFoundError(f"File delle credenziali non trovato: {self.client_secret_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_path,
                    SCOPES)
                creds = flow.run_local_server(port=8080)

            # Salva le credenziali per la prossima esecuzione
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds

class ConfigManager:
    def __init__(self):
        self.config_path = os.environ.get('CONFIG_PATH', 'config.json')

    def load_config(self):
        """Carica la configurazione dal file config.json"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            logging.info(f"File di configurazione non trovato: {self.config_path}. Utilizzo configurazione predefinita.")
            return self._get_default_config()
        except json.JSONDecodeError:
            logging.info("Errore nel file di configurazione. Utilizzo configurazione predefinita.")
            return self._get_default_config()

    def _get_default_config(self):
        """Restituisce la configurazione predefinita"""
        return {
            "rules": {},
            "settings": {
                "max_emails_to_process": 50,
                "check_body": True,
                "body_extract_length": 1000
            }
        }

class GmailService:
    def __init__(self):
        self.authenticator = GmailAuthenticator()
        self.service = None
        self.categorizer = AICategorizer()

    def get_service(self):
        """Crea e restituisce il servizio Gmail autenticato"""
        if not self.service:
            creds = self.authenticator.get_credentials()
            self.service = build('gmail', 'v1', credentials=creds)
        return self.service

    def process_email(self, email_data):
        """Processa un'email e la categorizza"""
        # Ottieni la categoria usando il modello
        category = self.categorizer.categorize_email(email_data)
        
        if category:
            # Applica l'etichetta all'email
            self._apply_label(email_data['id'], category)
            return category
        return None

    def _apply_label(self, email_id, category):
        """Applica un'etichetta a un'email"""
        try:
            # Ottieni tutte le etichette esistenti
            labels_response = self.service.users().labels().list(userId='me').execute()
            labels = labels_response.get('labels', [])
            
            # Cerca l'ID dell'etichetta
            label_id = None
            for label_obj in labels:
                if label_obj['name'] == category:
                    label_id = label_obj['id']
                    break
            
            # Crea l'etichetta se non esiste
            if not label_id:
                created_label = self.service.users().labels().create(
                    userId='me',
                    body={'name': category}
                ).execute()
                label_id = created_label['id']

            # Applica l'etichetta all'email
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return True
        except Exception as e:
            logging.error(f"Errore nell'applicazione dell'etichetta: {e}")
            return False

def get_emails(service, max_results=50, include_body=True, body_length=1000):
    """Ottiene le email dalla casella di posta"""
    try:
        # Ottieni la lista delle email
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            logging.info('Nessuna email trovata.')
            return []

        logging.info(f"Recupero dettagli di {len(messages)} email...")
        emails = []
        for i, message in enumerate(messages):
            if i % 10 == 0 and i > 0:
                logging.info(f"Elaborate {i}/{len(messages)} email...")
            
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            # Controlla se l'email ha già delle etichette
            if 'labelIds' in msg and len(msg['labelIds']) > 0:
                # Ignora le etichette di sistema di Gmail
                system_labels = ['INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH', 'CATEGORY_PERSONAL', 
                               'CATEGORY_SOCIAL', 'CATEGORY_PROMOTIONS', 'CATEGORY_UPDATES', 
                               'CATEGORY_FORUMS', 'STARRED', 'IMPORTANT', 'UNREAD']
                custom_labels = [label for label in msg['labelIds'] if label not in system_labels]
                
                if custom_labels:
                    logging.info(f"Email {message['id']} già etichettata, ignorata")
                    continue

            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'Nessun oggetto')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Mittente sconosciuto')
            date_str = next((header['value'] for header in headers if header['name'] == 'Date'), '')
            
            # Estrai il corpo dell'email
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
    except Exception as e:
        logging.error(f"Errore nel recupero delle email: {e}")
        return []

def process_emails(service, emails, config):
    """Processa le email e le categorizza"""
    if not emails:
        logging.info("Nessuna email da processare.")
        return

    logging.info(f"Inizio elaborazione di {len(emails)} email...")
    categorized_count = 0
    skipped_count = 0
    gmail_service = GmailService()
    gmail_service.service = service

    # Crea la barra di caricamento
    with tqdm(total=len(emails), desc="Elaborazione email", unit="email") as pbar:
        for email in emails:
            # Verifica se l'email ha già delle etichette personalizzate
            msg = service.users().messages().get(userId='me', id=email['id']).execute()
            if 'labelIds' in msg:
                system_labels = ['INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH', 'CATEGORY_PERSONAL', 
                               'CATEGORY_SOCIAL', 'CATEGORY_PROMOTIONS', 'CATEGORY_UPDATES', 
                               'CATEGORY_FORUMS', 'STARRED', 'IMPORTANT', 'UNREAD']
                custom_labels = [label for label in msg['labelIds'] if label not in system_labels]
                
                if custom_labels:
                    pbar.set_postfix({"Stato": "Saltata", "Etichette": ', '.join(custom_labels)})
                    skipped_count += 1
                    pbar.update(1)
                    continue

            # Categorizza l'email
            category = gmail_service.process_email(email)
            
            if category:
                pbar.set_postfix({"Stato": "Categorizzata", "Categoria": category})
                categorized_count += 1
            else:
                pbar.set_postfix({"Stato": "Categorizzata", "Categoria": "Other"})
                # Applica l'etichetta "Other"
                gmail_service._apply_label(email['id'], "Other")
                categorized_count += 1
            
            pbar.update(1)

    logging.info(f"Elaborazione completata!")
    logging.info(f"Email categorizzate: {categorized_count}/{len(emails)}")
    logging.info(f"Email saltate (già etichettate): {skipped_count}")
    logging.info(f"Percentuale di successo: {(categorized_count/(len(emails)-skipped_count)*100):.1f}%")

def main():
    """Funzione principale dell'applicazione"""
    gmail_service = None
    try:
        print("\n🚀 Avvio Email Organizer IA v2.0")
        print("=" * 40)
        
        # Carica la configurazione
        config_manager = ConfigManager()
        config = config_manager.load_config()
        settings = config.get("settings", {})
        
        logging.info("Configurazione caricata con successo!")
        logging.info(f"Impostazioni: {settings}")
        
        # Inizializza il servizio Gmail
        gmail_service = GmailService()
        service = gmail_service.get_service()
        
        # Ottieni le email
        max_emails = settings.get("max_emails_to_process", 50)
        check_body = settings.get("check_body", True)
        body_length = settings.get("body_extract_length", 1000)
        
        logging.info(f"Recupero delle ultime {max_emails} email...")
        emails = get_emails(service, max_results=max_emails, include_body=check_body, body_length=body_length)
        
        if emails:
            # Processa le email
            process_emails(service, emails, config)
        else:
            logging.info("Nessuna email da processare.")

    except Exception as e:
        logging.error(f"Errore durante l'esecuzione: {e}")
        return 1
    finally:
        # Chiudi la connessione con il modello
        if gmail_service and gmail_service.categorizer:
            gmail_service.categorizer.close()

    return 0

if __name__ == '__main__':
    exit(main())
