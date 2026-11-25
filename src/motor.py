"""Motor general: carga un paquete de dominio, arma el prompt y llama al modelo.

No sabe nada de medicina ni de negocios. Todo lo específico vive en la carpeta
del paquete (system_prompt.md + config.json).
"""
import json
import os
import re
from pathlib import Path

from .llm import generar

RAIZ = Path(__file__).resolve().parent.parent


def cargar_paquete(nombre):
    carpeta = RAIZ / "paquetes" / nombre
    if not carpeta.is_dir():
        raise FileNotFoundError(f"No existe el paquete '{nombre}' en {carpeta.parent}")
    system = (carpeta / "system_prompt.md").read_text(encoding="utf-8")
    config = json.loads((carpeta / "config.json").read_text(encoding="utf-8"))
    return system, config


def extraer(etiqueta, texto):
    m = re.search(rf"<{etiqueta}>(.*?)</{etiqueta}>", texto, re.S)
    return m.group(1).strip() if m else ""


def procesar(nota, paquete, proveedor, modelo=None):
    system, config = cargar_paquete(paquete)
    modelo = modelo or os.getenv("MODEL_ID") or config.get("modelo_por_defecto", "")
    mensaje = f"<nota_paciente>\n{nota.strip()}\n</nota_paciente>"
    respuesta = generar(
        proveedor,
        system,
        mensaje,
        modelo,
        config.get("temperatura", 0.2),
        config.get("max_tokens", 1500),
    )
    return {
        "borrador": extraer("borrador", respuesta),
        "faltantes": extraer("faltantes", respuesta),
        "crudo": respuesta,
    }
