"""
SUS Triagem IA Ética - Ponta Grossa/PR
Arquivo único (app + prompts + CSS inline)
"""

import streamlit as st
import google.generativeai as genai
import qrcode
from io import BytesIO
import base64
import datetime

# ─────────────────────────────────────────────
#  ESTILOS CSS
# ─────────────────────────────────────────────
CSS = """
:root {
  --sus-green:  #009c3b;
  --sus-yellow: #ffdf00;
  --sus-blue:   #002776;
  --sus-light:  #e8f5e9;
}
.stApp { background-color: #f0f7f0; }
.sus-header {
  background: linear-gradient(135deg, var(--sus-green) 0%, var(--sus-blue) 100%);
  color: white;
  padding: 24px 20px 18px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 20px;
}
.sus-header h1 { font-size: 2rem; margin: 0; font-weight: 800; }
.sus-header p  { font-size: 1rem; margin: 6px 0 0; opacity: 0.9; }
.disclaimer-box {
  background: #fff3cd;
  border-left: 6px solid #ffdf00;
  border-radius: 8px;
  padding: 14px 18px;
  font-size: 0.95rem;
  margin-bottom: 18px;
  color: #4a3f00;
  font-weight: 600;
}
.user-bubble {
  background: #d1e7dd;
  border-radius: 16px 16px 4px 16px;
  padding: 14px 18px;
  margin: 10px 0;
  font-size: 1.05rem;
  color: #0a3622;
}
.ai-bubble {
  background: white;
  border: 2px solid var(--sus-green);
  border-radius: 16px 16px 16px 4px;
  padding: 14px 18px;
  margin: 10px 0;
  font-size: 1.05rem;
  color: #1a1a1a;
}
.ai-bubble .supervisao {
  display: block;
  margin-top: 12px;
  font-size: 0.85rem;
  color: #005f20;
  font-weight: 700;
  border-top: 1px dashed #009c3b;
  padding-top: 8px;
}
.timestamp { font-size: 0.75rem; color: #888; text-align: right; }
.metric-card {
  background: white;
  border: 2px solid var(--sus-green);
  border-radius: 10px;
  padding: 16px;
  text-align: center;
}
.metric-card .value { font-size: 2rem; font-weight: 800; color: var(--sus-green); }
.metric-card .label { font-size: 0.85rem; color: #555; }
.stButton > button {
  background-color: var(--sus-green) !important;
  color: white !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  padding: 12px 28px !important;
  border: none !important;
  width: 100%;
}
.stButton > button:hover { background-color: #007a2f !important; }
.stTextArea textarea {
  font-size: 1.05rem !important;
  border: 2px solid #009c3b !important;
  border-radius: 10px !important;
}
@media (max-width: 600px) {
  .sus-header h1 { font-size: 1.4rem; }
  .ai-bubble, .user-bubble { font-size: 0.95rem; }
}
"""

# ─────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """Você é o assistente de triagem do SUS de Ponta Grossa, Paraná.

DIRETRIZES OBRIGATÓRIAS:
1. Siga rigorosamente os protocolos do Ministério da Saúde do Brasil e do SUS
2. Use linguagem simples, acessível à população geral, sem jargão médico excessivo
3. SEMPRE termine qualquer resposta com: "⚕️ Este serviço NÃO substitui avaliação médica. Procure a UBS ou ligue SAMU 192."
4. Para sintomas graves (dor no peito, falta de ar severa, AVC, etc.), oriente IMEDIATAMENTE a ligar 192 (SAMU)
5. Oriente sobre as UBSs de Ponta Grossa quando relevante
6. Seja acolhedor, empático e respeitoso
7. Não faça diagnósticos — faça orientação de triagem e encaminhamento
8. Considere contexto socioeconômico do SUS (acesso público, gratuito)
9. Inclua informações sobre prevenção quando pertinente
10. Se a situação não for emergência, oriente sobre o nível de urgência (pode aguardar / ir hoje / ir agora)

ESTRUTURA DA RESPOSTA:
- 🔍 Análise dos Sintomas (breve)
- 🚦 Nível de Urgência: [Verde/Amarelo/Laranja/Vermelho]
- 📋 Orientação Inicial
- 🏥 Onde Procurar Atendimento
- ⚕️ Lembrete ético (obrigatório)

Responda sempre em português brasileiro."""

# ─────────────────────────────────────────────
#  TEMPLATES HTML
# ─────────────────────────────────────────────
HEADER_HTML = """
<div class="sus-header">
  <h1>🏥 Triagem IA</h1>
  <p>Ponta Grossa · Paraná · Protocolo Brasileiro de Triagem</p>
</div>
"""

DISCLAIMER_HTML = """
<div class="disclaimer-box">
  ⚠️ <strong>AVISO IMPORTANTE:</strong> Esta ferramenta é apenas orientativa e
  <strong>NÃO substitui consulta médica</strong>. Em casos graves ou dúvidas, procure a
  <strong>UBS mais próxima</strong> ou ligue para o <strong>SAMU (192)</strong>.
  Toda resposta requer supervisão de profissional de saúde.
</div>
"""

EMPTY_CHAT_HTML = """
<div style="background:white;border-radius:12px;padding:20px;text-align:center;
            color:#555;border:2px dashed #009c3b;">
  👋 Olá! Descreva seus sintomas abaixo para receber orientação de triagem do SUS.<br>
  <small>Ex: "Tenho febre há 2 dias, dor de cabeça e tosse"</small>
</div>
"""

FOOTER_HTML = """
<div style="text-align:center;font-size:0.8rem;color:#666;padding:10px;">
  🏥 <strong>SUS Triagem IA Ética</strong> · Ponta Grossa/PR · Código Aberto (MIT)<br>
  Desenvolvido com responsabilidade ética · Supervisão humana sempre recomendada<br>
  <strong>⚕️ NÃO substitui médico · UBS · SAMU 192</strong>
</div>
"""

def user_bubble_html(content):
    return f'<div class="user-bubble">👤 <strong>Você:</strong><br>{content}</div>'

def ai_bubble_html(content, timestamp=""):
    return f"""
<div class="ai-bubble">
  🏥 <strong>Triagem SUS IA:</strong><br>{content}
  <span class="supervisao">👨‍⚕️ Resposta gerada por IA — recomenda-se supervisão de profissional de saúde</span>
</div>
<div class="timestamp">{timestamp}</div>
"""

def metric_card_html(value, label):
    return f"""
<div class="metric-card">
  <div class="value">{value}</div>
  <div class="label">{label}</div>
</div>
"""

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SUS Triagem IA Ética",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ESTADO DA SESSÃO
# ─────────────────────────────────────────────
if "messages"          not in st.session_state: st.session_state.messages          = []
if "disclaimer_count"  not in st.session_state: st.session_state.disclaimer_count  = 0
if "total_queries"     not in st.session_state: st.session_state.total_queries     = 0
if "session_start"     not in st.session_state: st.session_state.session_start     = datetime.datetime.now()
if "gemini_configured" not in st.session_state: st.session_state.gemini_configured = False

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuração")

    # Tenta carregar a API Key do Streamlit Secrets (deploy),
    # caso não exista, exibe campo para o usuário digitar manualmente (uso local)
    api_key = st.secrets.get("GOOGLE_API_KEY", "") if hasattr(st, "secrets") else ""

    if not api_key:
        api_key = st.text_input(
            "🔑 Google AI Studio API Key",
            type="password",
            placeholder="AIza...",
            help="Obtenha grátis em https://aistudio.google.com/apikey",
        )

    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.session_state.gemini_configured = True
            st.success("✅ API conectada!")
        except Exception as e:
            st.error(f"Erro na API: {e}")
            st.session_state.gemini_configured = False
    else:
        st.info("Cole sua API Key gratuita do Google AI Studio acima.")

    st.markdown("---")

    # ── Métricas Éticas ──
    st.markdown("### 📊 Métricas Éticas")
    tempo = (datetime.datetime.now() - st.session_state.session_start).seconds // 60

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(metric_card_html(st.session_state.total_queries, "Consultas"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card_html(st.session_state.disclaimer_count, "Disclaimers"), unsafe_allow_html=True)

    st.markdown(f"""
    | Métrica | Valor |
    |---|---|
    | ⏱️ Sessão ativa | {tempo} min |
    | 🔒 Supervisão humana | 100% |
    | 📋 Protocolos SUS | ✅ |
    | 🧑‍⚕️ Substitui médico? | ❌ Nunca |
    | 💾 Dados armazenados | ❌ Nenhum |
    """)

    st.markdown("---")

    # ── QR Code ──
    st.markdown("### 📲 Deploy Público")
    deploy_url = st.text_input(
        "URL do app (após deploy)",
        value="https://seu-app.streamlit.app",
        help="Cole aqui a URL após fazer deploy no Streamlit Cloud",
    )
    if st.button("🔲 Gerar QR Code"):
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(deploy_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#009c3b", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown(
            f'<img src="data:image/png;base64,{b64}" style="width:100%;border-radius:8px;" />',
            unsafe_allow_html=True,
        )
        st.caption("Escaneie para acessar o app")

    st.markdown("---")

    # ── Emergências ──
    st.markdown("### 🚨 Emergências")
    st.markdown("""
    | Serviço | Número |
    |---|---|
    | 🚑 SAMU | **192** |
    | 🚒 Bombeiros | **193** |
    | 🏥 UBS PG | **(42) 3220-xxxx** |
    | ☎️ CVV | **188** |
    """)

    if st.button("🗑️ Limpar Histórico"):
        st.session_state.messages = []
        st.rerun()

# ─────────────────────────────────────────────
#  CONTEÚDO PRINCIPAL
# ─────────────────────────────────────────────
st.markdown(HEADER_HTML, unsafe_allow_html=True)
st.markdown(DISCLAIMER_HTML, unsafe_allow_html=True)

# ── Histórico ──
if st.session_state.messages:
    st.markdown("### 💬 Histórico da Consulta")
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(user_bubble_html(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(ai_bubble_html(msg["content"], msg.get("timestamp", "")), unsafe_allow_html=True)
else:
    st.markdown(EMPTY_CHAT_HTML, unsafe_allow_html=True)

st.markdown("---")

# ── Formulário ──
st.markdown("### 📝 Descreva seus sintomas")

with st.form("triagem_form", clear_on_submit=True):
    sintomas = st.text_area(
        "Sintomas e informações",
        placeholder="Ex: Tenho 38°C de febre há 2 dias, dor de garganta, estou sem apetite. Sou adulto de 35 anos.",
        height=120,
        label_visibility="collapsed",
    )
    col_a, col_b = st.columns([3, 1])
    with col_a:
        submitted = st.form_submit_button("🔍 Analisar Sintomas", use_container_width=True)
    with col_b:
        st.form_submit_button("🗑️ Limpar", use_container_width=True)

# ─────────────────────────────────────────────
#  PROCESSAMENTO — GEMINI 1.5 FLASH
# ─────────────────────────────────────────────
if submitted and sintomas.strip():
    if not st.session_state.gemini_configured:
        st.error("⚠️ Configure sua API Key do Google AI Studio na barra lateral para usar o app.")
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": sintomas,
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        })

        with st.spinner("🔄 Analisando sintomas com protocolos SUS..."):
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=SYSTEM_PROMPT,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=1024,
                    ),
                )

                history = [
                    {
                        "role": msg["role"] if msg["role"] == "user" else "model",
                        "parts": [msg["content"]],
                    }
                    for msg in st.session_state.messages[:-1]
                ]

                chat = model.start_chat(history=history)
                response = chat.send_message(sintomas)
                resposta = response.text

                st.session_state.total_queries += 1
                st.session_state.disclaimer_count += resposta.count("NÃO substitui") + resposta.count("SAMU") + 1

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": resposta,
                    "timestamp": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                })

                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro ao consultar a API: {str(e)}")
                st.info("Verifique se sua API Key está correta e tem cota disponível.")

elif submitted and not sintomas.strip():
    st.warning("⚠️ Por favor, descreva seus sintomas antes de enviar.")

# ── Rodapé ──
st.markdown("---")
st.markdown(FOOTER_HTML, unsafe_allow_html=True)
