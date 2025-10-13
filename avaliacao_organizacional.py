# avaliacao_organizacional_final.py
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
import matplotlib.pyplot as plt

# --- PALETA DE CORES E CONFIGURAÇÃO DA PÁGINA ---
COLOR_PRIMARY = "#70D1C6"
COLOR_TEXT_DARK = "#333333"
COLOR_BACKGROUND = "#FFFFFF"

st.set_page_config(
    page_title="Inventário Organizacional — Cultura e Prática",
    layout="wide"
)

# --- CSS CUSTOMIZADO (Omitido para economizar espaço) ---
st.markdown(f"""<style><style>
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
        /* Inputs e Labels */
        div[data-testid="textInputRootElement"] > label,
        div[data-testid="stTextArea"] > label,
        div[data-testid="stRadioGroup"] > label {{
            color: {COLOR_TEXT_DARK}; font-weight: 600;
        }}
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stTextArea"] textarea {{
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: #FFFFFF;
        }}
        /* Expanders */
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
        /* Botão de Finalizar */
        .stButton button {{
            background-color: {COLOR_PRIMARY}; color: white; font-weight: bold;
            padding: 0.75rem 1.5rem; border-radius: 8px; border: none;
        }}
        .stButton button:hover {{
            background-color: {COLOR_TEXT_DARK}; color: white;
        }}
    </style>""", unsafe_allow_html=True)

# --- CONEXÃO COM GOOGLE SHEETS (COM CACHE) ---
@st.cache_resource
def connect_to_gsheet():
    """Conecta ao Google Sheets e retorna o objeto da aba de respostas."""
    try:
        creds_dict = dict(st.secrets["google_credentials"])
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        gc = gspread.service_account_from_dict(creds_dict)
        spreadsheet = gc.open("Respostas Formularios")
        
        # Retorna apenas a aba principal
        return spreadsheet.worksheet("Organizacional")
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
        return None

ws_respostas = connect_to_gsheet()

if ws_respostas is None:
    st.error("Não foi possível conectar à aba 'Organizacional' da planilha. Verifique o nome e as permissões.")
    st.stop()


# --- CABEÇALHO DA APLICAÇÃO ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo_wedja.jpg", width=120)
    except FileNotFoundError:
        st.warning("Logo 'logo_wedja.jpg' não encontrada.")
with col2:
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
        <h1 style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>Inventário Organizacional</h1>
        <h3 style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>Cultura e Prática</h3>
    </div>
    """, unsafe_allow_html=True)


# --- SEÇÃO DE IDENTIFICAÇÃO ---
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Identificação</h3>", unsafe_allow_html=True)
    col1_form, col2_form = st.columns(2)
    with col1_form:
        respondente = st.text_input("Respondente:", key="input_respondente")
        data = st.text_input("Data:", datetime.now().strftime('%d/%m/%Y'))
    with col2_form:
        organizacao_coletora = st.text_input("Organização Coletora:", "Instituto Wedja de Socionomia", disabled=True)


# --- INSTRUÇÕES ---
with st.expander("Ver Orientações aos Respondentes", expanded=True):
    st.info(
        """
        - **Objetivo:** Avaliar dimensões da organização como regras, normas, reputação, valores e práticas.
        - **Escala Likert 1–5:** 1=Discordo totalmente, 2=Discordo parcialmente, 3=Neutro, 4=Concordo parcialmente, 5=Concordo totalmente.
        - **Confidencialidade:** Responda de forma individual e espontânea. Suas respostas são confidenciais.
        """
    )


# --- LÓGICA DO QUESTIONÁRIO (BACK-END) ---
@st.cache_data
def carregar_itens():
    data = [
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
        ('Comunicação e Ambiente', 'CA01', 'Sistemas suportam o trabalho (não criam retrabalho ou gargalos).', 'NÃO'),
        ('Comunicação e Ambiente', 'CA02', 'Indicadores de pessoas e segurança são acompanhados periodicamente.', 'NÃO'),
        ('Comunicação e Ambiente', 'CA03', 'A linguagem interna é respeitosa e inclusiva.', 'NÃO'),
        ('Comunicação e Ambiente', 'CA04', 'Termos e siglas são explicados para evitar exclusão.', 'NÃO'),
        ('Comunicação e Ambiente', 'CA05', 'A comunicação interna é clara e no tempo certo.', 'NÃO'),
        ('Comunicação e Ambiente', 'CA06', 'Metas e resultados são divulgados com clareza.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP01', 'Sinto segurança psicológica para expor opiniões e erros.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP02', 'Consigo equilibrar trabalho e vida pessoal.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP03', 'Práticas de contratação e promoção são justas e inclusivas.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP04', 'A empresa promove ambientes livres de assédio e discriminação.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP05', 'Tenho acesso a ações de saúde/apoio emocional quando preciso.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP06', 'Carga de trabalho é ajustada para prevenir sobrecarga crônica.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP07', 'Recebo treinamentos relevantes ao meu perfil de risco e função.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP08', 'Tenho oportunidades reais de desenvolvimento profissional.', 'NÃO'),
        ('Segurança Psicológica e Bem-estar', 'SP09', 'Sou ouvido(a) nas decisões que afetam meu trabalho.', 'NÃO'),
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

# --- INICIALIZAÇÃO E FORMULÁRIO DINÂMICO ---
df_itens = carregar_itens()
if 'respostas' not in st.session_state:
    st.session_state.respostas = {}

st.subheader("Questionário")
blocos = df_itens["Bloco"].unique().tolist()
def registrar_resposta(item_id, key):
    st.session_state.respostas[item_id] = st.session_state[key]

for bloco in blocos:
    df_bloco = df_itens[df_itens["Bloco"] == bloco]
    prefixo_bloco = df_bloco['ID'].iloc[0][:2] if not df_bloco.empty else bloco
    
    with st.expander(f"{prefixo_bloco}", expanded=bloco == blocos[0]):
        for _, row in df_bloco.iterrows():
            item_id = row["ID"]
            label = f'({item_id}) {row["Item"]}'
            widget_key = f"radio_{item_id}"
            st.radio(
                label, options=["N/A", 1, 2, 3, 4, 5],
                horizontal=True, key=widget_key,
                on_change=registrar_resposta, args=(item_id, widget_key)
            )

# O campo de observações foi removido

# --- BOTÃO DE FINALIZAR E LÓGICA DE RESULTADOS/EXPORTAÇÃO ---
if st.button("Finalizar e Enviar Respostas", type="primary"):
    if not st.session_state.respostas:
        st.warning("Nenhuma resposta foi preenchida.")
    else:
        st.subheader("Resultados e Envio")

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
            resumo_blocos = dfr_numerico.groupby("Bloco")["Pontuação"].mean().round(2).reset_index(name="Média").sort_values("Média")
        else:
            media_geral = 0
            resumo_blocos = pd.DataFrame(columns=["Bloco", "Média"])

        st.metric("Pontuação Média Geral (somente itens de 1 a 5)", f"{media_geral:.2f}")
        
        if not resumo_blocos.empty:
            st.subheader("Média por Dimensão")
            st.dataframe(resumo_blocos.rename(columns={"Bloco": "Dimensão"}), use_container_width=True, hide_index=True)
            
            st.subheader("Gráfico Comparativo por Dimensão")
            
            # Criação do gráfico de pizza com Matplotlib
            fig, ax = plt.subplots()
            ax.pie(resumo_blocos["Média"], labels=resumo_blocos["Bloco"], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Garante que a pizza seja um círculo.
            
            # Exibe o gráfico no Streamlit
            st.pyplot(fig)
        # --- LÓGICA DE ENVIO PARA GOOGLE SHEETS ---
        with st.spinner("Enviando dados para a planilha..."):
            try:
                timestamp_str = datetime.now().isoformat(timespec="seconds")
                respostas_para_enviar = []
                
                for _, row in dfr.iterrows():
                    respostas_para_enviar.append([
                        timestamp_str,
                        respondente,
                        data,
                        organizacao_coletora,
                        row["Bloco"],
                        row["Item"],
                        row["Resposta"] if pd.notna(row["Resposta"]) else "N/A"
                    ])
                
                ws_respostas.append_rows(respostas_para_enviar, value_input_option='USER_ENTERED')
                
                st.success("Suas respostas foram enviadas com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao enviar dados para a planilha: {e}")

                with st.container():
                    st.markdown('<div id="autoclick-div">', unsafe_allow_html=True)
                    if st.button("Ping Button", key="autoclick_button"):
                    # A ação aqui pode ser um simples print no log do Streamlit
                      print("Ping button clicked by automation.")
                    st.markdown('</div>', unsafe_allow_html=True)