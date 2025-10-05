# UD1 — La confianza en el Derecho y la tecnología (Streamlit)

## Objetivo
Entender el paso de la confianza institucional (fe pública) a la verificación criptográfica (hash, timestamp, ledger distribuido) y detectar qué funciones del Derecho replica la tecnología.

## Contenido en la app
- Teoría: fe pública, registro, validación, trazabilidad; comparación Registro Civil vs ledger.
- Práctica S1: hash, alteración de 1 carácter, alerta de integridad.
- Práctica S2: sellado de tiempo simulado, pseudo-firma (HMAC), registro en un mini-ledger y cuadro comparativo TTP vs blockchain.
- Lecturas guiadas: Nakamoto (2008, intro) y Lessig (1999, cap. 1).
- Entregables: explicación en 5 líneas (S1) y cuadro comparativo “confianza humana vs algorítmica” (S2), con exportación.

## Ejecución
```bash
pip install -r requirements.txt
streamlit run app.py
