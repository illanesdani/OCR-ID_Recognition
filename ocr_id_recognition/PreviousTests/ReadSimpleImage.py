import pytesseract
import cv2
import json
from PIL import Image
import re


#el codigo a continuación lee sólo una imagen normal y simple


#configuración de los numeros a utilizar para el psm y el oem
myconfig= r"--psm 6 --oem 3"


#Especificacion de la ruta de tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'




try:
    image_path="text_example.jpg"
    img= cv2.imread(image_path)
    text = pytesseract.image_to_string(img, config=myconfig)
    heoght, width, _ = img.shape
    print(text)


except FileNotFoundError:
    print(f"Error: El archivo {image_path} no se encuentra.")
except pytesseract.pytesseract.TesseractError as e:
    print(f"Error al ejecutar Tesseract: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
           
