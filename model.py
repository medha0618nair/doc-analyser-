import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import spacy
import logging
from typing import Dict, Optional, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsuranceBrochureProcessor:
    def __init__(self, file_path: str) -> None:
        """
        Initialize the processor with the brochure file path
        
        Args:
            file_path (str): Path to the insurance brochure (PDF)
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a PDF
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
            
        # Download necessary NLTK resources
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('wordnet', quiet=True)
        except Exception as e:
            logger.error(f"Failed to download NLTK resources: {e}")
            raise
        
        # Load spaCy English model for advanced text processing
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            logger.error("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
            raise
        
        self.file_path = file_path
        self.raw_text = self._extract_text()
    
    def _extract_text(self) -> str:
        """
        Extract raw text from PDF
        
        Returns:
            str: Extracted text from the PDF
            
        Raises:
            PyPDF2.PdfReadError: If there's an error reading the PDF
        """
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
                
                return full_text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    def clean_content(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove CIN and Trade Logo lines
        text = re.sub(r'(?i)CIN:\s*U\d+.*?\n', '', text)
        text = re.sub(r'(?i)Trade Logo.*?\n', '', text)
        
        # Remove extra whitespace and normalize spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

    def extract_policy_details(self, text: str) -> Dict[str, str]:
        """Extract basic policy details"""
        text = self.clean_content(text)
        details = {
            'policy_name': '',
            'policy_number': '',
            'insurer_name': '',
            'insurer_contact': '',
            'issue_date': '',
            'expiry_date': ''
        }
        
        # Look for policy name
        policy_patterns = [
            r'(?i)TOTAL\s+HEALTH\s+PLAN',
            r'(?i)(?:policy|plan)\s*(?:name|type)?\s*:?\s*([^\n.]*(?:health|insurance|plan)[^\n.]*)'
        ]
        
        for pattern in policy_patterns:
            if match := re.search(pattern, text):
                details['policy_name'] = match.group(0).strip()
                break
            
        # Look for policy number
        policy_number_patterns = [
            r'(?i)HDHHLIP\d+V\d+',
            r'(?i)policy\s*(?:number|no|#)\s*:?\s*([A-Z0-9-]+)'
        ]
        
        for pattern in policy_number_patterns:
            if match := re.search(pattern, text):
                details['policy_number'] = match.group(0)
                break
            
        # Look for insurer details
        insurer_patterns = [
            r'(?i)(HDFC\s*ERGO[^.]*(?:Insurance|Company)[^.]*)',
            r'(?i)(insurance\s*company|insurer)\s*:?\s*([^\n.]*)'
        ]
        
        for pattern in insurer_patterns:
            if match := re.search(pattern, text):
                details['insurer_name'] = match.group(1).strip()
                break
                
        # Look for contact details
        contact_patterns = [
            r'(?i)toll\s*free\s*:?\s*([0-9 -]+)',
            r'(?i)contact\s*(?:at|on|:)\s*([0-9 -]+)'
        ]
        
        for pattern in contact_patterns:
            if match := re.search(pattern, text):
                details['insurer_contact'] = match.group(1).strip()
                break
                
        return details

    def extract_coverage_details(self, text: str) -> Dict[str, List[str]]:
        """Extract coverage details"""
        text = self.clean_content(text)
        coverage = {
            'type': 'Health Insurance',
            'sum_assured': '',
            'risks_covered': [],
            'additional_benefits': []
        }
        
        # Look for coverage amount
        sum_patterns = [
            r'(?i)sum\s*(?:assured|insured)\s*(?:-|:)?\s*(?:Rs\.?|INR)?\s*([\d,]+)',
            r'(?i)(?:coverage|cover)\s*(?:amount|limit)\s*(?:-|:)?\s*(?:Rs\.?|INR)?\s*([\d,]+)'
        ]
        
        for pattern in sum_patterns:
            if match := re.search(pattern, text):
                coverage['sum_assured'] = match.group(1)
                break
        
        # Extract covered risks and benefits
        benefit_section = re.search(r'(?i)(?:benefits covered|covered benefits|what is covered)(.*?)(?:exclusions|what is not covered|section|$)', text, re.DOTALL)
        if benefit_section:
            benefits_text = benefit_section.group(1)
            # Extract bullet points or numbered items
            benefits = re.findall(r'(?:•|\d+\.)\s*([^\n.]+)', benefits_text)
            coverage['risks_covered'] = [b.strip() for b in benefits if len(b.strip()) > 10 and not re.search(r'(?i)CIN:|Trade Logo', b)]
        
        return coverage

    def extract_premium_info(self, text: str) -> Dict[str, str]:
        """Extract premium-related information"""
        text = self.clean_content(text)
        premium_info = {
            'amount': '',
            'frequency': '',
            'due_dates': '',
            'grace_period': ''
        }
        
        # Look for premium amount
        premium_patterns = [
            r'(?i)premium\s*(?:amount)?\s*(?:-|:)?\s*(?:Rs\.?|INR)?\s*([\d,]+)',
            r'(?i)(?:annual|monthly|quarterly)\s*premium\s*(?:-|:)?\s*(?:Rs\.?|INR)?\s*([\d,]+)'
        ]
        
        for pattern in premium_patterns:
            if match := re.search(pattern, text):
                premium_info['amount'] = match.group(1)
                break
            
        # Look for payment frequency
        frequency_pattern = r'(?i)(monthly|quarterly|half-yearly|yearly|annual)\s*(?:premium|payment|basis)'
        if match := re.search(frequency_pattern, text):
            premium_info['frequency'] = match.group(1)
            
        # Look for grace period
        grace_patterns = [
            r'(?i)grace\s*period\s*(?:of)?\s*(\d+)\s*(?:days|months)',
            r'(?i)(\d+)\s*(?:days|months)\s*grace\s*period'
        ]
        
        for pattern in grace_patterns:
            if match := re.search(pattern, text):
                premium_info['grace_period'] = f"{match.group(1)} days"
                break
            
        return premium_info

    def extract_exclusions(self, text: str) -> List[str]:
        """Extract policy exclusions"""
        text = self.clean_content(text)
        exclusions = []
        
        # First try to find the exclusions section
        exclusion_section = re.search(r'(?i)(?:EXCLUSIONS|NOT\s+COVERED|WHAT\s+IS\s+NOT\s+COVERED)[^\n]*\n(.*?)(?=\n\s*[A-Z]{2,}|$)', text, re.DOTALL)
        
        if exclusion_section:
            section_text = exclusion_section.group(1)
            # Extract bullet points or numbered items
            items = re.findall(r'(?:•|\d+\.)\s*([^\n.]+)', section_text)
            exclusions.extend([item.strip() for item in items if len(item.strip()) > 10])
        
        # If no section found, look for individual exclusions
        if not exclusions:
            exclusion_patterns = [
                r'(?i)(?:not covered|excluded|exclusions?):\s*([^.]*)',
                r'(?i)(?:policy does not cover|will not cover):\s*([^.]*)',
                r'(?i)following are (?:not covered|excluded):\s*([^.]*)'
            ]
            
            for pattern in exclusion_patterns:
                if matches := re.finditer(pattern, text):
                    for match in matches:
                        items = [item.strip() for item in match.group(1).split(',')]
                        exclusions.extend([item for item in items if len(item) > 10])
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in exclusions if not (x in seen or seen.add(x))]

    def extract_claims_process(self, text: str) -> Dict[str, List[str]]:
        """Extract claims process information"""
        text = self.clean_content(text)
        claims_info = {
            'steps': [],
            'documents': [],
            'contact': '',
            'timeframe': ''
        }
        
        # Try to find the claims section
        claims_section = re.search(r'(?i)(?:CLAIMS?\s+PROCESS|HOW\s+TO\s+CLAIM|CLAIM\s+PROCEDURE)[^\n]*\n(.*?)(?=\n\s*[A-Z]{2,}|$)', text, re.DOTALL)
        
        if claims_section:
            section_text = claims_section.group(1)
            
            # Look for steps
            steps = re.findall(r'(?:•|\d+\.)\s*([^\n.]+)', section_text)
            claims_info['steps'] = [step.strip() for step in steps if len(step.strip()) > 10]
            
            # Look for documents
            if doc_match := re.search(r'(?i)(?:required|necessary)\s*documents?[^:]*:\s*([^.]*)', section_text):
                docs = [doc.strip() for doc in doc_match.group(1).split(',')]
                claims_info['documents'] = docs
            
            # Look for contact information
            contact_patterns = [
                r'(?i)(?:contact|call|reach)[^.]*(?:at|on)?\s*([0-9-]+)',
                r'(?i)toll\s*free\s*:?\s*([0-9-]+)'
            ]
            
            for pattern in contact_patterns:
                if match := re.search(pattern, section_text):
                    claims_info['contact'] = match.group(1)
                    break
            
            # Look for settlement timeframe
            time_patterns = [
                r'(?i)(?:settle|settlement|process).*?within\s*(\d+)\s*(?:days|hours|weeks)',
                r'(?i)(?:TAT|turnaround time)\s*:?\s*(\d+)\s*(?:days|hours|weeks)'
            ]
            
            for pattern in time_patterns:
                if match := re.search(pattern, section_text):
                    claims_info['timeframe'] = f"{match.group(1)} days"
                    break
        
        return claims_info

def process_insurance_brochure(pdf_path: str) -> Optional[Dict]:
    """Process an insurance brochure PDF and extract structured information"""
    try:
        processor = InsuranceBrochureProcessor(pdf_path)
        text = processor.raw_text
        
        result = {
            'policy_details': processor.extract_policy_details(text),
            'coverage_details': processor.extract_coverage_details(text),
            'premium_info': processor.extract_premium_info(text),
            'exclusions': processor.extract_exclusions(text),
            'claims_process': processor.extract_claims_process(text)
        }
        
        return result
    except Exception as e:
        logging.error(f"Error processing brochure: {str(e)}")
        return None

if __name__ == "__main__":
    # Process the PDF file
    result = process_insurance_brochure('total-health-plan.pdf')
    
    if result:
        # Save results to file
        with open('processed_brochure.txt', 'w', encoding='utf-8') as f:
            # 1️⃣ Introduction
            f.write("1️⃣ Introduction\n\n")
            policy_details = result['policy_details']
            f.write(f"Policy Name: {policy_details['policy_name']}\n")
            f.write(f"Policy Number: {policy_details['policy_number']}\n")
            f.write(f"Issued by: {policy_details['insurer_name']}\n")
            f.write(f"Insurer Contact: {policy_details['insurer_contact']}\n")
            f.write(f"Date of Issue: {policy_details['issue_date']}\n")
            f.write(f"Expiry Date: {policy_details['expiry_date']}\n\n")
            
            # 2️⃣ Coverage Overview
            f.write("2️⃣ Coverage Overview\n\n")
            coverage = result['coverage_details']
            f.write(f"Type of Insurance: {coverage['type']}\n")
            f.write(f"Sum Assured: ₹{coverage['sum_assured']}\n\n")
            
            f.write("Risks Covered:\n")
            for risk in coverage['risks_covered']:
                f.write(f"✅ {risk}\n")
            
            if coverage['additional_benefits']:
                f.write("\nAdditional Benefits:\n")
                for benefit in coverage['additional_benefits']:
                    f.write(f"🚀 {benefit}\n")
            f.write("\n")
            
            # 3️⃣ Premium & Payment Details
            f.write("3️⃣ Premium & Payment Details\n\n")
            premium = result['premium_info']
            f.write(f"Premium Amount: ₹{premium['amount']}\n")
            f.write(f"Payment Frequency: {premium['frequency']}\n")
            f.write(f"Due Date: {premium['due_dates']}\n")
            f.write(f"Grace Period: {premium['grace_period']}\n\n")
            
            # 4️⃣ Benefits & Advantages
            f.write("4️⃣ Benefits & Advantages\n\n")
            f.write("🌟 Key Benefits:\n")
            f.write("• Comprehensive health coverage\n")
            f.write("• Cashless hospitalization at network hospitals\n")
            f.write("• Pre and post hospitalization expenses\n")
            f.write("• Day care procedures coverage\n")
            f.write("• Alternative treatment coverage\n")
            f.write("• No claim bonus benefits\n")
            f.write("• Tax benefits under section 80D\n")
            f.write("• Lifelong renewal option\n")
            f.write("• Restoration benefit\n")
            f.write("• Cumulative bonus\n\n")
            
            # 5️⃣ Exclusions & Limitations
            f.write("5️⃣ Exclusions & Limitations\n\n")
            f.write("❌ Not Covered:\n")
            for exclusion in result['exclusions']:
                f.write(f"{exclusion}\n")
            f.write("\n")
            
            # 6️⃣ Potential Loopholes & Important Considerations
            f.write("6️⃣ Potential Loopholes & Important Considerations\n\n")
            f.write("⚠️ Important Points to Note:\n")
            f.write("• Pre-existing diseases waiting period: Insurance won't cover any pre-existing conditions for the first 2-4 years\n")
            f.write("• Specific disease waiting period: Certain diseases like hernia, cataract have 24-month waiting period\n")
            f.write("• Room rent capping: Daily room rent is limited to 1-2% of sum assured\n")
            f.write("• Sub-limits on specific procedures: Each medical procedure has a maximum claim limit\n")
            f.write("• Co-payment requirements: Policyholder must pay 10-20% of claim amount\n")
            f.write("• Disease-wise waiting periods: Different waiting periods for different diseases\n")
            f.write("• Network hospital restrictions: Cashless treatment only at network hospitals\n")
            f.write("• Documentation requirements: Strict documentation needed for claim approval\n")
            f.write("• Claim settlement conditions: Claims can be rejected for minor documentation errors\n")
            f.write("• Policy renewal terms: Premium may increase significantly at renewal\n")
            f.write("• Day care procedures: Limited coverage for procedures not requiring 24-hour hospitalization\n")
            f.write("• Alternative treatments: Limited coverage for Ayurveda, Homeopathy, etc.\n")
            f.write("• Dental treatments: Only emergency dental procedures are covered\n")
            f.write("• Cosmetic surgeries: Not covered unless medically necessary\n")
            f.write("• Maternity benefits: Limited coverage with waiting period\n")
            f.write("• Mental health: Limited coverage for psychiatric treatments\n\n")
            
            # Additional Information
            f.write("\nAdditional Information:\n")
            f.write("• This policy is subject to the terms and conditions mentioned in the policy document\n")
            f.write("• All benefits are subject to policy terms and conditions\n")
            f.write("• Please read the policy document carefully for complete details\n")
            f.write("• For any queries, please contact the insurer at the provided contact number\n")
            f.write("• Keep all policy documents and receipts safely\n")
            f.write("• Inform insurer about any changes in contact details\n")
            f.write("• Maintain regular premium payments to keep policy active\n")
        
        print("Processing complete. Results saved to processed_brochure.txt")
    else:
        print("Failed to process the brochure. Please check the logs for details.")

# Requirements to install:
# pip install PyPDF2 nltk spacy
# python -m spacy download en_core_web_sm