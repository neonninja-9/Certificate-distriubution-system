import os
import csv
import io
from flask import Flask, render_template, request, jsonify, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from pypdf import PdfReader, PdfWriter

app = Flask(__name__)

# Configuration
DATA_FILE = os.path.join('data', 'SALE_Sorted_Final.csv')
BASE_CERT_FILE = os.path.join('assets', 'base_certificate.pdf')


def normalize_enrollment(value):
    return "".join(ch for ch in str(value).upper() if ch.isalnum())


def normalize_name(value):
    return " ".join(str(value).split()).casefold()

def load_students():
    students = {}
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                enrollment = normalize_enrollment(row.get('ENROLLMENT', ''))
                name = row.get('NAME', '').strip()
                if enrollment:
                    students[enrollment] = name
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return students

# Load students into memory at startup
STUDENTS_DB = load_students()

def generate_certificate_pdf(name, enrollment):
    # Create the overlay with the student's name
    packet = io.BytesIO()
    
    # Read the existing base certificate to get actual page size
    existing_pdf = PdfReader(open(BASE_CERT_FILE, "rb"))
    page = existing_pdf.pages[0]
    
    # Get dimensions (usually points, A4 landscape is 842.0 x 595.0)
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    
    c = canvas.Canvas(packet, pagesize=(width, height))

    # Keep the recipient name directly below the "presented to" line.
    font_name = "Times-Bold"
    font_size = 28
    min_font_size = 20
    max_name_width = width * 0.62

    text_width = c.stringWidth(name, font_name, font_size)
    while text_width > max_name_width and font_size > min_font_size:
        font_size -= 1
        text_width = c.stringWidth(name, font_name, font_size)

    c.setFont(font_name, font_size)

    x = width / 2.0
    y = height / 2.0 + 28

    c.drawCentredString(x, y, name)
    c.save()
    
    packet.seek(0)
    new_pdf = PdfReader(packet)
    
    output = PdfWriter()
    
    # Add the "watermark" (the new pdf with the name) on the existing page
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    
    # Write to an output stream
    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)
    
    return output_stream

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid data format."}), 400

    enrollment_input = normalize_enrollment(data.get('enrollment', ''))
    name_input = data.get('name', '').strip()
    
    if not enrollment_input or not name_input:
        return jsonify({"success": False, "message": "Both Name and Enrollment Number are required."}), 400
        
    # Validation against CSV
    if enrollment_input not in STUDENTS_DB:
        return jsonify({"success": False, "message": "Enrollment Number not found in our records."}), 404
        
    registered_name = STUDENTS_DB[enrollment_input]

    # Case-insensitive name match with whitespace normalization.
    if normalize_name(name_input) != normalize_name(registered_name):
        return jsonify({"success": False, "message": f"Name does not match the records for enrollment {enrollment_input}."}), 400
        
    try:
        pdf_stream = generate_certificate_pdf(registered_name, enrollment_input)
        
        # Safe filename
        safe_name = "".join([c for c in registered_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filename = f"Certificate_{safe_name.replace(' ', '_')}.pdf"
        
        return send_file(
            pdf_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({"success": False, "message": "An internal error occurred while generating the certificate."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
