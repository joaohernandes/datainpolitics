import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Dashboard Eleitoral", layout="wide")
# Adicionar Logo
logo = "aplicacao/img/Main Logo Black.png"
st.image(logo, width=150)
if "dataLocais2020" not in st.session_state:
    st.session_state["dataLocais2020"] = None  # Ou inicialize com algum valor padrão
    st.write("### Dados não foram carregados. Por favor, clique na página -> **|Carregador de Dados|**. Que fica no menu do lado esquerdo da tela.")
# Puxando os dados da sessão
perfil2024 = st.session_state["dataPerfil2024"]
perfil2020 = st.session_state["dataPerfil"]
boletim1Pref = st.session_state["dataBoletim1Pref"]
boletimVere = st.session_state["dataBoletimVere"]
locais2024 = st.session_state["dataLocais2024"]
locais2020 = st.session_state["dataLocais2020"]
cidade_selecionada = st.session_state["cidade_selecionada"]

# Inject custom CSS
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

st.write(f'Cidade de Análise: {cidade_selecionada}')

boletimVereCidade = boletimVere[boletimVere['NM_MUNICIPIO'] == cidade_selecionada]
boletim1PrefCidade = boletim1Pref[boletim1Pref['NM_MUNICIPIO'] == cidade_selecionada]
perfil2024Cidade = perfil2024[perfil2024['NM_MUNICIPIO'] == cidade_selecionada]
perfil2020Cidade = perfil2020[perfil2020['NM_MUNICIPIO'] == cidade_selecionada]
Local2020 = locais2020[locais2020['NM_MUNICIPIO'] == cidade_selecionada]
Local2024 = locais2024[locais2024['NM_MUNICIPIO'] == cidade_selecionada]

mergePerfilLocal = pd.merge(perfil2024Cidade, Local2024, on='NR_SECAO')
mergeBoletim1Vere = pd.merge(boletimVereCidade, Local2020, on='NR_SECAO')
mergeBoletim1Pref = pd.merge(boletim1PrefCidade, Local2020, on='NR_SECAO')

# Operações
totalVotosVereadores = boletimVereCidade['QT_VOTOS'].sum()
totalVotosPrefeitos1 = boletim1PrefCidade['QT_VOTOS'].sum()
totalEleitores2020 = perfil2020Cidade['QT_ELEITORES_PERFIL'].sum()
totalEleitores2024 = perfil2024Cidade['QT_ELEITORES_PERFIL'].sum()
taxaParticipacao = (totalVotosVereadores / totalEleitores2020) * 100

# Cabeçalho
st.title("Eleições Municipais 2020 - Visão Geral")
# "{:,}".format(totalVotosVereadores).replace(",", ".")

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size: 20px;">Total de Votos em 2020</h1>
                <p style="font-size: 40px;">{"{:,}".format(totalVotosVereadores).replace(",", ".")}</p>
            </div>
        """, unsafe_allow_html=True)
col2.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size: 20px;">Total de Eleitores Aptos a Votar em 2024</h1>
                <p style="font-size: 40px;">{"{:,}".format(totalEleitores2024).replace(",", ".")}</p>
            </div>
        """, unsafe_allow_html=True)
col3.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size: 20px;">Porcentagem de Eleitores que votaram para vereador em 2020</h1>
                <p style="font-size: 40px;">{f"{taxaParticipacao:.2f}%"}</p>
            </div>
        """, unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)
# Criar Fitro para selecionar Prefeito ou Vereador
tipo_eleicao = st.selectbox('Selecione um tipo de eleição:', placeholder='Escolha um tipo de eleição',
                            options=('Vereador', 'Prefeito'))

# Dividir a página em duas colunas
if 'Vereador' in tipo_eleicao:
    candidatos_unicos = sorted(mergeBoletim1Vere['NM_VOTAVEL'].astype(str).unique())
    candidatos_selecionados = st.multiselect('Selecione Candidatos para Analise', candidatos_unicos)

    # Criar Fitro para selecionar candidatos
    # Filtrar o DataFrame conforme os candidatos selecionados
    df_fil_candidatos = mergeBoletim1Vere[mergeBoletim1Vere['NM_VOTAVEL'].isin(candidatos_selecionados)]

    # Proporção de Votos por Seção
    if candidatos_selecionados:
        totalVotosSecao = mergeBoletim1Vere.groupby('NM_LOCAL_VOTACAO', )['QT_VOTOS'].sum().reset_index()
        # Agrupar os votos por seção e calcular o total de votos por seção
        df_total_votos_secao = totalVotosSecao.rename(columns={'QT_VOTOS': 'TOTAL_VOTOS_SECAO'})

        # Agrupar os votos por candidato e seção
        df_votosSecaoCandidato = df_fil_candidatos.groupby(['NM_VOTAVEL', 'NM_LOCAL_VOTACAO']).agg(
            {'QT_VOTOS': 'sum'}).reset_index()

        # Mesclar os dois dataframes para obter o total de votos por seção em cada linha
        df_votosSecaoCandidato = pd.merge(df_votosSecaoCandidato, df_total_votos_secao, on='NM_LOCAL_VOTACAO')

        # Calcular a proporção de votos para cada candidato em cada seção
        df_votosSecaoCandidato['PROPORCAO_VOTOS'] = df_votosSecaoCandidato['QT_VOTOS'] / df_votosSecaoCandidato[
            'TOTAL_VOTOS_SECAO']

        # Criar um gráfico de barras usando Plotly Express com rótulos de dados
        fig = px.bar(df_votosSecaoCandidato,
                     x='NM_LOCAL_VOTACAO',
                     y='PROPORCAO_VOTOS',
                     color='NM_VOTAVEL',
                     text='PROPORCAO_VOTOS',  # Adiciona os rótulos de dados
                     labels={'PROPORCAO_VOTOS': 'Proporção de Votos', 'NM_LOCAL_VOTACAO': 'Local de Votação'},
                     title='Proporção de Votos por Candidato e Local de Votação',
                     barmode='group',
                     color_discrete_sequence=px.colors.qualitative.Plotly)

        # Atualizar o layout para melhor exibir os rótulos
        fig.update_traces(texttemplate='%{text:.2%}',
                          textposition='outside')  # Formato de porcentagem e posição externa
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', height=600, margin=dict(t=50),
                          xaxis_tickangle=-45)
        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)

        st.write(
            "**Dica:** Analise em quais locais de votação esses candidatos foram melhor e na página **PERFIL POR SEÇÃO** **descubra** qual o **perfil do eleitor** que vota naquele local")
        st.write('**Clique no botão abaixo e descubra o Perfil do Eleitor de cada seção.**')
        if st.button('Clique Aqui'):
            switch_page('perfil por seção')

        st.write('### O que entender a partir deste gráfico?')
        st.markdown("""
                        <div style='text-align: justify;'>
                        Este gráfico é importante para um candidato a porque mostra a proporção de votos por seção para diferentes candidatos.

                Aqui estão alguns motivos pelos quais essa análise é essencial:

                -**Identificação de Padrões Geográficos:** O gráfico permite ao candidato **identificar** onde ele está mais **forte** ou **fraco** em termos de apoio eleitoral. Isso pode indicar áreas onde o candidato precisa **concentrar** mais esforços de campanha ou onde ele já tem uma base sólida.

                -**Comparação com Concorrentes:** Ao comparar sua performance com outros candidatos, o candidato pode **entender melhor** como sua campanha está se saindo em **diferentes regiões** em relação aos **concorrentes.**

                -**Ajuste de Estratégias de Campanha:** Com base nas áreas onde a proporção de votos é mais baixa, o candidato pode **ajustar** sua **mensagem ou suas atividades** de campanha para melhorar seu desempenho nessas regiões.

                -**Foco em Seções Estratégicas:** **Identificar seções** onde há uma disputa acirrada pode ser crucial para decidir onde **concentrar recursos e esforços** para garantir uma **vitória** em áreas estratégicas.

                -**Tomada de Decisões:** Analisar as seções com **melhor** ou **pior** desempenho pode ajudar o candidato a tomar decisões informadas sobre onde **intensificar** visitas, eventos e presença em geral.

                **Em resumo, este tipo de análise ajuda o candidato a alocar recursos de maneira mais eficiente e a ajustar sua estratégia de campanha de forma a maximizar seu apoio eleitoral.**
                        </div>
                        """, unsafe_allow_html=True)

    else:
        st.markdown("""Selecione ao menos um candidato para a Análise""")
        st.write("##### Top candidatos com mais votos")
        mergeBoletim1VereFil = mergeBoletim1Vere[~mergeBoletim1Vere['NM_VOTAVEL'].isin(['Branco', 'Nulo'])]
        df_grouped = mergeBoletim1VereFil.groupby('NM_VOTAVEL', as_index=False)['QT_VOTOS'].sum()

        # Pegue os 4 candidatos mais votados
        top_4 = df_grouped.nlargest(4, 'QT_VOTOS')

        # Criar as colunas no Streamlit
        col1, col2, col3, col4 = st.columns(4)

        # Iterar pelos candidatos mais votados e exibir as informações
        for i, (col, row) in enumerate(zip([col1, col2, col3, col4], top_4.itertuples())):
            nome = row.NM_VOTAVEL
            votos = row.QT_VOTOS

            col.markdown(f"""
                    <div style="text-align: center;">
                        <h1 style="font-size: 20px;">{nome}</h1>
                        <p style="font-size: 40px;">{votos} votos</p>
                    </div>
                """, unsafe_allow_html=True)
if tipo_eleicao in "Prefeito":
    candidatos_selecionados2 = st.multiselect('Selecione Candidatos para Analise',
                                              sorted(mergeBoletim1Pref['NM_VOTAVEL'].unique()))
    # Criar Fitro para selecionar candidatos
    # Filtrar o DataFrame conforme os candidatos selecionados
    df_fil_candidatos = mergeBoletim1Pref[mergeBoletim1Pref['NM_VOTAVEL'].isin(candidatos_selecionados2)]

    # Proporção de Votos por Seção
    if candidatos_selecionados2:
        totalVotosSecao = mergeBoletim1Pref.groupby('NM_LOCAL_VOTACAO', )['QT_VOTOS'].sum().reset_index()
        # Agrupar os votos por seção e calcular o total de votos por seção
        df_total_votos_secao = totalVotosSecao.rename(columns={'QT_VOTOS': 'TOTAL_VOTOS_SECAO'})

        # Agrupar os votos por candidato e seção
        df_votosSecaoCandidato = df_fil_candidatos.groupby(['NM_VOTAVEL', 'NM_LOCAL_VOTACAO']).agg(
            {'QT_VOTOS': 'sum'}).reset_index()

        # Mesclar os dois dataframes para obter o total de votos por seção em cada linha
        df_votosSecaoCandidato = pd.merge(df_votosSecaoCandidato, df_total_votos_secao, on='NM_LOCAL_VOTACAO')

        # Calcular a proporção de votos para cada candidato em cada seção
        df_votosSecaoCandidato['PROPORCAO_VOTOS'] = df_votosSecaoCandidato['QT_VOTOS'] / df_votosSecaoCandidato[
            'TOTAL_VOTOS_SECAO']

        # Criar um gráfico de barras usando Plotly Express com rótulos de dados
        fig = px.bar(df_votosSecaoCandidato,
                     x='NM_LOCAL_VOTACAO',
                     y='PROPORCAO_VOTOS',
                     color='NM_VOTAVEL',
                     text='PROPORCAO_VOTOS',  # Adiciona os rótulos de dados
                     labels={'PROPORCAO_VOTOS': 'Proporção de Votos', 'NM_LOCAL_VOTACAO': 'Local de Votação'},
                     title='Proporção de Votos por Candidato e Local de Votação',
                     barmode='group',
                     color_discrete_sequence=px.colors.qualitative.Plotly)

        # Atualizar o layout para melhor exibir os rótulos
        fig.update_traces(texttemplate='%{text:.2%}',
                          textposition='outside')  # Formato de porcentagem e posição externa
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',height=600, margin=dict(t=50), xaxis_tickangle=-45)
        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig)

        st.write('**Clique no botão abaixo e descubra o Perfil do Eleitor de cada seção**')
        if st.button('Clique Aqui'):
            switch_page('perfil por seção')

        st.write('### O que entender a partir deste gráfico?')
        st.markdown("""
            <div style='text-align: justify;'>
            Este gráfico é importante para um candidato a porque mostra a proporção de votos por seção para diferentes candidatos.
    
    Aqui estão alguns motivos pelos quais essa análise é essencial:
            
    -**Identificação de Padrões Geográficos:** O gráfico permite ao candidato **identificar** onde ele está mais **forte** ou **fraco** em termos de apoio eleitoral. Isso pode indicar áreas onde o candidato precisa **concentrar** mais esforços de campanha ou onde ele já tem uma base sólida.
    
    -**Comparação com Concorrentes:** Ao comparar sua performance com outros candidatos, o candidato pode **entender melhor** como sua campanha está se saindo em **diferentes regiões** em relação aos **concorrentes.**
    
    -**Ajuste de Estratégias de Campanha:** Com base nas áreas onde a proporção de votos é mais baixa, o candidato pode **ajustar** sua **mensagem ou suas atividades** de campanha para melhorar seu desempenho nessas regiões.
    
    -**Foco em Seções Estratégicas:** **Identificar seções** onde há uma disputa acirrada pode ser crucial para decidir onde **concentrar recursos e esforços** para garantir uma **vitória** em áreas estratégicas.
    
    -**Tomada de Decisões:** Analisar as seções com **melhor** ou **pior** desempenho pode ajudar o candidato a tomar decisões informadas sobre onde **intensificar** visitas, eventos e presença em geral.
    
    Em resumo, este tipo de análise ajuda o candidato a alocar recursos de maneira mais eficiente e a ajustar sua estratégia de campanha de forma a maximizar seu apoio eleitoral.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""Selecione ao menos um candidato para a Análise""")
    st.markdown("##### Top candidatos com mais votos")
    mergeBoletim1PrefFil = mergeBoletim1Pref[~mergeBoletim1Pref['NM_VOTAVEL'].isin(['Branco', 'Nulo'])]
    df_grouped = mergeBoletim1PrefFil.groupby('NM_VOTAVEL', as_index=False)['QT_VOTOS'].sum()

    # Pegue os 4 candidatos mais votados
    top_4 = df_grouped.nlargest(4, 'QT_VOTOS')

    # Criar as colunas no Streamlit
    col1, col2, col3, col4 = st.columns(4)

    # Iterar pelos candidatos mais votados e exibir as informações
    for i, (col, row) in enumerate(zip([col1, col2, col3, col4], top_4.itertuples())):
        nome = row.NM_VOTAVEL
        votos = row.QT_VOTOS

        col.markdown(f"""
                <div style="text-align: center;">
                    <h1 style="font-size: 20px;">{nome}</h1>
                    <p style="font-size: 40px;">{votos} votos</p>
                </div>
            """, unsafe_allow_html=True)
    st.write(
        "**Dica:** Analise em quais locais de votação esses candidatos foram melhor e na página **PERFIL POR SEÇÃO** **descubra** qual o **perfil do eleitor** que vota naquele local")