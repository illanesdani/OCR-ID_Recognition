import random
import ollama
import re
from ImageAnalyzer import analyze_image, analyze_date, extract_json

def random_image():
    num = random.randint(1,5)

    rutas = {
        1: "TicketsPrueba/ticket_1.jpg",
        2: "TicketsPrueba/ticket_2.jpg",
        3: "TicketsPrueba/ticket_3.jpg",
        4: "TicketsPrueba/ticket_4.jpg",
        5: "TicketsPrueba/ticket_5.jpg"

    }

    return(rutas[num])


def analyze_text_ollama(text):
    model="llama3.1"

    prompt = (
        "Please extract the following information from the provided text while ensuring it corresponds accurately to the titles: "
        "Date, Currency, FinalAmount, TypeOfExpense"
        "Transform the date of the expense into a string format, such as '10 May 1998', using the month name in English, "
        "and make sure that the type of expense is one of the following: "
        "Fuel, Toll, Food, Accommodation, Repair or Other"
        "The currency types are argentinian pesos, chilenian pesos, dollars an reales"
        "Also, ignore any single letters or unusual non-letter characters. "
        "Return the extracted data in JSON format with the exact field names specified above. "
        "Only provide the JSON response without any additional text. Here is the text:\n"
        f"{text}"
    )

    response = ollama.chat(model=model, messages= [
         {
            'role':'user',
            'content':prompt
        }
    ])

    extracted_data = response['message']['content']
    return extracted_data

def analyze_expense_type(expense_type):
    expense_type = expense_type.lower()

    if("fuel" in expense_type or "combustible" in expense_type or re.search(r'combustible', expense_type)  or re.search(r'fuel', expense_type)):
        return "COMBUSTIBLE"
    
    if("toll" in expense_type or "peaje" in expense_type or re.search(r'peaje', expense_type) or re.search(r'toll', expense_type) ):
        return "PEAJE"
    
    if("food" in expense_type or "comida" in expense_type or re.search(r'comida', expense_type) or re.search(r'food', expense_type) ):
        return "COMIDA"
    
    if("accommodation" in expense_type or "alojamiento" in expense_type or re.search(r'alojamiento', expense_type) or re.search(r'accommodation', expense_type) ):
        return "ALOJAMIENTO"
    
    if("repair" in expense_type or "arreglo" in expense_type or re.search(r'arreglo', expense_type) or re.search(r'repair', expense_type) ):
        return "COMBUSTIBLE"
    else:
        return "OTRO"
    
def analyze_currency(currency):
    currency = currency.lower()

    if("dollar" in currency or "dolar" in currency or "usd" in currency or re.search(r'dollar', currency)  or re.search(r'dollar', currency)):
        return "1ba246ad-c25a-4de8-a38d-ef02663d5a7f"
      
    if("pesos argentinos" in currency or "argentinian pesos" in currency or re.search(r'ars', currency)  or re.search(r'pesos argentinos', currency)):
        return "bdb9dd01-49e0-4e33-aa07-a8915cd0db10"
    
    if("pesos chilenos" in currency or "chilenian pesos" in currency or re.search(r'clp', currency)  or re.search(r'pesos chilenos', currency)):
        return "bdb9dd01-49e0-4e33-aa07-a8915cd0db11"
    
    if("reales" in currency or "reais" in currency or "r" in currency or re.search(r'reales', currency)  or re.search(r'reais', currency)):
        return "ada02306-dca7-4442-b54f-c3af23731b11"
    else:
        return None
    

def final_json(extracted_data):
    if(extracted_data):
        new_json= {}

        if "Date" in extracted_data:
            new_json["Fecha"] = analyze_date(extracted_data["Date"])

        if "Currency" in extracted_data:
            new_json["idMoneda"] = analyze_currency(extracted_data["Currency"])
        
        if "FinalAmount" in extracted_data:
            new_json["montoLocal"] = extracted_data["FinalAmount"]
        
        if "TypeOfExpense" in extracted_data:
            new_json["TipoGasto"] = analyze_expense_type(extracted_data["TypeOfExpense"])

        return new_json
    else:
        return 

def analyze_ticket(text):
    ollama_text= analyze_text_ollama(text)
    print(ollama_text)
    ollama_json= extract_json(ollama_text)
    print(ollama_json)
    id_json= final_json(ollama_json)
    print(id_json)

    return id_json
