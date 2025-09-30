# app_lifenergy_v18.py
import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- PALETA DE CORES E CONFIGURAÇÃO DA PÁGINA ---
COLOR_PRIMARY = "#70D1C6"
COLOR_TEXT_DARK = "#333333"
COLOR_BACKGROUND = "#FFFFFF"

st.set_page_config(
    page_title="Consultoria Lifenergy - Cultura Organizacional",
    layout="wide"
)

# --- CSS CUSTOMIZADO PARA A INTERFACE ---
st.markdown(f"""
    <style>
        /* Remoção de elementos do Streamlit Cloud */
        div[data-testid="stHeader"], div[data-testid="stDecoration"] {{
            visibility: hidden; height: 0%; position: fixed;
        }}
        footer {{ visibility: hidden; height: 0%; }}

        /* Estilos gerais */
        .stApp {{ background-color: {COLOR_BACKGROUND}; color: {COLOR_TEXT_DARK}; }}
        h1, h2, h3 {{ color: {COLOR_TEXT_DARK}; }}
        
        /* Cabeçalho customizado */
        .stApp > header {{
            background-color: {COLOR_PRIMARY}; padding: 1rem;
            border-bottom: 5px solid {COLOR_TEXT_DARK};
        }}
        
        /* Card de container */
        div.st-emotion-cache-1r4qj8v {{
             background-color: #f0f2f6; border-left: 5px solid {COLOR_PRIMARY};
             border-radius: 5px; padding: 1.5rem; margin-top: 1rem;
             margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        /* Labels dos Inputs */
        div[data-testid="textInputRootElement"] > label, 
        div[data-testid="numberInput-root"] > label,
        div[data-testid="stSelectbox"] > label,
        div[data-testid="stRadioGroup"] > label,
        div[data-testid="stTextArea"] > label {{
            color: {COLOR_TEXT_DARK}; font-weight: 600;
        }}
        
        /* Adiciona bordas visíveis aos campos de input e selectbox */
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div {{
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 8px !important;
        }}
        
        /* Estiliza o campo de texto de observações */
        div[data-testid="stTextArea"] textarea {{
            background-color: #FFFFFF;
            border: 1px solid #cccccc;
            border-radius: 5px;
        }}
        
        /* Expanders (Blocos de Perguntas) */
        .streamlit-expanderHeader {{
            background-color: {COLOR_PRIMARY}; color: white; font-size: 1.2rem;
            font-weight: bold; border-radius: 8px; margin-top: 1rem;
            padding: 0.75rem 1rem; border: none; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .streamlit-expanderHeader:hover {{ background-color: {COLOR_TEXT_DARK}; }}
        .streamlit-expanderContent {{
            background-color: #f9f9f9; border-left: 3px solid {COLOR_PRIMARY}; padding: 1rem;
            border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; margin-bottom: 1rem;
        }}

        /* Botões de rádio (Likert) responsivos */
        div[data-testid="stRadio"] > div {{
            display: flex; flex-wrap: wrap; justify-content: flex-start;
        }}
        div[data-testid="stRadio"] label {{
            margin-right: 1.2rem; margin-bottom: 0.5rem; color: {COLOR_TEXT_DARK};
        }}
        
        /* Botões de ação */
        .stButton button {{
            background-color: {COLOR_PRIMARY}; color: white; font-weight: bold;
            padding: 0.75rem 1.5rem; border-radius: 8px; border: none;
            transition: all 0.2s ease-in-out;
        }}
        .stButton button:hover {{
            background-color: {COLOR_TEXT_DARK}; color: white;
            transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
        }}
    </style>
""", unsafe_allow_html=True)


# --- CABEÇALHO DA APLICAÇÃO ---
col1, col2 = st.columns([1, 3])
with col1:
    try:
        st.image("logo_wedja.jpg", width=120)
    except FileNotFoundError:
        st.warning("Logo 'logo_wedja.jpg' não encontrada.")
with col2:
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
        <h2 style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>CONSULTORIA LIFENERGY</h2>
        <p style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>CULTURA ORGANIZACIONAL COM FOCO EM SAÚDE MENTAL</p>
    </div>
    """, unsafe_allow_html=True)


# --- SEÇÃO DE IDENTIFICAÇÃO ---
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Identificação Mínima</h3>", unsafe_allow_html=True)
    
    empresa = st.text_input("Empresa")
    cargo_setor = st.text_input("Cargo/Setor")
    instituicao_coletora = st.text_input("Instituição Coletora", "Instituto Wedja de Socionomia SS Ltda", disabled=True)

# --- INSTRUÇÕES ---
with st.expander("Ver Orientações aos Respondentes", expanded=True):
    st.info(
        """
        - **Janela de referência:** últimos 3 meses.
        - **Escala Likert 01–05:** 01=Discordo totalmente · 02=Discordo · 03=Neutro · 04=Concordo · 05=Concordo totalmente.
        - **Confidencialidade/LGPD:** dados agrupados para fins de diagnóstico (Cultura, ESG e NR ‑ 1/FRPS); sem avaliações individuais.
        - Em caso de dúvida, utilize o julgamento mais prudente e use o campo de observações.
        """
    )


# --- LÓGICA DO QUESTIONÁRIO (BACK-END) ---
@st.cache_data
def carregar_itens():
    data = [
        # Bloco: Cultura, Liderança e Rituais
        ('Cultura, Liderança e Rituais', 'CL01', 'As práticas diárias refletem o que a liderança diz e cobra.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL02', 'Processos críticos têm donos claros e rotina de revisão.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL03', 'A comunicação visual (quadros, murais, campanhas) reforça os valores da empresa.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL04', 'Reconhecimentos e premiações estão alinhados ao comportamento esperado.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL05', 'Feedbacks e aprendizados com erros ocorrem sem punição inadequada.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL06', 'Conflitos são tratados com respeito e foco em solução.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL07', 'Integridade e respeito orientam decisões, mesmo sob pressão.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL08', 'Não há tolerância a discriminação, assédio ou retaliação.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL09', 'Critérios de decisão são transparentes e consistentes.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL10', 'A empresa cumpre o que promete a pessoas e clientes.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL11', 'Acreditamos que segurança e saúde emocional são inegociáveis.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL12', 'Acreditamos que diversidade melhora resultados.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL13', 'Há rituais de reconhecimento (semanal/mensal) que celebram comportamentos-chave.', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL14', 'Reuniões de resultado incluem aprendizados (o que manter, o que ajustar).', 'NÃO'),
        ('Cultura, Liderança e Rituais', 'CL15', 'Políticas internas são conhecidas e aplicadas (não ficam só no papel).', 'NÃO'),

        # Bloco: Comunicação e Ambiente
        ('Comunicação e Ambiente', 'CA01', 'Sistemas suportam o trabalho (não criam retrabalho ou gargalos).', 'NÃO'),
        ('Comunicação e Ambiente', 'CA02', 'Indicadores de pessoas e segurança são acompanhados periodicamente.', 'NÃO'),
        ('Comunicação e Ambiente', 'CA03', 'A linguagem interna é respeitosa e inclusiva.', 'NÃO'),
        ('Comunicação e Ambiente', 'CA04', 'Termos e siglas são explicados para evitar exclusão.', 'NÃO'),
        ('Comunicação e Ambiente', 'CA05', 'A comunicação interna é clara e no tempo certo.', 'NÃO'),
        ('Comunicação e Ambiente', 'CA06', 'Metas e resultados são divulgados com clareza.', 'NÃO'),

        # Bloco: Segurança Psicológica e Bem-estar
        ('Segurança Psicológica e Bem-estar', 'SP01', 'Sinto segurança psicológica para expor opiniões e erros.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP02', 'Consigo equilibrar trabalho e vida pessoal.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP03', 'Práticas de contratação e promoção são justas e inclusivas.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP04', 'A empresa promove ambientes livres de assédio e discriminação.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP05', 'Tenho acesso a ações de saúde/apoio emocional quando preciso.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP06', 'Carga de trabalho é ajustada para prevenir sobrecarga crônica.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP07', 'Recebo treinamentos relevantes ao meu perfil de risco e função.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP08', 'Tenho oportunidades reais de desenvolvimento profissional.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP09', 'Sou ouvido(a) nas decisões que afetam meu trabalho.', 'NÃO'),

        # Bloco: Governança, Riscos e Controles
        ('Governança, Riscos e Controles', 'GR01', 'Existe canal de denúncia acessível e confiável.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR02', 'Conheço o Código de Ética e como reportar condutas impróprias.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR03', 'Sinto confiança nos processos de investigação e resposta a denúncias.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR04', 'Há prestação de contas sobre planos e ações corretivas.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR05', 'Riscos relevantes são identificados e acompanhados regularmente.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR06', 'Controles internos funcionam e são revisados quando necessário.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR07', 'Inventário de riscos e planos de ação (PGR) estão atualizados e acessíveis.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR08', 'Mudanças de processo passam por avaliação de risco antes da implantação.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR09', 'O canal de denúncia é acessível e protege contra retaliações.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR10', 'Sinto que denúncias geram ações efetivas.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR11', 'Tenho meios simples para reportar incidentes/quase-acidentes e perigos.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR12', 'No meu posto, riscos são avaliados considerando exposição e severidade x probabilidade.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR13', 'A empresa prioriza eliminar/substituir riscos antes de recorrer ao EPI.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR14', 'Recebo treinamento quando há mudanças de função/processo/equipamentos.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR15', 'Há inspeções/observações de segurança com frequência adequada.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR16', 'Sinalização e procedimentos são claros e atualizados.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR17', 'Sou convidado(a) a participar das discussões de riscos e soluções.', 'NÃO'),
        ('Governança, Riscos e Controles', 'GR18', 'Planos de emergência são conhecidos e incidentes são investigados com ações corretivas.', 'NÃO'),

        # Bloco: Fatores de Risco Psicossocial (Itens Reversos)
        ('Fatores de Risco Psicossocial (Reversos)', 'FR01', 'No meu ambiente há piadas, constrangimentos ou condutas indesejadas.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR02', 'Tenho receio de represálias ao reportar assédio ou condutas impróprias.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR03', 'Conflitos entre áreas/pessoas permanecem sem solução por muito tempo.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR04', 'Falta respeito nas interações do dia a dia.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR05', 'Falta de informações atrapalha minha entrega.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR06', 'Mensagens importantes chegam tarde ou de forma confusa.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR07', 'Trabalho frequentemente isolado sem suporte adequado.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR08', 'Em teletrabalho me sinto desconectado(a) da equipe.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR09', 'A sobrecarga e prazos incompatíveis são frequentes.', 'SIM'),
        ('Fatores de Risco Psicossocial (Reversos)', 'FR10', 'As expectativas de produtividade são irreais no meu contexto.', 'SIM'),
    ]
    df = pd.DataFrame(data, columns=["Bloco", "ID", "Item", "Reverso"])
    return df

# --- INICIALIZAÇÃO ---
df_itens = carregar_itens()
if 'respostas' not in st.session_state:
    st.session_state.respostas = {}

# --- PAINEL DE PROGRESSO ---
st.subheader("Progresso do Preenchimento")
with st.container(border=True):
    respostas_dadas = [r for r in st.session_state.respostas.values() if r is not None]
    num_respostas = len(respostas_dadas)
    total_perguntas = len(df_itens)
    st.metric("Respostas Preenchidas", f"{num_respostas} de {total_perguntas}")


# --- FORMULÁRIO DINÂMICO ---
st.subheader("Questionário")
blocos = df_itens["Bloco"].unique().tolist()
def registrar_resposta(item_id, key):
    st.session_state.respostas[item_id] = st.session_state[key]

for bloco in blocos:
    expandido = "Reversos" in bloco
    with st.expander(f"Dimensão: {bloco}", expanded=expandido):
        df_bloco = df_itens[df_itens["Bloco"] == bloco]
        for _, row in df_bloco.iterrows():
            item_id = row["ID"]
            label = f'({item_id}) {row["Item"]}'
            widget_key = f"radio_{item_id}"
            st.radio(
                label, options=["N/A", 1, 2, 3, 4, 5],
                horizontal=True, key=widget_key,
                on_change=registrar_resposta, args=(item_id, widget_key)
            )

# --- CAMPO DE OBSERVAÇÕES E BOTÃO DE FINALIZAR ---
observacoes = st.text_area("Observações (opcional):")

if st.button("Finalizar e Gerar Download", type="primary"):
    if not st.session_state.respostas:
        st.warning("Nenhuma resposta foi preenchida. Preencha o formulário antes de gerar o download.")
    else:
        st.subheader("Resultados e Exportação")

        # --- LÓGICA DE CÁLCULO ---
        respostas_list = []
        for index, row in df_itens.iterrows():
            item_id = row['ID']
            resposta_usuario = st.session_state.respostas.get(item_id)
            respostas_list.append({
                "Bloco": row["Bloco"],
                "Item": row["Item"],
                "Resposta": resposta_usuario,
                "Reverso": row["Reverso"]
            })
        dfr = pd.DataFrame(respostas_list)

        dfr_numerico = dfr[pd.to_numeric(dfr['Resposta'], errors='coerce').notna()].copy()
        if not dfr_numerico.empty:
            dfr_numerico['Resposta'] = dfr_numerico['Resposta'].astype(int)
            def ajustar_reverso(row):
                return (6 - row["Resposta"]) if row["Reverso"] == "SIM" else row["Resposta"]
            dfr_numerico["Pontuação"] = dfr_numerico.apply(ajustar_reverso, axis=1)
            media_geral = dfr_numerico["Pontuação"].mean()
            
            # ##### ADICIONADO: Cálculo das médias por bloco para o gráfico #####
            resumo_blocos = dfr_numerico.groupby("Bloco")["Pontuação"].mean().round(2).reset_index(name="Média").sort_values("Média")

        else:
            media_geral = 0
            resumo_blocos = pd.DataFrame(columns=["Bloco", "Média"]) # Cria dataframe vazio se não houver respostas

        st.metric("Pontuação Média Geral (somente itens de 1 a 5)", f"{media_geral:.2f}")
        
        # ##### ADICIONADO: Exibição da tabela e do gráfico de barras #####
        if not resumo_blocos.empty:
            st.subheader("Média por Dimensão")
            st.dataframe(resumo_blocos.rename(columns={"Bloco": "Dimensão"}), use_container_width=True, hide_index=True)
            
            st.subheader("Gráfico Comparativo por Dimensão")
            st.bar_chart(resumo_blocos.set_index("Bloco")["Média"])


        # --- LÓGICA DE EXPORTAÇÃO ---
        st.subheader("Exportar Dados")
        
        dfr_respostas = dfr[['Bloco', 'Item', 'Resposta']].copy()
        dfr_respostas = dfr_respostas.rename(columns={"Bloco": "Dimensão"})
        dfr_respostas['Resposta'] = dfr_respostas['Resposta'].fillna('N/A')
        
        timestamp_str = datetime.now().isoformat(timespec="seconds")
        dados_cabecalho = {
            'Campo': ["Timestamp", "Empresa", "Cargo/Setor", "Instituição Coletora"],
            'Valor': [timestamp_str, empresa, cargo_setor, instituicao_coletora]
        }
        df_cabecalho = pd.DataFrame(dados_cabecalho)

        dados_obs = {
            "Timestamp": [timestamp_str], "Empresa": [empresa], "Cargo/Setor": [cargo_setor], "Observações": [observacoes]
        }
        dfr_observacoes = pd.DataFrame(dados_obs)
        
        dados_media = {
            'Dimensão': ['PONTUAÇÃO MÉDIA GERAL'],
            'Item': [''],
            'Resposta': [f"{media_geral:.2f}"]
        }
        df_media = pd.DataFrame(dados_media)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_cabecalho.to_excel(writer, sheet_name='Respostas', index=False, header=False, startrow=0)
            dfr_respostas.to_excel(writer, sheet_name='Respostas', index=False, startrow=4)
            start_row_media = 4 + 1 + len(dfr_respostas) + 1
            df_media.to_excel(writer, sheet_name='Respostas', index=False, header=False, startrow=start_row_media)
            dfr_observacoes.to_excel(writer, sheet_name='Observacoes', index=False)
        
        processed_data = output.getvalue()
        
        st.download_button(
            label="Baixar respostas completas (Excel)",
            data=processed_data,
            file_name=f"lifenergy_respostas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.success("Arquivo pronto para download!")