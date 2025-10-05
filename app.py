import os
import io
import random
import string
import hmac
import hashlib
import zipfile
from datetime import datetime, timezone

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

# Estilos extra para tema oscuro (complementa .streamlit/config.toml base=dark)
st.markdown("""
<style>
pre, code, .stCode, .stMarkdown code {
  background:#0f1b2d !important;
  color:#e5e7eb !important;
}
[data-testid="stTable"] th, [data-testid="stDataFrame"] thead th {
  background:#0f172a !important;
  color:#e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

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
    alphabet = string.ascii_letters + string.digits + " .,-_:;()¿?¡!/'\""
    new_char = original_char
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

def _zip_folder_md(folder_path: str) -> io.BytesIO:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, folder_path)
                    zf.write(full_path, arcname=arcname)
    mem.seek(0)
    return mem

def _list_md_files(folder: str):
    if not os.path.isdir(folder):
        return []
    return sorted([f for f in os.listdir(folder) if f.endswith(".md")])

def _delete_md_in_folder(folder: str) -> int:
    if not os.path.isdir(folder):
        return 0
    count = 0
    for f in os.listdir(folder):
        if f.endswith(".md"):
            try:
                os.remove(os.path.join(folder, f))
                count += 1
            except Exception:
                pass
    return count

# ---------------------------
# Cargar datasets
# ---------------------------
@st.cache_data
def load_docs_demo():
    try:
        df = pd.read_csv("data/docs_demo.csv")
        return df
    except Exception:
        st.warning("No se encontró data/docs_demo.csv. Cargando ejemplos por defecto.")
        return pd.DataFrame({
            "id": [1, 2, 3],
            "texto": [
                "Nacimiento de Juan Pérez, 15/03/1995, Madrid. Registro Civil Sección 3ª, Tomo 122, Folio 45.",
                "Matrimonio de Ana López y Luis García, 20/06/2010, Sevilla. Acta nº 6789.",
                "Defunción de María Díaz, 02/11/1980, Valencia. Certificado emitido por el Encargado del Registro."
            ]
        })

@st.cache_data
def load_modelos_confianza():
    try:
        df = pd.read_csv("data/modelos_confianza.csv")
        return df
    except Exception:
        st.warning("No se encontró data/modelos_confianza.csv. Cargando tabla por defecto.")
        return pd.DataFrame({
            "modelo": ["TTP", "Blockchain"],
            "rol": ["Notarías/Registro", "Nodos/Validadores"],
            "garantia": ["Fe pública", "Inmutabilidad probabilística"],
            "mecanismos": ["Identidad verificada", "Criptografía+Consenso"],
            "riesgos": ["Error humano", "Errores de clave/gobernanza"],
            "ejemplos": ["Registro Civil", "Bitcoin/Ethereum"]
        })

docs_df = load_docs_demo()
modelos_df = load_modelos_confianza()

# ---------------------------
# Estado para S1 (selector + texto)
# ---------------------------
if "s1_pick" not in st.session_state:
    st.session_state.s1_pick = int(docs_df["id"].iloc[0])

def _load_selected_text_from_pick():
    """Callback: al cambiar el ID seleccionado, actualiza el texto base y el 'alterado'."""
    pick = st.session_state["s1_pick"]
    base_text = docs_df.loc[docs_df["id"] == pick, "texto"].values[0]
    st.session_state["s1_text"] = base_text
    st.session_state["s1_altered"] = base_text

if "s1_text" not in st.session_state:
    _load_selected_text_from_pick()
if "ledger" not in st.session_state:
    st.session_state.ledger = []  # [{"texto","hash","timestamp","pseudo_firma"}]

# ---------------------------
# Encabezado
# ---------------------------
st.title("UD1 — La confianza en el Derecho y la tecnología")
st.caption("Asignatura: *Blockchain: fundamentos técnicos y problemática jurídica*")

c1, c2, c3, c4 = st.columns(4)
c1.metric("S1", "Hash & Integridad", delta="Registro vs Cadena")
c2.metric("S2", "Sellado de tiempo", delta="Pseudo-firma (HMAC)")
c3.metric("Lecturas", "Nakamoto & Lessig", delta="Preguntas guía")
c4.metric("Entrega", "S1 + S2", delta="Exportación incluida")
st.divider()

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
**Fe pública (Derecho):** garantía institucional de veracidad y autenticidad.  
**Registro:** sistema formal de asientos con reglas de identificación, publicidad, prioridad y oponibilidad.  
**Validación:** procedimientos que confirman requisitos de forma/fondo.  
**Trazabilidad:** reconstrucción íntegra y cronológica del historial.

**En blockchain (tecnología):**
- **Hash (SHA-256)**: huella digital; mínimo cambio → hash totalmente distinto.
- **Cadena de bloques**: cada bloque referencia el hash del anterior.
- **Sellado de tiempo**: fija el momento (timestamp) de un estado.
- **Consenso**: reglas algorítmicas para acordar la versión válida sin un tercero único.
- **Trazabilidad**: historial replicado e (probablemente) inmutable.

> **Idea clave:** el **Derecho** asegura confianza por **autoridad y procedimiento**; la **blockchain**, por **matemática distribuida**.
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
    st.write("**Objetivo:** ver cómo un cambio mínimo rompe la integridad y cómo una **cadena** dificulta la alteración invisible.")

    colA, colB = st.columns([1, 1])
    with colA:
        st.markdown("#### 2.1 Carga un texto de ejemplo")
        id_list = docs_df["id"].tolist()
        index_pick = id_list.index(st.session_state.s1_pick)
        st.selectbox(
            "Selecciona un registro demo (puedes editarlo luego):",
            options=id_list,
            index=index_pick,
            format_func=lambda x: f"ID {x}",
            key="s1_pick",
            on_change=_load_selected_text_from_pick,
        )
        st.text_area("Documento (editable):", key="s1_text", height=120)

        if st.button("🔁 Alterar 1 carácter", key="alter_btn"):
            st.session_state.s1_altered = alter_one_char(st.session_state.s1_text)

        s1_altered = st.session_state.get("s1_altered", st.session_state.s1_text)

    with colB:
        st.markdown("#### 2.2 Hash original vs alterado")
        h_original = sha256_hex(st.session_state.s1_text)
        h_alterado = sha256_hex(s1_altered)

        c1_, c2_ = st.columns(2)
        with c1_:
            st.caption("Hash original")
            st.code(h_original)
        with c2_:
            st.caption("Hash alterado")
            st.code(h_alterado)

        if h_original == h_alterado:
            st.success("Integridad OK: el contenido no ha cambiado.")
        else:
            st.error("⚠️ Integridad rota: el hash no coincide. Cadena de custodia comprometida.")

    st.markdown("#### 2.3 Cadena simulada de 3 asientos")
    st.write("Cada asiento referencia el hash del anterior (prev_hash). Si alteras el primero, **rompes la cadena**.")
    block1 = {"idx": 1, "contenido": st.session_state.s1_text, "hash": sha256_hex(st.session_state.s1_text), "prev_hash": "-"}
    block2 = {"idx": 2, "contenido": "Asiento 2: actualización de domicilio.", "hash": "", "prev_hash": block1["hash"]}
    block2["hash"] = sha256_hex(block2["contenido"] + "|" + block2["prev_hash"])
    block3 = {"idx": 3, "contenido": "Asiento 3: rectificación ortográfica.", "hash": "", "prev_hash": block2["hash"]}
    block3["hash"] = sha256_hex(block3["contenido"] + "|" + block3["prev_hash"])

    chain_df = pd.DataFrame([block1, block2, block3])
    st.dataframe(chain_df, width="stretch")

    st.markdown("#### 2.4 Entrega S1 — Explica en 5 líneas")
    s1_entrega = st.text_area(
        "En 5 líneas: ¿por qué el hash soporta la cadena de custodia y qué aporta encadenar hashes?",
        height=120, key="s1_entrega_text"
    )

    colS1a, colS1b = st.columns([1, 1])
    with colS1a:
        if st.button("💾 Guardar entrega S1 (MD)"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"entregas/S1_explicacion_{ts}.md"
            with open(fname, "w", encoding="utf-8") as f:
                f.write("# Entrega S1 — Hash & Cadena de custodia\n\n")
                f.write(f"**Fecha:** {ts}\n\n")
                f.write("## Texto base\n\n")
                f.write(st.session_state.s1_text + "\n\n")
                f.write(f"**Hash base:** `{h_original}`\n\n")
                f.write("## Explicación (máx. 5 líneas)\n\n")
                f.write((s1_entrega or "").strip() + "\n")
            st.success(f"Entrega guardada en {fname}")

            with open(fname, "r", encoding="utf-8") as fh:
                st.download_button(
                    "⬇️ Descargar ahora (S1)",
                    data=fh.read(),
                    file_name=os.path.basename(fname),
                    mime="text/markdown",
                    key=f"dl_now_{ts}"
                )
    with colS1b:
        st.caption("Criterios: precisión técnica (40%), claridad (30%), conexión con custodia (30%).")

# ---------------------------
# 3) S2 — Sellado de tiempo simulado
# ---------------------------
with tabs[2]:
    st.header("S2 — Sellado de tiempo y pseudo-firma")
    st.write("**Objetivo:** registrar (hash, fecha ISO, pseudo-firma) y comparar TTP vs blockchain.")

    colL, colR = st.columns([1, 1])
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
        st.dataframe(ledger_df, width="stretch", height=240)
        download_csv_button(ledger_df, "⬇️ Exportar ledger CSV", "ledger_ud1.csv")
    else:
        st.caption("Aún no hay entradas registradas.")

    st.markdown("#### Cuadro comparativo: confianza humana vs algorítmica")
    st.dataframe(load_modelos_confianza(), width="stretch")

# ---------------------------
# 4) Comparativa Registro Civil vs Ledger distribuido
# ---------------------------
with tabs[3]:
    st.header("Registro Civil (folio/libro) vs Ledger distribuido (bloques)")
    comp = pd.DataFrame([
        {
            "Función jurídica": "Identificación / Autenticidad",
            "Derecho (Registro Civil)": "Autoridad del Encargado; verificación de identidad; formalidades; fe pública.",
            "Tecnología (Ledger)": "Firmas criptográficas; claves públicas; control de acceso y/o permisos."
        },
        {
            "Función jurídica": "Integridad",
            "Derecho (Registro Civil)": "Cadena de asientos; controles; sellos; copias auténticas.",
            "Tecnología (Ledger)": "Hash y encadenamiento; detección inmediata de cambios."
        },
        {
            "Función jurídica": "Trazabilidad / Historial",
            "Derecho (Registro Civil)": "Asientos cronológicos; certificaciones; anotaciones marginales.",
            "Tecnología (Ledger)": "Historial replicado; timestamps; exploradores de bloques."
        },
        {
            "Función jurídica": "Publicidad / Oponibilidad",
            "Derecho (Registro Civil)": "Publicidad formal bajo la ley; efectos frente a terceros.",
            "Tecnología (Ledger)": "Replicación y lectura compartida; depende del diseño (público/permisionado)."
        },
        {
            "Función jurídica": "Gobernanza",
            "Derecho (Registro Civil)": "Normas, jerarquía, recursos, control judicial.",
            "Tecnología (Ledger)": "Reglas de consenso y upgrades; gobernanza on/off-chain."
        },
    ])
    st.dataframe(comp, width="stretch")
    st.info("La tecnología replica muy bien integridad y trazabilidad; autenticidad y oponibilidad suelen requerir capa jurídica adicional.")

# ---------------------------
# 5) Lecturas guiadas  (MODIFICADO: descarga inmediata + listado + ZIP)
# ---------------------------
with tabs[4]:
    st.header("Lecturas y guía de estudio")
    st.markdown(
        """
**Nakamoto (2008), introducción**  
- Problema: pagos P2P sin TTP.  
- Claves: transacciones encadenadas, PoW, timestamp, nodos honestos.  
- Preguntas: (1) Sustituto del TTP; (2) Timestamp y doble gasto; (3) Réplica/propagación.

**Lessig (1999), Cap. 1 — “Code is Law”**  
- Tesis: el código regula la conducta como la ley/mercado/normas.  
- Preguntas: arquitectura y posibilidad jurídica; auditabilidad/gobernanza; controles en pública vs permisionada.

**Actividad de integración (UD1):**  
- 3 funciones replicadas por tecnología: integridad, trazabilidad, disponibilidad.  
- 2 funciones que dependen de la norma: identidad fuerte, oponibilidad frente a terceros.
"""
    )

    # Generar/guardar guía y ofrecer descarga inmediata
    if st.button("📄 Generar y guardar guía de lectura (MD)"):
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
- 3 funciones replicadas: integridad, trazabilidad, disponibilidad.
- 2 dependientes: identidad fuerte, oponibilidad/efectos frente a terceros.
"""
        os.makedirs("materiales", exist_ok=True)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        st.success(f"Guía guardada en {fname}")

        # Descarga inmediata
        with open(fname, "r", encoding="utf-8") as fh:
            st.download_button(
                "⬇️ Descargar ahora (Guía UD1)",
                data=fh.read(),
                file_name=os.path.basename(fname),
                mime="text/markdown",
                key=f"dl_lect_{ts}"
            )

    st.markdown("---")
    st.info(
        "ℹ️ **Dónde está la guía:** se guarda en el **servidor** dentro de `./materiales`. "
        "Aquí abajo puedes **descargar cualquier guía** ya generada o **todas en ZIP**."
    )

    # Materiales guardados (descarga por archivo)
    st.markdown("#### Materiales guardados (en el servidor)")
    mats = _list_md_files("materiales")
    if mats:
        for idx, f in enumerate(mats):
            path = os.path.join("materiales", f)
            with open(path, "r", encoding="utf-8") as fh:
                st.download_button(
                    label=f"⬇️ Descargar {f}",
                    data=fh.read(),
                    file_name=f,
                    mime="text/markdown",
                    key=f"dl_mat_{idx}_{f}"
                )
    else:
        st.caption("No hay materiales .md generados aún.")

    # ZIP masivo de materiales
    st.markdown("#### Exportación masiva")
    if mats:
        memzip_mat = _zip_folder_md("materiales")
        st.download_button(
            "⬇️ Descargar TODO (ZIP)",
            data=memzip_mat,
            file_name="materiales_ud1.zip",
            mime="application/zip",
            key="zip_materiales_ud1"
        )
    else:
        st.caption("No hay materiales .md para comprimir aún.")

# ---------------------------
# 6) Entregables y rúbrica (con explicación, descargas, ZIP y borrado)
# ---------------------------
with tabs[5]:
    st.header("Entregables (Semana 1) y rúbrica")

    st.info(
        "ℹ️ **Dónde se guardan y cómo bajarlas**\n\n"
        "Cuando pulsas **Guardar entrega**, el archivo se crea en el **servidor** dentro de `./entregas`. "
        "Desde **esta última página** puedes **descargar cada entrega** o **todas en ZIP** al ordenador. "
        "Si trabajas en un entorno efímero, te recomiendo **descargar** tras guardar."
    )

    st.subheader("Entrega S1 — 5 líneas (hash y cadena de custodia)")
    s1_extra = st.text_area("(Opcional) Pegar explicación S1 aquí:", height=120)

    st.subheader("Entrega S2 — Cuadro comparativo: confianza humana vs algorítmica")
    cols = ["Aspecto", "Confianza humana (TTP)", "Confianza algorítmica (Blockchain)"]
    s2_base = pd.DataFrame([
        ["Garantía de veracidad", "Fe pública / autoridad / procedimiento", "Criptografía / consenso / réplica"],
        ["Integridad", "Sellos, controles, copias auténticas", "Hash encadenado, detección de cambios"],
        ["Trazabilidad", "Asientos cronológicos y certificaciones", "Historial inmutable con timestamp"],
        ["Identidad", "Verificación presencial/administrativa", "Claves públicas; capas de identidad externa"],
        ["Oponibilidad", "Efectos legales frente a terceros", "Depende del reconocimiento normativo/gobernanza"],
    ], columns=cols)
    s2_edit = st.data_editor(s2_base, num_rows="dynamic", width="stretch")

    cL, cR = st.columns([1, 1])
    with cL:
        if st.button("⬇️ Exportar comparativo S2 (CSV)"):
            download_csv_button(s2_edit, "Descargar CSV", "S2_comparativo.csv")
    with cR:
        st.caption("Rúbrica: precisión (40%), claridad (30%), aplicación (30%).")

    st.markdown("---")

    # Entregas guardadas
    st.markdown("#### Entregas guardadas (en el servidor)")
    md_files = _list_md_files("entregas")
    if md_files:
        for idx, f in enumerate(md_files):
            file_path = os.path.join("entregas", f)
            with open(file_path, "r", encoding="utf-8") as fh:
                st.download_button(
                    label=f"⬇️ Descargar {f}",
                    data=fh.read(),
                    file_name=f,
                    mime="text/markdown",
                    key=f"dl_file_{idx}_{f}"
                )
    else:
        st.caption("No hay entregas guardadas aún.")

    # ZIP masivo de entregas
    st.markdown("#### Exportación masiva")
    if md_files:
        memzip = _zip_folder_md("entregas")
        st.download_button(
            "⬇️ Descargar TODO (ZIP)",
            data=memzip,
            file_name="entregas_ud1.zip",
            mime="application/zip",
            key="zip_entregas_ud1"
        )
    else:
        st.caption("No hay entregas .md para comprimir aún.")

    # Borrado tras descarga (con confirmación)
    st.markdown("#### Borrado tras descarga")
    confirm = st.checkbox("He descargado mis entregas y quiero borrarlas del servidor")
    if st.button("🧹 Borrar todas las entregas (.md)", disabled=not confirm):
        removed = _delete_md_in_folder("entregas")
        if removed > 0:
            st.success(f"Se borraron {removed} archivo(s) .md de la carpeta 'entregas'.")
        else:
            st.warning("No había archivos .md que borrar.")

    st.markdown(
        """
**Resultado de aprendizaje (UD1):** identificar funciones del Derecho que replica la tecnología (**RA1**),
evaluar herramientas básicas de privacidad/ciberseguridad (**RA2**), y aplicar nociones de sistemas de información (**RA3**).
"""
    )
    st.caption("Aviso: la pseudo-firma HMAC es docente; no equivale a firma electrónica cualificada.")


