"""Uso:
  python -m src.main --paquete evolucion_clinica_co --entrada paquetes/evolucion_clinica_co/ejemplos --proveedor mock
  python -m src.main --paquete evolucion_clinica_co --entrada nota.txt --proveedor bedrock

`--entrada` puede ser un archivo .txt o una carpeta con varios .txt (un turno completo).
"""
import argparse
from pathlib import Path

from .motor import procesar


def main():
    p = argparse.ArgumentParser(description="Asistente de dominio configurable")
    p.add_argument("--paquete", default="evolucion_clinica_co")
    p.add_argument("--entrada", required=True, help="archivo .txt o carpeta de .txt")
    p.add_argument("--proveedor", choices=["mock", "bedrock", "anthropic"], default="mock")
    p.add_argument("--modelo", default=None, help="ID del modelo (o variable MODEL_ID)")
    a = p.parse_args()

    ruta = Path(a.entrada)
    archivos = sorted(ruta.glob("*.txt")) if ruta.is_dir() else [ruta]
    if not archivos:
        raise SystemExit("No se encontraron archivos .txt en la entrada.")

    for f in archivos:
        r = procesar(f.read_text(encoding="utf-8"), a.paquete, a.proveedor, a.modelo)
        print(f"\n===== {f.name} =====")
        print(r["borrador"])
        print("\n-- DATOS FALTANTES / POR CONFIRMAR --")
        print(r["faltantes"])
        print("\n(Borrador de apoyo: el médico lo revisa, corrige y firma.)")


if __name__ == "__main__":
    main()
