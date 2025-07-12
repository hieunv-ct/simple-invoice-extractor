# simple-invoice-extractor

A simple demonstration of AI-powered Vietnamese invoice data extraction using OpenAI's GPT-4 Vision API.

## 🎯 Purpose

This project demonstrates how to:
- Extract structured data from Vietnamese invoices (VAT/GTGT)
- Process both image and PDF formats
- Use GPT-4 Vision API for optical character recognition
- Handle Vietnamese text encoding properly
- Structure and export extracted data

## ✨ Features

- **Multi-format Support**: PDF, PNG, JPG, JPEG
- **AI-Powered Extraction**: GPT-4 Vision API
- **Vietnamese Text Processing**: Proper encoding and recognition
- **Structured Output**: JSON and CSV export
- **Educational Focus**: Clean, documented code

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd simple-invoice-extractor
pip install -r requirements.txt
```

### 2. Configurate API Key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run the Application
```bash
streamlit run app.py
```

## 📋 Usage
- Upload Invoice: Choose a Vietnamese invoice file (PDF or image)
- Extract Data: Click "Extract Data with AI" button
- Review Results: View structured data in the interface
- Export: Download extracted data as JSON or CSV

## 🏗️ Architecture
```
app.py                 # Streamlit interface
├── InvoiceProcessor   # Core extraction logic
├── AI Prompts         # Vietnamese-specific prompts
├── Utils              # Display and export functions
└── Examples           # Sample invoices and outputs
```

## 🔧 Configuration
Required Environment Variables
- OPENAI_API_KEY: Your OpenAI API key

Optional Configuration
- OPENAI_API_BASE_URL: Custom OpenAI endpoint (for Azure OpenAI)

📊 Data Structure
The extractor returns structured JSON with:
```json
{
  "company_info": {
    "seller_name": "...",
    "seller_tax_code": "...",
    "buyer_name": "..."
  },
  "invoice_details": {
    "invoice_number": "...",
    "invoice_date": "...",
    "serial": "..."
  },
  "financial_info": {
    "total_amount_before_tax": 0,
    "vat_rate": 10,
    "total_amount_after_tax": 0
  },
  "items": [...]
}
```

## 🛠️ Customization
Modifying Extraction Fields
Edit src/prompts.py to change the JSON structure:

```python
VIETNAMESE_INVOICE_PROCESSOR_PROMPT = """
        Extract these fields:
        {
        "custom_field": "...",
        ...
        }
    """
```

