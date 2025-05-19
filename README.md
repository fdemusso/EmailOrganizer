# Email Organizer

A Python application to automatically organize Gmail emails into custom categories. Available in two versions: with and without artificial intelligence.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Gmail API](https://img.shields.io/badge/Gmail-API-red.svg)
![Ollama](https://img.shields.io/badge/Ollama-Gemma3:12b-orange.svg)

## 📋 Overview

Email Organizer is an application that helps you keep your Gmail inbox automatically organized. It's available in two versions:

### 🤖 AI Version (Email_IA.py)
Uses artificial intelligence (Gemma 3 12B model from Ollama) to analyze email content and categorize it intelligently. Ideal for those who want more sophisticated and adaptive categorization.

### 📝 Standard Version (Email_NoIA.py)
Uses predefined rules based on keywords to categorize emails. Lighter and faster, ideal for those who prefer more direct control over categorization.

## ✨ Features

### Common to Both Versions
- Gmail API Integration
- Custom Label System
- Flexible Configuration
- Detailed Logging
- Docker Support

### AI Version Specific
- AI-based Categorization
- Continuous Learning
- Semantic Content Analysis
- Automatic Category Management

### Standard Version Specific
- Rule-based Categorization
- Precise Category Control
- Optimized Performance
- No External AI Dependencies

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- Gmail Account
- Google API Credentials
- Docker (optional)

### Google Cloud Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download the `google_credentials.json` file

### Docker Installation (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/tuousername/email-organizer.git
cd email-organizer
```

2. Choose the version to use:
   - For AI version: `cd IA`
   - For Standard version: `cd No_IA`

3. Place configuration files:
   - `google_credentials.json`
   - `config.json`

4. Start the application:
```bash
docker-compose up --build
```

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/tuousername/email-organizer.git
cd email-organizer
```

2. Choose the version to use:
   - For AI version: `cd IA`
   - For Standard version: `cd No_IA`

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. For AI version, install Ollama:
   - Follow instructions at [ollama.com](https://ollama.com)

6. Place configuration files:
   - `google_credentials.json`
   - `config.json`

7. Run the application:
```bash
# For AI version
python Email_IA.py

# For Standard version
python Email_NoIA.py
```

## 📁 Project Structure

```
email-organizer/
├── IA/                    # AI Version
│   ├── Email_IA.py
│   ├── categories.json
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
│
├── No_IA/                 # Standard Version
│   ├── Email_NoIA.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
│
└── README.md             # This file
```

## ⚙️ Configuration

### config.json File
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

## 📊 Usage

1. On first run, a browser will open for Google authentication
2. The application will start processing uncategorized emails
3. Emails will be automatically categorized and labeled in Gmail

## 🔍 Version Differences

| Feature | AI Version | Standard Version |
|---------|------------|------------------|
| Categorization | AI-based | Predefined rules |
| Performance | Slower | Faster |
| Resources | Higher | Lower |
| Flexibility | High | Medium |
| Control | Low | High |

## 🤝 Contributing

Contributions are welcome! Please read the contribution guidelines before submitting a pull request.

## 📝 License

This project is distributed under the MIT License. See the `LICENSE` file for more details.

## 🙏 Acknowledgments

- Google for the Gmail API
- Ollama for the Gemma 3 12B model
- All project contributors 