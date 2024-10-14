# Importamos librerias
import cv2
import pytesseract   #Libreria deteccion de texto
import re

#Código de un video que lee de que nacionalidad es el dni y lo devuelve
# Variables
cuadro = 100
doc = 0

# Captura de video
cap = cv2.VideoCapture(1)
cap.set(3,1280)
cap.set(4,720)

def texto(image):
    global doc
    # Variables
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # Escala de grises
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Umbral
    umbral = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, 25)

    # Configuracion del OCR
    config = "--psm 1"
    texto = pytesseract.image_to_string(umbral, config=config)

    # Palabras clave Colombia
    sececol = r'COLOMBIA'
    sececol2 = r'IDENTIFICACION'

    # Palabras clave Salvador
    secesal = r'SALVADO'

    buscecol = re.findall(sececol, texto)
    buscecol2 = re.findall(sececol2, texto)

    buscesal = re.findall(secesal, texto)

    print(texto)

    # Si es de colombia
    if len(buscecol) != 0 and len(buscecol2) != 0:
        doc = 1

    elif len(buscesal) != 0:
        doc = 2

# Empezamos
while True:
    # Lectura de la VideoCaptura

    #ret indica si la captura fue exitosa o no y cap.read() toma un fotograma de la cámara y lo almacena en frame
    ret, frame = cap.read()

    # 'Interfaz'
    #Agrega texto al fotograma en la posicion indicada con el mensaje ubique el documento de identidad
    #usa la fuente hershey simplex en o.71, color verde y 2 pixeles de grosor
    cv2.putText(frame, 'Ubique el documento de identidad', (458, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.71, (0, 255, 0), 2)
    #Lo mismo pero en vez de poner texto pone un rectangulo donde se debería colocar el documento
    cv2.rectangle(frame, (cuadro, cuadro), (1280 - cuadro, 720 - cuadro), (0, 255, 0), 2)

    # Reset ID

    #si el documento es cero es porque no se identificó de qué pais es el dni
    if doc == 0:
        cv2.putText(frame, 'PRESIONA S PARA IDENTIFICAR', (470, 750 - cuadro), cv2.FONT_HERSHEY_SIMPLEX, 0.71,(0, 255, 0), 2)
        #print(" LISTO PARA DETECTAR ID")

    elif doc == 1:
        cv2.putText(frame, 'IDENTIFICACION COLOMBIANA', (470, 750 - cuadro), cv2.FONT_HERSHEY_SIMPLEX, 0.71,(0, 255, 255), 2)
        print('Cedula de Ciudadania Colombiana')

    elif doc == 2:
        cv2.putText(frame, 'DOCUMENTO SALVADORENO', (470, 750 - cuadro), cv2.FONT_HERSHEY_SIMPLEX, 0.71,(187, 170, 3), 2)
        print('Documento Salvadoreño')

    t = cv2.waitKey(1)
    # Funcion Texto

    # Reset [R] [r]

    #si la letra presionada es s (con codigo 83 o 115 dependiendo si es mayuscula o minuscula) llama a la funcion para extraer datos
    #sino setea al documento en cero y se sigue ejecutando el bucle
    if t == 82 or t == 114:
        doc = 0

    # Scan [S] [s]
    if t == 83 or t == 115:
        texto(frame)

    # Mostramos FPS
    cv2.imshow("ID INTELIGENTE", frame)
    #27 es la tecla de esc y que saca al usuario de la vista
    if t == 27:
        break

cap.release()
cv2.destroyAllWindows()

