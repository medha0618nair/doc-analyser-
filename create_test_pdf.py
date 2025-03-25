from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    c = canvas.Canvas("test_brochure.pdf", pagesize=letter)
    
    # Set font and size
    c.setFont("Helvetica", 12)
    
    # Add content
    content = [
        "Insurance Policy Overview",
        "",
        "This insurance policy provides comprehensive coverage for your needs.",
        "",
        "Key Benefits:",
        "1. Medical Coverage",
        "   - Hospitalization expenses",
        "   - Outpatient treatment",
        "   - Prescription medications",
        "",
        "2. Life Insurance",
        "   - Death benefit",
        "   - Accidental death coverage",
        "   - Critical illness coverage",
        "",
        "3. Additional Benefits",
        "   - Dental coverage",
        "   - Vision care",
        "   - Mental health services",
        "",
        "Terms and Conditions:",
        "- Policy term: 1 year",
        "- Premium payment: Monthly",
        "- Deductible: $500",
        "- Co-pay: 20%",
        "",
        "For more information, please contact our customer service."
    ]
    
    # Position for text
    y = 750  # Starting y position
    
    # Write content
    for line in content:
        if y < 50:  # If we're near the bottom of the page
            c.showPage()  # Start a new page
            c.setFont("Helvetica", 12)
            y = 750  # Reset y position
        c.drawString(50, y, line)
        y -= 15  # Move down for next line
    
    c.save()

if __name__ == "__main__":
    create_test_pdf() 