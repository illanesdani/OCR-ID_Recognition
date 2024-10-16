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


def analyze_text_ollama(text):
    #modelo de ollama que analizará el prompt
    model="llama2"

    prompt = (
    "Extract the following information from the provided text, making sure that makes sense with the corresponding title" 
    "and ignore single letters or rare non-letter characters (as long as they are not on the date): "
    "Nombre, Apellido, FechaDeNacimiento, TipoDocumento, and Documento. "
    "Please return the data in a JSON format with the exact field names specified before. "
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


image_path = random_image()
text = extract_text_from_image(image_path)
ollama_text= analyze_text_ollama(text)
final_json = extract_json(ollama_text)
print(final_json)
