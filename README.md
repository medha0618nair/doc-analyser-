# Insurance Brochure Processor API

This API processes insurance brochures in PDF format and extracts structured information including policy details, coverage, exclusions, and more.

## Features

- PDF processing and text extraction
- Structured information extraction
- Policy details analysis
- Coverage information extraction
- Exclusions and limitations identification
- Premium information extraction

## API Endpoints

- `GET /`: Welcome message and available endpoints
- `GET /health`: Health check endpoint
- `POST /process-brochure`: Process an insurance brochure PDF

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following settings:
   - Name: insurance-brochure-processor
   - Environment: Docker
   - Branch: main
   - Build Command: (leave empty, handled by Dockerfile)
   - Start Command: (leave empty, handled by Dockerfile)

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   uvicorn app:app --reload
   ```

## API Usage

1. Send a POST request to `/process-brochure` with a PDF file
2. The API will return structured information about the insurance brochure

Example curl command:

```bash
curl -X POST "http://localhost:8000/process-brochure" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/your/brochure.pdf"
```

## Dependencies

- FastAPI
- PyPDF2
- NLTK
- spaCy
- Python 3.9+
