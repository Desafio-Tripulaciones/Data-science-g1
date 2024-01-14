from flask import Flask, render_template, jsonify, request
import psycopg2

app = Flask(__name__)

# Configuración de la conexión a la base de datos
config = {
    'user': 'postgres',
    'password': 'DesafioNG1',
    'host': '35.241.146.138',
    'port': '5432',
    'database': 'postgres'
}

# Ruta para mostrar el formulario
@app.route('/', methods=['GET'])
def consultar_cias():
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**config)

        # Crear un cursor para ejecutar la consulta
        cursor = conn.cursor()

        # Consulta SQL para CIAs
        consulta_cias = "SELECT DISTINCT cia FROM precios_fijo"
        cursor.execute(consulta_cias)
        cias = [fila[0] for fila in cursor.fetchall()]

        # Consulta SQL para Fees (usando la primera CIA como ejemplo)
        primera_cia = cias[0] if cias else None
        consulta_fees = f"SELECT DISTINCT producto_cia FROM precios_fijo WHERE cia = '{primera_cia}'"
        cursor.execute(consulta_fees)
        fees = [fila[0] for fila in cursor.fetchall()]

        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()

        return render_template('consulta.html', cias=cias, fees=fees)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Ruta para manejar la selección del botón y cargar las Fees
@app.route('/seleccionar_fees', methods=['POST'])
def seleccionar_fees():
    cia_seleccionada = request.form.get('cia')

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**config)

        # Crear un cursor para ejecutar la consulta
        cursor = conn.cursor()

        # Consulta SQL para Fees
        consulta_fees = f"SELECT DISTINCT producto_cia FROM precios_fijo WHERE cia = '{cia_seleccionada}'"
        cursor.execute(consulta_fees)
        fees = [fila[0] for fila in cursor.fetchall()]

        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()

        # Devolver las Fees como respuesta JSON
        return jsonify({'fees': fees})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



if __name__ == '__main__':
    app.run(debug=True)



