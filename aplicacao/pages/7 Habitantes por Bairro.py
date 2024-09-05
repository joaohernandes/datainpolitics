import streamlit as st
import folium
from streamlit_folium import st_folium
import mapclassify as mc
import branca.colormap as cm
from folium.plugins import LocateControl

st.set_page_config(
    page_title="Quantidade de Habitantes",  # Título da página
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

dadosSP2022 = st.session_state["data2022"]
cidade_selecionada = st.session_state["cidade_selecionada"]
loc = {
    'cidade': ['OSVALDO CRUZ', 'PRESIDENTE PRUDENTE', 'ADAMANTINA', 'MARÍLIA', 'LUCÉLIA', 'TUPÃ', 'DRACENA','RANCHARIA','PARAPUÃ'],
    'loc': ['-21.795450918386685, -50.87059777886744','-22.121783307524524, -51.385720678582814','-21.689766076459964, -51.07890033614077','-22.218264211045604, -49.94820592972984','-21.722895152425764, -51.02034509088641','-21.93260724196584, -50.505536035317824','-21.488463664321024, -51.53776488930268','-22.22959408660625, -50.892107735273726','-21.777976264553036, -50.79059984550763']
}
indice = loc['cidade'].index(cidade_selecionada)
coordenada_str = loc['loc'][indice]
# Converte a string de coordenadas para uma tupla de floats
latitude, longitude = map(float, coordenada_str.split(', '))
resultado = (latitude, longitude)

cidadelower = str(cidade_selecionada.title())

st.title('Quantidade de Habitantes por Bairro')

dadosSPfiltrado = dadosSP2022[dadosSP2022['NM_MUN'] == cidadelower]

qt_habitantes = dadosSPfiltrado['v0001'].sum()
qt_habitantes_formatado = "{:,}".format(qt_habitantes).replace(',', '.')

st.write(f'###### A cidade de {cidadelower} tem {qt_habitantes_formatado} habitantes')

### Map ###
# Coluna usada para coloração
column = 'v0001'

# Classificação dos dados em quantis
quantiles = mc.Quantiles(dadosSPfiltrado[column], k=6)

# Colormap baseado na paleta 'YlGn'
colormap = cm.linear.YlGn_09.scale(dadosSPfiltrado[column].min(), dadosSPfiltrado[column].max())
colormap = colormap.to_step(n=6)


# Função para determinar o estilo dos polígonos
def style_function(feature):
    value = feature['properties'][column]
    return {
        'fillColor': colormap(value),
        'color': 'black',
        'weight': 0.2,
        'fillOpacity': 0.6,
    }


# Criar o mapa centrado em uma localização específica
m = folium.Map(location=resultado, zoom_start=12)

# Adicionar as geometrias ao mapa com estilo
folium.GeoJson(
    dadosSPfiltrado.to_json(),
    style_function=style_function
).add_to(m)

# Adicionar o controle de localização
LocateControl(
    position="topleft",  # Posição do botão no mapa
    strings={"title": "Mostrar minha localização"},  # Texto de dica quando se passa o mouse
    flyTo=True,  # Se deve mover o mapa para a localização encontrada
).add_to(m)

# Adicionar a legenda ao mapa
colormap.caption = 'Número de Habitantes'
colormap.add_to(m)

# Adicionar controle de camadas
folium.LayerControl().add_to(m)

# Exibir o mapa no Streamlit
st_folium(m, width=800, height=400)

st.write('Dados do IBGE | Censo 2022')