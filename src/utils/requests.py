
import requests

def embedding_multilangue( texte,url):
    try:
        response = requests.get(url, params={"texte": texte})
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")
