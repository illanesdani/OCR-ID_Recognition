import cv2
import pytesseract
import json
from PIL import Image

#El codigo este intenta extraer los datos de un documento 

# Configurar la ruta del ejecutable de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Cargar y preprocesar la imagen del DNI
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar un filtro de suavizado para reducir el ruido
    gray = cv2.medianBlur(gray, 3)

    # Opción de aplicar un umbral para mejorar el contraste
    # ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    #Deteccion de bordes para resaltar areas con alto contraste
    edges = cv2.Canny(gray, 50, 150)
    #Contornos de la imagen del dni
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #Dimensiones de la imagen
    img_height, img_width = img.shape[:2]


    for contour in contours:
          # Obtiene el rectángulo delimitador de cada contorno
        x, y, w, h = cv2.boundingRect(contour)

        # Calcula el área del contorno y su proporción respecto al área total de la imagen
        contour_area = w * h
        img_area = img_width * img_height

        # Si el área del contorno es significativa y tiene una forma rectangular (como una foto)
        #if contour_area > 0.05 * img_area and 0.8 < w/h < 1.2:  # Evitar hardcodear valores fijos
            # Dibujar un rectángulo blanco sobre la región de la imagen (para "eliminarla")
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), -1)

    return img

# Extraer texto usando Tesseract
def extract_text_from_image(image_path):
    processed_img = preprocess_image(image_path)
    # Guardar la imagen preprocesada como archivo temporal
    temp_image_path = "dni_test_2.jpg"
    cv2.imwrite(temp_image_path, processed_img)
    
    # Configurar Tesseract (psm 6 para un bloque de texto uniforme)
    custom_config = r'--oem 3 --psm 6'
    
    # Extraer texto de la imagen preprocesada
    text = pytesseract.image_to_string(Image.open(temp_image_path), config=custom_config)
    
    return text

# Analizar el texto y convertirlo en un diccionario (JSON)
def parse_dni_text(text):
    data = {}


    #dividimos el texto en lineas
    lines = text.split('\n')
    # Recorrer todas las líneas del texto
    for i in range(len(lines)):
        line = lines[i].strip()  # Limpiar espacios en blanco alrededor
        keywords=["Nombre", "Apellido", "Documento", "Fecha De Nacimiento", "Nacionalidad", "Sexo"]

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
        """
        # Verificamos si la línea contiene una palabra clave como "Nombre", "Apellido", etc.
        if "Nombre" in line:
            # Suponemos que el valor está en la siguiente línea
            if i + 1 < len(lines):
                data["Nombre"] = lines[i + 1].strip()
        elif "Apellido" in line:
            # Suponemos que el valor está en la siguiente línea
            if i + 1 < len(lines):
                data["Apellido"] = lines[i + 1].strip()
        elif "Sexo" in line:
            # Suponemos que el valor está en la siguiente línea
            if i + 1 < len(lines):
                data["Sexo"] = lines[i + 1].strip()
        elif "Nacionalidad" in line:
            # Suponemos que el valor está en la siguiente línea
            if i + 1 < len(lines):
                data["Nacionalidad"] = lines[i + 1].strip()
        elif "Fecha de Nacimiento" in line:
            # Suponemos que el valor está en la siguiente línea
            if i + 1 < len(lines):
                data["FechaDeNacimiento"] = lines[i + 1].strip()
        elif "Documento" in line :
            # Suponemos que el valor está en la siguiente línea
            if i + 1 < len(lines):
                data["DNI"] = lines[i + 1].strip()
        elif "Fecha de Nacimiento" in line:
            # Suponemos que el valor está en la siguiente línea
            if i + 1 < len(lines):
                data["Fecha_Nacimiento"] = lines[i + 1].strip()
                
    """
    return data

# Convertir los datos a JSON
def dni_to_json(image_path):
    text = extract_text_from_image(image_path)
    dni_data = parse_dni_text(text)
    
    # Convertir el diccionario a JSON
    dni_json = json.dumps(dni_data, indent=4, ensure_ascii=False)
    
    return dni_json

# Ejemplo de uso
image_path = "dni_test.jpg"  # Ruta de tu imagen de DNI
dni_json = dni_to_json(image_path)
print(dni_json)
