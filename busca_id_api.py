import requests
import os
from dotenv import load_dotenv
import json

# Eu carrego a minha chave secreta do ficheiro .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# --- COLOQUE O NOME DO FILME AQUI ---
NOME_DO_FILME_PARA_BUSCAR = "Sex and the City"

# Função para buscar o ID
def encontrar_id_filme(nome_filme):
    print(f"--- Buscando pelo filme: '{nome_filme}' ---")
    url_base = "https://api.themoviedb.org/3/search/movie" # Mudei de /tv para /movie
    parametros = {
        'api_key': TMDB_API_KEY,
        'query': nome_filme,
        'language': 'pt-BR'
    }
    resposta = requests.get(url_base, params=parametros)
    dados = resposta.json()

    if dados.get("results"):
        print("✅ Encontrei os seguintes resultados:")
        for filme in dados["results"]:
            # Imprimo os detalhes mais importantes para a gente identificar o filme certo
            titulo = filme.get('title')
            ano = filme.get('release_date', 'N/A')[:4]
            id_filme = filme.get('id')
            print(f"  - Título: {titulo} ({ano}), ID: {id_filme}")
    else:
        print("❌ Nenhum resultado encontrado.")

# Executa a busca
encontrar_id_filme(NOME_DO_FILME_PARA_BUSCAR)