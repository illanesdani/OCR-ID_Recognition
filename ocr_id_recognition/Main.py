import pytesseract
import cv2
import json
from PIL import Image
import re
import random
import numpy as np
import pytesseract.pytesseract
import ollama
from datetime import datetime
from dateutil import parser


#configuracion de la orientacion de la pagina y el modelo de ocr
custom_config = r"--psm 11 --oem 3"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# **
# Selecciona una imagen de las existentes aleatoriamente para analizar
# **
def random_image():
    num = random.randint(1, 11)
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
        10: "DocumentosPrueba/dni_usa.jpg",
        11: "DocumentosPrueba/dni-dani.jpeg"
    }


    # print(rutas[num])
    return rutas[11]




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


def analyze_text_ollama(text):
    #modelo de ollama que analizará el prompt
    model="llama2"

    prompt = (
    "Please extract the following information from the provided text while ensuring it corresponds accurately to the titles: "
    "Nombre, Apellido, FechaDeNacimiento, TipoDocumento, and Documento. "
    "Transform the date of birth into a string format, such as '10 May 1998', using the month name in English. "
    "Also, ignore any single letters or unusual non-letter characters. "
    "Return the extracted data in JSON format with the exact field names specified above. "
    "Only provide the JSON response without any additional text. Here is the text:\n"
    f"{text}"
    )


    response = ollama.chat(model=model, messages=[
        {
            'role':'user',
            'content':prompt
        }
    ])

    extracted_data = response['message']['content']
    return extracted_data


def extract_json(text):
    # Usar una expresión regular para encontrar el JSON en el texto
    match = re.search(r'{.*}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        # Convertir el string JSON a un objeto Python (dict)
        return json.loads(json_str)
    else:
        return None  # Retornar None si no se encuentra un JSON

def analyze_id_type(id_type):
    id_type = id_type.lower()  # Convertimos todo el texto a minúsculas para facilitar comparaciones
    
    if "documento nacional de identidad" in id_type or "dni" in id_type or re.search(r'documento', id_type):
        return "DNI"
    
    elif "cni" in id_type or "carte nationale d'identité" in id_type or "carte nationale" in id_type or re.search(r'cédula', id_type):
        return "CNI"
    
    elif "ci" in id_type or "cédula de identidad" in id_type or re.search(r'cedula', id_type):
        return "CI"
    
    elif "cpf" in id_type or "cadastro de pessoas fisicas" in id_type or "cadastro de pessoas físicas" in id_type:
        return "CPF"
    
    elif "pasaporte" in id_type or "passport" in id_type:
        return "PASAPORTE"
    
    else:
        return "OTRO"
    
def analyze_dob(dob):
    try:
        # Analiza la fecha en varios formatos
        fecha = parser.parse(dob)
    except (ValueError, TypeError):
        # Si ocurre un error, devolver 31 de diciembre de 1969
        print("Error al analizar la fecha, devolviendo fecha predeterminada.")
        fecha = datetime(1969, 12, 31)
    
    # Retorna la fecha en formato dd/mm/yyyy
    return fecha.strftime("%d/%m/%Y")

def final_json(extracted_data):
    if(extracted_data):
        new_json = {}

        if "Nombre" in extracted_data:
            new_json["Nombre"] = extracted_data["Nombre"]
        if "Apellido" in extracted_data:
            new_json["Apellido"] = extracted_data["Apellido"]
        if "Documento" in extracted_data:
            new_json["Documento"] = extracted_data["Documento"]
        if "FechaDeNacimiento" in extracted_data or "fecha de nacimiento" in extracted_data.lower():
            fechaDeNacimiento = analyze_dob(extracted_data["FechaDeNacimiento"])
            new_json["FechaDeNacimiento"] = fechaDeNacimiento
        if "TipoDocumento" in extracted_data or "tipo documento" in extracted_data.lower():
            tipoDocumento = analyze_id_type(extracted_data["TipoDocumento"])
            new_json["TipoDocumento"] = tipoDocumento

        new_json_str = json.dumps(new_json, indent=4, ensure_ascii=False)
        return new_json_str
    else:
        return "No se encontró un JSON válido."

image_path = random_image()
text = extract_text_from_image(image_path)
ollama_text= analyze_text_ollama(text)

ollama_json = extract_json(ollama_text)
print(ollama_json)

final_json = final_json(ollama_json)
print(final_json)
