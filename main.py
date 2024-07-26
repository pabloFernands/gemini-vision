from google.cloud import vision
import os
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def read_image():
    """Access VisionAi to read the text in the image. Search for a good quality image."""
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../Key-vertex/smart-axis-430501-p2-37b965d9833b.json"
    client = vision.ImageAnnotatorClient()

    # Path of the IMG
    with open('./img/nf-1.jpg', 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    itens_list = []
    for text in texts:
        itens_list.append(text.description)
    
    gemini_help(itens_list)



def gemini_help(itens_list):
    """Access gemini and ask it to organize the information into a formatted string."""
    gemini_key = os.getenv("gemini_key")
    genai.configure(api_key=gemini_key)

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([f"{itens_list}" + "Consegue criar um tabela com essas informações da nota fiscal?"])
    ia_response = response.text
    format_response(ia_response)


def format_response(ia_response):
    """Get the IA response and remover blank lines and another useles lines"""
    ia_response = ia_response.split('\n')[1:]
    data = [linha.strip().split(' | ') for linha in ia_response]
    data = [row for row in data if row != ['|---|---|---|---|---|---|---|']]
    data = [row for row in data if row != ['']]

    #print(data)
    upload_sheets(data)


def upload_sheets(data):
    """Upload all the response for the sheet"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('../Key-vertex/smart-axis-430501-p2-37b965d9833b.json', scope)
    
    try:
        client = gspread.authorize(creds)
        #name of sheet
        spreadsheet = client.open("Mercado gasto")
        sheet = spreadsheet.sheet1

        for linha in data:
            sheet.append_row(linha)
        
        print("Data was loaded successfully.")
    except:
        print("Error. Verify that the spreadsheet exists and is released for the service account.")


read_image()

