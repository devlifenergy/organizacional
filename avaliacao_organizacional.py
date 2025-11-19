# avaliacao_organizacional_final.py
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
import matplotlib.pyplot as plt
import urllib.parse
import hmac
import hashlib

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
        # --- Lógica de Verificação da URL ---
    org_coletora_valida = "Instituto Wedja de Socionomia" # Valor padrão seguro
    link_valido = False # Começa como inválido por padrão

try:
    query_params = st.query_params
    org_encoded_from_url = query_params.get("org")
    exp_from_url = query_params.get("exp") # Parâmetro de expiração
    sig_from_url = query_params.get("sig") # Parâmetro de assinatura
    
    # 1. Verifica se todos os parâmetros de segurança existem
    if org_encoded_from_url and exp_from_url and sig_from_url:
        org_decoded = urllib.parse.unquote(org_encoded_from_url)
        
        # 2. Recalcula a assinatura (com base na org + exp)
        secret_key = st.secrets["LINK_SECRET_KEY"].encode('utf-8')
        message = f"{org_decoded}|{exp_from_url}".encode('utf-8')
        calculated_sig = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
        
        # 3. Compara as assinaturas
        if hmac.compare_digest(calculated_sig, sig_from_url):
            # Assinatura OK! Agora verifica a data de validade
            timestamp_validade = int(exp_from_url)
            timestamp_atual = int(datetime.now().timestamp())
            
            if timestamp_atual <= timestamp_validade:
                # SUCESSO: Assinatura válida E dentro da data
                link_valido = True
                org_coletora_valida = org_decoded
            else:
                # FALHA: Link expirou
                st.error("Link Expirado. Por favor, solicite um novo link.")
        else:
            # FALHA: Assinatura não bate, link adulterado
            st.error("Link inválido ou adulterado.")
    else:
         # Se nenhum parâmetro for passado (acesso direto), permite o uso com valor padrão
         if not (org_encoded_from_url or exp_from_url or sig_from_url):
             link_valido = True
         else:
             st.error("Link inválido. Faltando parâmetros de segurança.")

except KeyError:
     st.error("ERRO DE CONFIGURAÇÃO: O app não pôde verificar a segurança do link. Contate o administrador.")
     link_valido = False
except Exception as e:
    st.error(f"Erro ao processar o link: {e}")
    link_valido = False

# Renderiza os campos de identificação
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Identificação</h3>", unsafe_allow_html=True)
    col1_form, col2_form = st.columns(2)
    with col1_form:
        respondente = st.text_input("Respondente:", key="input_respondente")
        data = st.text_input("Data:", datetime.now().strftime('%d/%m/%Y')) 
    with col2_form:
        # O campo agora usa o valor validado e está sempre desabilitado
        organizacao_coletora = st.text_input(
            "Organização Coletora:", 
            value=org_coletora_valida, 
            disabled=True
        )

# --- BLOQUEIO DO FORMULÁRIO SE O LINK FOR INVÁLIDO ---
if not link_valido:
    st.error("Acesso ao formulário bloqueado.")
    st.stop() # Para a execução, escondendo o questionário e o botão de envio
else:
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

    # --- VALIDAÇÃO E BOTÃO DE FINALIZAR (MOVIDO PARA O FINAL) ---
    # Calcula o número de respostas válidas (excluindo N/A)
    respostas_validas_contadas = 0
    if 'respostas' in st.session_state:
        for resposta in st.session_state.respostas.values():
            if resposta is not None and resposta != "N/A":
                respostas_validas_contadas += 1

    total_perguntas = len(df_itens)
    limite_respostas = total_perguntas / 2

    # Determina se o botão deve ser desabilitado
    botao_desabilitado = respostas_validas_contadas < limite_respostas

    # Exibe aviso se o botão estiver desabilitado
    if botao_desabilitado:
        st.warning(f"Responda 50% das perguntas (excluindo 'N/A') para habilitar o envio. ({respostas_validas_contadas}/{total_perguntas} válidas)")

    # Botão Finalizar com estado dinâmico (habilitado/desabilitado)
    if st.button("Finalizar e Enviar Respostas", type="primary", disabled=botao_desabilitado):
            st.subheader("Enviando Respostas...")

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
        
            with st.spinner("Enviando dados para a planilha..."):
                try:
                    timestamp_str = datetime.now().isoformat(timespec="seconds")

                    nome_limpo = organizacao_coletora.strip().upper()
                    id_organizacao = hashlib.md5(nome_limpo.encode('utf-8')).hexdigest()[:8].upper()

                    respostas_para_enviar = []
                    
                    for _, row in dfr.iterrows():
                        resposta = row["Resposta"]
                        pontuacao = "N/A" # Valor padrão se for N/A ou None
                    
                        if pd.notna(resposta) and resposta != "N/A":
                            try:
                                valor = int(resposta)
                                if row["Reverso"] == "SIM":
                                    pontuacao = 6 - valor # Inverte: 1->5, 2->4, etc.
                                else:
                                    pontuacao = valor # Normal
                            except ValueError:
                                pass

                        respostas_para_enviar.append([
                            timestamp_str,
                            id_organizacao,
                            respondente,
                            data,
                            org_coletora_valida,
                            row["Bloco"],
                            row["Item"],
                            row["Resposta"] if pd.notna(row["Resposta"]) else "N/A",
                            pontuacao
                        ])
                    
                    ws_respostas.append_rows(respostas_para_enviar, value_input_option='USER_ENTERED')
                    
                    st.success("Suas respostas foram enviadas com sucesso!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao enviar dados para a planilha: {e}")

with st.empty():
    st.markdown('<div id="autoclick-div">', unsafe_allow_html=True)
    if st.button("Ping Button", key="autoclick_button"):
    # A ação aqui pode ser um simples print no log do Streamlit
        print("Ping button clicked by automation.")
    st.markdown('</div>', unsafe_allow_html=True)