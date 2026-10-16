import json
import sys
import urllib.request
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.generate import (
    LLM_MODEL,
    build_context,
    build_prompt,
    generate_answer,
)
from src.retrieval.search import search

st.set_page_config(page_title="UniTo Guide", page_icon="🎓")
import base64
logo = base64.b64encode(
    (PROJECT_ROOT / "frontend/assets/logo_unito.svg").read_bytes()
).decode("ascii")
st.markdown(
    f'<img src="data:image/svg+xml;base64,{logo}" '
    'alt="Università di Torino" '
    'style="width:120px;max-width:100%;height:auto;margin-bottom:12px;">',
    unsafe_allow_html=True,
)
st.title("🎓 UniTo Guide")
st.markdown("""
<style>
.block-container {max-width: 1050px; padding-top: 6rem;}
[data-testid="stSidebar"] {border-right: 1px solid #e5e5e5;}
h1 {
    font-family: "Avenir Next", Avenir, "Helvetica Neue", Arial, sans-serif !important;
    font-weight: 500 !important;
    color: #54565A !important;
    letter-spacing: -0.03em;
}
[data-testid="stForm"] {border-top: 4px solid #EA0029;}
[data-testid="stFormSubmitButton"] button {
    background-color: #EA0029; color: white; border-color: #EA0029;
}
[data-testid="stFormSubmitButton"] button:hover {
    background-color: #910e19; color: white; border-color: #910e19;
}
</style>
""", unsafe_allow_html=True)
st.write("Fai una domanda sull’orientamento al corso di Informatica.")
st.caption(
    "Prototipo sperimentale: le risposte possono contenere errori. "
    "Controlla sempre i testi e i collegamenti delle fonti recuperate."
)

with st.sidebar:
    st.header("Stato del sistema")
    st.caption(f"Modello: {LLM_MODEL}")
    st.button("Aggiorna stato")
    ready = False
    try:
        with urllib.request.urlopen(
            "http://localhost:11434/api/tags", timeout=3
        ) as response:
            models = json.load(response).get("models", [])
        names = {model.get("name") for model in models}
        if LLM_MODEL in names:
            st.success("Ollama disponibile · modello installato")
            ready = True
        else:
            st.warning(f"Ollama disponibile, ma manca {LLM_MODEL}.")
    except Exception:
        st.error("Ollama non raggiungibile. Apri Ollama e aggiorna lo stato.")

    top_k = 5
    st.caption("Passaggi consultati per domanda: 5")
    st.caption("Pipeline: RAG originale")

with st.form("question_form"):
    question = st.text_input(
        "La tua domanda",
        placeholder="Quale TOLC serve per iscriversi a Informatica?",
    )
    submitted = st.form_submit_button("Cerca e rispondi")

if submitted:
    if not question.strip():
        st.warning("Scrivi una domanda prima di procedere.")
    elif not ready:
        st.warning("Verifica lo stato di Ollama nella barra laterale.")
    else:
        st.session_state.pop("last_result", None)
        try:
            with st.spinner("Cerco i passaggi nelle fonti UniTo…"):
                results = search(question.strip(), top_k)
            if not results:
                st.warning("Nessun passaggio recuperato.")
            else:
                with st.spinner("Genero la risposta con Ollama…"):
                    context = build_context(results)
                    prompt = build_prompt(question.strip(), context)
                    answer = generate_answer(prompt)
                st.session_state["last_result"] = {
                    "question": question.strip(),
                    "answer": answer,
                    "sources": results,
                }
        except Exception as error:
            st.error(f"Non è stato possibile completare la richiesta: {error}")

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    st.subheader("Domanda")
    st.write(result["question"])
    st.subheader("Risposta")
    st.write(result["answer"])
    st.subheader("Fonti recuperate")
    st.caption(
        "I numeri corrispondono alle etichette [FONTE N] del contesto. "
        "Il recupero di un passaggio non garantisce che la risposta lo interpreti correttamente."
    )
    for position, source in enumerate(result["sources"], start=1):
        with st.expander(f"[FONTE {position}] {source['title']}"):
            st.write(source["url"])
            st.caption(
                f"Passaggio: {source['chunk_id']} · "
                f"Similarità: {source['score']:.4f}"
            )
            st.write(source["text"])
