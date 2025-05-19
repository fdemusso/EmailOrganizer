# Email Organizer Standard

A Python application that uses predefined rules to automatically organize Gmail emails into custom categories.

## Features

- Gmail API Integration
- Rule-based email categorization
- Custom label system
- Configurable rules
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
    "rules": {
        "Work": ["meeting", "project", "deadline"],
        "Personal": ["family", "friends", "vacation"],
        "Shopping": ["order", "invoice", "confirmation"]
    },
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
git clone <repository-url>
cd email-organizer/No_IA
```

2. Place configuration files:
   - `google_credentials.json` in the No_IA directory
   - `config.json` in the No_IA directory

3. Start the application:
```bash
docker-compose up --build
```

### Method 2: Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd email-organizer/No_IA
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

4. Place configuration files:
   - `google_credentials.json` in the No_IA directory
   - `config.json` in the No_IA directory

5. Run the application:
```bash
python Email_NoIA.py
```

## Usage

1. On first run, a browser will open for Google authentication
2. The application will start processing uncategorized emails
3. Emails will be automatically categorized and labeled in Gmail based on the defined rules

## Project Structure

```
No_IA/
├── Email_NoIA.py
├── tokens/
├── config.json
├── google_credentials.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Logging

Logs are saved in the `email_organizer.log` file in the No_IA directory.

## Notes

- The application uses predefined rules for categorization
- OAuth credentials are saved in `tokens/token.pickle`
- Rules are defined in `config.json`

## License

Apache License 2.0 