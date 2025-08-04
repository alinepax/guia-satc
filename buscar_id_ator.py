import requests
import os
from dotenv import load_dotenv
import json

# Eu carrego a minha chave secreta do ficheiro .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# --- COLOQUE A LISTA DE NOMES AQUI ---
# Agora eu tenho uma lista com todos os nomes que quero buscar
NOMES_PARA_BUSCAR = [
    "Sarah Jessica Parker",
    "Kim Cattrall",
    "Kristin Davis",
    "Cynthia Nixon",
    "Chris Noth",
    "Sara Ramirez", # Che Diaz
    "Sarita Choudhury", # Seema Patel
    "Nicole Ari Parker", # Lisa Todd Wexley
    "Karen Pittman", # Dr. Nya Wallace
    "David Eigenberg", # Steve Brady
    "Evan Handler" # Harry Goldenblatt
]

# Função para buscar o ID da pessoa
def encontrar_id_pessoa(nome_pessoa):
    print(f"--- Buscando por: '{nome_pessoa}' ---")
    url_base = "https://api.themoviedb.org/3/search/person" # O endpoint para pessoas
    parametros = {
        'api_key': TMDB_API_KEY,
        'query': nome_pessoa
    }
    resposta = requests.get(url_base, params=parametros)
    dados = resposta.json()

    if dados.get("results"):
        print("✅ Encontrei os seguintes resultados:")
        for pessoa in dados["results"]:
            # Imprimo os detalhes para a gente identificar a pessoa certa
            nome = pessoa.get('name')
            departamento = pessoa.get('known_for_department')
            id_pessoa = pessoa.get('id')
            print(f"  - Nome: {nome} (Conhecida por: {departamento}), ID: {id_pessoa}")
    else:
        print("❌ Nenhum resultado encontrado.")

# --- Executa a busca para cada nome na minha lista ---
for nome in NOMES_PARA_BUSCAR:
    encontrar_id_pessoa(nome)
    print("\n" + "="*40 + "\n") # Adiciono uma linha para separar os resultados
