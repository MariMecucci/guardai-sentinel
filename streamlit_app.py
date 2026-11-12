"""GuardAI Sentinel UI: no uploaded code is executed or stored by the service."""
import json
import os
from pathlib import Path

import streamlit as st

from sentinel.service import analyze_code

ROOT = Path(__file__).resolve().parent
EXAMPLES = {
    "Python — SQL vulnerável": ROOT / "examples/vulnerable_login.py",
    "Python — Consulta segura": ROOT / "examples/secure_login.py",
    "SQL — Template suspeito": ROOT / "examples/template_query.sql",
    "SQL — Consulta parametrizada": ROOT / "examples/secure_query.sql",
}

st.set_page_config(page_title="GuardAI Sentinel | AppSec Lab", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.stApp { background: #0b1325; color: #e9efff; }
.block-container { max-width: 1120px; padding-top: 2.2rem; }
[data-testid="stSidebar"] { background: #101d35; }
h1,h2,h3 { letter-spacing: -.035em; }
[data-testid="stMetric"] { padding: 17px; border: 1px solid #304363; border-radius: 12px; background: #101d35; }
div.stButton>button[kind="primary"] { background: #71c6d1; color: #06212a; border: 0; font-weight: 750; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### GUARD<span style='color:#71c6d1'>AI</span> / SENTINEL", unsafe_allow_html=True)
    st.caption("AI Security & Data Engineering Copilot")
    st.divider()
    st.markdown("**Modo seguro**")
    st.write("Análise estática disponível sem cadastro, sem API e sem enviar código para terceiros.")
    st.caption("MVP educacional · Python / SQL · Nenhum código enviado é executado")
    st.divider()
    st.caption("Baseado no projeto GuardAI desenvolvido durante a formação DIO/Santander.")
    st.link_button("Ver projeto de origem", "https://github.com/MariMecucci/guardai-cybersecurity-agent")

st.caption("DEFENSIVE AI ENGINEERING / PORTFOLIO PROJECT")
st.title("GuardAI Sentinel")
st.write("Inspecione padrões de risco em código Python e SQL. Evidências primeiro; sugestões de IA apenas quando ativadas explicitamente.")

scan_tab, compare_tab, info_tab = st.tabs(["Scanner", "Comparação segura", "Metodologia"])

with scan_tab:
    left, right = st.columns([2.2, 1], gap="large")
    with left:
        input_mode = st.radio("Origem do código", ["Exemplo didático", "Enviar arquivo", "Colar código"], horizontal=True)
        filename = "example.py"
        source = ""
        if input_mode == "Exemplo didático":
            sample_label = st.selectbox("Exemplo", list(EXAMPLES))
            file_path = EXAMPLES[sample_label]
            filename, source = file_path.name, file_path.read_text(encoding="utf-8")
        elif input_mode == "Enviar arquivo":
            uploaded = st.file_uploader("Arquivo .py ou .sql (até 30 KB)", type=["py", "sql"])
            if uploaded is not None:
                filename = uploaded.name
                data = uploaded.getvalue()
                try:
                    source = data.decode("utf-8")
                except UnicodeDecodeError:
                    st.error("O arquivo precisa estar codificado em UTF-8.")
        else:
            filename = st.selectbox("Extensão", ["snippet.py", "snippet.sql"])
            source = st.text_area("Código para análise", height=260, placeholder="Cole somente código fictício ou que você pode compartilhar.")
        if input_mode != "Colar código" and source:
            st.code(source, language="python" if filename.endswith(".py") else "sql")

    with right:
        st.markdown("#### Execução")
        st.info("O scanner usa regras locais. Sem execução de scripts, queries ou arquivos enviados.")
        ai_enabled = os.getenv("GUARDAI_ENABLE_AI", "0") == "1"
        if ai_enabled:
            use_ai = st.checkbox("Solicitar revisão Gemini", value=False,
                                 help="Envia o conteúdo para a API do Google. Use SOMENTE código sintético/autorizado.")
            consent = st.checkbox("Autorizo enviar este código ao Gemini", value=False) if use_ai else False
        else:
            use_ai, consent = False, False
            st.caption("Revisão Gemini desativada por padrão. Veja o README para habilitá-la localmente.")
        analyze = st.button("Analisar código", type="primary", use_container_width=True,
                            disabled=(use_ai and not consent))

    if analyze:
        try:
            report = analyze_code(filename, source, use_ai=use_ai and consent).to_dict()
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.divider()
            st.subheader("Resultado da triagem")
            c1, c2, c3 = st.columns(3)
            c1.metric("Achados", report["finding_count"])
            c2.metric("Linhas analisadas", report["lines_scanned"])
            c3.metric("Linguagem", report["language"].upper())
            for finding in report["findings"]:
                with st.expander(f"{finding['severity'].upper()} · {finding['title']} · linha {finding['line']}", expanded=True):
                    st.caption(f"Regra {finding['rule_id']} · confiança {finding['confidence']}")
                    st.code(finding["evidence"])
                    st.write("**Por quê:**", finding["why"])
                    st.write("**Correção:**", finding["remediation"])
                    if finding["reference"]:
                        st.link_button("Referência técnica", finding["reference"])
            if report.get("retrieved_passages"):
                st.subheader("Trechos recuperados (BM25 local)")
                st.caption("Resumos editoriais versionados, não citações literais. Recuperação não valida alegações da IA.")
                for passage in report["retrieved_passages"]:
                    with st.expander(f"{passage['id']} — {passage['title']}"):
                        st.write(passage["text"])
                        st.caption(f"Versão editorial: {passage['source_version']}")
                        st.link_button("Ler referência original", passage["url"])
            if report.get("grounding_references"):
                st.subheader("Referências recuperadas (base local)")
                st.caption("Selecionadas por regras do scanner, não pela IA. Os resumos não comprovam exploração nem validam a resposta do modelo.")
                for ref in report["grounding_references"]:
                    st.markdown(f"- **{ref['id']}** — [{ref['title']}]({ref['url']})")
            if report["ai_summary"]:
                st.subheader("Revisão opcional Gemini")
                st.write(report["ai_summary"])
                for suggestion in report["ai_suggestions"]:
                    st.markdown("- " + suggestion)
                st.caption("As sugestões de LLM não foram verificadas independentemente.")
            for warning in report["warnings"]:
                st.warning(warning)
            st.download_button("Exportar relatório JSON", json.dumps(report, ensure_ascii=False, indent=2),
                               file_name="guardai-report.json", mime="application/json")

with compare_tab:
    st.markdown("### Mesma tarefa, estratégias diferentes")
    x, y = st.columns(2, gap="medium")
    with x:
        st.markdown("**Consulta vulnerável (somente demonstração)**")
        st.code(EXAMPLES["Python — SQL vulnerável"].read_text(encoding="utf-8"), language="python")
    with y:
        st.markdown("**Consulta parametrizada**")
        st.code(EXAMPLES["Python — Consulta segura"].read_text(encoding="utf-8"), language="python")
    st.write("A construção de SQL com valores interpolados pode alterar a semântica da consulta. Placeholders mantêm dados separados do comando SQL.")
    st.caption("Nenhuma consulta é executada pela interface. Veja os testes automatizados do repositório.")

with info_tab:
    st.markdown("### Como este MVP funciona")
    st.markdown("""
    1. **Validação de entrada:** aceita somente texto UTF-8 de .py ou .sql, limitado a 30 KB e 600 linhas.
    2. **Inspeção local:** regras AST (Python) e heurísticas SQL identificam padrões suspeitos.
    3. **Evidências:** resultado inclui regra, localização, explicação, recomendação e confiança.
    4. **Gemini opcional:** só roda com configuração local explícita e consentimento no uso da interface.
    5. **Fundamentação:** passagens editoriais OWASP/CWE/Python ranqueadas por BM25, a partir de regras detectadas; a IA recebe esses resumos somente com opt-in.\n    6. **Avaliação:** suíte sintética rotulada e métricas de precisão/recall/F1 separadas do modelo de IA.

    **Limitações:** regras limitadas, falsos positivos e falsos negativos possíveis, sem execução de código, sem auditoria completa, com BM25 local por relevância e corpus editorial versionado (sem embeddings ou busca vetorial).
    """)
    st.markdown("**Referências:** [OWASP SQL Injection Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) · [MITRE CWE](https://cwe.mitre.org/)")

st.caption("GuardAI Sentinel — defensive coding portfolio MVP · Educational only")
