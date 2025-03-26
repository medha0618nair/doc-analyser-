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
        
        # Format the response using actual extracted data
        formatted_response = {
            "content": {
                "1️⃣ Introduction": {
                    "Policy Name": result['policy_details'].get('policy_name', 'Not found'),
                    "Policy Number": result['policy_details'].get('policy_number', 'Not found'),
                    "Issued by": result['policy_details'].get('insurer_name', 'Not found'),
                    "Insurer Contact": result['policy_details'].get('insurer_contact', 'Not found'),
                    "Date of Issue": result['policy_details'].get('issue_date', 'Not found'),
                    "Expiry Date": result['policy_details'].get('expiry_date', 'Not found')
                },
                "2️⃣ Coverage Overview": {
                    "Type of Insurance": result['coverage_details'].get('type', 'Not found'),
                    "Sum Assured": f"₹{result['coverage_details'].get('sum_assured', 'Not found')}",
                    "Risks Covered": [f"✅ {risk}" for risk in result['coverage_details'].get('risks_covered', [])],
                    "Additional Benefits": [f"🚀 {benefit}" for benefit in result['coverage_details'].get('additional_benefits', [])]
                },
                "3️⃣ Premium & Payment Details": {
                    "Premium Amount": f"₹{result['premium_info'].get('amount', 'Not found')}",
                    "Payment Frequency": result['premium_info'].get('frequency', 'Not found'),
                    "Due Date": result['premium_info'].get('due_dates', 'Not found'),
                    "Grace Period": result['premium_info'].get('grace_period', 'Not found')
                },
                "4️⃣ Benefits & Advantages": {
                    "Key Benefits": [f"🌟 {benefit}" for benefit in result['coverage_details'].get('additional_benefits', [])]
                },
                "5️⃣ Exclusions & Limitations": {
                    "Not Covered": [f"❌ {exclusion}" for exclusion in result.get('exclusions', [])]
                },
                "6️⃣ Potential Loopholes & Important Considerations": {
                    "Important Points to Note": [
                        f"⚠️ {point}" for point in result.get('loopholes', [])
                    ]
                }
            },
            "additional_information": [
                "This policy is subject to the terms and conditions mentioned in the policy document",
                "All benefits are subject to policy terms and conditions",
                "Please read the policy document carefully for complete details",
                "For any queries, please contact the insurer at the provided contact number",
                "Keep all policy documents and receipts safely",
                "Inform insurer about any changes in contact details",
                "Maintain regular premium payments to keep policy active"
            ]
        }
        
        return formatted_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 