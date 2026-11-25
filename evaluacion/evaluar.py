"""Evaluador con graders de código (sin costo extra, resultado reproducible).

Para cada caso revisa:
  1. Estructura: están las cuatro secciones S, O, A, P y la lista de faltantes.
  2. Datos clave: aparecen los datos que el interno dio (signos, pesos, pendientes).
  3. Faltantes: el borrador marca como "por confirmar" lo que la nota no traía.
  4. Fidelidad numérica: ningún número del borrador es ajeno a la nota de entrada
     (detector simple de datos inventados).

Uso:
  python -m evaluacion.evaluar --proveedor mock
  python -m evaluacion.evaluar --proveedor bedrock --modelo <ID>
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.motor import procesar  # noqa: E402

SECCIONES = ["S (Subjetivo)", "O (Objetivo)", "A (Análisis)", "P (Plan)"]


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def numeros(t):
    return set(re.findall(r"\d+(?:[.,]\d+)?", t))


def evaluar_caso(caso, paquete, proveedor, modelo):
    nota = (RAIZ / caso["archivo"]).read_text(encoding="utf-8")
    r = procesar(nota, paquete, proveedor, modelo)
    borrador, faltantes = r["borrador"], r["faltantes"]
    fallos = []

    for s in SECCIONES:
        if norm(s) not in norm(borrador):
            fallos.append(f"falta la sección '{s}'")
    if not faltantes:
        fallos.append("no devolvió la lista de faltantes")

    for dato in caso.get("debe_contener", []):
        if norm(dato) not in norm(borrador):
            fallos.append(f"no incluye el dato '{dato}'")

    for palabra in caso.get("debe_marcar_faltante", []):
        if norm(palabra) not in norm(faltantes):
            fallos.append(f"no marca como faltante '{palabra}'")

    inventados = numeros(borrador) - numeros(nota)
    if inventados:
        fallos.append(f"números que no estaban en la nota: {sorted(inventados)}")

    return fallos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--paquete", default="evolucion_clinica_co")
    p.add_argument("--proveedor", choices=["mock", "bedrock", "anthropic"], default="mock")
    p.add_argument("--modelo", default=None)
    a = p.parse_args()

    casos = json.loads((Path(__file__).parent / "casos.json").read_text(encoding="utf-8"))
    lineas = [f"# Reporte de evaluación ({a.proveedor})\n"]
    ok = 0
    for c in casos:
        fallos = evaluar_caso(c, a.paquete, a.proveedor, a.modelo)
        estado = "OK" if not fallos else "FALLA"
        ok += not fallos
        print(f"{estado}  {c['archivo']}")
        lineas.append(f"- **{estado}** `{c['archivo']}`")
        for f in fallos:
            print(f"      - {f}")
            lineas.append(f"  - {f}")
    resumen = f"\nCasos aprobados: {ok}/{len(casos)}"
    print(resumen)
    lineas.append(resumen)
    if a.proveedor == "mock":
        aviso = "Nota: el modo simulado solo prueba el flujo, no la calidad de un modelo real."
        print(aviso)
        lineas.append(aviso)
    (Path(__file__).parent / "reporte.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
