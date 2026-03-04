# =============================================
#   Triagem IA — System Prompt e Templates HTML
# =============================================

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


# ── Templates HTML ──

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


def user_bubble_html(content: str) -> str:
    return f'<div class="user-bubble">👤 <strong>Você:</strong><br>{content}</div>'


def ai_bubble_html(content: str, timestamp: str = "") -> str:
    return f"""
<div class="ai-bubble">
  🏥 <strong>Triagem SUS IA:</strong><br>{content}
  <span class="supervisao">👨‍⚕️ Resposta gerada por IA — recomenda-se supervisão de profissional de saúde</span>
</div>
<div class="timestamp">{timestamp}</div>
"""


def metric_card_html(value, label: str) -> str:
    return f"""
<div class="metric-card">
  <div class="value">{value}</div>
  <div class="label">{label}</div>
</div>
"""