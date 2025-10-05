import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Explorador de Licencias", page_icon="📄", layout="wide")
st.title("Explorador de Licencias — Código de Smart Contracts")

st.caption("Objetivo: comprender obligaciones y riesgos de licencias OSS al reutilizar contratos (p. ej., OpenZeppelin).")

licencia = st.selectbox("Licencia", ["MIT", "GPL-3.0", "Apache-2.0", "CC0-1.0"])
uso = st.selectbox("Tipo de uso", ["Comercial cerrado", "Comercial con publicación", "Académico/Investigación", "Open source"])
derivadas = st.checkbox("Habrá obras derivadas (fork/modificación)")
redistribucion = st.checkbox("Habrá redistribución del binario/código")

oblig = []
riesgos = []

if licencia == "MIT":
    oblig.append("Mantener aviso de copyright y licencia.")
    if redistribucion: oblig.append("Incluir la licencia en redistribución.")
    riesgos.append("Pocas obligaciones; responsabilidad limitada del autor.")
elif licencia == "GPL-3.0":
    oblig += ["Copyleft: si distribuyes derivadas, deben ser GPL.", "Publicar código fuente al distribuir binarios."]
    if uso.startswith("Comercial"):
        riesgos.append("Copyleft puede incompatibilizar con uso cerrado.")
elif licencia == "Apache-2.0":
    oblig += ["Aviso de licencia y NOTICES.", "Concesión de patente explícita."]
    riesgos.append("Revisar patentes propias/terceros.")
elif licencia == "CC0-1.0":
    oblig.append("Dominio público (renuncia de derechos); buena práctica citar fuente.")
    riesgos.append("Poca protección frente a reclamaciones de terceros.")

if derivadas and licencia in ("GPL-3.0",):
    riesgos.append("Obligación de mantener copyleft en derivadas.")
if uso == "Comercial cerrado" and licencia == "GPL-3.0":
    riesgos.append("Riesgo alto de incompatibilidad de licencias.")

st.subheader("Obligaciones")
for o in oblig: st.markdown(f"- {o}")

st.subheader("Riesgos")
for r in riesgos: st.markdown(f"- {r}")

st.divider()
st.subheader("Síntesis / Dictamen")
texto = st.text_area("Redacta un breve dictamen sobre la idoneidad de la licencia para tu caso (6–8 líneas).")

e1 = st.slider("Ético", 0, 10, 7); e2 = st.slider("Epistémico", 0, 10, 8); e3 = st.slider("Económico", 0, 10, 8)
score = round((e1+e2+e3)/3, 2)

md = f"""# Explorador de Licencias
- Fecha: {datetime.utcnow().isoformat()}Z
- Licencia: {licencia}
- Uso: {uso}
- Derivadas: {derivadas}
- Redistribución: {redistribucion}

## Obligaciones
{chr(10).join('- ' + x for x in oblig) if oblig else '- (Ninguna específica)'}

## Riesgos
{chr(10).join('- ' + x for x in riesgos) if riesgos else '- (Bajos/Ninguno)'}

## Dictamen
{texto}

## Rúbrica EEE
Ético: {e1} · Epistémico: {e2} · Económico: {e3} · **Score**: {score}
"""
st.download_button("Descargar evidencia (.md)", md.encode("utf-8"), file_name="lab_licencias.md")
