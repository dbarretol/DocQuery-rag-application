Analiza los requisitos definidos en `@docs\RUBRIC-DETAILS.md` y diseña una propuesta de solución que cumpla completamente con la rúbrica indicada.

La aplicación a desarrollar será una plataforma de consulta inteligente sobre documentos cargados por el usuario. El objetivo es que el usuario pueda subir uno o varios documentos y posteriormente realizar preguntas sobre su contenido utilizando capacidades de IA.

## Funcionalidades principales

### 1. Carga de documentos

La interfaz debe incluir una zona de arrastrar y soltar (drag & drop) que permita cargar distintos tipos de archivos, incluyendo como mínimo:

* Markdown (`.md`)
* PDF (`.pdf`)
* Imágenes (`.png`, `.jpg`, `.jpeg`, `.webp`)
* Otros formatos que consideres razonables y sencillos de soportar

### 2. Procesamiento e indexación

Una vez cargados, los documentos deben ser procesados e indexados para permitir consultas posteriores mediante técnicas de búsqueda semántica y/o RAG (Retrieval-Augmented Generation).

### 3. Chat de consultas

El usuario podrá realizar preguntas sobre los documentos cargados y recibir respuestas generadas por IA.

### 4. Trazabilidad de las respuestas

Cada respuesta debe indicar claramente qué fragmentos, documentos o fuentes fueron utilizados como contexto para generar la respuesta. La interfaz debe mostrar esta información de forma visible para que el usuario pueda verificar el origen de los datos.

### 5. Preguntas sugeridas

La aplicación debe generar automáticamente preguntas sugeridas relacionadas con los documentos cargados para facilitar la exploración del contenido.

## Restricciones técnicas

* Revisa el contenido de `@legacy\` (proyecto generico de rag usando google genai) para comprender la arquitectura existente y reutilizar patrones, componentes o código cuando resulte conveniente.
* Considera el proyecto dentro del alcance de la asignatura y evita complejidad innecesaria.
* Prioriza una implementación robusta, sencilla de ejecutar y fácil de evaluar.
* Todas las dependencias deben gestionarse mediante **uv**.
* Utiliza exclusivamente comandos de **PowerShell** en toda la documentación, scripts y ejemplos.
* Ejemplos esperados:

  * `uv add <paquete>`
  * `uv sync`
  * `uv run python main.py`
  * `uv run pytest`

## Entregable solicitado

Genera un documento en `@docs\INITIAL-IDEA.md` que contenga un resumen ejecutivo de la propuesta.

El documento debe incluir como mínimo:

1. Descripción general de la aplicación.
2. Objetivo y caso de uso.
3. Arquitectura de alto nivel.
4. Componentes principales.
5. Flujo de usuario.
6. Tecnologías recomendadas.
7. Estrategia de procesamiento e indexación de documentos.
8. Estrategia de generación de respuestas y citación de fuentes.
9. Consideraciones de despliegue mediante Docker.
10. Cómo la solución satisface cada criterio definido en `@docs\RUBRIC-DETAILS.md`.

Antes de redactar la propuesta, analiza detalladamente la rúbrica y verifica explícitamente que cada requisito quede cubierto.