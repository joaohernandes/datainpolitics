import streamlit as st
import geopandas as gp
import pandas as pd

st.set_page_config(
    page_title="Dashboard Eleitoral",  # Título da página
    page_icon=":bar_chart:",  # Ícone da página (pode ser um emoji ou caminho para uma imagem)
    layout="wide",  # Layout da página ("centered" ou "wide")
    initial_sidebar_state="expanded"  # Estado inicial da barra lateral ("expanded" ou "collapsed")
)
# Adicionar Logo
logo = "aplicacao/img/Main Logo Black.png"
st.image(logo, width=150)
st.title('Olá! Bem-Vindo!')
st.write('##### Todos os dados foram carregados com sucesso!')
st.write('##### Acesse a barra lateral para navegar entre as páginas.')
st.markdown(
    """
    <style>
    div[data-testid="stSelectbox"] > div > div > div {
        background-color: #ADD8E6; /* Cor de fundo */
        color: #000000; /* Cor do texto */
    }
    div[data-testid="stSelectbox"] > div > div > div:hover {
        background-color: #87CEFA; /* Cor de fundo ao passar o mouse */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# Inject custom CSS
st.markdown(
    """
    <style>
    div[data-testid="stMultiSelect"] > div > div > div {
        background-color: #ADD8E6; /* Cor de fundo */
        color: #000000; /* Cor do texto */
    }
    div[data-testid="stMultiSelect"] > div > div > div:hover {
        background-color: #87CEFA; /* Cor de fundo ao passar o mouse */
    }
    div[data-testid="stMultiSelect"] > div > div > div:focus {
        background-color: #4682B4; /* Cor de fundo quando o foco está no componente */
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data()
def carregarDados():
    dadosSP = gp.read_file('aplicacao/Dados/newdatabaseSP.shp')
    dadosSP2022 = gp.read_file('aplicacao/Dados/setores2022Cidades.shp')
    perfil2024 = pd.read_csv('aplicacao/Dados/perfil2024Cidades.csv', decimal=',')
    perfil2020 = pd.read_csv('aplicacao/Dados/perfil2020Cidades.csv', decimal=',')
    boletim1Pref = pd.read_csv('aplicacao/Dados/boletimPrefCidades.csv')
    boletimVere = pd.read_csv('aplicacao/Dados/boletimVereCidades.csv')
    locais2024 = pd.read_csv('aplicacao/Dados/local2024Cidades.csv')
    locais2020 = pd.read_csv('aplicacao/Dados/local2020Cidades.csv')

    return dadosSP, dadosSP2022, perfil2024, perfil2020, boletim1Pref, boletimVere, locais2024, locais2020


# Uso da função em seu aplicativo Streamlit
dadosSP, dadosSP2022, perfil2024, perfil2020, boletim1Pref, boletimVere, locais2024, locais2020 = carregarDados()
if "data" not in st.session_state:
    st.session_state["data"] = dadosSP

if "data2022" not in st.session_state:
    st.session_state["data2022"] = dadosSP2022

if "dataPerfil2024" not in st.session_state:
    st.session_state["dataPerfil2024"] = perfil2024

if "dataPerfil" not in st.session_state:
    st.session_state["dataPerfil"] = perfil2020

if "dataBoletim1Pref" not in st.session_state:
    st.session_state["dataBoletim1Pref"] = boletim1Pref
if "dataBoletimVere" not in st.session_state:
    st.session_state["dataBoletimVere"] = boletimVere
if "dataLocais2024" not in st.session_state:
    st.session_state["dataLocais2024"] = locais2024
if "dataLocais2020" not in st.session_state:
    st.session_state["dataLocais2020"] = locais2020

# Filtrar as cidades 'MARILIA' e 'PRESIDENTE PRUDENTE'
cidades_disponiveis = boletimVere[~boletimVere['NM_MUNICIPIO'].isin(['MARÍLIA', 'PRESIDENTE PRUDENTE'])][
    'NM_MUNICIPIO'].unique()

cidade_selecionada = st.selectbox('Selecione uma Cidade para Análise:', cidades_disponiveis)

# Armazena a seleção na session state
st.session_state['cidade_selecionada'] = cidade_selecionada
# Agora você pode usar a cidade_selecionada para filtrar os dados ou outras operações
st.write(f'Você selecionou: {cidade_selecionada}')
