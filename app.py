from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import process_insurance_brochure
import tempfile
import os
from typing import Dict, Optional

app = FastAPI(
    title="Insurance Brochure Processor API",
    description="API to process insurance brochures and extract structured information",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Insurance Brochure Processor API",
        "endpoints": {
            "/process-brochure": "POST - Process an insurance brochure PDF",
            "/health": "GET - Check API health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/process-brochure")
async def process_brochure(file: UploadFile = File(...)) -> Dict:
    """
    Process an insurance brochure PDF and return structured information
    
    Args:
        file: PDF file containing the insurance brochure
        
    Returns:
        Dict containing processed information
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the brochure
        result = process_insurance_brochure(temp_file_path)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to process the brochure")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 