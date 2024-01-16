from flask import Flask, request, jsonify
import pdfplumber
import re



app = Flask(__name__)



def extract_text_from_pdf(pdf_content):
    text = ""
    with pdfplumber.open(pdf_content) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text
@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API"

@app.route('/procesar_pdf', methods=['POST'])
def procesar_pdf():
    # Verifica si se ha enviado un archivo PDF
    if 'file' not in request.files:
        return jsonify({"error": "No se ha proporcionado un archivo PDF"}), 400

    pdf_file = request.files['file']

    # Verifica si el archivo tiene una extensión válida
    if not pdf_file.filename.endswith('.pdf'):
        return jsonify({"error": "El archivo no tiene la extensión PDF"}), 400

    try:
        pdf_text = extract_text_from_pdf(pdf_file)
        
        #Patron consumo y precio energia

        patron = re.compile(r'Facturación del Consumo (\d+) kWh x ([\d\.,-]+)\s+Eur/kWh')
        coincidencia = patron.search(pdf_text)

        consumo = int(coincidencia.group(1)) if coincidencia else None
        precio_energia = float(coincidencia.group(2).replace(',', '.')) if coincidencia else None
        

        #Patron para dias    
        patron2 = r'\b(\d{2})\s*días\b'
        resultado = re.search(patron2, pdf_text) 

        dias = int(resultado.group(1)) if resultado else None

        #Patron alquiler
        patron3 = r'\bAlquiler\b.*?(\d+\,\d{6})'

        resultado3 = re.search(patron3, pdf_text)
        precio_alquiler = float(resultado3.group(1).replace(',', '.')) if resultado3 else None
            
        #Patron Valle

        patron4 = r'\bValle\s+(\d+\,\d{1,2})\s+kW.*?(\d+\,\d{6})'
        resultado4 = re.search(patron4, pdf_text)

        potencia = float(resultado4.group(1).replace(',', '.')) if resultado4 else None
        precio_valle = float(resultado4.group(2).replace(',', '.')) if resultado4 else None

        #patron Punta
                
        patron5 = r'\bPunta\b.*?(\d+\,\d{6})'

        resultado5 = re.search(patron5, pdf_text)
                
        precio_punta = float(resultado5.group(1).replace(',', '.')) if resultado5 else None
            
        # Patron descuento

        patron6 = r'Descuentos\s+(-?\d+\,\d{1,2})\s+€' 
        resultado6 = re.search(patron6, pdf_text)  

        descuento = float(resultado6.group(1).replace(',', '.')) if resultado6 else None

        # Patron Otros

        patron7 = r'Otros\s+(-?\d+\,\d{1,2})\s+€' 
        resultado7 = re.search(patron7, pdf_text)  

        otros = float(resultado7.group(1).replace(',', '.')) if resultado7 else None
                    
        # Devuelve los resultados como JSON
        return jsonify({'Consumo': consumo,
                'precio energia': precio_energia,
                'Dias': dias,
                'Precio Alquiler': precio_alquiler,
                'Precio valle': precio_valle,
                'precio Punta': precio_punta,
                'Potencia': potencia,
                'Descuentos' : descuento ,
                'Otros' : otros,
                }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)