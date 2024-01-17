# Flask app
from flask import Flask, render_template, jsonify, send_file, request
import psycopg2
import json

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from io import BytesIO
app = Flask(__name__)

# Configuración de la conexión a la base de datos
config = {
    'user': 'postgres',
    'password': 'DesafioNG1',
    'host': '35.241.146.138',
    'port': '5432',
    'database': 'postgres'
}

def consulta_resultados(sistema, tarifa, cia, metodo, producto_cia, fee, mes=None):
    
    print("request url:", request.url)
    print("request:", request.form)

    sistema_seleccionado = sistema
    tarifa_seleccionada = tarifa
    cia_seleccionada = cia
    metodo_seleccionado = metodo
    producto_cia_seleccionada = producto_cia
    fee_seleccionado = fee
    mes_seleccionado = mes

    print("sistema_seleccionado:", sistema_seleccionado)
    print("tarifa_seleccionada:", tarifa_seleccionada)
    print("cia_seleccionada:", cia_seleccionada)
    print("metodo_seleccionado:", metodo_seleccionado)
    print("producto_cia_seleccionada:", producto_cia_seleccionada)
    print("fee_seleccionado:", fee_seleccionado)
    print("mes_seleccionado:", mes_seleccionado)


    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**config)

        # Crear un cursor para ejecutar la consulta
        cursor = conn.cursor()
        if metodo_seleccionado == 'FIJO':
            # Consulta SQL para obtener los datos según los filtros
            consulta_datos = f"""
                SELECT p1, p2, p3, p4, p5, p6, p1_, p2_, p3_, p4_, p5_, p6_
                FROM precios_fijo
                WHERE sistema = '{sistema_seleccionado}' 
                    AND tarifa = '{tarifa_seleccionada}' 
                    AND cia = '{cia_seleccionada}' 
                    AND producto_cia = '{producto_cia_seleccionada}'
                    AND fee = '{fee_seleccionado}'
            """
            cursor.execute(consulta_datos)

            data = cursor.fetchall()
            print(data)
            cursor.close()  
            conn.close()

            return data

        elif metodo_seleccionado == 'INDEXADO':
            print("-----ENTRA-----")
            consulta_datos_energia = f"""
                SELECT p1_, p2_, p3_, p4_, p5_, p6_
                FROM precios_index_energia
                WHERE sistema = '{sistema_seleccionado}' 
                    AND tarifa = '{tarifa_seleccionada}' 
                    AND cia = '{cia_seleccionada}' 
                    AND fee = '{fee_seleccionado}'
                    AND mes = '{mes_seleccionado}'
                    
            """
            cursor.execute(consulta_datos_energia)

            data_energia = cursor.fetchall()

            consulta_datos_potencia = f"""
                SELECT p1, p2, p3, p4, p5, p6
                FROM precios_index_potencia
                WHERE sistema = '{sistema_seleccionado}' 
                    AND tarifa = '{tarifa_seleccionada}' 
                    AND cia = '{cia_seleccionada}'
                    AND producto_cia = '{producto_cia_seleccionada}'
                    
            """
            cursor.execute(consulta_datos_potencia)

            data_potencia = cursor.fetchall()

            cursor.close()  
            conn.close()

            print("data_energia: ", data_energia)
            print("data_potencia: ", data_potencia)
            data_total = [data_energia[0] + data_potencia[0]]
            
            print("----Datos totales:", data_total)
            return data_total
       
        
        

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
def transformar_precios(precios):
    nuevos_precios = {}

    for i, valor in enumerate(precios):
        if i < 6:
            clave = f"p{i+1}"
        elif 6 <= i < 12:
            clave = f"P{i-5}"
        else:
            clave = f"PM{i-11}"

        nuevos_precios[clave] = valor

    return nuevos_precios


@app.route('/')

@app.route('/load_filters', methods=['GET'])
def cargar_filtros():

    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()

        # Consulta SQL para CIAs
        consulta_cias = "SELECT DISTINCT cia FROM precios_fijo"
        cursor.execute(consulta_cias)
        cias = [fila[0] for fila in cursor.fetchall()]
        print("cias:", cias)
        # Consulta SQL para Fees (usando la primera CIA como ejemplo)
        primera_cia = cias[0] if cias else None
        print(primera_cia)
        consulta_producto_cia = f"SELECT DISTINCT producto_cia FROM precios_fijo WHERE cia = '{primera_cia}'"
        cursor.execute(consulta_producto_cia)
        producto_cia = [fila[0] for fila in cursor.fetchall()]
        primer_producto_cia = producto_cia[0] if producto_cia else None

        consulta_fee = f"SELECT DISTINCT fee FROM precios_fijo WHERE cia = '{primera_cia}'"
        cursor.execute(consulta_fee)
        fee = [fila[0] for fila in cursor.fetchall()]
        primer_fee = fee[0] if fee else None

        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()

        # Forzamos la definición de los valores de los otros filtros.
        sistemas = ['PENINSULA', 'BALEARES', 'CANARIAS']
        primer_sistema = sistemas[0] if sistemas else None
        tarifas = ['2.0TD', '3.0TD', '6.1TD', '6.2TD']
        primera_tarifa = tarifas[0] if tarifas else None
        metodos =['FIJO', 'INDEXADO']
        primer_metodo = metodos[0] if metodos else None
        meses =['-']
        primer_mes = meses[0] if meses else None

        # Parametros necesarios: cia, sistema, tarifa, fee
        precios = consulta_resultados(primer_sistema, primera_tarifa, primera_cia, primer_metodo, primer_producto_cia, primer_fee, primer_mes)

        
        # Crear un diccionario con los resultados
        resultado_json = {'sistemas': sistemas,'tarifas': tarifas,'cias': cias,'metodos': metodos, 'producto_cia': producto_cia,'precios': precios,'fee':fee}
        # Modificamos el json para añadir etiquetas para los precios.
        resultado_json["precios"] = [transformar_precios(resultado_json["precios"][0])]

        # Convertir el diccionario a formato JSON
        json_resultado = json.dumps(resultado_json)
        # Retornar el JSON
        return json_resultado

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Ruta para manejar la selección del botón y cargar las Fees
@app.route('/reload_filters', methods=['POST'])
def recargar_filtros():
    #sistema_seleccionado = request.args.get('sistema') #peninsula
    sistema_seleccionado = "PENINSULA"
    tarifa_seleccionada = request.args.get('tarifa') #2.0TD
    cia_seleccionada = request.args.get('cia') #iberdrola
    metodo_seleccionado = request.args.get('metodo') # FIJO
    #producto_cia_selecionado = request.args.get('producto_cia') 
    #fee_seleccionado = request.args.get('fee')
    #mes_seleccionado = request.args.get('mes')

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()

        if metodo_seleccionado == 'INDEXADO':
            print('----- INDEXADO -----')

            #probar mañana
            consulta_cia = f"SELECT DISTINCT cia FROM precios_index_energia"
            cursor.execute(consulta_cia)
            cia_index = [fila[0] for fila in cursor.fetchall()]
            print(cia_index)

            consulta_fee = f"SELECT DISTINCT fee FROM precios_index_energia WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            cursor.execute(consulta_fee)
            fee_index = [fila[0] for fila in cursor.fetchall()]
            print(fee_index)

            consulta_producto_cia = f"SELECT DISTINCT producto_cia FROM precios_index_potencia WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            cursor.execute(consulta_producto_cia)
            producto_cia_index = [fila[0] for fila in cursor.fetchall()]
            print(producto_cia_index)

            consulta_meses_energia = f"SELECT DISTINCT mes FROM precios_index_energia WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            cursor.execute(consulta_meses_energia)
            meses_index_energia = [fila[0] for fila in cursor.fetchall()]
            print(meses_index_energia)

            # Cerrar el cursor y la conexión
            cursor.close()
            conn.close()

            meses_index_energia = [fecha.strftime('%Y-%m-%d') for fecha in meses_index_energia]

            primer_fee= fee_index[0] if fee_index else None
            primer_producto_cia = producto_cia_index[0] if producto_cia_index else None
            primer_mes = meses_index_energia[0] if meses_index_energia else None

            #precios = consulta_resultados(sistema_seleccionado, tarifa_seleccionada, cia_seleccionada, metodo_seleccionado, primer_producto_cia, primer_fee, primer_mes)
            #######
            resultado_json = {'cia':cia_index,'fee': fee_index, 'producto_cia':producto_cia_index, 'meses': meses_index_energia}
            #resultado_json["precios"] = [transformar_precios(resultado_json["precios"][0])]
            # Convertir el diccionario a formato JSON
            json_resultado = json.dumps(resultado_json)
            # Retornar el JSON
            return json_resultado

        elif metodo_seleccionado == 'FIJO':
            print('----- FIJO -----')

            #probar mañana
            consulta_cia = f"SELECT DISTINCT cia FROM precios_fijo"
            cursor.execute(consulta_cia)
            cia_fijo = [fila[0] for fila in cursor.fetchall()]
            print(cia_fijo)

            consulta_fee = f"SELECT DISTINCT fee FROM precios_fijo WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            print(consulta_fee)
            cursor.execute(consulta_fee)
            fee_fijo = [fila[0] for fila in cursor.fetchall()]
            print(fee_fijo)

            consulta_producto_cia = f"SELECT DISTINCT producto_cia FROM precios_fijo WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            print(consulta_producto_cia)
            cursor.execute(consulta_producto_cia)
            producto_cia_fijo = [fila[0] for fila in cursor.fetchall()]
            print(producto_cia_fijo)

            cursor.close()
            conn.close()

            primer_fee= fee_fijo[0] if fee_fijo else None
            primer_producto_cia = producto_cia_fijo[0] if producto_cia_fijo else None
            meses =['-']
            primer_mes = meses[0] if meses else None
            

            #precios = consulta_resultados(sistema_seleccionado, tarifa_seleccionada, cia_seleccionada, metodo_seleccionado, primer_producto_cia, primer_fee, primer_mes)
            ######
            resultado_json = {'cia':cia_fijo,'fee': fee_fijo, 'producto_cia':producto_cia_fijo}
            #resultado_json["precios"] = [transformar_precios(resultado_json["precios"][0])]
            
            # Convertir el diccionario a formato JSON
            json_resultado = json.dumps(resultado_json)
            # Retornar el JSON
            return json_resultado

        

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

#____________________________________________________________________________________________________________________________


@app.route('/cargar_precios', methods=['POST'])
def cargar_precios():
    sistema_seleccionado = request.args.get('sistema') 
    tarifa_seleccionada = request.args.get('tarifa') 
    cia_seleccionada = request.args.get('cia') 
    metodo_seleccionado = request.args.get('metodo') 
    producto_cia_seleccionada = request.args.get('producto_cia') 
    fee_seleccionado = request.args.get('fee')
    mes_seleccionado = request.args.get('mes')    

    print("sistema_seleccionado:", sistema_seleccionado)
    print("tarifa_seleccionada:", tarifa_seleccionada)
    print("cia_seleccionada:", cia_seleccionada)
    print("metodo_seleccionado:", metodo_seleccionado)
    print("producto_cia_seleccionada:", producto_cia_seleccionada)
    print("fee_seleccionado:", fee_seleccionado)
    print("mes_seleccionado:", mes_seleccionado)


    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**config)

        # Crear un cursor para ejecutar la consulta
        cursor = conn.cursor()
        if metodo_seleccionado == 'FIJO':
            # Consulta SQL para obtener los datos según los filtros
            consulta_datos = f"""
                SELECT p1, p2, p3, p4, p5, p6, p1_, p2_, p3_, p4_, p5_, p6_
                FROM precios_fijo
                WHERE sistema = '{sistema_seleccionado}' 
                    AND tarifa = '{tarifa_seleccionada}' 
                    AND cia = '{cia_seleccionada}' 
                    AND producto_cia = '{producto_cia_seleccionada}'
                    AND fee = '{fee_seleccionado}'
            """
            cursor.execute(consulta_datos)

            data = cursor.fetchall()
            print(data)
            cursor.close()  
            conn.close()

            resultado_json = {'precios': data}
            resultado_json["precios"] = [transformar_precios(resultado_json["precios"][0])]
            
            # Convertir el diccionario a formato JSON
            json_resultado = json.dumps(resultado_json)
            # Retornar el JSON
            return json_resultado

        elif metodo_seleccionado == 'INDEXADO':
            print("-----ENTRA_2-----")
            consulta_datos_energia = f"""
                SELECT p1_, p2_, p3_, p4_, p5_, p6_
                FROM precios_index_energia
                WHERE sistema = '{sistema_seleccionado}' 
                    AND tarifa = '{tarifa_seleccionada}' 
                    AND cia = '{cia_seleccionada}' 
                    AND fee = '{fee_seleccionado}'
                    AND mes = '{mes_seleccionado}'
                    
            """
            print(consulta_datos_energia)

            cursor.execute(consulta_datos_energia)

            data_energia = cursor.fetchall()

            consulta_datos_media = f"""
                SELECT 
                    AVG(p1_) AS media_p1,
                    AVG(p2_) AS media_p2,
                    AVG(p3_) AS media_p3,
                    AVG(p4_) AS media_p4,
                    AVG(p5_) AS media_p5,
                    AVG(p6_) AS media_p6
                FROM precios_index_energia
                WHERE 
                    sistema = '{sistema_seleccionado}' 
                    AND tarifa = '{tarifa_seleccionada}' 
                    AND cia = '{cia_seleccionada}' 
                    AND fee = '{fee_seleccionado}'
                    AND mes BETWEEN 
                        (DATE '{mes_seleccionado}' - INTERVAL '11 months') AND DATE '{mes_seleccionado}'"""


            cursor.execute(consulta_datos_media)

            data_energia_media = cursor.fetchall()

            consulta_datos_potencia = f"""
                SELECT p1, p2, p3, p4, p5, p6
                FROM precios_index_potencia
                WHERE sistema = '{sistema_seleccionado}' 
                    AND tarifa = '{tarifa_seleccionada}' 
                    AND cia = '{cia_seleccionada}'
                    AND producto_cia = '{producto_cia_seleccionada}'
                    
            """
            print(consulta_datos_potencia)
            cursor.execute(consulta_datos_potencia)

            data_potencia = cursor.fetchall()

            cursor.close()  
            conn.close()

            print("data_energia: ", data_energia)
            print("data_potencia: ", data_potencia)
            print("data_energia_media:", data_energia_media)
            data_total = [data_energia[0] + data_potencia[0] + data_energia_media[0]]
            
            resultado_json = {'precios': data_total}
            resultado_json["precios"] = [transformar_precios(resultado_json["precios"][0])] 
            
            # Convertir el diccionario a formato JSON
            json_resultado = json.dumps(resultado_json)
            
            # Retornar el JSON
            return  json_resultado

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

#____________________________________________________________________________________________________________________________

@app.route('/descargar_pdf', methods=['GET'])
def descargar_pdf():
    # Generar el PDF en memoria
    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    # Head izquierda
    c.setFont("Helvetica", 12)
    #c.drawImage("imagen.png", 20, 770, width=160, height=60)
    c.drawString(30, 740, "Cliente: NOMBRE CLIENTE")
    c.drawString(30, 725, "Dirección: DIRECCIÓN CLIENTE")
    c.drawString(30, 710, "CUPS: NÚMERO CUPS")
    # Head derecha
    c.setFillColor(colors.gray)
    c.drawString(360, 815, "Asesor Energético: VARIABLE NOMBRE ASESOR")
    c.drawString(360, 800, "Contacto: NÚMERO ASESOR")
    c.drawString(360, 785, "Delegación: LOCALIDAD")
    c.setFillColor(colors.black)
    ####
    c.setFont("Helvetica", 10)
    c.drawString(360, 750, "Válido por 7 días a partir de la propuesta")
    c.drawString (360, 735, "Documentación para modificar la propuesta:")
    c.drawString (360, 720, "- DNI titular   - CIF empresa")
    c.drawString (360, 705, "- Copia Facturas   - Recibo bancario")

    # Franja horizontal gris claro con opacidad baja
    #Color
    c.setFillColorRGB(0.9, 0.9, 0.9)  # Color gris claro
    c.setStrokeColorRGB(0.9, 0.9, 0.9)  # Color de borde igual al de relleno para evitar contorno visible
    # Forma
    c.rect (0, 650, 600, 20, 0, fill=1)

    # Restaurar el color de relleno y borde a valores no transparentes
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 16) 

    # Título
    c.drawString(140, 655, "Oferta de contratación de suministro eléctrico")

    # Ahorro ¿?
    c.setFont("Helvetica", 12)
    c.drawString(120, 630, "Ahorro actual")
    c.drawString(380, 630, "Ahorro anual") 
    #
    c.setStrokeColorRGB(0, 0, 0) # Color del borde
    c.setLineWidth(1) #Grosor de la línea 
    c.roundRect (85,580, 150, 35, 11,fill=0) 
    c.roundRect (340,580, 150, 35, 11, fill=0)
    #
    c.setFillColorRGB(0.5, 0.8, 0.2)  
    c.setStrokeColorRGB(0.5, 0.8, 0.2)
    c.circle(115, 597, 12, fill=1)
    c.circle(375, 597,12, fill=1)
    # Texto
    c.setFillColorRGB(1.0, 1.0, 1.0)  
    c.setStrokeColorRGB(1.0, 1.0, 1.0)
    c.drawString(100, 593, "12%")
    c.drawString(360, 593, "12%")
    #
    c.setFillColorRGB(0.0, 0.0, 0.0)  
    c.setStrokeColorRGB(0.0, 0.0, 0.0)
    c.setFont("Helvetica", 16)
    c.drawString(150,593, "€20.51")
    c.drawString(410, 593, "€20.51")

    # Franja horizontal
    c.setFillColorRGB(0.9, 0.9, 0.9)  # Color gris claro
    c.setStrokeColorRGB(0.9, 0.9, 0.9)  # Color de borde igual al de relleno para evitar contorno visible
    # Forma
    c.rect (0, 540, 600, 20, 0, fill=1)

    # Restaurar el color de relleno y borde a valores no transparentes
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 16) 

    # Título
    c.drawString(230, 545, "Oferta Several")

    # Franja horizontal
    c.setFillColorRGB(0.9, 0.9, 0.9)  # Color gris claro
    c.setStrokeColorRGB(0.9, 0.9, 0.9)  # Color de borde igual al de relleno para evitar contorno visible
    # Forma
    c.rect (0, 270, 600, 20, 0, fill=1)

    # Restaurar el color de relleno y borde a valores no transparentes
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 16) 

    # Título
    c.drawString(230, 275, "Oferta de Distribuidora Actual")
    # Guardar los cambios en el documento
    c.save()
    buffer.seek(0)

    # Descargar el PDF como un archivo adjunto
    return send_file(buffer, as_attachment=True, download_name='pdf2.5.pdf')


#____________________________________________________________________________________________________________________________

if __name__ == '__main__':
    app.run(debug=True)
