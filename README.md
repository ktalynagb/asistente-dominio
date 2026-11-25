# Asistente de dominio configurable

Plantilla pequeña para construir asistentes con Claude. El motor es general; cada disciplina es una carpeta en `paquetes/` con su prompt del sistema y su configuración. Incluye un primer paquete de ejemplo: **evolución clínica (Colombia)**.

> ## Aviso importante
> Este es un **prototipo de investigación y portafolio**, no un dispositivo médico ni una herramienta para uso clínico.
> - Genera **borradores** de apoyo a la redacción. El médico siempre revisa, corrige y firma.
> - **No diagnostica ni recomienda tratamientos.** No inventa datos: lo que falta lo marca como "por confirmar".
> - Todos los casos incluidos son **ficticios**. No uses datos reales de pacientes: la historia clínica es reservada (Resolución 1995 de 1999) y sus datos personales están protegidos (Ley 1581 de 2012). Usarla con pacientes reales requiere cumplir esas normas y las políticas de la institución.

## Cómo funciona

```
nota suelta del interno ──► motor (prompt del sistema + etiquetas XML) ──► Claude
                                                                            │
        borrador SOAP + lista de faltantes  ◄───────────────────────────────┘
```

- `src/llm.py`: capa de modelo intercambiable (`bedrock`, `anthropic` o `mock`).
- `src/motor.py`: carga el paquete, arma el mensaje y separa borrador y faltantes.
- `paquetes/evolucion_clinica_co/`: `system_prompt.md`, `config.json` y casos de ejemplo.
- `evaluacion/`: casos de prueba y evaluador con graders de código.

Conceptos del curso que aplica esta versión: prompt del sistema, etiquetas XML, parámetros (temperatura baja, `max_tokens`), Amazon Bedrock y evaluación de prompts con graders de código. Quedan para una siguiente etapa: streaming, uso de herramientas por lotes, RAG, MCP y grader de modelo.

## Probarlo sin gastar nada (modo simulado)

```bash
python3 -m src.main --paquete evolucion_clinica_co --entrada paquetes/evolucion_clinica_co/ejemplos --proveedor mock
python3 -m evaluacion.evaluar --proveedor mock
```

El modo simulado solo comprueba que el flujo funciona. **No refleja la calidad de un modelo real.**

## Usarlo con un modelo real

Con Amazon Bedrock (requiere AWS configurado y acceso al modelo habilitado en tu cuenta; Bedrock se cobra por tokens):

```bash
pip install boto3
export AWS_REGION=us-east-1
export MODEL_ID="<ID del modelo copiado de tu consola de Bedrock>"
python3 -m src.main --entrada paquetes/evolucion_clinica_co/ejemplos --proveedor bedrock
python3 -m evaluacion.evaluar --proveedor bedrock
```

Con la API directa de Anthropic:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
export MODEL_ID="<ID del modelo>"
python3 -m src.main --entrada nota.txt --proveedor anthropic
```

`--entrada` acepta un archivo `.txt` o una carpeta con varios (un turno completo de pacientes).

## Qué mide la evaluación

Para cada caso ficticio, el evaluador revisa que el borrador tenga las secciones S, O, A y P, que incluya los datos clave que se dieron, que marque como faltante lo que la nota no traía y que **no contenga números ajenos a la nota** (detector simple de datos inventados). Escribe el resultado en `evaluacion/reporte.md`.

## Crear un paquete para otra disciplina

1. Copia `paquetes/evolucion_clinica_co` con otro nombre.
2. Cambia `system_prompt.md` (rol, reglas y formato de salida).
3. Ajusta `config.json` y agrega tus casos en `evaluacion/casos.json`.
4. Ejecuta con `--paquete tu_paquete`.

## Estado y próximos pasos

Versión mínima. Si funciona bien, siguen: streaming, procesamiento por lotes con herramientas, grader de modelo para fidelidad, comparación de modelos (calidad, latencia y costo) y un segundo paquete (por ejemplo, notas de reunión para CRM).

## Hoja de ruta

- [ ] **Streaming** de la respuesta para ver el borrador mientras se genera.
- [ ] **Procesamiento por lotes con herramientas** (tool use) para un turno completo de pacientes.
- [ ] **Grader de modelo** que revise la fidelidad del borrador frente a la nota, además de los graders de código.
- [ ] **Comparación Haiku vs. Sonnet** en calidad, latencia y costo, con el mismo set de evaluación.
- [ ] **Más casos de prueba** ficticios, revisados por alguien del área de la salud.

## Licencia

[MIT](LICENSE) © 2026 Ktalyna García Benavides.
