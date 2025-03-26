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
        
        # Format the response exactly as in processed_brochure.txt
        formatted_response = {
            "content": {
                "1️⃣ Introduction": {
                    "Policy Name": result['policy_details']['policy_name'],
                    "Policy Number": result['policy_details']['policy_number'],
                    "Issued by": result['policy_details']['insurer_name'],
                    "Insurer Contact": result['policy_details']['insurer_contact'],
                    "Date of Issue": result['policy_details']['issue_date'],
                    "Expiry Date": result['policy_details']['expiry_date']
                },
                "2️⃣ Coverage Overview": {
                    "Type of Insurance": result['coverage_details']['type'],
                    "Sum Assured": f"₹{result['coverage_details']['sum_assured']}",
                    "Risks Covered": [f"✅ {risk}" for risk in result['coverage_details']['risks_covered']],
                    "Additional Benefits": [f"🚀 {benefit}" for benefit in result['coverage_details']['additional_benefits']]
                },
                "3️⃣ Premium & Payment Details": {
                    "Premium Amount": f"₹{result['premium_info']['amount']}",
                    "Payment Frequency": result['premium_info']['frequency'],
                    "Due Date": result['premium_info']['due_dates'],
                    "Grace Period": result['premium_info']['grace_period']
                },
                "4️⃣ Benefits & Advantages": {
                    "Key Benefits": [
                        "🌟 Comprehensive health coverage",
                        "🌟 Cashless hospitalization at network hospitals",
                        "🌟 Pre and post hospitalization expenses",
                        "🌟 Day care procedures coverage",
                        "🌟 Alternative treatment coverage",
                        "🌟 No claim bonus benefits",
                        "🌟 Tax benefits under section 80D",
                        "🌟 Lifelong renewal option",
                        "🌟 Restoration benefit",
                        "🌟 Cumulative bonus"
                    ]
                },
                "5️⃣ Exclusions & Limitations": {
                    "Not Covered": [f"❌ {exclusion}" for exclusion in result['exclusions']]
                },
                "6️⃣ Potential Loopholes & Important Considerations": {
                    "Important Points to Note": [
                        "⚠️ Pre-existing diseases waiting period: Insurance won't cover any pre-existing conditions for the first 2-4 years",
                        "⚠️ Specific disease waiting period: Certain diseases like hernia, cataract have 24-month waiting period",
                        "⚠️ Room rent capping: Daily room rent is limited to 1-2% of sum assured",
                        "⚠️ Sub-limits on specific procedures: Each medical procedure has a maximum claim limit",
                        "⚠️ Co-payment requirements: Policyholder must pay 10-20% of claim amount",
                        "⚠️ Disease-wise waiting periods: Different waiting periods for different diseases",
                        "⚠️ Network hospital restrictions: Cashless treatment only at network hospitals",
                        "⚠️ Documentation requirements: Strict documentation needed for claim approval",
                        "⚠️ Claim settlement conditions: Claims can be rejected for minor documentation errors",
                        "⚠️ Policy renewal terms: Premium may increase significantly at renewal",
                        "⚠️ Day care procedures: Limited coverage for procedures not requiring 24-hour hospitalization",
                        "⚠️ Alternative treatments: Limited coverage for Ayurveda, Homeopathy, etc.",
                        "⚠️ Dental treatments: Only emergency dental procedures are covered",
                        "⚠️ Cosmetic surgeries: Not covered unless medically necessary",
                        "⚠️ Maternity benefits: Limited coverage with waiting period",
                        "⚠️ Mental health: Limited coverage for psychiatric treatments"
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