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
    with st.form("password_form"):
        st.markdown("### Oi amor! Digite a senha para acessar o guia (dica: a bebida favorita da Carrie):")
        password = st.text_input("Senha", type="password", label_visibility="collapsed")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            # Usamos .get() para que o app não quebre se a secret não existir localmente
            correct_password = st.secrets.get("APP_PASSWORD", "")
            if password == correct_password:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
    return False

# --- DADOS GLOBAIS E FUNÇÕES DE API ---
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# IDs, BIOS, LINKS, etc.
SERIES_IDS = { "Sex and the City": 105, "And Just Like That...": 116450 }
MOVIE_IDS = { "Sex and the City: O Filme": 4564, "Sex and the City 2": 37786 }
MAIN_CAST_INFO = [
    {"personagem": "Carrie Bradshaw", "display_name": "Carrie", "ator_id": 520},
    {"personagem": "Samantha Jones", "display_name": "Samantha", "ator_id": 2109},
    {"personagem": "Charlotte York", "display_name": "Charlotte", "ator_id": 38025},
    {"personagem": "Miranda Hobbes", "display_name": "Miranda", "ator_id": 38024}
]
FRIENDS_AND_LOVERS_INFO = [
    # Amores
    {"personagem": "Mr. Big", "display_name": "Mr. Big", "ator_id": 38026},
    {"personagem": "Aidan Shaw", "display_name": "Aidan", "ator_id": 38405},
    {"personagem": "Steve Brady", "display_name": "Steve", "ator_id": 27552},
    {"personagem": "Harry Goldenblatt", "display_name": "Harry", "ator_id": 3212},
    {"personagem": "Smith Jerrod", "display_name": "Smith", "ator_id": 32224},
    
    # Amigos
    {"personagem": "Stanford Blatch", "display_name": "Stanford", "ator_id": 1542},
    {"personagem": "Anthony Marentino", "display_name": "Anthony", "ator_id": 58058},
    
    # Elenco de "And Just Like That..."
    {"personagem": "Che Diaz", "display_name": "Che Diaz", "ator_id": 125055},
    {"personagem": "Seema Patel", "display_name": "Seema", "ator_id": 20275},
    {"personagem": "Lisa Todd Wexley", "display_name": "Lisa", "ator_id": 74615},
    {"personagem": "Dr. Nya Wallace", "display_name": "Dr. Nya", "ator_id": 1398879},
    
    # Coadjuvante Icônica
    {"personagem": "Magda", "display_name": "Magda", "ator_id": 8792}
]
CHARACTER_BIOS = {
    # Bios que você já tinha
    "Carrie Bradshaw": "A narradora da série e colunista do 'New York Star', onde escreve a coluna 'Sex and the City'. Conhecida pela sua paixão pela moda (especialmente sapatos), pelas suas amizades e pela sua complexa e intermitente relação com Mr. Big.",
    "Samantha Jones": "Uma executiva de relações públicas bem-sucedida, independente e sexualmente liberada. É a mais velha do grupo, ferozmente leal e oferece uma perspetiva hilariante e sem rodeios sobre sexo e relacionamentos.",
    "Charlotte York": "Uma negociante de arte e a mais tradicional e otimista do grupo. Uma romântica incurável que acredita no amor e procura o seu 'príncipe encantado', enfrentando desafios de fertilidade e adoção no seu caminho para construir uma família.",
    "Miranda Hobbes": "Uma advogada de Harvard, inteligente, cínica e focada na carreira. A sua visão pragmática e, por vezes, pessimista sobre os relacionamentos e os homens serve como um contraponto para a natureza romântica de Charlotte.",
    "Mr. Big": "Um empresário rico, charmoso e evasivo, que se torna o grande amor da vida de Carrie. A sua relação tumultuada, cheia de idas e vindas, é um dos arcos centrais de toda a série.",
    "Steve Brady": "Um barman com os pés na terra que se torna o namorado intermitente e, eventualmente, o marido de Miranda. A sua simplicidade e bom coração contrastam com a natureza mais cínica de Miranda.",
    "Harry Goldenblatt": "O advogado de divórcio de Charlotte que, inesperadamente, se torna o amor da sua vida e o seu segundo marido. Apesar de não ser o que Charlotte idealizava, a sua bondade e devoção conquistam-na.",
    "Che Diaz": "Uma comediante de stand-up não-binária e apresentadora de um podcast em que Carrie participa em 'And Just Like That...'. A sua presença desafia as visões de Miranda sobre identidade e relacionamento.",
    "Seema Patel": "Uma bem-sucedida corretora de imóveis de luxo que se torna uma das novas amigas de Carrie em 'And Just Like That...'. É solteira, fabulosa e partilha com Carrie as complexidades de namorar em Nova Iorque numa idade mais madura.",
    "Lisa Todd Wexley": "Uma documentarista e mãe de três filhos que se torna amiga de Charlotte em 'And Just Like That...'. É uma mulher sofisticada e bem-sucedida que navega pelos desafios da alta sociedade de Nova Iorque.",
    "Dr. Nya Wallace": "Uma professora de direito na Universidade de Columbia que se torna amiga de Miranda em 'And Just Like That...'. A sua história explora os desafios da fertilidade e as complexidades de um casamento moderno.",

    # --- NOVAS BIOS ADICIONADAS ---
    "Aidan Shaw": "O segundo grande amor da vida de Carrie. Um designer de móveis charmoso, carinhoso e com os pés no chão. Sua relação com Carrie é marcada pela estabilidade e por um amor genuíno, representando um caminho de vida mais simples e seguro, em contraste direto com o caos de Mr. Big.",
    "Stanford Blatch": "O melhor amigo gay de Carrie e seu confidente mais leal. Estiloso, espirituoso e sempre com um ombro amigo, Stanford navega pelo complexo mundo dos encontros em Nova York ao lado de Carrie, oferecendo uma perspectiva divertida e, por vezes, dolorosamente honesta.",
    "Anthony Marentino": "Inicialmente o planejador de casamentos de Charlotte, Anthony se torna seu melhor amigo gay, com uma língua afiada e um senso de humor impagável. Suas opiniões fortes e seu jeito extravagante o tornam um personagem inesquecível, especialmente em sua hilária rivalidade e posterior casamento com Stanford.",
    "Smith Jerrod": "O jovem e lindo ator que conquista o coração de Samantha. Com sua bondade, paciência e devoção, Smith Jerrod mostra um lado de Samantha que ninguém conhecia, apoiando-a nos momentos mais difíceis e provando ser muito mais do que apenas um rosto bonito. Um verdadeiro príncipe encantado moderno.",
    "Magda": "A governanta ucraniana de Miranda, que se torna uma figura materna e parte essencial da família. Com seus valores tradicionais e seu jeito durão, mas de coração mole, Magda cuida de Miranda, Steve e do pequeno Brady com um amor protetor, oferecendo sabedoria e, claro, garantindo que todos usem um porta-copos."
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

# Dados para o Quiz
QUIZ_QUESTIONS = [
    {
        "question": "Sua noite de sábado ideal é:",
        "answers": {
            "Jantar com as amigas, seguido de uma festa badalada onde posso usar um look novo.": "Carrie",
            "Um encontro quente com alguém interessante... ou talvez dois.": "Samantha",
            "Uma abertura de galeria de arte, seguida de um jantar romântico.": "Charlotte",
            "Pedir comida chinesa, uma garrafa de vinho e relaxar no sofá com um bom filme.": "Miranda"
        }
    },
    {
        "question": "Um 'não' definitivo num relacionamento é...",
        "answers": {
            "Falta de 'borboletas no estômago' ou uma conexão misteriosa.": "Carrie",
            "Sexo ruim. A vida é muito curta para isso.": "Samantha",
            "Falta de boas maneiras ou não querer um compromisso sério.": "Charlotte",
            "Falta de ambição ou inteligência. Preciso de alguém que me desafie.": "Miranda"
        }
    },
    {
        "question": "Suas amigas te procuram para conselhos sobre...",
        "answers": {
            "Dilemas do coração e para analisar mensagens de texto complicadas.": "Carrie",
            "Sexo, confiança e como conseguir o que se quer.": "Samantha",
            "Etiqueta, relacionamentos e o 'felizes para sempre'.": "Charlotte",
            "Carreira, finanças e para ter uma opinião honesta e direta.": "Miranda"
        }
    },
    {
        "question": "Seu drink preferido para uma noite especial:",
        "answers": {
            "Um Cosmopolitan, claro!": "Carrie",
            "Um Dry Martini, bem forte.": "Samantha",
            "Uma taça de champanhe ou vinho branco.": "Charlotte",
            "Uma cerveja gelada ou um whisky. Sem frescura.": "Miranda"
        }
    },
    {
        "question": "Como você lida com um grande problema?",
        "answers": {
            "Analiso demais, escrevo sobre isso e converso com todas as minhas amigas.": "Carrie",
            "Enfrento de frente, sem medo e geralmente saio por cima.": "Samantha",
            "Sigo as regras e procuro a solução mais 'correta' e otimista.": "Charlotte",
            "Crio uma lista de prós e contras e resolvo de forma lógica e racional.": "Miranda"
        }
    }
]
QUIZ_RESULTS = {
    "Carrie": {"img_id": 520, "text": "Você é uma Carrie! Curiosa, romântica e uma amiga leal. Você vive para as grandes perguntas sobre o amor e a vida, e se expressa através do seu estilo único. Suas amizades são seu porto seguro e você não tem medo de seguir seu coração, mesmo que ele se meta em algumas confusões."},
    "Samantha": {"img_id": 2109, "text": "Você é uma Samantha! Poderosa, independente e fabulosamente sem remorsos. Você sabe o que quer e não tem medo de ir atrás, seja na carreira ou na cama. Lealdade é seu sobrenome e você sempre defende suas amigas com unhas e dentes."},
    "Charlotte": {"img_id": 38025, "text": "Você é uma Charlotte! Otimista, sonhadora e com um coração de ouro. Você acredita no poder do amor e busca a beleza e a ordem em tudo. É uma amiga carinhosa, que oferece o ombro e os melhores conselhos sobre etiqueta e relacionamentos."},
    "Miranda": {"img_id": 38024, "text": "Você é uma Miranda! Inteligente, sarcástica e com os pés no chão. Você é a voz da razão do grupo, com uma visão realista e pragmática da vida. Sua carreira é importante, mas seu coração se abre para as pessoas que realmente importam. É uma amiga fiel e protetora."}
}

# DICIONÁRIO DE FRASES PARA O ORÁCULO COM A FONTE
ORACLE_QUOTES = {
    "Carrie": [
        {"quote": "Talvez nossas amigas sejam nossas almas gêmeas e os caras sejam apenas pessoas para nos divertirmos.", "source": "Temporada 4, Episódio 1"},
        {"quote": "Eu gosto do meu dinheiro onde posso vê-lo: pendurado no meu armário.", "source": "Temporada 6, Episódio 9"},
        {"quote": "Afinal, computadores quebram, pessoas morrem, relacionamentos acabam. A única coisa que podemos garantir é que um dia tudo pode ser diferente.", "source": "Temporada 4, Episódio 16"},
        {"quote": "O relacionamento mais emocionante, desafiador e significativo de todos é aquele que você tem consigo mesma.", "source": "Temporada 6, Episódio 20"}
    ],
    "Samantha": [
        {"quote": "Eu te amo, mas eu me amo mais.", "source": "Sex and the City: O Filme"},
        {"quote": "Se eu me preocupasse com o que toda vadia em Nova York está dizendo sobre mim, eu nunca sairia de casa.", "source": "Temporada 3, Episódio 14"},
        {"quote": "Eu não vou ser julgada por você ou pela sociedade. Eu vou usar o que eu quiser e transar com quem eu quiser.", "source": "Temporada 6, Episódio 1"},
        {"quote": "Eu sou uma 'tentante-sexual'. Eu tento de tudo pelo menos uma vez.", "source": "Temporada 3, Episódio 16"}
    ],
    "Charlotte": [
        {"quote": "Eu estou namorando desde os quinze anos. Estou exausta! Onde ele está?", "source": "Temporada 3, Episódio 1"},
        {"quote": "Talvez nós possamos ser as almas gêmeas umas das outras.", "source": "Temporada 4, Episódio 1"},
        {"quote": "Eu amaldiçoo o dia em que você nasceu!", "source": "Sex and the City: O Filme (para o Big)"},
        {"quote": "Amigos são a família que você escolhe.", "source": "Um sentimento de toda a série"}
    ],
    "Miranda": [
        {"quote": "Homens são como táxis. Quando eles estão disponíveis, a luz deles acende.", "source": "Temporada 5, Episódio 1"},
        {"quote": "Como pode algo que parece tão certo, de repente, parecer tão errado?", "source": "Temporada 4, Episódio 12"},
        {"quote": "Sexy é como eu me sinto. E eu me sinto sexy de moletom e camiseta.", "source": "Temporada 2, Episódio 5"},
        {"quote": "Ele está tão na minha.", "source": "Temporada 6, Episódio 14 (sobre Steve)"}
    ]
}

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

# --- PONTO DE ENTRADA DO APP ---
if not check_password():
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA E CSS ---
st.set_page_config(page_title="Guia SATC", page_icon="🍸")
st.markdown("""
        <style>
    @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');
    html, body { overflow-x: hidden; }
    .main-title { font-family: 'Great Vibes', cursive; font-weight: 400; font-style: normal; font-size: clamp(3.5em, 8vw, 7em); text-align: center; color: #F8B4D9; overflow-wrap: break-word; }
    .sub-title { text-align: center; color: #CCCCCC; font-style: italic; font-size: 1.2em; margin-top: -20px; }
    .menu-header { text-align: center; color: #CCCCCC; font-style: italic; font-size: 1.5em; margin-top: 20px; margin-bottom: 20px; }
    
    /* Centraliza a imagem dentro da coluna, já que o tamanho agora é fixo */
    div[data-testid="stImage"] {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'pagina_ativa' not in st.session_state: st.session_state.pagina_ativa = "INICIO"
if 'temporada_selecionada' not in st.session_state: st.session_state.temporada_selecionada = None
if 'filme_selecionado' not in st.session_state: st.session_state.filme_selecionado = None
if 'personagem_selecionada' not in st.session_state: st.session_state.personagem_selecionada = None
if 'sugestao_gerada' not in st.session_state: st.session_state.sugestao_gerada = False
if 'sugestao_atual' not in st.session_state: st.session_state.sugestao_atual = None
if 'oracle_quote' not in st.session_state: st.session_state.oracle_quote = None
if 'quiz_step' not in st.session_state: st.session_state.quiz_step = 0
if 'quiz_scores' not in st.session_state: st.session_state.quiz_scores = {"Carrie": 0, "Samantha": 0, "Charlotte": 0, "Miranda": 0}


# --- CABEÇALHO PRINCIPAL ---
st.markdown('<p class="main-title">I Couldn\'t Help But Wonder...</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">um guia definitivo de Sex and the City, feito para Sara <span style="color: #F8B4D9;">❤️</span></p>', unsafe_allow_html=True)
st.markdown('<a name="top"></a>', unsafe_allow_html=True)
st.markdown("---")

# --- LÓGICA DE NAVEGAÇÃO ---
if st.session_state.pagina_ativa == "INICIO":
    st.markdown('<p class="menu-header">O que você quer explorar hoje?</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📚 Guia da Série", use_container_width=True):
            st.session_state.pagina_ativa = "GUIA"
            st.rerun()
        if st.button("👭 Encontros Cariocas", use_container_width=True):
            st.session_state.pagina_ativa = "ENCONTROS"
            st.rerun()
    with col2:
        if st.button("🔮 Oráculo da Cidade", use_container_width=True):
            st.session_state.pagina_ativa = "ORACULO"
            st.rerun()
        if st.button("🗺️ Mapa de Lugares", use_container_width=True):
            st.session_state.pagina_ativa = "MAPA"
            st.rerun()
    with col3:
        if st.button("🎶 Hello, Lover!", use_container_width=True):
            st.session_state.pagina_ativa = "TRILHA"
            st.rerun()
        if st.button("🥂 O Quiz", use_container_width=True):
            st.session_state.pagina_ativa = "QUIZ"
            st.rerun()

elif st.session_state.pagina_ativa == "GUIA":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.temporada_selecionada = None
        st.session_state.filme_selecionado = None
        st.session_state.personagem_selecionada = None
        st.session_state.pagina_ativa = "INICIO"
        st.rerun()
    st.markdown("---")
    
    tipo_conteudo = st.radio("Escolha uma categoria:", ("Séries", "Filmes", "Personagens"), horizontal=True)

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
                if sinopse_temporada: st.write(f"*{sinopse_temporada}*")
                else: st.write("*Sinopse não disponível para esta temporada.*")
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
            if detalhes_temporada_pt and 'episodes' in detalhes_temporada_pt:
                for episodio in detalhes_temporada_pt['episodes']:
                    st.markdown("---")
                    num_ep = episodio.get('episode_number')
                    titulo_final = episodio.get('name')
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
            st.header("As Quatro Protagonistas")
            cols_principais = st.columns(len(MAIN_CAST_INFO))
            for i, info in enumerate(MAIN_CAST_INFO):
                detalhes = buscar_detalhes_ator(info["ator_id"])
                if detalhes and detalhes.get('profile_path'):
                    with cols_principais[i]:
                        url_poster = f"https://image.tmdb.org/t/p/w500{detalhes['profile_path']}"
                        st.image(url_poster, width=180) # TAMANHO FIXO
                        if st.button(info["display_name"], key=info["ator_id"], use_container_width=True):
                            st.session_state.personagem_selecionada = (info["personagem"], detalhes)
                            st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            st.header("Amigos & Amantes")
            num_colunas = 6
            num_colunas_reais = min(num_colunas, len(FRIENDS_AND_LOVERS_INFO))
            cols_apoio = st.columns(num_colunas_reais)
            for i, info in enumerate(FRIENDS_AND_LOVERS_INFO):
                detalhes = buscar_detalhes_ator(info["ator_id"])
                if detalhes and detalhes.get('profile_path'):
                    with cols_apoio[i % num_colunas_reais]:
                        url_poster = f"https://image.tmdb.org/t/p/w500{detalhes['profile_path']}"
                        st.image(url_poster, width=180) # TAMANHO FIXO
                        if st.button(info["display_name"], key=info["ator_id"], use_container_width=True):
                            st.session_state.personagem_selecionada = (info["personagem"], detalhes)
                            st.rerun()
        else: 
            nome_personagem, detalhes_ator = st.session_state.personagem_selecionada
            if st.button("⬅️ Voltar para Personagens"):
                st.session_state.personagem_selecionada = None
                st.rerun()
            st.header(f"{nome_personagem}")
            st.caption(f"Interpretado(a) por **{detalhes_ator.get('name')}**")
            col1, col2 = st.columns([1, 2])
            with col1:
                poster_path = detalhes_ator.get('profile_path')
                if poster_path: st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=180) # TAMANHO FIXO
            with col2:
                biografia = CHARACTER_BIOS.get(nome_personagem, "Biografia do personagem não disponível.")
                st.write(f"**Sobre o Personagem:** {biografia}")

elif st.session_state.pagina_ativa == "QUIZ":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_ativa = "INICIO"
        st.session_state.quiz_step = 0
        st.session_state.quiz_scores = {"Carrie": 0, "Samantha": 0, "Charlotte": 0, "Miranda": 0}
        st.rerun()
    st.header("O Quiz: Qual delas é você? 🥂")
    st.markdown("---")
    step = st.session_state.quiz_step
    
    if step < len(QUIZ_QUESTIONS):
        question_data = QUIZ_QUESTIONS[step]
        st.subheader(f"Pergunta {step + 1} de {len(QUIZ_QUESTIONS)}")
        st.markdown(f"#### {question_data['question']}")
        
        answers = list(question_data["answers"].keys())
        user_answer = st.radio("Escolha sua resposta:", answers, key=f"q{step}", index=None)

        if st.button("Próxima Pergunta", use_container_width=True):
            if user_answer:
                character = question_data["answers"][user_answer]
                st.session_state.quiz_scores[character] += 1
                st.session_state.quiz_step += 1
                st.rerun()
            else:
                st.warning("Por favor, escolha uma resposta para continuar.")
    else:
        st.balloons()
        st.header("Resultado!")
        final_scores = st.session_state.quiz_scores
        result_char = max(final_scores, key=final_scores.get)
        result_info = QUIZ_RESULTS[result_char]
        
        st.subheader(f"Você é uma {result_char}!")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            ator_details = buscar_detalhes_ator(result_info["img_id"])
            if ator_details and ator_details.get("profile_path"):
                st.image(f"https://image.tmdb.org/t/p/w500{ator_details.get('profile_path')}")

        with col2:
            st.info(f"*{result_info['text']}*")

        if st.button("Refazer o Quiz", use_container_width=True):
            st.session_state.quiz_step = 0
            st.session_state.quiz_scores = {"Carrie": 0, "Samantha": 0, "Charlotte": 0, "Miranda": 0}
            st.rerun()

elif st.session_state.pagina_ativa == "ORACULO":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.oracle_quote = None
        st.session_state.pagina_ativa = "INICIO"
        st.rerun()
    st.header("O Oráculo da Cidade 🔮")
    st.markdown("Precisa de um conselho sobre amor, carreira ou amizade? Escolha sua guru e veja o que ela diria.")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("O que a Carrie diria?", use_container_width=True):
            quote_info = random.choice(ORACLE_QUOTES["Carrie"])
            st.session_state.oracle_quote = ("Carrie", quote_info["quote"], quote_info["source"])
            st.rerun()
        if st.button("O que a Charlotte diria?", use_container_width=True):
            quote_info = random.choice(ORACLE_QUOTES["Charlotte"])
            st.session_state.oracle_quote = ("Charlotte", quote_info["quote"], quote_info["source"])
            st.rerun()
    with c2:
        if st.button("O que a Samantha diria?", use_container_width=True):
            quote_info = random.choice(ORACLE_QUOTES["Samantha"])
            st.session_state.oracle_quote = ("Samantha", quote_info["quote"], quote_info["source"])
            st.rerun()
        if st.button("O que a Miranda diria?", use_container_width=True):
            quote_info = random.choice(ORACLE_QUOTES["Miranda"])
            st.session_state.oracle_quote = ("Miranda", quote_info["quote"], quote_info["source"])
            st.rerun()
            
    if st.session_state.oracle_quote:
        st.markdown("---")
        character, quote, source = st.session_state.oracle_quote
        st.info(f'**{character} diria:**\n\n*"{quote}"*')
        st.caption(f"Fonte: {source}")

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

elif st.session_state.pagina_ativa == "MAPA":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_ativa = "INICIO"
        st.rerun()
    st.header("Mapa de Lugares Icônicos da Série 🗺️")
    st.markdown("Que tal sonharmos com uma viagem para conhecer estes cenários?")
    selected_place_name = st.selectbox('Escolha um lugar para ver no mapa de Nova York:', df_places['Nome'])
    selected_place_data = df_places[df_places['Nome'] == selected_place_name]
    st.map(selected_place_data)
    st.info(f"**{selected_place_name}:** {selected_place_data['Descrição'].iloc[0]}")

elif st.session_state.pagina_ativa == "TRILHA":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_ativa = "INICIO"
        st.rerun()
    st.header("Hello, Lover! 🎶")
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