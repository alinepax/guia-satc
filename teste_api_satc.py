import requests
import os
from dotenv import load_dotenv
import json

# Eu carrego a minha chave secreta do ficheiro .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def buscar_serie_id(nome_serie):
    """
    Eu uso esta função para buscar uma série na API do TMDb
    e ver os detalhes que ela me retorna.
    """
    print(f"--- Buscando por: '{nome_serie}' ---")
    
    url_base = "https://api.themoviedb.org/3/search/tv"
    parametros = {
        'api_key': TMDB_API_KEY,
        'query': nome_serie,
        'language': 'pt-BR'
    }

    try:
        resposta = requests.get(url_base, params=parametros)
        resposta.raise_for_status() # Verifica se houve algum erro na requisição
        dados = resposta.json()

        if dados.get("results"):
            # Eu pego o primeiro resultado, que geralmente é o mais relevante
            primeiro_resultado = dados["results"][0]
            
            print(f"✅ Encontrado! ID: {primeiro_resultado.get('id')}")
            print("Dados recebidos:")
            # Eu imprimo os dados de forma bonita para conseguir analisar
            print(json.dumps(primeiro_resultado, indent=4, ensure_ascii=False))
        else:
            print("❌ Nenhum resultado encontrado.")

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na minha requisição: {e}")

# --- MINHA EXECUÇÃO ---
if __name__ == "__main__":
    buscar_serie_id("Sex and the City")
    print("\n" + "="*40 + "\n") # Uma linha para separar
    buscar_serie_id("And Just Like That...")
