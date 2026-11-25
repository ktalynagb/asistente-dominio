"""Capa de modelo intercambiable: Amazon Bedrock, API directa de Anthropic o modo simulado.

El resto del proyecto solo llama a `generar(...)`, así que cambiar de proveedor
no requiere tocar nada más.
"""
import os
import re


def generar(proveedor, system, mensaje_usuario, modelo, temperatura, max_tokens):
    if proveedor == "bedrock":
        return _bedrock(system, mensaje_usuario, modelo, temperatura, max_tokens)
    if proveedor == "anthropic":
        return _anthropic(system, mensaje_usuario, modelo, temperatura, max_tokens)
    if proveedor == "mock":
        return _mock(mensaje_usuario)
    raise ValueError(f"Proveedor desconocido: {proveedor}")


def _bedrock(system, mensaje_usuario, modelo, temperatura, max_tokens):
    import boto3  # se importa aquí para que el modo simulado no lo requiera

    cliente = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    resp = cliente.converse(
        modelId=modelo,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": mensaje_usuario}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperatura},
    )
    return resp["output"]["message"]["content"][0]["text"]


def _anthropic(system, mensaje_usuario, modelo, temperatura, max_tokens):
    import anthropic

    cliente = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno
    resp = cliente.messages.create(
        model=modelo,
        max_tokens=max_tokens,
        temperature=temperatura,
        system=system,
        messages=[{"role": "user", "content": mensaje_usuario}],
    )
    return resp.content[0].text


def _mock(mensaje_usuario):
    """Respuesta simulada y determinista. Sirve SOLO para probar el flujo sin
    gastar dinero; no refleja la calidad de un modelo real."""
    m = re.search(r"<nota_paciente>(.*?)</nota_paciente>", mensaje_usuario, re.S)
    nota = (m.group(1) if m else mensaje_usuario).strip()
    lineas = [l.strip() for l in nota.splitlines() if l.strip()]
    texto = nota.lower()

    def contiene(*palabras):
        return any(p in texto for p in palabras)

    faltantes = []
    if not contiene("alergia"):
        faltantes.append("Alergias: no se mencionan, confirmar.")
    if not contiene("tensión", "tension", "ta ", "fc", "frecuencia"):
        faltantes.append("Signos vitales: no se mencionan, confirmar.")
    if not contiene("plan", "pendiente"):
        faltantes.append("Plan o pendientes: no se mencionan, confirmar.")
    if not faltantes:
        faltantes.append("Ninguno detectado en el modo simulado; revisar igualmente.")

    cuerpo = "\n".join(f"- {l}" for l in lineas)
    return (
        "<borrador>\n"
        "S (Subjetivo):\n" + cuerpo + "\n\n"
        "O (Objetivo):\n" + cuerpo + "\n\n"
        "A (Análisis):\nPor completar por el médico.\n\n"
        "P (Plan):\nPor completar por el médico.\n"
        "</borrador>\n"
        "<faltantes>\n" + "\n".join(f"- {f}" for f in faltantes) + "\n</faltantes>"
    )
