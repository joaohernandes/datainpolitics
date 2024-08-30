import streamlit as st
import folium
from streamlit_folium import st_folium
import mapclassify as mc
import branca.colormap as cm
from folium.plugins import LocateControl

st.set_page_config(
    page_title="Dados Demográficos",  # Título da página
    page_icon=":🇧🇷:",  # Ícone da página (pode ser um emoji ou caminho para uma imagem)
    layout="wide",  # Layout da página ("centered" ou "wide")
    initial_sidebar_state="expanded"  # Estado inicial da barra lateral ("expanded" ou "collapsed")
)
# Inicializar session_state se a chave não existir
if "data2022" not in st.session_state:
    st.session_state["data2022"] = None  # Ou inicialize com algum valor padrão
try:
    dadosSP2022 = st.session_state["data2022"]
    if dadosSP2022 is None:
        # Mostra uma mensagem personalizada caso não haja dados
        st.write("### Dados não foram carregados. Por favor, clique na página -> **|Carregador de Dados|**. Que fica no menu do lado esquerdo da tela.")
except KeyError as e:
    # Captura e exibe o erro com uma mensagem personalizada
    st.error("### Dados não foram carregados. Por favor, clique na página -> **|Carregador de Dados|**. Que fica no menu do lado esquerdo da tela.")

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

st.title('Análise Demográfica')

dadosSP = st.session_state["data"]
cidade_selecionada = st.session_state["cidade_selecionada"]


loc = {
    'cidade': ['OSVALDO CRUZ', 'PRESIDENTE PRUDENTE', 'ADAMANTINA', 'MARÍLIA', 'LUCÉLIA', 'TUPÃ', 'DRACENA','RANCHARIA'],
    'loc': ['-21.795450918386685, -50.87059777886744','-22.121783307524524, -51.385720678582814','-21.689766076459964, -51.07890033614077','-22.218264211045604, -49.94820592972984','-21.722895152425764, -51.02034509088641','-21.93260724196584, -50.505536035317824','-21.488463664321024, -51.53776488930268','-22.22959408660625, -50.892107735273726']
}
indice = loc['cidade'].index(cidade_selecionada)
coordenada_str = loc['loc'][indice]
# Converte a string de coordenadas para uma tupla de floats
latitude, longitude = map(float, coordenada_str.split(', '))
resultado = (latitude, longitude)

st.write(f'Você está em: {cidade_selecionada}')
dadosSPfiltrado = dadosSP[dadosSP['NM_MUNICIP'] == cidade_selecionada]

coluna_mapeamento = {
    'Rendimento': 'Renda Média',
    'racaBranca': 'Distribuição por Cor/Raça Branca',
    'racaPreta': 'Distribuição por Cor/Raça Preta',
    'racaAmarel': 'Distribuição por Cor/Raça Amarela',
    'racaParda': 'Distribuição por Cor/Raça Parda',
    'racaIndige': 'Distribuição por Cor/Raça Indigena',
    'mulheresRe': 'Mulheres Responsáveis pelo Domicílio',
    'avos': 'Domicilio onde residem Avôs e/ou Avós',
    'SomaSemIlu': 'Localidade sem Iluminação Pública',
    'SomaSemPav': 'Localidade sem Pavimentação',
    'SomaSemCal': 'Localidade sem Calçada',
    'Domicilio_': 'Domicilio sem Energia Elétrica'
}

opcoes = list(coluna_mapeamento.values())

coluna_amigavel_selecionada = st.selectbox("Escolha a categoria para visualização", opcoes)
coluna_selecionada = [k for k, v in coluna_mapeamento.items() if v == coluna_amigavel_selecionada][0]

# Dicionário de colormaps para cada variável
colormap_dict = {
    'Rendimento': cm.linear.YlGn_09,
    'racaBranca': cm.linear.Reds_09,
    'racaPreta': cm.linear.Blues_09,
    'racaAmarel': cm.linear.Oranges_09,
    'racaParda': cm.linear.Purples_09,
    'racaIndige': cm.linear.Greens_09,
    'mulheresRe': cm.linear.PuRd_09,
    'avos': cm.linear.Greys_09,
    'SomaSemIlu': cm.linear.YlOrRd_09,
    'SomaSemPav': cm.linear.YlGnBu_09,
    'SomaSemCal': cm.linear.YlOrBr_09,
    'Domicilio_': cm.linear.BuPu_09,
}

# Seleciona o colormap com base na variável escolhida
colormap = colormap_dict[coluna_selecionada].scale(dadosSPfiltrado[coluna_selecionada].min(),
                                                   dadosSPfiltrado[coluna_selecionada].max())
colormap = colormap.to_step(n=6)

### Mapa ###

st.write(f"### Mapa da {coluna_amigavel_selecionada}")
# E a coluna que você quer usar para coloração seja 'V005'
column = coluna_selecionada

# Classificação dos dados em quantis
quantiles = mc.Quantiles(dadosSPfiltrado[column], k=4)


# Função para determinar o estilo dos polígonos
def style_function(feature):
    value = feature['properties'][column]
    return {
        'fillColor': colormap(value),
        'color': 'black',
        'weight': 0.2,
        'fillOpacity': 0.8,
    }


# Criar o mapa centrado em uma localização específica
m = folium.Map(location=resultado, zoom_start=12)

# Adicionar as geometrias ao mapa com estilo
folium.GeoJson(
    dadosSPfiltrado.to_json(),
    style_function=style_function
).add_to(m)

LocateControl(
    position="topleft",  # Posição do botão no mapa
    strings={"title": "Mostrar minha localização"},  # Texto de dica quando se passa o mouse
    flyTo=True,  # Se deve mover o mapa para a localização encontrada
).add_to(m)

# Adicionar a legenda ao mapa
colormap.caption = coluna_amigavel_selecionada
colormap.add_to(m)

# Adicionar manualmente etiquetas
folium.LayerControl().add_to(m)

# Exibir o mapa
st_folium(m, width=900, height=600)
