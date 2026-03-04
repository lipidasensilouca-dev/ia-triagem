"""
SUS Triagem IA Ética - Ponta Grossa/PR
"""

import streamlit as st
import google.generativeai as genai
import qrcode
from io import BytesIO
import base64
import datetime
from pathlib import Path

from prompts import (
    SYSTEM_PROMPT,
    HEADER_HTML, DISCLAIMER_HTML, EMPTY_CHAT_HTML, FOOTER_HTML,
    user_bubble_html, ai_bubble_html, metric_card_html,
)

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SUS Triagem IA Ética",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Carrega CSS externo ──
css_path = Path(__file__).parent / "styles.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

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

    api_key = st.text_input(
        "AIzaSyDE7zVzFCKDTNpp_TAEccKdO5vymasEKmI",
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
```
