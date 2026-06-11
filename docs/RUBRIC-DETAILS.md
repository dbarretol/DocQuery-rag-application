# Control — App de IA/ML en contenedor

**Modelos en Producción · UNI 2026 · Rodrigo López Vera**

## Objetivo

Construir una pequeña app de IA/ML que reciba una entrada (p. ej. una pregunta o un texto) y devuelva una respuesta (una respuesta de AI o una predicción), empaquetarla en una imagen Docker, y entregármela para que yo la levante y la pruebe.

## Qué construir

Un servicio que recibe una entrada y devuelve una salida usando IA/ML. Tú eliges el tema y el enfoque. No tiene que ser complejo; tiene que funcionar y correr.

## Proyectos sugeridos (elige uno)

- API como la de clase: FastAPI con un endpoint que recibe una pregunta y responde (RAG con un LLM sobre tus propios documentos).
- QA sobre una página web: indexa el contenido de una web y responde preguntas sobre ella.
- Problema clásico de ML: entrena o usa un modelo (p. ej. clasificador de sentimiento/spam) y exponlo como API que "responde" a una entrada.

## Definición de "Hecho"

1. Va empaquetado en una imagen Docker que arranca con un solo comando.
2. Incluye un README con: cómo construir o cargar la imagen, cómo correrla, y1 ejemplo de entrada → respuesta.
3. Si usas una API key (Gemini, OpenAI, etc.), se inyecta en runtime (`-e API_KEY=...`), nunca dentro de la imagen.
4. Me entregas la imagen de cualquier forma: link a GHCR, archivo `.tar` (`docker save`), o un repo con el Dockerfile.

## Evaluación

Sigo tu README. Normalmente:

```bash
docker run --rm -p 8000:8000 -e API_KEY=... TU_IMAGEN
```

(o `docker load` si me mandas un `.tar`).

Luego pruebo tu ejemplo y un par de entradas mías. Si no arranca siguiendo tu README, no puedo evaluarlo: prioriza que corra.

## Puntos extra (opcional, suma sobre lo visto en clase)

- Repo en Git limpio: `.gitignore` + `.dockerignore`, sin secretos.
- Dockerfile de producción: base slim + uv con lockfile + orden de capas.
- Imagen publicada en GHCR.
- CI con GitHub Actions (lint/test/build/push, tag por SHA).
- Tests (`pytest`), lint (`ruff`) o pre-commit; o `/metrics`.
- Cualquier otra práctica vista en clase (Kubernetes, observabilidad, MLflow).

## Rúbrica (20 pts)

| Criterio | Pts |
|-----------|-----|
| La imagen arranca con un solo `docker run` | 6 |
| El modelo/IA funciona: responde de forma correcta y pertinente a la entrada | 6 |
| README claro (construir/correr + 1 ejemplo) | 3 |
| Puntos extra (Git, GHCR, CI, Dockerfile slim/uv, tests/lint, etc.) | 5 |