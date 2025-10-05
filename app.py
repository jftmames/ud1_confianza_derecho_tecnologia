
---

# app.py

```python
import os
import io
import random
import string
import hmac
import hashlib
from datetime import datetime, timezone
from dateutil import tz

import pandas as pd
import streamlit as st

# ---------------------------
# Configuración general
# ---------------------------
st.set_page_config(
    page_title="UD1 — Confianza en el Derecho y la tecnología",
    page_icon="✅",
    layout="wide",
)

PRIMARY = "#0f766e"
os.makedirs("entregas", exist_ok=True)
os.makedirs("materiales", exist_ok=True)

# ---------------------------
# Utilidades
# ---------------------------
def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def alter_one_char(text: str) -> str:
    if not text:
        return text
    pos = random.randrange(len(text))
    original_char = text[pos]
    # Alfabeto de sustitución básico (evita repetir el mismo char)
    alphabet = string.ascii_letters + string.digits + " .,-_:;()¿?¡!/'\""
    new_char = original_char
    # Garantizar cambio
    for _ in range(10):
        candidate = random.choice(alphabet)
        if candidate != original_char:
            new_char = candidate
            break
    return text[:pos] + new_char + text[pos+1:]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def pseudo_signature(hash_value: str, timestamp_iso: str, key: str = "DEMO_SECRET") -> str:
    msg = f"{hash_value}|{timestamp_iso}".encode("utf-8")
    return hmac.new(key.encode("utf-8"), msg, hashlib.sha256).hexdigest()

def download_csv_button(df: pd.DataFrame, label: str, filename: str):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button(label, buf.getvalue(), file_name=filename, mime="text/csv")


# ---------------------------
# Cargar datasets
# ---------------------------
@st.cache_data
def load_docs_demo():
    try:
        df = pd.read_csv("data/docs_demo.csv")
        return df
    except Exception as e:
        st.warning("No se encontró data/docs_demo.csv. Cargando ejemplos por defecto.")
        return pd.DataFrame({
            "id": [1,2],
            "texto": [
                "Nacimiento de Juan Pérez... Registro Civil Sección 3ª.",
                "Matrimonio de Ana López y Luis García... Acta nº 6789."
            ]
        })

@st.cache_data
def load_modelos_confianza():
    try:
        df = pd.read_csv("data/modelos_confianza.csv")
        return df
    except Exception as e:
        st.warning("No se encontró data/modelos_confianza.csv. Cargando tabla por defecto.")
        return pd.DataFrame({
            "modelo": ["TTP","Blockchain"],
            "rol": ["Notarías/Registro","Nodos/Validadores"],
            "garantia": ["Fe pública","Inmutabilidad probabilística"],
            "mecanismos": ["Identidad verificada","Criptografía+Consenso"],
            "riesgos": ["Error humano","Errores de clave/gobernanza"],
            "ejemplos": ["Registro Civil","Bitcoin/Ethereum"]
        })

docs_df = load_docs_demo()
modelos_df = load_modelos_confianza()

# Estado
if "ledger" not in st.session_state:
    st.session_state.ledger = []  # lista de dicts: {"texto","hash","timestamp","psig"}

# ---------------------------
# Encabezado
# ---------------------------
st.title("UD1 — La confianza en el Derecho y la tecnología")
st.caption("Asignatura: *Blockchain: fundamentos técnicos y problemática jurídica*")

with st.container():
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("S1", "Hash & Integridad", delta="Registro vs Cadena")
    c2.metric("S2", "Sellado de tiempo", delta="Pseudo-firma (HMAC)")
    c3.metric("Lecturas", "Nakamoto & Lessig", delta="Preguntas guía")
    c4.metric("Entrega", "S1 + S2", delta="Exportación incluida")

st.divider()

# ---------------------------
# Tabs principales
# ---------------------------
tabs = st.tabs([
    "1) Teoría",
    "2) S1 — Hash & Cadena de custodia",
    "3) S2 — Sellado de tiempo simulado",
    "4) Comparativa Registro vs Ledger",
    "5) Lecturas guiadas",
    "6) Entregables y rúbrica"
])

# ---------------------------
# 1) Teoría
# ---------------------------
with tabs[0]:
    st.subheader("Confianza: del Derecho a la verificación criptográfica")
    st.markdown(
        """
**Fe pública (Derecho):** garantía institucional de veracidad y autenticidad otorgada por funcionarios/órganos (p. ej. Encargado del Registro, notario).  
**Registro:** sistema formal de asientos (folio/libro) con reglas de **identificación, publicidad, prioridad y oponibilidad**.  
**Validación:** reglas y procedimientos que confirman requisitos de forma/fondo; control humano y normativo.  
**Trazabilidad:** capacidad de reconstruir el historial **íntegro** y **cronológico** de un dato/asiento (quién, cuándo, qué).

**En blockchain (tecnología):**
- **Hash (SHA-256)**: huella digital del contenido. Un cambio mínimo → hash distinto (**efecto avalancha**).
- **Cadena de bloques**: cada bloque referencia el hash del anterior → **integridad enlazada**.
- **Sellado de tiempo**: fija el momento de creación/verificación (timestamp) de un estado.
- **Consenso**: reglas algorítmicas para acordar qué versión es válida (PoW/PoS/…) sin un tercero único.
- **Trazabilidad**: historial inmutable (probabilísticamente) replicado en múltiples nodos.

> **Idea clave:** el **Derecho** asegura confianza por **autoridad y procedimiento**; la **blockchain**, por **matemática distribuida** (hash, consenso, réplica).
"""
    )

    st.markdown("### Mini-demo: calcula el hash de un texto")
    demo_text = st.text_area("Texto", "Acta: Nacimiento de Juan Pérez, 15/03/1995, Madrid.", height=90)
    st.code(sha256_hex(demo_text), language="bash")
    st.info("Si cambias una sola letra, el hash cambia por completo (efecto avalancha).")

# ---------------------------
# 2) S1 — Hash & Cadena de custodia
# ---------------------------
with tabs[1]:
    st.header("S1 — Registro centralizado vs cadena con hash")
    st.write("**Objetivo:** ver cómo un cambio mínimo rompe la integridad, y cómo una **cadena** dificulta la alteración invisible.")

    colA, colB = st.columns([1,1])
    with colA:
        st.markdown("#### 2.1 Carga un texto de ejemplo")
        pick = st.selectbox(
            "Selecciona un registro demo (puedes editarlo luego):",
            options=docs_df["id"].tolist(),
            format_func=lambda x: f"ID {x}"
        )
        base_text = docs_df.loc[docs_df["id"] == pick, "texto"].values[0]
        text_input = st.text_area("Documento (editable):", base_text, height=120, key="s1_text")

        if st.button("🔁 Alterar 1 carácter", key="alter_btn"):
            st.session_state.s1_altered = alter_one_char(text_input)
        # Estado inicial si aún no existe
        s1_altered = st.session_state.get("s1_altered", text_input)

    with colB:
        st.markdown("#### 2.2 Hash original vs alterado")
        h_original = sha256_hex(text_input)
        h_alterado = sha256_hex(s1_altered)

        c1, c2 = st.columns(2)
        with c1:
            st.caption("Hash original")
            st.code(h_original)
        with c2:
            st.caption("Hash alterado")
            st.code(h_alterado)

        if h_original == h_alterado:
            st.success("Integridad OK: el contenido no ha cambiado.")
        else:
            st.error("⚠️ Integridad rota: el hash no coincide. La cadena de custodia estaría comprometida.")

    st.markdown("#### 2.3 Cadena simulada de 3 asientos")
    st.write("Cada asiento referencia el hash del anterior (prev_hash). Si alteras el primero, **rompes la cadena**.")
    # Construcción de cadena simple a partir del texto actual
    block1 = {"idx": 1, "contenido": text_input, "hash": sha256_hex(text_input), "prev_hash": "-"}
    block2 = {"idx": 2, "contenido": "Asiento 2: actualización de domicilio.", "hash": "", "prev_hash": block1["hash"]}
    block2["hash"] = sha256_hex(block2["contenido"] + "|" + block2["prev_hash"])
    block3 = {"idx": 3, "contenido": "Asiento 3: rectificación ortográfica.", "hash": "", "prev_hash": block2["hash"]}
    block3["hash"] = sha256_hex(block3["contenido"] + "|" + block3["prev_hash"])

    chain_df = pd.DataFrame([block1, block2, block3])
    st.dataframe(chain_df, use_container_width=True)

    st.markdown("#### 2.4 Entrega S1 — Explica en 5 líneas")
    s1_entrega = st.text_area(
        "En 5 líneas: ¿por qué el hash soporta la cadena de custodia y qué aporta encadenar hashes?",
        height=120, key="s1_entrega_text"
    )

    colS1a, colS1b = st.columns([1,1])
    with colS1a:
        if st.button("💾 Guardar entrega S1 (MD)"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"entregas/S1_explicacion_{ts}.md"
            with open(fname, "w", encoding="utf-8") as f:
                f.write("# Entrega S1 — Hash & Cadena de custodia\n\n")
                f.write(f"**Fecha:** {ts}\n\n")
                f.write("## Texto base\n\n")
                f.write(text_input + "\n\n")
                f.write(f"**Hash base:** `{h_original}`\n\n")
                f.write("## Explicación (máx. 5 líneas)\n\n")
                f.write(s1_entrega.strip() + "\n")
            st.success(f"Entrega guardada en {fname}")
    with colS1b:
        st.caption("Criterios: precisión técnica (40%), claridad (30%), conexión con custodia (30%).")

# ---------------------------
# 3) S2 — Sellado de tiempo simulado
# ---------------------------
with tabs[2]:
    st.header("S2 — Sellado de tiempo y pseudo-firma")
    st.write("**Objetivo:** registrar (hash, fecha ISO, pseudo-firma) y comparar TTP vs blockchain.")

    colL, colR = st.columns([1,1])
    with colL:
        s2_text = st.text_area("Texto a registrar (puedes pegar del S1 o nuevo):", height=130, key="s2_text")

        if st.button("🕒 Generar hash + timestamp + pseudo-firma"):
            _hash = sha256_hex(s2_text)
            _iso = now_iso()
            _psig = pseudo_signature(_hash, _iso, key="DEMO_SECRET")

            st.session_state.last_record = {"texto": s2_text, "hash": _hash, "timestamp": _iso, "pseudo_firma": _psig}
            st.success("Registro preparado. Revisa la derecha y pulsa 'Registrar en ledger' si estás conforme.")

    with colR:
        st.markdown("#### Previsualización del registro")
        last = st.session_state.get("last_record")
        if last:
            st.json(last, expanded=False)
            if st.button("📌 Registrar en ledger"):
                st.session_state.ledger.append(last)
                st.success("Añadido al mini-ledger local (memoria de la app).")
        else:
            st.info("Genera un registro a la izquierda para previsualizarlo aquí.")

    st.markdown("#### Mini-ledger (local, en memoria)")
    ledger_df = pd.DataFrame(st.session_state.ledger)
    if not ledger_df.empty:
        st.dataframe(ledger_df, use_container_width=True, height=240)
        download_csv_button(ledger_df, "⬇️ Exportar ledger CSV", "ledger_ud1.csv")
    else:
        st.caption("Aún no hay entradas registradas.")

    st.markdown("#### Cuadro comparativo: confianza humana vs algorítmica")
    st.dataframe(modelos_df, use_container_width=True)

# ---------------------------
# 4) Comparativa Registro Civil vs Ledger distribuido
# ---------------------------
with tabs[3]:
    st.header("Registro Civil (folio/libro) vs Ledger distribuido (bloques)")
    comp = pd.DataFrame([
        {
            "Función jurídica": "Identificación / Autenticidad",
            "Derecho (Registro Civil)": "Autoridad del Encargado; verificación de identidad; formalidades; fe pública.",
            "Tecnología (Ledger)": "Firmas criptográficas; claves públicas; control de acceso y/o permisos en consorcio."
        },
        {
            "Función jurídica": "Integridad",
            "Derecho (Registro Civil)": "Cadena de asientos; controles; sellos; copias auténticas.",
            "Tecnología (Ledger)": "Hash y encadenamiento de bloques; detección inmediata de cambios (diferencia de hash)."
        },
        {
            "Función jurídica": "Trazabilidad / Historial",
            "Derecho (Registro Civil)": "Asientos cronológicos; certificaciones; anotaciones marginales.",
            "Tecnología (Ledger)": "Historial inmutable replicado; timestamps; exploradores de bloques."
        },
        {
            "Función jurídica": "Publicidad / Oponibilidad",
            "Derecho (Registro Civil)": "Publicidad formal bajo la ley; efectos frente a terceros.",
            "Tecnología (Ledger)": "Replicación y lectura compartida; en público/permisionado según diseño."
        },
        {
            "Función jurídica": "Gobernanza",
            "Derecho (Registro Civil)": "Normas, jerarquía, recursos, control judicial.",
            "Tecnología (Ledger)": "Reglas de consenso y upgrades; gobernanza on/off-chain; riesgos de captura."
        },
    ])
    st.dataframe(comp, use_container_width=True)

    st.info(
        "Conclusión operativa: la tecnología **replica** funciones de **integridad** y **trazabilidad** muy bien; "
        "la **autenticidad** y la **oponibilidad** requieren a menudo acoplar identidad, gobernanza y norma."
    )

# ---------------------------
# 5) Lecturas guiadas
# ---------------------------
with tabs[4]:
    st.header("Lecturas y guía de estudio")
    st.markdown(
        """
**Nakamoto (2008), introducción — “Bitcoin: A Peer-to-Peer Electronic Cash System”**  
- Qué problema ataca: pagos P2P sin intermediario de confianza.  
- Piezas técnicas clave en la intro: transacciones encadenadas, prueba de trabajo, timestamping, nodos honestos.  
- Preguntas guía:  
  1) ¿Qué reemplaza al tercero de confianza?  
  2) ¿Cómo ayuda el timestamping a resolver el doble gasto?  
  3) ¿Por qué la propagación y réplica aportan robustez?

**Lessig (1999), Cap. 1 — “Code is Law”**  
- Tesis: el **código** (arquitectura técnica) regula la conducta como la ley, el mercado y las normas sociales.  
- Preguntas guía:  
  1) ¿Cómo la arquitectura técnica condiciona lo jurídicamente posible?  
  2) ¿Qué riesgos ves si la arquitectura no es auditable ni gobernable?  
  3) ¿Dónde colocarías los “controles” en una blockchain pública vs. permisionada?

**Actividad de integración (UD1):**  
- Identifica **3 funciones del Derecho** que **sí** replica la tecnología de forma fiable.  
- Identifica **2 funciones** que todavía **dependen** de estructuras jurídicas (identidad fuerte, efectos frente a terceros, etc.).
"""
    )

    if st.button("📄 Descargar guía de lectura (MD)"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"materiales/UD1_lecturas_{ts}.md"
        content = """# Guía de lectura — UD1

## Nakamoto (2008), introducción
- Problema: pagos P2P sin TTP.
- Claves: cadena de transacciones, PoW, timestamp, nodos honestos.
- Preguntas: (1) Sustituto del TTP; (2) Timestamp y doble gasto; (3) Réplica/propagación.

## Lessig (1999), Cap. 1
- Tesis: el código regula (como la ley/mercado/normas).
- Preguntas: arquitectura y posibilidad jurídica; auditabilidad/gobernanza; controles en pública vs permisionada.

## Integración
- 3 funciones replicadas (tecnología): integridad, trazabilidad, disponibilidad.
- 2 funciones dependientes (jurídicas): identidad fuerte, oponibilidad/efectos frente a terceros.
"""
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        st.success(f"Guía guardada en {fname}")

# ---------------------------
# 6) Entregables y rúbrica
# ---------------------------
with tabs[5]:
    st.header("Entregables (Semana 1) y rúbrica")

    st.subheader("Entrega S1 — 5 líneas (hash y cadena de custodia)")
    st.write("Sube la explicación ya guardada en S1 o pégala aquí si la vas a exportar aparte.")
    s1_extra = st.text_area("(Opcional) Pegar explicación S1 aquí:", height=120)

    st.subheader("Entrega S2 — Cuadro comparativo: confianza humana vs algorítmica")
    st.write("Completa el cuadro con tus propios matices. Puedes exportarlo.")
    cols = ["Aspecto", "Confianza humana (TTP)", "Confianza algorítmica (Blockchain)"]
    s2_base = pd.DataFrame([
        ["Garantía de veracidad", "Fe pública / autoridad / procedimiento", "Criptografía / consenso / réplica"],
        ["Integridad", "Sellos, controles, copias auténticas", "Hash encadenado, detección de cambios"],
        ["Trazabilidad", "Asientos cronológicos y certificaciones", "Historial inmutable con timestamp"],
        ["Identidad", "Verificación presencial/administrativa", "Claves públicas; capas de identidad externa"],
        ["Oponibilidad", "Efectos legales frente a terceros", "Depende del reconocimiento normativo/gobernanza"],
    ], columns=cols)
    s2_edit = st.experimental_data_editor(s2_base, num_rows="dynamic", use_container_width=True)

    cL, cR = st.columns([1,1])
    with cL:
        if st.button("⬇️ Exportar comparativo S2 (CSV)"):
            download_csv_button(s2_edit, "Descargar CSV", "S2_comparativo.csv")
    with cR:
        st.caption("Rúbrica (ambas entregas): precisión (40%), claridad (30%), aplicación (30%).")

    st.markdown("---")
    st.markdown(
        f"""
**Resultado de aprendizaje (UD1):** identificar qué funciones del Derecho **replica** la tecnología  
(**RA1**), evaluar herramientas de privacidad/ciberseguridad básicas (**RA2**) y aplicar nociones de sistemas de información a soluciones legales (**RA3**).
"""
    )

    st.caption("Aviso: la pseudo-firma HMAC aquí mostrada es **docente** y no equivale a firma electrónica cualificada.")

# Fin
