from flask import Flask, request, jsonify
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.chrome.service import Service



app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API del modelo advertising"

@app.route("/cups", methods=['POST'])
def tu_endpoint():
    try:
        # Obtener el dato del CUPS desde la solicitud POST
        data = request.get_json()
        cups = data['cups']

        def webscraping (num_cup):
            #directorio_actual = os.path.dirname(os.path.abspath(__file__))
            #chromedriver_path = os.path.join(directorio_actual, 'chromedriver.exe')
            #service = Service(executable_path=chromedriver_path)
            
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            

            driver.get("https://agentes.candelaenergia.es/#/sips")

            empresa_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'empresaLogin'))
    )

            # Encuentra los campos de empresa, usuario y contraseña por su nombre o cualquier otro atributo
            empresa_input = driver.find_element(By.NAME, 'empresaLogin')
            usuario_input = driver.find_element(By.NAME, 'usuario')
            contrasena_input = driver.find_element(By.NAME, 'password')

            # Ingresa las credenciales
            empresa_input.send_keys('CANDELA COMERCIALIZADORA, S.L ELECTRICIDAD')
            usuario_input.send_keys('CA091')
            contrasena_input.send_keys('CI001-091/8463')

            # Encuentra el botón de "Entrar" por su clase (puedes usar otro selector según sea necesario)
            entrar_button = driver.find_element(By.CLASS_NAME, 'btn-white')

            # Haz clic en el botón usando JavaScript
            driver.execute_script("arguments[0].click();", entrar_button)

            # Encuentra el enlace que representa la sección "SIPS" por su atributo href
            wait = WebDriverWait(driver, 10)  

            enlace_sips = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="#/sips"]')))

            # Haz clic en el enlace usando JavaScript
            driver.execute_script("arguments[0].click();", enlace_sips)
            
            # Encuentra el campo de entrada por su ID (puedes usar otro selector según sea necesario)
            
            campo_input = wait.until(EC.presence_of_element_located((By.ID, 'input_6')))
            
            # Ingresa el número deseado en el campo
            campo_input.send_keys(num_cup)

            # Puedes también enviar una tecla "Enter" para confirmar el ingreso del número (opcional)
            campo_input.send_keys(Keys.RETURN)
            
            # Encuentra el botón "Consultar" por su clase (puedes usar otro selector según sea necesario)
            boton_consultar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'md-raised')))

            # Haz clic en el botón usando JavaScript
            driver.execute_script("arguments[0].click();", boton_consultar)
            time.sleep(5)

            # Recogemos todas las variables 
            
            municipio_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsMunicipio']")
            municipio = municipio_element.text

            provincia_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsProvincia']")
            provincia = provincia_element.text

            CP_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsCodigoPostal']")
            cp = CP_element.text

            tarifa_element = driver.find_element(By.ID, "SipsTarifa")
            tarifa = tarifa_element.text

            cons_anu_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsConsumoAnual && VerEnergia']")
            cons_anu_t = cons_anu_element.text
            cons_anu = ''.join(filter(str.isdigit, cons_anu_t))
            cons_anu = float(cons_anu)

            cons_anu_p1_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsConsumoP1 && VerEnergia']")
            cons_anu_p1_t = cons_anu_p1_element.text
            cons_anu_p1 = ''.join(filter(str.isdigit, cons_anu_p1_t))
            cons_anu_p1 = float(cons_anu_p1)

            cons_anu_p2_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsConsumoP2 && VerEnergia']")
            cons_anu_p2_t = cons_anu_p2_element.text
            cons_anu_p2 = ''.join(filter(str.isdigit, cons_anu_p2_t))
            cons_anu_p2 = float(cons_anu_p2)

            cons_anu_p3_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsConsumoP3 && VerEnergia']")
            cons_anu_p3_t = cons_anu_p3_element.text
            cons_anu_p3 = ''.join(filter(str.isdigit, cons_anu_p3_t))
            cons_anu_p3 = float(cons_anu_p3)

            cons_anu_p4_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsConsumoP4 && VerEnergia']")
            cons_anu_p4_t = cons_anu_p4_element.text
            cons_anu_p4 = ''.join(filter(str.isdigit, cons_anu_p4_t))
            cons_anu_p4 = float(cons_anu_p4)

            cons_anu_p5_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsConsumoP5 && VerEnergia']")
            cons_anu_p5_t = cons_anu_p5_element.text
            cons_anu_p5 = ''.join(filter(str.isdigit, cons_anu_p5_t))
            cons_anu_p5 = float(cons_anu_p5)

            cons_anu_p6_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsConsumoP6 && VerEnergia']")
            cons_anu_p6_t = cons_anu_p6_element.text
            cons_anu_p6 = ''.join(filter(str.isdigit, cons_anu_p6_t))
            cons_anu_p6 = float(cons_anu_p6)

            p1_element = driver.find_element(By.ID, "PotenciaP1")
            p1_t = p1_element.text.replace(',', '.')
            p1 = float(p1_t)

            p2_element = driver.find_element(By.ID, "PotenciaP2")
            p2_t = p2_element.text.replace(',', '.')
            p2 = float(p2_t)

            p3_element = driver.find_element(By.ID, "PotenciaP3")
            p3 = float(p3_element.text) if p3_element.text else 0.0


            p4_element = driver.find_element(By.ID, "PotenciaP4")
            p4 = float(p4_element.text) if p4_element.text else 0.0


            p5_element = driver.find_element(By.ID, "PotenciaP5")
            p5 = float(p5_element.text) if p5_element.text else 0.0


            p6_element = driver.find_element(By.ID, "PotenciaP6")
            p6 = float(p6_element.text) if p6_element.text else 0.0


            distribuidora_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsDistribuidora']")
            distribuidora = distribuidora_element.text

            ult_cam_comer_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsUltimoCambioComercializadora']")
            ult_cam_comer = ult_cam_comer_element.text

            bie_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsUltimoCambioBIE']")
            bie = bie_element.text

            tension_element = driver.find_element(By.XPATH, "//any[@ng-switch-when='02']")
            tension = tension_element.text

            ult_cam_contra_element = driver.find_element(By.XPATH, "//td[@class='md-cell ng-binding' and @ng-show='MostrarSipsUltimoCambioContrato']")
            ult_cam_contr = ult_cam_contra_element.text

            # Recogemos todos los datos y los almacenamos como diccionario

            datos_json = {
                'Municipio': municipio,
                'Provincia': provincia,
                'Codigo Postal': cp,
                'Tarifa': tarifa,
                'Consumo Anual': cons_anu,
                'Consumo Anual P1': cons_anu_p1,
                'Consumo Anual P2': cons_anu_p2,
                'Consumo Anual P3': cons_anu_p3,
                'Consumo Anual P4': cons_anu_p4,
                'Consumo Anual P5': cons_anu_p5,
                'Consumo Anual P6': cons_anu_p6,
                'P1': p1,
                'P2': p2,
                'P3': p3,
                'P4': p4,
                'P5': p5,
                'P6': p6,
                'Distribuidora': distribuidora,
                'Cambio comercializadora': ult_cam_comer,
                'Ultimo cambio BIE': bie,
                'Tensión': tension,
                'Ultimo Cambio Contrato': ult_cam_contr
            }
            
            #convertimos el diccionario a modo JSON
            
            json_resultado = json.dumps(datos_json)

            return json_resultado

        # Llamar a la funcion de webscraping
        resultado_cups = webscraping(cups)
        

        # Devolver el resultado como JSON
        return jsonify({"resultado": resultado_cups})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)