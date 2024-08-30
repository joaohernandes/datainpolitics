import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Análise do Eleitorado", layout="wide")
if "dataLocais2020" not in st.session_state:
    st.session_state["dataLocais2020"] = None  # Ou inicialize com algum valor padrão
    st.write("### Dados não foram carregados. Por favor, clique na página -> **|Carregador de Dados|**. Que fica no menu do lado esquerdo da tela.")

# Adicionar Logo
logo = "img/Main Logo Black.png"
st.image(logo, width=150)

# Puxando os dados da sessão
perfil2024 = st.session_state["dataPerfil2024"]
boletim1Pref = st.session_state["dataBoletim1Pref"]
boletimVere = st.session_state["dataBoletimVere"]
locais2024 = st.session_state["dataLocais2024"]
locais2020 = st.session_state["dataLocais2020"]
cidade_selecionada = st.session_state["cidade_selecionada"]

st.write(f'Cidade de Análise: {cidade_selecionada}')

perfil2024Cidade = perfil2024[perfil2024['NM_MUNICIPIO'] == cidade_selecionada]
Local2024 = locais2024[locais2024['NM_MUNICIPIO'] == cidade_selecionada]
mergePerfilLocal = pd.merge(perfil2024Cidade, Local2024, on='NR_SECAO')
mergePerfilLocal['DS_FAIXA_ETARIA'] = mergePerfilLocal['DS_FAIXA_ETARIA'].str.strip()

st.title(f'Perfil do Eleitorado')

# Agrupar por estado civil
qt_estadoCivil = mergePerfilLocal.groupby(['DS_ESTADO_CIVIL'])['QT_ELEITORES_PERFIL'].sum().reset_index()
# Agrupar por genero
qt_genero = mergePerfilLocal.groupby(['DS_GENERO'])['QT_ELEITORES_PERFIL'].sum().reset_index()

col1, col2 = st.columns([2, 2])
# Definir as cores personalizadas
cores_personalizadas = {
    'MASCULINO': 'darkblue',  # Cor mais escura para masculino
    'FEMININO': 'lightblue'  # Cor mais clara para feminino
}
with col1:
    # Criar o gráfico de pizza
    fig = px.pie(qt_genero,
                 values='QT_ELEITORES_PERFIL',
                 names='DS_GENERO',
                 title='Distribuição de Eleitores por Gênero',
                 color='DS_GENERO',
                 color_discrete_map=cores_personalizadas
                 )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)

with col2:
    # Agrupar por faixa etária e somar o número de eleitores
    df_agrupado = mergePerfilLocal.groupby('DS_FAIXA_ETARIA')['QT_ELEITORES_PERFIL'].sum().reset_index()
    # Ordenar as faixas etárias para um melhor visual
    ordem_faixa_etaria = ["16 anos", "17 anos", "18 a 20 anos", "21 a 24 anos", "25 a 34 anos", "35 a 44 anos","45 a 59 anos",
                          "60 a 69 anos","70 a 79 anos", "Superior a 79 anos"]
    df_agrupado['DS_FAIXA_ETARIA'] = pd.Categorical(df_agrupado['DS_FAIXA_ETARIA'], categories=ordem_faixa_etaria,
                                                    ordered=True)
    df_agrupado = df_agrupado.sort_values('DS_FAIXA_ETARIA')


    # Criar o gráfico de barras horizontais
    fig = go.Figure(go.Bar(
        y=df_agrupado['DS_FAIXA_ETARIA'],
        x=df_agrupado['QT_ELEITORES_PERFIL'],
        orientation='h',
        marker=dict(color='steelblue'),
        text=df_agrupado['QT_ELEITORES_PERFIL'],  # Mostrar os valores nas barras
        textposition='auto',  # Mostrar o texto automaticamente
        textangle=0
    ))

    # Customizar o layout
    fig.update_layout(
        title='Distribuição de Eleitores por Faixa Etária',
        # xaxis=''
        yaxis=dict(title='Faixa Etária'),
        bargap=0.1,
        height=600  # Aumentar a altura do gráfico (em pixels)

    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)

# Agrupar os dados por faixa etária e gênero, somando a quantidade de eleitores
grupo_por_genero_faixa = mergePerfilLocal.groupby(['DS_FAIXA_ETARIA', 'DS_GENERO'])[
    'QT_ELEITORES_PERFIL'].sum().unstack().fillna(0)
# Tornar os valores femininos negativos para aparecerem à esquerda
grupo_por_genero_faixa['FEMININO'] = -grupo_por_genero_faixa['FEMININO']
# Ordenar as faixas etárias, incluindo "100 anos ou mais" acima de "90 a 94 anos"
ordem_faixa_etaria = ["16 anos", "17 anos", "18 a 20 anos", "21 a 24 anos", "25 a 34 anos", "35 a 44 anos","45 a 59 anos",
                          "60 a 69 anos","70 a 79 anos", "Superior a 79 anos"]
grupo_por_genero_faixa = grupo_por_genero_faixa.reindex(ordem_faixa_etaria)

# Criar o gráfico de pirâmide etária
fig = go.Figure()

# Adicionar barras de Masculino
fig.add_trace(go.Bar(
    y=grupo_por_genero_faixa.index,
    x=grupo_por_genero_faixa['MASCULINO'],
    name='Masculino',
    orientation='h',
    marker=dict(color='darkblue'),
    hovertemplate='<b>%{y}, Masculino: %{x:.0f}</b><extra></extra>',
    hoverlabel=dict(font_size=16)  # Aumentar o tamanho da fonte para 16
))

# Adicionar barras de Feminino
fig.add_trace(go.Bar(
    y=grupo_por_genero_faixa.index,
    x=grupo_por_genero_faixa['FEMININO'],
    name='Feminino',
    orientation='h',
    marker=dict(color='lightblue'),
    hovertemplate='<b>%{y}, Feminino: %{customdata:.0f}</b><extra></extra>',
    hoverlabel=dict(font_size=16),  # Aumentar o tamanho da fonte para 16]
    customdata=abs(grupo_por_genero_faixa['FEMININO'])  # Usar o valor absoluto no hover
))

# Customizar o layout
fig.update_layout(
    title='Pirâmide Etária por Gênero',
    barmode='overlay',
    xaxis=dict(
        title='',
        showticklabels=False,  # Remover os números do eixo X
        showgrid=False,  # Opcional: remover as linhas da grade no eixo X
        zeroline=False,  # Remover a linha central zero
    ),
    yaxis=dict(
        title='Faixa Etária'
    ),
    bargap=0.1
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig)

# Agrupar por local de votação e somar o número de eleitores
df_local = mergePerfilLocal.groupby('NM_LOCAL_VOTACAO')['QT_ELEITORES_PERFIL'].sum().reset_index()

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

col3, col4 = st.columns([2, 2])
with col3:
    # Agrupar por escolaridade e somar o número de eleitores
    df_agrupadoEscolaridade = mergePerfilLocal.groupby('DS_GRAU_ESCOLARIDADE')[
        'QT_ELEITORES_PERFIL'].sum().reset_index()
    df_agrupadoEscolaridade = df_agrupadoEscolaridade.sort_values('QT_ELEITORES_PERFIL', ascending=True)

    # Criar uma escala de cores com tons de azul
    colors = ['#e0f3ff', '#b3dfff', '#80ccff', '#4db8ff', '#1aa3ff', '#008ae6', '#006bb3', '#004d80']

    # Aplicar a escala de cores às barras
    fig = go.Figure(go.Bar(
        y=df_agrupadoEscolaridade['DS_GRAU_ESCOLARIDADE'],
        x=df_agrupadoEscolaridade['QT_ELEITORES_PERFIL'],
        orientation='h',
        marker=dict(color=colors[:len(df_agrupadoEscolaridade)]),  # Aplicar tons de azul
        text=df_agrupadoEscolaridade['QT_ELEITORES_PERFIL'],  # Mostrar os valores nas barras
        textposition='auto',  # Mostrar o texto automaticamente
    ))

    # Customizar o layout
    fig.update_layout(
        title='Distribuição de Eleitores por Faixa Etária',
        xaxis=dict(title='Quantidade de Eleitores'),
        yaxis=dict(title='Grau de Escolaridade'),
        bargap=0.1,
        height=600  # Aumentar a altura do gráfico (em pixels)
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)

with col4:
    # Criar o gráfico de pizza Estado Civil
    fig = px.pie(qt_estadoCivil,
                 values='QT_ELEITORES_PERFIL',
                 names='DS_ESTADO_CIVIL',
                 title='Distribuição de Eleitores por Estado Civil',
                 color='DS_ESTADO_CIVIL',
                 )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig_local)
