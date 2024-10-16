import pytesseract
import cv2
import json
from PIL import Image
import re
import random
from pytesseract import Output
import numpy as np
import pytesseract.pytesseract
import ollama


#configuracion de la orientacion de la pagina y el modelo de ocr
custom_config = r"--psm 11 --oem 3"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# **
# Selecciona una imagen de las existentes aleatoriamente para analizar
# **
def random_image():
    num = random.randint(1, 10)
    rutas = {
        1: "DocumentosPrueba/dni_argentina_nuevo.png",
        2: "DocumentosPrueba/dni_argentina.jpg",
        3: "DocumentosPrueba/dni_brasil.jpg",
        4: "DocumentosPrueba/dni_chile.png",
        5: "DocumentosPrueba/dni_espana.jpg",
        6: "DocumentosPrueba/dni_newYork.jpg",
        7: "DocumentosPrueba/dni_peru.png",
        8: "DocumentosPrueba/dni_tenesse.png",
        9: "DocumentosPrueba/dni_uruguay.jpg",
        10: "DocumentosPrueba/dni_usa.jpg"
    }


    print(rutas[num])
    return rutas[num]




# **
# Lee la imagen y la convierte a escala de grises y luego la hace binaria
# **
def preprocess_image(image_path):
    # Lee la imagen y la convierte a escala de grises
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    # Aplica un filtro GaussianBlur ligero para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)


    # Aplica binarización Otsu para mejorar el contraste del texto
    _, thresh_img = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


    # Retorna la imagen procesada (sin invertir para mantener texto oscuro y fondo claro)
    return thresh_img


# **
# Extrae el texto de la imagen y crea una copia temporal de la imagen original
# **
def extract_text_from_image(image_path):
    #se crea una imagen temporal copia de la imagen original pero procesada anteriormente y se extrae el texto
   
    processed_img= preprocess_image(image_path)


    # data_image= pytesseract.image_to_data(processed_img, output_type=Output.DICT)
   
    # image_boxes(data_image, processed_img, image_path)
   
    temp_img_path = "dni_temporal.jpg"
    cv2.imwrite(temp_img_path, processed_img)


    text = pytesseract.image_to_string(Image.open(temp_img_path), config=custom_config)


    print("*******************")
    print(text)
    print("*******************")


    return text
   


# **
# Coloca cajas en el texto que detecta pytesseract dentro de la imagen
# **
def image_boxes(data_image, processed_img, image_path):
    n_boxes = len(data_image['text'])
    imgColor = cv2.imread(image_path)




    for i in range(n_boxes):
        if int(data_image['conf'][i]) > 50 :
            (x, y, w, h) = (data_image['left'][i], data_image['top'][i],data_image['width'][i], data_image['height'][i])
            img = cv2.rectangle(processed_img, (x, y),(x + w, y + h),(255,0,0), 2)
            imgColor = cv2.rectangle(processed_img, (x, y),(x + w, y + h),(255,0,0), 2)


   
    cv2.imwrite('ImagenRectangulos.jpg',img)
    cv2.imwrite('ImagenRectangulosColor.jpg',imgColor )




# **
# Procesa el texto obtenido y lo convierte a JSON dependiendo del pais
# **
def process_image_text(text):


    global type
    global tipo_documento


    #USA es el unico pais con formato distinto entonces se procesa aparte
    usa_keywords=["USA","United States Of America","United States of America"]
   
    if any(keyword in text for keyword in usa_keywords):
        tipo_documento = "USA"
    elif "DNI" in text or "Documento Nacional de Identidad" in text:
        tipo_documento = "DNI"
    elif "Pasaporte" in text or "Passport" in text:
        tipo_documento = "Pasaporte"
    else:
        tipo_documento = "Otro"
   
   
    keywords=["Nombre","Nombres","Apellido","Apellidos","ID","Documento","RUN","RUT", "Nacimiento", "Fecha de Nacimiento"]
    #futuro JSON donde se guardarán los datos
   
    data={}
    lines = text.split('\n')
   
    data["TipoDocumento"] = tipo_documento


    if tipo_documento == "USA":
            for i, line in enumerate(lines):
                if "Name" in line:
                    # Las primeras dos líneas después del título son el nombre
                    data["Nombre"] = " ".join(lines[i + 1:i + 3]).strip()
                elif "Address" in line:
                    # Las siguientes tres líneas son la dirección
                    data["Direccion"] = " ".join(lines[i + 1:i + 4]).strip()
                elif "License" in line:
                    # La siguiente línea es el número de licencia
                    data["NumeroLicencia"] = lines[i + 1].strip()
                elif "DOB" in line or "Date of Birth" in line:
                    # La siguiente línea es la fecha de nacimiento
                    data["FechaNacimiento"] = lines[i + 1].strip()


    else:
        keywords = ["Nombre", "Nombres", "Apellido", "Apellidos", "ID", "Documento", "RUN", "RUT", "Nacimiento", "Fecha de Nacimiento"]
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword in line:
                    if i + 1 < len(lines):
                        # Extraer la línea siguiente al título como el valor
                        data[keyword] = lines[i + 1].strip()




    return data


def analyze_text_ollama(text):
    #modelo de ollama que analizará el prompt
    model="llama2"
    prompt= f"Please extract dob, name and lastname and other aditional information that might be useful from this messy text extracted from an ID and convert it into a json : \n{text}"

    response = ollama.chat(model=model, messages=[
        {
            'role':'user',
            'content':prompt
        }
    ])

    extracted_data = response['message']['content']
    print(response['message']['content'])
    return extracted_data

def dni_to_json(image_path):
    text = extract_text_from_image(image_path)
    dni_data= process_image_text(text)
    json_ollama= analyze_text_ollama(text)

    dni_json = json.dumps(dni_data, indent=4, ensure_ascii=False)

    return dni_json


image_path = random_image()
dni_json = dni_to_json(image_path)
print(dni_json)
















   


