import sys
import os

# Ensure we're running in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import STUDENTS_DB, generate_certificate_pdf

if __name__ == "__main__":
    test_enrollment = "A60205225120"
    if test_enrollment in STUDENTS_DB:
        print("Student found in DB.")
    else:
        print("Student not found.")
        sys.exit(1)
    
    name = STUDENTS_DB[test_enrollment]
    print(f"Generating for: {name}")
    pdf_stream = generate_certificate_pdf(name, test_enrollment)
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_stream.read())
    print("PDF generated successfully: test_output.pdf")
