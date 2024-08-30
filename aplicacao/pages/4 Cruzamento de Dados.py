import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Análise do Eleitorado", layout="wide")
# Inicializar session_state se a chave não existir
if "dataLocais2020" not in st.session_state:
    st.session_state["dataLocais2020"] = None  # Ou inicialize com algum valor padrão
    st.write("### Dados não foram carregados. Por favor, clique na página -> **|Carregador de Dados|**. Que fica no menu do lado esquerdo da tela.")
# Adicionar Logo
logo = "aplicacao/img/Main Logo Black.png"
st.image(logo, width=150)
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

# Puxando os dados da sessão
perfil2024 = st.session_state["dataPerfil2024"]
boletim1Pref = st.session_state["dataBoletim1Pref"]
boletimVere = st.session_state["dataBoletimVere"]
locais2024 = st.session_state["dataLocais2024"]
locais2020 = st.session_state["dataLocais2020"]
cidade_selecionada = st.session_state["cidade_selecionada"]

st.write(f'Cidade de Análise: {cidade_selecionada}')

st.title(f'Cruzamento de Dados do Perfil do Eleitorado')
st.write(f'##### Cruze informações do Perfil do Eleitor para descobrir quantos eleitores de um determinado perfil existem em cada Local de Votação')

perfil2024Cidade = perfil2024[perfil2024['NM_MUNICIPIO'] == cidade_selecionada]
Local2024 = locais2024[locais2024['NM_MUNICIPIO'] == cidade_selecionada]
mergePerfilLocal = pd.merge(perfil2024Cidade, Local2024, on='NR_SECAO')

col1, col2 = st.columns(2)
with col1:
    # Filtrar os dados com base no perfil do eleitor
    faixa_etaria = st.selectbox('Selecione a faixa etária:', mergePerfilLocal['DS_FAIXA_ETARIA'].unique())
    genero = st.selectbox('Selecione o gênero:', mergePerfilLocal['DS_GENERO'].unique())

with col2:
    escolaridade = st.selectbox('Selecione a escolaridade:', mergePerfilLocal['DS_GRAU_ESCOLARIDADE'].unique())
    estado_civil = st.selectbox('Selecione o estado civil:', mergePerfilLocal['DS_ESTADO_CIVIL'].unique())

perfilCruzado = mergePerfilLocal[mergePerfilLocal['DS_FAIXA_ETARIA'] == faixa_etaria]
perfilCruzado2 = perfilCruzado[perfilCruzado['DS_GENERO'] == genero]
perfilCruzado3 = perfilCruzado2[perfilCruzado2['DS_GRAU_ESCOLARIDADE'] == escolaridade]
perfilCruzado4 = perfilCruzado3[perfilCruzado3['DS_ESTADO_CIVIL'] == estado_civil]

# Agrupar por local de votação e somar o número de eleitores
df_local = perfilCruzado4.groupby('NM_LOCAL_VOTACAO')['QT_ELEITORES_PERFIL'].sum().reset_index()

# Criar o gráfico de barras
fig_local = go.Figure(go.Bar(
    x=df_local['NM_LOCAL_VOTACAO'],
    y=df_local['QT_ELEITORES_PERFIL'],
    marker=dict(color='blue'),  # Aplicar tons de azul
    text=df_local['QT_ELEITORES_PERFIL'],  # Mostrar os valores nas barras
    textposition='auto',  # Mostrar o texto automaticamente
))

# Customizar o layout
fig_local.update_layout(
    title='Quantidade de Eleitores por Local de Votação',
    xaxis=dict(title='Local de Votação'),
    yaxis=dict(title='Quantidade de Eleitores'),
    height=500
)
# Exibir o gráfico no Streamlit
st.plotly_chart(fig_local)
