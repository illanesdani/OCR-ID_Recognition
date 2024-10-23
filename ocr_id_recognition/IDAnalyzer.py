import ollama
import json
from PIL import Image
import re
from datetime import datetime
from typing import Annotated
from dateutil import parser
from ImageAnalyzer import extract_json, analyze_date



def analyze_text_ollama(text):
    #modelo de ollama que analizará el prompt
    model="llama3.1"

    prompt = (
    "Please extract the following information from the provided text while ensuring it corresponds accurately to the titles: "
    "Name, Lastname, DateOfBirth, DocumentType, and DocumentNumber. "
    "Transform the date of birth into a string format, such as '10 May 1998', using the month name in English, "
    "and make sure that document number doesnt have any letters, just numbers"
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



def analyze_id_type(id_type):
    id_type = id_type.lower()  # Convertimos todo el texto a minúsculas para facilitar comparaciones
    
    if "documento nacional de identidad" in id_type or "dni" in id_type or "documento" in id_type or re.search(r'documento', id_type):
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
    

def final_json(extracted_data):
    if(extracted_data):
        new_json = {}

        if "Name" in extracted_data:
            new_json["Nombre"] = extracted_data["Name"]
        if "Lastname" in extracted_data:
            new_json["Apellido"] = extracted_data["Lastname"]
        if "DocumentNumber" in extracted_data:
            new_json["Documento"] = extracted_data["DocumentNumber"]
        if "DateOfBirth" in extracted_data or "date of birth" in extracted_data.lower():
            fechaDeNacimiento = analyze_date(extracted_data["DateOfBirth"])
            new_json["FechaDeNacimiento"] = fechaDeNacimiento
        if "DocumentType" in extracted_data or "document type" in extracted_data.lower():
            tipoDocumento = analyze_id_type(extracted_data["DocumentType"])
            new_json["TipoDocumento"] = tipoDocumento

        return new_json
    else:
        return "No se encontró un JSON válido."

def analyze_id(text):
    ollama_text = analyze_text_ollama(text)
    print(ollama_text)
    ollama_json = extract_json(ollama_text)
    print(ollama_json)
    id_json = final_json(ollama_json)
    print(id_json)
    return id_json