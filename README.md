# Document Automation

A web application that extracts data from passport and G-28 forms using AI vision and automatically populates web forms using browser automation.

## Features

- **Document Upload**: Upload passport and G-28 forms (PDF or images)
- **AI-Powered Extraction**: Uses AI vision to extract structured data from documents
- **Multiple Extraction Providers**: Choose from Anthropic Claude, Ollama Vision models, or OCR + Ollama text models
- **Data Review**: Review and edit extracted data before form submission
- **Browser Automation**: Automatically fills web forms using Playwright
- **Screenshot Capture**: Captures screenshots of filled forms for verification

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Vite
- **AI Extraction**: Configurable providers:
  - Anthropic Claude API (vision) - default
  - Ollama with vision models (LLaVA, Qwen-VL)
  - OCR + Ollama text models (NuMarkdown-8B, Mistral, etc.)
- **Browser Automation**: Playwright

## Project Structure

```
document-automation/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── routers/
│   │   │   ├── upload.py        # Document upload endpoints
│   │   │   └── automation.py    # Form filling endpoints
│   │   ├── services/
│   │   │   ├── extractor.py     # Claude API extraction
│   │   │   └── form_filler.py   # Playwright automation
│   │   └── schemas/
│   │       └── documents.py     # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── ExtractedData.tsx
│   │   │   └── FormFiller.tsx
│   │   └── api/
│   │       └── client.ts
│   └── package.json
└── .env.example
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Poppler (for PDF processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sreekanth489/document-automation.git
   cd document-automation
   ```

2. **Install Poppler (macOS)**
   ```bash
   brew install poppler
   ```

3. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Configure Environment**
   ```bash
   cp .env.example backend/.env
   # Edit backend/.env - see "Extraction Providers" section below
   ```

## Extraction Providers

The application supports three extraction providers. Configure via `EXTRACTION_PROVIDER` in your `.env` file.

### 1. Anthropic Claude (Default)

Uses Claude's vision API for highest accuracy. Requires an API key.

```env
EXTRACTION_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### 2. Ollama Vision Models

Uses local vision-capable models via Ollama. Free and runs locally.

```bash
# Install Ollama and pull a vision model
ollama pull llava:13b
# or: ollama pull qwen-vl, bakllava, etc.
```

```env
EXTRACTION_PROVIDER=ollama_vision
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_VISION_MODEL=llava:13b
```

### 3. OCR + Ollama Text Models

Uses OCR (EasyOCR/Tesseract) for text extraction, then a text LLM for structuring. Most cost-effective option.

```bash
# Install Ollama and pull a text model
ollama pull numind/numarkdown-8b-thinking
# or: ollama pull llama3.1:8b, mistral, etc.
```

```env
EXTRACTION_PROVIDER=ollama_ocr
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TEXT_MODEL=numind/numarkdown-8b-thinking
OCR_ENGINE=easyocr
OCR_LANGUAGES=en
```

### Check Provider Status

Once the backend is running, check provider availability:
```bash
curl http://localhost:8000/api/provider-status
```

## Running the Application

1. **Start Backend** (Terminal 1)
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

## Usage

1. Open http://localhost:5173 in your browser
2. Upload a passport image/PDF and/or G-28 form
3. Wait for AI extraction to complete
4. Review and edit the extracted data if needed
5. Click "Fill Form" to automatically populate the target form
6. View the screenshot of the filled form

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload documents for extraction |
| `/api/extract/{session_id}` | GET | Get extracted data by session |
| `/api/fill-form` | POST | Fill form with extracted data |
| `/api/screenshot/{filename}` | GET | Get form screenshot |
| `/api/provider-status` | GET | Check extraction provider status |

## Extracted Data

### From Passport
- Full name (last, first, middle)
- Passport number
- Country of issue
- Nationality
- Date of birth
- Place of birth
- Sex
- Issue and expiration dates

### From G-28 Form
- Attorney name
- Address (street, city, state, ZIP, country)
- Contact information (phone, email)
- Bar number and licensing authority
- Law firm name

## License

MIT
