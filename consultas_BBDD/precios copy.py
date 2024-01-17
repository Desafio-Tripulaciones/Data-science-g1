# Flask app
from flask import Flask, render_template, jsonify, request
import psycopg2
import json

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
        clave = f"p{i+1}" if i < 6 else f"P{i-5}"
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
    sistema_seleccionado = request.args.get('sistema')
    tarifa_seleccionada = request.args.get('tarifa')
    cia_seleccionada = request.args.get('cia')
    metodo_seleccionado = request.args.get('metodo')
    producto_cia_selecionado = request.args.get('producto_cia')
    fee_seleccionado = request.args.get('fee')
    mes_seleccionado = request.args.get('mes')

    print(sistema_seleccionado)
    print(tarifa_seleccionada)
    print(cia_seleccionada)
    print(metodo_seleccionado)
    print(producto_cia_selecionado)
    print(fee_seleccionado)
    print(mes_seleccionado)

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**config)

        # Crear un cursor para ejecutar la consulta
        cursor = conn.cursor()

        # Consulta SQL para Fees
        if metodo_seleccionado == 'INDEXADO':
            # !!!
            consulta_tarifa = f"SELECT DISTINCT tarifa FROM precios_index_energia"
            cursor.execute(consulta_tarifa)
            tarifa_index = [fila[0] for fila in cursor.fetchall()]

            consulta_cia = f"SELECT DISTINCT cia FROM precios_index_energia"
            cursor.execute(consulta_cia)
            cia_index = [fila[0] for fila in cursor.fetchall()]

            consulta_producto_cia = f"SELECT DISTINCT producto_cia FROM precios_index_potencia WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            cursor.execute(consulta_producto_cia)
            producto_cia_index = [fila[0] for fila in cursor.fetchall()]

            consulta_meses = f"SELECT DISTINCT mes FROM precios_index_energia WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            cursor.execute(consulta_meses)
            meses_index = [fila[0] for fila in cursor.fetchall()]

            consulta_fee = f"SELECT DISTINCT fee FROM precios_index_energia WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            cursor.execute(consulta_fee)
            fees_index = [fila[0] for fila in cursor.fetchall()]

            # Cerrar el cursor y la conexión
            cursor.close()
            conn.close()
           
            meses_index = [fecha.strftime('%Y-%m-%d') for fecha in meses_index]

            precios = consulta_resultados(sistema_seleccionado, tarifa_seleccionada, cia_seleccionada, metodo_seleccionado, producto_cia_selecionado,fee_seleccionado, mes_seleccionado)

            resultado_json = {'tarifa': tarifa_index, 'cia':cia_index, 'producto_cia': producto_cia_index, 'meses': meses_index, 'fees': fees_index, 'precios': precios}
            
            resultado_json["precios"] = [transformar_precios(resultado_json["precios"][0])]

            # Convertir el diccionario a formato JSON
            json_resultado = json.dumps(resultado_json)
            # Retornar el JSON
            return json_resultado
        
        elif metodo_seleccionado == 'FIJO':

            consulta_tarifa = f"SELECT DISTINCT tarifa FROM precios_fijo"
            cursor.execute(consulta_tarifa)
            tarifa_fijo = [fila[0] for fila in cursor.fetchall()]
            
            print("tarifa:", tarifa_fijo)

            consulta_cia = f"SELECT DISTINCT cia FROM precios_fijo"
            cursor.execute(consulta_cia)
            cia_fijo = [fila[0] for fila in cursor.fetchall()]

            print("cia:",cia_fijo)

            consulta_producto_cia = f"SELECT DISTINCT producto_cia FROM precios_fijo WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            cursor.execute(consulta_producto_cia)
            producto_cia_fijo = [fila[0] for fila in cursor.fetchall()]
            print('producto_cia_fijo', producto_cia_fijo)

            consulta_fee = f"SELECT DISTINCT fee FROM precios_fijo WHERE cia = '{cia_seleccionada}' AND tarifa = '{tarifa_seleccionada}'"
            cursor.execute(consulta_fee)
            fee_fijo = [fila[0] for fila in cursor.fetchall()]
            print("fee:",fee_fijo)

            # Cerrar el cursor y la conexión
            cursor.close()
            conn.close()

            precios = consulta_resultados(sistema_seleccionado, tarifa_seleccionada, cia_seleccionada, metodo_seleccionado, producto_cia_selecionado, fee_seleccionado)

            resultado_json = {'tarifa': tarifa_fijo, 'cia':cia_fijo, 'producto_cia': producto_cia_fijo,'fee':fee_fijo ,'precios': precios}
            
            resultado_json["precios"] = [transformar_precios(resultado_json["precios"][0])]

            # Convertir el diccionario a formato JSON
            json_resultado = json.dumps(resultado_json)
            # Retornar el JSON
            return json_resultado

            # Devolver las Fees como respuesta JSON
            # YA TENEMOS EL JSON QUE DEVUELVE LOS PRODUCTOS CUANDO ES FIJO, LOS PROUCTOS Y LAS FECHAS CUANDO ES INDEXADO

        

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



if __name__ == '__main__':
    app.run(debug=True)


