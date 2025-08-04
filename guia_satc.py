import streamlit as st
import requests
import os
import random
import pandas as pd
from dotenv import load_dotenv
import streamlit.components.v1 as components

# --- FUNÇÃO DE VERIFICAÇÃO DE SENHA ---
def check_password():
    """Retorna `True` se a senha estiver correta ou se o login já foi feito."""

    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # Usa st.form para agrupar o input e o botão
    with st.form("password_form"):
        st.markdown("### Por favor, digite a senha para acessar o guia:")
        password = st.text_input("Senha", type="password", label_visibility="collapsed")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            # Compara a senha digitada com a senha guardada nos Secrets
            if password == st.secrets["APP_PASSWORD"]:
                st.session_state.password_correct = True
                st.rerun()  # Recarrega a página para mostrar o app
            else:
                st.error("Senha incorreta. Tente novamente.")
    return False

# --- CONFIGURAÇÕES E DADOS GLOBAIS ---

# Carrega as chaves secretas do ficheiro .env
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# IDs das séries, filmes e personagens
SERIES_IDS = { "Sex and the City": 105, "And Just Like That...": 116450 }
MOVIE_IDS = { "Sex and the City: O Filme": 4564, "Sex and the City 2": 37786 }
ORIGINAL_CAST_INFO = [
    {"personagem": "Carrie Bradshaw", "display_name": "Carrie", "ator_id": 520},
    {"personagem": "Samantha Jones", "display_name": "Samantha", "ator_id": 2109},
    {"personagem": "Charlotte York", "display_name": "Charlotte", "ator_id": 38025},
    {"personagem": "Miranda Hobbes", "display_name": "Miranda", "ator_id": 38024},
    {"personagem": "Mr. Big", "display_name": "Mr. Big", "ator_id": 38026}
]
NEW_CAST_INFO = [
    {"personagem": "Che Diaz", "display_name": "Che Diaz", "ator_id": 125055},
    {"personagem": "Seema Patel", "display_name": "Seema", "ator_id": 20275},
    {"personagem": "Lisa Todd Wexley", "display_name": "Lisa", "ator_id": 74615},
    {"personagem": "Dr. Nya Wallace", "display_name": "Dr. Nya", "ator_id": 1398879},
    {"personagem": "Steve Brady", "display_name": "Steve", "ator_id": 27552},
    {"personagem": "Harry Goldenblatt", "display_name": "Harry", "ator_id": 3212}
]
CHARACTER_BIOS = {
    "Carrie Bradshaw": "A narradora da série e colunista do 'New York Star', onde escreve a coluna 'Sex and the City'. Conhecida pela sua paixão pela moda (especialmente sapatos), pelas suas amizades e pela sua complexa e intermitente relação com Mr. Big.",
    "Samantha Jones": "Uma executiva de relações públicas bem-sucedida, independente e sexualmente liberada. É a mais velha do grupo, ferozmente leal e oferece uma perspetiva hilariante e sem rodeios sobre sexo e relacionamentos.",
    "Charlotte York": "Uma negociante de arte e a mais tradicional e otimista do grupo. Uma romântica incurável que acredita no amor e procura o seu 'príncipe encantado', enfrentando desafios de fertilidade e adoção no seu caminho para construir uma família.",
    "Miranda Hobbes": "Uma advogada de Harvard, inteligente, cínica e focada na carreira. A sua visão pragmática e, por vezes, pessimista sobre os relacionamentos e os homens serve como um contraponto para a natureza romântica de Charlotte.",
    "Mr. Big": "Um empresário rico, charmoso e evasivo, que se torna o grande amor da vida de Carrie. A sua relação tumultuada, cheia de idas e vindas, é um dos arcos centrais de toda a série.",
    "Steve Brady": "Um barman com os pés na terra que se torna o namorado intermitente e, eventually, o marido de Miranda. A sua simplicidade e bom coração contrastam com a natureza mais cínica de Miranda.",
    "Harry Goldenblatt": "O advogado de divórcio de Charlotte que, inesperadamente, se torna o amor da sua vida e o seu segundo marido. Apesar de não ser o que Charlotte idealizava, a sua bondade e devoção conquistam-na.",
    "Che Diaz": "Uma comediante de stand-up não-binária e apresentadora de um podcast em que Carrie participa em 'And Just Like That...'. A sua presença desafia as visões de Miranda sobre identidade e relacionamento.",
    "Seema Patel": "Uma bem-sucedida corretora de imóveis de luxo que se torna uma das novas amigas de Carrie em 'And Just Like That...'. É solteira, fabulosa e partilha com Carrie as complexidades de namorar em Nova Iorque numa idade mais madura.",
    "Lisa Todd Wexley": "Uma documentarista e mãe de três filhos que se torna amiga de Charlotte em 'And Just Like That...'. É uma mulher sofisticada e bem-sucedida que navega pelos desafios da alta sociedade de Nova Iorque.",
    "Dr. Nya Wallace": "Uma professora de direito na Universidade de Columbia que se torna amiga de Miranda em 'And Just Like That...'. A sua história explora os desafios da fertilidade e as complexidades de um casamento moderno."
}
STREAMING_LINKS = {
    "Sex and the City": { "Max": "https://play.hbomax.com/show/2641fd06-387f-4d92-a322-accb8e180713", "Netflix": "https://www.netflix.com/title/70136137" },
    "And Just Like That...": { "Max": "https://play.hbomax.com/show/b9c27771-247a-459d-b751-85460d3fd5a2" },
    "Sex and the City: O Filme": { "Max": "https://play.hbomax.com/page/urn:hbo:page:GVU2cNAg6x642iAEAAAAA:type:feature", "Netflix": "https://www.netflix.com/title/70087542" },
    "Sex and the City 2": { "Max": "https://play.hbomax.com/page/urn:hbo:page:GVU2cNAg6x642iAEAAAAA:type:feature", "Netflix": "https://www.netflix.com/title/70122679" }
}
DATE_IDEAS_RJ = [
    {"title": "Almoço com Propósito na Lapa 🍽️", "description": "Que tal um almoço especial e cheio de significado no Gastromotiva Refeitório? Um lugar incrível que une gastronomia e impacto social. Depois, podemos esticar com uma caipirinha em algum bar clássico da Lapa."},
    {"title": "Dia de Museus: do Catete ao Flamengo 🏛️", "description": "Um tour cultural pela vizinhança! Começamos mergulhando na cultura popular no Museu do Folclore (Catete) e depois caminhamos até o Musehum (Flamengo) para explorar a ciência e a humanidade. Terminamos com um lanche ou drink em algum dos charmosos locais da região."},
    {"title": "Um Doce Passeio no Leblon 🍦", "description": "Um encontro leve e delicioso: uma caminhada pela orla do Leblon e uma parada estratégica no quiosque da Bacio di Latte. A desculpa perfeita para colocar o papo em dia com um gelato na mão."},
    {"title": "Piquenique de Rainhas na Quinta da Boa Vista 👑", "description": "Vamos nos sentir da realeza por um dia! Preparamos uma cesta de piquenique e aproveitamos os jardins da Quinta. Se der vontade, podemos dar uma volta no BioParque para ver os animais."},
    {"title": "Arte e Brisa do Mar em Niterói 🌉", "description": "Uma pequena viagem para um grande encontro. Atravessamos a ponte para admirar a arquitetura do MAC, sentir a brisa do mar e almoçar com uma vista espetacular da Baía de Guanabara."},
    {"title": "Magia e Charme no Bondinho de Santa Teresa 🚋", "description": "Hoje o dia é para se encantar. Pegamos o bondinho amarelo, exploramos as ruas de pedra, os ateliês de arte e escolhemos um restaurante com vista para um almoço demorado e especial."},
    {"title": "Café da Manhã com História no Forte de Copacabana ❤️", "description": "Um clássico irresistível. Um café da manhã caprichado na Confeitaria Colombo ou no Café 18 do Forte, com a vista mais icônica do Rio como cenário. Perfeito para começar o dia juntas."},
    {"title": "Passeio Parisiense no Centro do Rio 🌳", "description": "Que tal uma caminhada romântica pela Praça Paris? Seus jardins inspirados em Versalhes são o cenário perfeito para a gente se sentir em um filme. Depois, podemos procurar um bom lugar para comer ali pelo Centro."}
]
ICONIC_PLACES_DATA = {
    'Nome': ["Apartamento da Carrie", "Magnolia Bakery", "New York Public Library", "The Plaza Hotel", "The Loeb Boathouse (Central Park)", "Scout Bar (Onieal's)", "Buddakan Restaurant", "Columbus Circle Fountain", "Jefferson Market Garden"],
    'lat': [40.7389, 40.7423, 40.7531, 40.7647, 40.7753, 40.7198, 40.7424, 40.7680, 40.7354],
    'lon': [-74.0015, -74.0044, -73.9822, -73.9747, -73.9688, -74.0003, -74.0040, -73.9819, -74.0010],
    'Descrição': ["A famosa escadaria onde tantos looks, beijos e momentos aconteceram. O endereço mais icônico da série, no coração do West Village.", "O lugar que iniciou a febre mundial por cupcakes, graças a uma cena rápida de Carrie e Miranda. Parada obrigatória para um doce.", "O grandioso cenário do (quase) casamento de Carrie e Big no primeiro filme. Um lugar que guarda todas as grandes histórias de amor.", "Palco de muitos momentos, mas principalmente da festa de noivado de Big e Natasha, que partiu o coração de Carrie.", "Onde Carrie e Big se encontram para um almoço e acabam caindo (de forma hilária e romântica) no lago do Central Park.", "O bar de Aidan e Steve! Na vida real, o Onieal's é um speakeasy charmoso, palco de muitas conversas e dilemas da série.", "O restaurante asiático deslumbrante onde aconteceu o jantar de ensaio do casamento de Carrie e Big. Pura opulência e glamour.", "A fonte onde Carrie e Aidan terminam o noivado. Um lugar lindo para um momento tão agridoce e decisivo na história.", "O jardim secreto e encantador no West Village onde Miranda e Steve se casaram, provando que o amor não precisa de formalidades." ]
}
df_places = pd.DataFrame(ICONIC_PLACES_DATA)

# --- FUNÇÕES DE API ---
@st.cache_data
def buscar_detalhes_serie(serie_id):
    url = f"https://api.themoviedb.org/3/tv/{serie_id}?api_key={TMDB_API_KEY}&language=pt-BR"
    resposta = requests.get(url)
    return resposta.json() if resposta.status_code == 200 else None

@st.cache_data
def buscar_detalhes_temporada(serie_id, num_temporada, idioma="pt-BR"):
    url = f"https://api.themoviedb.org/3/tv/{serie_id}/season/{num_temporada}?api_key={TMDB_API_KEY}&language={idioma}"
    resposta = requests.get(url)
    return resposta.json() if resposta.status_code == 200 else None

@st.cache_data
def buscar_detalhes_filme(filme_id):
    url = f"https://api.themoviedb.org/3/movie/{filme_id}?api_key={TMDB_API_KEY}&language=pt-BR"
    resposta = requests.get(url)
    return resposta.json() if resposta.status_code == 200 else None

@st.cache_data
def buscar_detalhes_ator(ator_id):
    url = f"https://api.themoviedb.org/3/person/{ator_id}?api_key={TMDB_API_KEY}&language=pt-BR"
    resposta = requests.get(url)
    return resposta.json() if resposta.status_code == 200 else None

# --- PONTO DE ENTRADA DO APP E VERIFICAÇÃO DE SENHA ---
if not check_password():
    st.stop() # Se a senha não estiver correta, para a execução aqui

# --- CONFIGURAÇÃO DA PÁGINA E CSS ---
st.set_page_config(page_title="Guia SATC", page_icon="🍸")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');
    html, body { overflow-x: hidden; }
    .main-title { font-family: 'Great Vibes', cursive; font-weight: 400; font-style: normal; font-size: clamp(3.5em, 8vw, 7em); text-align: center; color: #F8B4D9; overflow-wrap: break-word; }
    .sub-title { text-align: center; color: #CCCCCC; font-style: italic; font-size: 1.2em; margin-top: -20px; }
    .menu-header { text-align: center; color: #CCCCCC; font-style: italic; font-size: 1.5em; margin-top: 20px; margin-bottom: 20px; }
    div[data-testid="column"] img { max-width: 180px; display: block; margin-left: auto; margin-right: auto; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO (st.session_state) ---
if 'pagina_ativa' not in st.session_state:
    st.session_state.pagina_ativa = "INICIO"
if 'temporada_selecionada' not in st.session_state: st.session_state.temporada_selecionada = None
if 'filme_selecionado' not in st.session_state: st.session_state.filme_selecionado = None
if 'personagem_selecionada' not in st.session_state: st.session_state.personagem_selecionada = None
if 'sugestao_gerada' not in st.session_state: st.session_state.sugestao_gerada = False
if 'sugestao_atual' not in st.session_state: st.session_state.sugestao_atual = None

# --- CABEÇALHO PRINCIPAL ---
st.markdown('<p class="main-title">I Couldn\'t Help But Wonder...</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">... um guia definitivo de Sex and the City, feito com amor para a Sara <span style="color: #F8B4D9;">❤️</span></p>', unsafe_allow_html=True)

# Marcador invisível no topo da página para o link "Voltar ao Topo"
st.markdown('<a name="top"></a>', unsafe_allow_html=True)

st.markdown("---")

# --- LÓGICA DE NAVEGAÇÃO E EXIBIÇÃO DAS PÁGINAS ---

# PÁGINA INICIAL (MENU)
if st.session_state.pagina_ativa == "INICIO":
    st.markdown('<p class="menu-header">O que você quer explorar hoje?</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Explorar o Guia da Série", use_container_width=True):
            st.session_state.pagina_ativa = "GUIA"
            st.rerun()
        if st.button("🗺️ Mapa de Lugares Icônicos", use_container_width=True):
            st.session_state.pagina_ativa = "MAPA"
            st.rerun()
    with col2:
        if st.button("👭 Gerador de Encontros Cariocas", use_container_width=True):
            st.session_state.pagina_ativa = "ENCONTROS"
            st.rerun()
        if st.button("🎶 Nossa Trilha Sonora", use_container_width=True):
            st.session_state.pagina_ativa = "TRILHA"
            st.rerun()

# PÁGINA DO GUIA (SÉRIES, FILMES, PERSONAGENS)
elif st.session_state.pagina_ativa == "GUIA":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.temporada_selecionada = None
        st.session_state.filme_selecionado = None
        st.session_state.personagem_selecionada = None
        st.session_state.pagina_ativa = "INICIO"
        st.rerun()
    st.markdown("---")
    
    tipo_conteudo = st.radio(
        "Escolha uma categoria:",
        ("Séries", "Filmes", "Personagens"),
        horizontal=True,
    )

    if tipo_conteudo == "Séries":
        if st.session_state.temporada_selecionada is None:
            for nome_serie, id_serie in SERIES_IDS.items():
                detalhes_da_serie = buscar_detalhes_serie(id_serie)
                if detalhes_da_serie:
                    nome_display = detalhes_da_serie.get('name')
                    if nome_serie == "Sex and the City": nome_display = nome_serie
                    st.header(f"Temporadas de *{nome_display}*")
                    if nome_serie in STREAMING_LINKS:
                        links_serie = STREAMING_LINKS[nome_serie]
                        links_md = [f"[{plataforma}]({url})" for plataforma, url in links_serie.items()]
                        st.markdown(f"**Onde Assistir:** {', '.join(links_md)}")
                    lista_de_temporadas = [t for t in detalhes_da_serie.get('seasons', []) if t.get('season_number') != 0]
                    num_colunas = 6
                    cols = st.columns(num_colunas)
                    col_idx = 0
                    for temporada in lista_de_temporadas:
                        poster_path = temporada.get('poster_path')
                        if poster_path:
                            url_poster = f"https://image.tmdb.org/t/p/w500{poster_path}"
                            with cols[col_idx % num_colunas]:
                                st.image(url_poster)
                                if st.button(f"{temporada.get('name')}", key=temporada.get('id'), use_container_width=True):
                                    st.session_state.temporada_selecionada = (temporada, id_serie, nome_display, lista_de_temporadas, nome_serie)
                                    st.rerun()
                            col_idx += 1
                    st.markdown("---")
        else:
            if isinstance(st.session_state.temporada_selecionada, tuple) and len(st.session_state.temporada_selecionada) == 5:
                temporada, id_da_serie, nome_da_serie, todas_as_temporadas, chave_streaming = st.session_state.temporada_selecionada
            else:
                st.session_state.temporada_selecionada = None
                st.rerun()
            if st.button("⬅️ Voltar para as Temporadas", key="voltar_btn_top"):
                st.session_state.temporada_selecionada = None
                st.rerun()
            st.header(f"{nome_da_serie}")
            st.subheader(f"*{temporada.get('name')}*")
            col1_info, col2_info = st.columns([1, 3])
            with col1_info:
                poster_temporada = temporada.get('poster_path')
                if poster_temporada:
                    st.image(f"https://image.tmdb.org/t/p/w500{poster_temporada}")
            with col2_info:
                sinopse_temporada = temporada.get('overview')
                if sinopse_temporada: 
                    st.write(f"*{sinopse_temporada}*")
                else:
                    st.write("*Sinopse não disponível para esta temporada.*")
                st.markdown("**Onde Assistir:**")
                if chave_streaming in STREAMING_LINKS:
                    links_serie = STREAMING_LINKS[chave_streaming]
                    links_md = [f"- [{plataforma}]({url})" for plataforma, url in links_serie.items()]
                    st.markdown("\n".join(links_md))
                else:
                    st.warning("Não encontrei informações de onde assistir para esta série.")
            st.markdown("---")
            st.subheader("Episódios")
            num_temp = temporada.get('season_number')
            detalhes_temporada_pt = buscar_detalhes_temporada(id_da_serie, num_temp, idioma="pt-BR")
            detalhes_temporada_en = buscar_detalhes_temporada(id_da_serie, num_temp, idioma="en-US")
            if detalhes_temporada_pt and 'episodes' in detalhes_temporada_pt:
                titulos_en = {ep.get('episode_number'): ep.get('name') for ep in detalhes_temporada_en.get('episodes', [])}
                for episodio in detalhes_temporada_pt['episodes']:
                    st.markdown("---")
                    titulo_pt = episodio.get('name')
                    num_ep = episodio.get('episode_number')
                    titulo_final = titulos_en.get(num_ep, titulo_pt) if f"Episódio {num_ep}" in titulo_pt else titulo_pt
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        img_path = episodio.get('still_path')
                        if img_path: st.image(f"https://image.tmdb.org/t/p/w500{img_path}")
                    with col2:
                        st.subheader(f"Ep. {num_ep}: {titulo_final}")
                        st.write(f"*{episodio.get('overview')}*")
                        st.caption(f"Nota Média: {episodio.get('vote_average'):.1f}/10")
                st.markdown("---")
                current_index = -1
                for i, t in enumerate(todas_as_temporadas):
                    if t['id'] == temporada['id']:
                        current_index = i
                        break
                col_nav1, col_nav2, col_nav3 = st.columns([2, 2, 2])
                with col_nav1:
                    if current_index > 0:
                        temporada_anterior = todas_as_temporadas[current_index - 1]
                        if st.button(f"⬅️ {temporada_anterior.get('name')}", use_container_width=True):
                            st.session_state.temporada_selecionada = (temporada_anterior, id_da_serie, nome_da_serie, todas_as_temporadas, chave_streaming)
                            st.rerun()
                with col_nav2:
                    if st.button("⬆️ Todas as Temporadas", use_container_width=True):
                        st.session_state.temporada_selecionada = None
                        st.rerun()
                with col_nav3:
                    if current_index < len(todas_as_temporadas) - 1:
                        proxima_temporada = todas_as_temporadas[current_index + 1]
                        if st.button(f"{proxima_temporada.get('name')} ➡️", use_container_width=True):
                            st.session_state.temporada_selecionada = (proxima_temporada, id_da_serie, nome_da_serie, todas_as_temporadas, chave_streaming)
                            st.rerun()

    elif tipo_conteudo == "Filmes":
        if st.session_state.filme_selecionado is None:
            st.header("Filmes")
            num_colunas_filmes = 6
            cols = st.columns(num_colunas_filmes)
            offset = (num_colunas_filmes - len(MOVIE_IDS)) // 2
            filmes_info = list(MOVIE_IDS.items())
            for i in range(len(filmes_info)):
                nome_filme, id_filme = filmes_info[i]
                with cols[i + offset]:
                    detalhes_filme = buscar_detalhes_filme(id_filme)
                    if detalhes_filme:
                        poster_path = detalhes_filme.get('poster_path')
                        if poster_path:
                            url_poster = f"https://image.tmdb.org/t/p/w500{poster_path}"
                            st.image(url_poster)
                            if st.button(f"Ver Detalhes", key=id_filme, use_container_width=True):
                                st.session_state.filme_selecionado = detalhes_filme
                                st.rerun()
        else:
            if st.button("⬅️ Voltar para os Filmes"):
                st.session_state.filme_selecionado = None
                st.rerun()
            filme = st.session_state.filme_selecionado
            st.header(f"{filme.get('title')} ({filme.get('release_date', '')[:4]})")
            col1, col2 = st.columns([1, 2])
            with col1:
                poster_path = filme.get('poster_path')
                if poster_path: st.image(f"https://image.tmdb.org/t/p/w500{poster_path}")
            with col2:
                st.metric(label="Nota Média (TMDb)", value=f"{filme.get('vote_average', 0):.1f}/10")
                st.write(f"**Sinopse:** {filme.get('overview', 'Não disponível.')}")
                st.subheader("Onde Assistir no Brasil")
                if filme.get('title') in STREAMING_LINKS:
                    links_filme = STREAMING_LINKS[filme.get('title')]
                    links_md = [f"- [{plataforma}]({url})" for plataforma, url in links_filme.items()]
                    st.markdown("\n".join(links_md))
                else:
                    st.warning("Não encontrei informações de onde assistir para este filme.")

    elif tipo_conteudo == "Personagens":
        if st.session_state.personagem_selecionada is None:
            st.header("O Elenco Original")
            cols_originais = st.columns(len(ORIGINAL_CAST_INFO))
            for i, info in enumerate(ORIGINAL_CAST_INFO):
                detalhes = buscar_detalhes_ator(info["ator_id"])
                if detalhes and detalhes.get('profile_path'):
                    with cols_originais[i]:
                        url_poster = f"https://image.tmdb.org/t/p/w500{detalhes['profile_path']}"
                        st.image(url_poster)
                        if st.button(info["display_name"], key=info["ator_id"], use_container_width=True):
                            st.session_state.personagem_selecionada = (info["personagem"], detalhes)
                            st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            st.header("Elenco de Apoio")
            cols_novas = st.columns(len(NEW_CAST_INFO))
            for i, info in enumerate(NEW_CAST_INFO):
                detalhes = buscar_detalhes_ator(info["ator_id"])
                if detalhes and detalhes.get('profile_path'):
                    with cols_novas[i]:
                        url_poster = f"https://image.tmdb.org/t/p/w500{detalhes['profile_path']}"
                        st.image(url_poster)
                        if st.button(info["display_name"], key=info["ator_id"], use_container_width=True):
                            st.session_state.personagem_selecionada = (info["personagem"], detalhes)
                            st.rerun()
        else: 
            nome_personagem, detalhes_ator = st.session_state.personagem_selecionada
            if st.button("⬅️ Voltar para as Personagens"):
                st.session_state.personagem_selecionada = None
                st.rerun()
            st.header(f"{nome_personagem}")
            st.caption(f"Interpretada por **{detalhes_ator.get('name')}**")
            col1, col2 = st.columns([1, 2])
            with col1:
                poster_path = detalhes_ator.get('profile_path')
                if poster_path: st.image(f"https://image.tmdb.org/t/p/w500{poster_path}")
            with col2:
                biografia = CHARACTER_BIOS.get(nome_personagem, "Biografia da personagem não disponível.")
                st.write(f"**Sobre a Personagem:** {biografia}")

# PÁGINA DO GERADOR DE ENCONTROS
elif st.session_state.pagina_ativa == "ENCONTROS":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_ativa = "INICIO"
        st.rerun()
    st.header("Gerador de Encontros Cariocas 👭💕")
    st.markdown("Sem ideias para o nosso próximo encontro? Deixa que a gente te inspira!")
    button_text = "Gerar novo encontro!" if st.session_state.sugestao_gerada else "Clique aqui para uma sugestão!"
    if st.button(button_text, use_container_width=True):
        sugestao = random.choice(DATE_IDEAS_RJ)
        st.session_state.sugestao_atual = sugestao
        st.session_state.sugestao_gerada = True
        st.rerun()
    if st.session_state.sugestao_atual:
        sugestao = st.session_state.sugestao_atual
        st.subheader(f"✨ {sugestao['title']}")
        st.info(sugestao['description'])

# PÁGINA DO MAPA
elif st.session_state.pagina_ativa == "MAPA":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_ativa = "INICIO"
        st.rerun()
    st.header("Mapa de Lugares Icônicos da Série 🗺️")
    st.markdown("Que tal sonharmos com uma viagem para conhecer estes cenários?")
    selected_place_name = st.selectbox(
        'Escolha um lugar para ver no mapa de Nova York:',
        df_places['Nome']
    )
    selected_place_data = df_places[df_places['Nome'] == selected_place_name]
    st.map(selected_place_data)
    st.info(f"**{selected_place_name}:** {selected_place_data['Descrição'].iloc[0]}")

# PÁGINA DA TRILHA SONORA
elif st.session_state.pagina_ativa == "TRILHA":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_ativa = "INICIO"
        st.rerun()
    st.header("Nossa Trilha Sonora 🎶")
    spotify_embed_code = """<iframe data-testid="embed-iframe" style="border-radius:12px" src="https://open.spotify.com/embed/playlist/1QhlZezx4L5D7ittb5LPjD?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>"""
    components.html(spotify_embed_code, height=352)

# --- RODAPÉ E CRÉDITOS ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.9em; color: grey;">
    <p><a href="#top" style="text-decoration: none; color: grey;">⬆️ Voltar ao Topo</a></p>
    <p>Desenvolvido com ❤️ por <strong>Aline Paz</strong></p>
    <p>Dados de filmes e séries fornecidos por <a href="https://www.themoviedb.org/" target="_blank">TMDb</a>.</p>
</div>
""", unsafe_allow_html=True)