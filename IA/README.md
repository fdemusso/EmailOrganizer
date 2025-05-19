# Email Organizer AI

A Python application that uses artificial intelligence to automatically organize Gmail emails into custom categories.

## Features

- Gmail API Integration
- Automatic email categorization using Ollama (Gemma 3 12B model)
- Custom label system
- Configurable category management
- Detailed operation logging

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- Gmail Account
- Google API Credentials (google_credentials.json)

## Configuration

1. Get Google API Credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download the `google_credentials.json` file

2. Create the `config.json` file:
```json
{
    "rules": {},
    "settings": {
        "max_emails_to_process": 50,
        "check_body": true,
        "body_extract_length": 1000
    }
}
```

## Installation

### Method 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/tuousername/email-organizer.git](https://github.com/fdemusso/EmailOrganizer.git
cd email-organizer/IA
```

2. Place configuration files:
   - `google_credentials.json` in the IA directory
   - `config.json` in the IA directory

3. Start the application:
```bash
docker-compose up --build
```

### Method 2: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/tuousername/email-organizer.git](https://github.com/fdemusso/EmailOrganizer.git
cd email-organizer/IA
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Ollama:
   - Follow instructions at [ollama.com](https://ollama.com)

5. Place configuration files:
   - `google_credentials.json` in the IA directory
   - `config.json` in the IA directory

6. Run the application:
```bash
python Email_IA.py
```

## Usage

1. On first run, a browser will open for Google authentication
2. The application will start processing uncategorized emails
3. Emails will be automatically categorized and labeled in Gmail

## Project Structure

```
IA/
├── Email_IA.py
├── categories.json
├── tokens/
├── config.json
├── google_credentials.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Logging

Logs are saved in the `email_organizer.log` file in the IA directory.

## Notes

- The application uses the Gemma 3 12B model from Ollama for categorization
- OAuth credentials are saved in `tokens/token.pickle`
- Categories are saved in `categories.json`

## License

Apache License 2.0 
