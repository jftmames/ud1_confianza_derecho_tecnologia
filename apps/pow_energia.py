import streamlit as st
import hashlib, random, time, math
from datetime import datetime

st.set_page_config(page_title="Simulador PoW", page_icon="⚡", layout="wide")
st.title("Simulador de energía y coste — Proof of Work")

dif = st.slider("Dificultad (nº de ceros al inicio)", 1, 6, 3)
kwh_por_mhash = st.number_input("kWh por 1e6 hashes (estimado)", 0.001, 10.0, 0.25, step=0.01)
c_kwh = st.number_input("Coste kWh (€)", 0.01, 2.0, 0.20, step=0.01)
target = "0" * dif

st.caption("Nota: es una simulación didáctica (no mide hardware real).")

if st.button("Ejecutar prueba breve"):
    N = 100_000  # intentos para el muestreo
    t0 = time.time()
    found = False
    for _ in range(N):
        raw = str(random.random())
        h = hashlib.sha256(raw.encode()).hexdigest()
        if h.startswith(target):
            found = True
            break
    t = max(time.time() - t0, 0.001)

    # Estimación simple: probabilidad de éxito 16^(-dif) ≈ (1/16)**dif
    p = (1/16)**dif
    hashes_esperados = 1/p  # valor esperado de intentos
    energia_kwh = (hashes_esperados/1e6) * kwh_por_mhash
    coste = energia_kwh * c_kwh

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Muestra (s)", f"{t:.2f}")
    c2.metric("Prob. teórica", f"{p:.2e}")
    c3.metric("Hash esperados", f"{hashes_esperados:,.0f}")
    c4.metric("Coste estimado (€)", f"{coste:,.4f}")

st.divider()
st.subheader("Síntesis (6–8 líneas)")
sintesis = st.text_area("¿Puede justificarse jurídicamente el gasto energético del PoW?")
e1 = st.slider("Ético", 0, 10, 7); e2 = st.slider("Epistémico", 0, 10, 8); e3 = st.slider("Económico", 0, 10, 6)
score = round((e1+e2+e3)/3, 2)

md = f"""# Simulador PoW
- Fecha: {datetime.utcnow().isoformat()}Z
- Dificultad: {dif}
- kWh/1e6 hashes: {kwh_por_mhash}
- Precio kWh: {c_kwh} €
## Síntesis
{sintesis}

## Rúbrica EEE
Ético: {e1} · Epistémico: {e2} · Económico: {e3} · **Score**: {score}
"""
st.download_button("Descargar evidencia (.md)", md.encode("utf-8"), file_name="lab_pow_energia.md")
