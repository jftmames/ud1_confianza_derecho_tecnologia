import streamlit as st
import hashlib
from datetime import datetime

st.set_page_config(page_title="Hash Visual Demo", page_icon="🔐", layout="wide")
st.title("Hash Visual Demo — Efecto avalancha")

col1, col2 = st.columns(2)
with col1:
    texto = st.text_area("Documento (texto)", "Contrato de arrendamiento 2025 ...", height=160)
    alterar = st.checkbox("Alterar un carácter final automáticamente")
    if alterar and texto:
        texto_mutado = texto[:-1] + ("X" if texto[-1] != "X" else "Y")
    else:
        texto_mutado = st.text_area("Versión B (alterada manualmente)", texto, height=160)
with col2:
    hA = hashlib.sha256((texto or "").encode("utf-8")).hexdigest()
    hB = hashlib.sha256((texto_mutado or "").encode("utf-8")).hexdigest()
    st.code(f"SHA-256 A: {hA}")
    st.code(f"SHA-256 B: {hB}")
    iguales = (hA == hB)
    st.metric("¿Hashes coinciden?", "Sí" if iguales else "No")
    if not iguales:
        st.info("Un solo cambio en el texto provoca un hash totalmente distinto (efecto avalancha).")

st.divider()
st.subheader("Síntesis (200–300 palabras)")
sintesis = st.text_area("¿Qué función jurídica complementa el hash dentro de una blockchain?")
eee1 = st.slider("Ético (0-10)", 0, 10, 7)
eee2 = st.slider("Epistémico (0-10)", 0, 10, 8)
eee3 = st.slider("Económico (0-10)", 0, 10, 7)
score = round((eee1+eee2+eee3)/3, 2)

md = f"""# Hash Visual Demo
- Fecha: {datetime.utcnow().isoformat()}Z
- Hash A: {hA}
- Hash B: {hB}
- Coinciden: {'Sí' if iguales else 'No'}
## Síntesis
{sintesis}

## Rúbrica EEE
- Ético: {eee1}
- Epistémico: {eee2}
- Económico: {eee3}
- **Score**: {score}
"""
st.download_button("Descargar evidencia (.md)", md.encode("utf-8"), file_name="lab_hash_visual.md")
