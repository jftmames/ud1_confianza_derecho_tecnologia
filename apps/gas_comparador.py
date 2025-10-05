import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Comparador de Gas", page_icon="⛽", layout="wide")
st.title("Comparador de Gas — Estimación didáctica por complejidad")

st.caption("Modelo didáctico: aproximación basada en operaciones abstractas (no sustituye a un estimator real).")

ops_lec = st.number_input("Operaciones de lectura/lectura de estado", 0, 10_000, 300, step=50)
ops_escr = st.number_input("Operaciones de escritura de estado", 0, 10_000, 120, step=20)
ops_cript = st.number_input("Operaciones criptográficas/pesadas", 0, 10_000, 40, step=10)
precio_gwei = st.number_input("Precio del gas (Gwei)", 1.0, 5000.0, 20.0, step=1.0)
eth_eur = st.number_input("Tipo de cambio ETH→EUR", 200.0, 10000.0, 3000.0, step=50.0)

# Pesos didácticos (gas por operación)
W_READ, W_WRITE, W_CRYPTO = 5, 20, 200
gas_est = ops_lec*W_READ + ops_escr*W_WRITE + ops_cript*W_CRYPTO

# 1 Gwei = 1e-9 ETH; Coste(ETH) = gas * precio_gwei * 1e-9
coste_eth = gas_est * precio_gwei * 1e-9
coste_eur = coste_eth * eth_eur

c1, c2, c3 = st.columns(3)
c1.metric("Gas estimado", f"{gas_est:,}")
c2.metric("Coste estimado (ETH)", f"{coste_eth:.6f}")
c3.metric("Coste estimado (€)", f"{coste_eur:.4f}")

st.info("Consejo: compara dos versiones de la misma función para ver el impacto de escribir estado o usar operaciones criptográficas.")

st.divider()
st.subheader("Evidencia y síntesis")
sintesis = st.text_area("Explica cómo la estimación de gas puede tener valor probatorio (verificación pública en Etherscan/otros).")

e1 = st.slider("Ético", 0, 10, 7); e2 = st.slider("Epistémico", 0, 10, 8); e3 = st.slider("Económico", 0, 10, 8)
score = round((e1+e2+e3)/3, 2)

md = f"""# Comparador de Gas (didáctico)
- Fecha: {datetime.utcnow().isoformat()}Z
- Lectura: {ops_lec} · Escritura: {ops_escr} · Cripto: {ops_cript}
- Gas estimado: {gas_est}
- Gas price: {precio_gwei} Gwei · ETH/EUR: {eth_eur}
- Coste: {coste_eth:.6f} ETH ≈ {coste_eur:.4f} €
## Síntesis
{sintesis}

## Rúbrica EEE
Ético: {e1} · Epistémico: {e2} · Económico: {e3} · **Score**: {score}
"""
st.download_button("Descargar evidencia (.md)", md.encode("utf-8"), file_name="lab_gas_comparador.md")
