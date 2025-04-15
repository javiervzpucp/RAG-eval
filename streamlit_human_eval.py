import streamlit as st
import pandas as pd
import os

st.title("🧠 GraphRAG Human Evaluation")
st.markdown("**Esta evaluación se realiza sobre las respuestas generadas por la app [RAG-Sudamérica](https://javiervzpucp-rag-sa.hf.space)**")

STORAGE_PATH = "human_eval_results.csv"
EVAL_SET_PATH = "eval_set_shared.json"

st.markdown("""
### 👥 Instrucciones para evaluadores

Evalúa la calidad de las respuestas generadas por modelos de recuperación aumentada con grafos (GraphRAG).

1. **Ingresa tu nombre o alias** abajo. Esto identificará tus respuestas.
2. Para cada ítem, lee la pregunta y la respuesta generada por el modelo.
3. Evalúa del 1 (muy malo) al 5 (excelente) según los siguientes criterios:
   - **Fidelidad factual**: ¿Está basada en el contexto, sin alucinaciones?
   - **Relevancia**: ¿Responde claramente a la pregunta?
   - **Claridad**: ¿Es comprensible y bien escrita?
   - **Brevedad adecuada**: ¿Es concisa pero suficiente?
   - **Precisión terminológica**: ¿Usa los términos lingüísticos apropiados?
4. Puedes dejar un comentario adicional si deseas.
5. Haz clic en "Guardar y continuar" para pasar al siguiente ítem.

⏱ Tiempo estimado: 15–20 minutos.
""")

evaluator = st.text_input("Nombre del evaluador (obligatorio)", key="evaluator_name")
if not evaluator:
    st.warning("Debes ingresar tu nombre para comenzar.")
    st.stop()

if not os.path.exists(EVAL_SET_PATH):
    st.error(f"No se encontró el archivo {EVAL_SET_PATH}.")
    st.stop()

data = pd.read_json(EVAL_SET_PATH)
st.session_state["data"] = data

if os.path.exists(STORAGE_PATH):
    with open(STORAGE_PATH, "rb") as f:
        st.download_button("📥 Descargar resultados actuales (CSV)", f, file_name="human_eval_results.csv")

if "index" not in st.session_state:
    st.session_state.index = 0

def next_example():
    if st.session_state.index + 1 < len(data):
        st.session_state.index += 1
    else:
        st.success("✅ Evaluación completada. ¡Gracias por participar!")
        st.stop()

row = data.iloc[st.session_state.index]
st.subheader(f"Pregunta {st.session_state.index + 1} de {len(data)}")
st.markdown(f"**Método:** `{row['method']}`")
st.markdown(f"**Pregunta:** {row['question']}")
st.markdown(f"**Respuesta generada:**\n> {row['answer']}")

with st.form(key="eval_form"):
    fidelidad = st.slider("Fidelidad factual", 1, 5, 3)
    relevancia = st.slider("Relevancia", 1, 5, 3)
    claridad = st.slider("Claridad", 1, 5, 3)
    brevedad = st.slider("Brevedad adecuada", 1, 5, 3)
    terminologia = st.slider("Precisión terminológica", 1, 5, 3)
    comentario = st.text_area("Comentarios adicionales", "")

    submitted = st.form_submit_button("Guardar y continuar")
    if submitted:
        result = {
            "evaluator": evaluator,
            "question": row['question'],
            "method": row['method'],
            "answer": row['answer'],
            "fidelidad": fidelidad,
            "relevancia": relevancia,
            "claridad": claridad,
            "brevedad": brevedad,
            "terminologia": terminologia,
            "comentarios": comentario
        }

        if os.path.exists(STORAGE_PATH):
            df = pd.read_csv(STORAGE_PATH)
            df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
        else:
            df = pd.DataFrame([result])

        df.to_csv(STORAGE_PATH, index=False)
        next_example()
