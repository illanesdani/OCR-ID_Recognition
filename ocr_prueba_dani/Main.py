import pytesseract
import cv2
import json
from PIL import Image
import re
import random



import pytesseract.pytesseract

#configuracion de la orientacion de la pagina y el modelo de ocr
custom_config = r"--psm 1 --oem 3"

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def random_image():
    #a partir de un numero aleatorio se selecciona un dni de los guardados en el archivo con sus rutas absolutas
    num = random.randint(1,10)

    if num == 1:
        print("Documento argentina nuevo")
        return "DocumentosPrueba/dni_argentina_nuevo.png"
    elif num == 2:
        print("Documento argentina")
        return "DocumentosPrueba/dni_argentina.jpg"
    elif num == 3:
        print("Documento brasil")
        return "DocumentosPrueba/dni_brasil.jpg"
    elif num == 4:
        print("Documento chile")
        return "DocumentosPrueba/dni_chile.png"
    elif num == 5:
        print("Documento españa")
        return "DocumentosPrueba/dni_españa.jpg"
    elif num == 6:
        print("Documento newYork")
        return "DocumentosPrueba/dni_newYork.jpg"
    elif num == 7:
        print("Documento peru")
        return "DocumentosPrueba/dni_peru.png"
    elif num == 8:
        print("Documento tenesse")
        return "DocumentosPrueba/dni_tenesse.png"
    elif num == 9:
        print("Documento uruguay")
        return "DocumentosPrueba/dni_uruguay.jpg"
    else:
        print("Documento usa")
        return "DocumentosPrueba/dni_usa.jpg"

def preprocess_image(image_path):

    #Se lee la imagen, se la convierte a escala de grises, se le queda el ruido y se le setea un umbral
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    umbral = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, 25)

    return umbral

def extract_text_from_image(image_path):
    #se crea una imagen temporal copia de la imagen original pero procesada anteriormente y se extrae el texto
    processed_img= preprocess_image(image_path)
    temp_img_path = "dni_temporal.jpg"
    cv2.imwrite(temp_img_path, processed_img)
    text = pytesseract.image_to_string(Image.open(temp_img_path), config=custom_config)

    return text
    

def process_image_text(text):

    #USA es el unico pais con formato distinto entonces se procesa aparte
    usa=["USA","United States Of America","United States of America"]
    keywords=["Nombre","Nombres","Apellido","Apellidos","ID","Documento","RUN","RUT", "Nacimiento", "Fecha de Nacimiento"]
    #futuro JSON donde se guardarán los datos
    data={}

    #dividimos el texto en lineas
    lines = text.split('\n')

    buscUSA = ""
    global type
    global tipoDocumento

    for u in usa:
        buscUSA += ''.join(re.findall(u, text))

    if len(buscUSA) != 0:
        type = "usa"
    else:
        type= "otro"

    if len(re.findall("Documento Nacional de Identidad", text)) != 0  or len(re.findall("DNI", text)) != 0:
        tipoDocumento = "DNI"
    elif len(re.findall("Pasaporte", text)) != 0  or len(re.findall("Passport", text)) != 0:
        tipoDocumento = "Pasaporte"
    elif len(re.findall("DL", text)) != 0 or len(re.findall("Driver License", text)) != 0 or len(re.findall("Driver's License", text)) != 0 :
        tipoDocumento = "Otro"
    else:
        tipoDocumento=""

    data["TipoDocumento"] = tipoDocumento

    for i in range(len(lines)):
        line = lines[i].strip()

        if(type == "usa"):
            data["nombre"] = "nombre prueba"
            #después pienso esto
        else:
            for keyword in keywords:
                if(keyword in line):
                    if(keyword == "Sexo" or keyword == "Nacionalidad"):
                        #si el titulo está en la linea, verificamos que haya una linea debajo
                        if i + 1 < len(lines):
                            #Extraemos de donde empieza el título
                            start_pos = line.find(keyword)
                            print(start_pos)
                            #Extraemos la longitud del título
                            keyword_length=len(keyword)
                            #extraemos la proxima linea y sacamos los espacios al inicio y al costado
                            next_line = lines[i + 1].strip()
                            #Ahora de la linea sacamos solo lo que está debajo de las posiciones del titulo
                            extracted_value = next_line[start_pos:start_pos + keyword_length].strip()
                            data[keyword] = extracted_value
                    else:
                        if i + 1 < len(lines):
                            data[keyword] = lines[i + 1].strip()

    return data


def dni_to_json(image_path):
    text = extract_text_from_image(image_path)
    dni_data= process_image_text(text)

    dni_json = json.dumps(dni_data, indent=4, ensure_ascii=False)

    return dni_json

image_path = random_image()
dni_json = dni_to_json(image_path)
print(dni_json)








    





