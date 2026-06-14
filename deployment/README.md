# Guía de Ejecución Individual de DocQuery

Esta guía detalla los pasos para ejecutar la aplicación **DocQuery** de forma aislada, sin el stack de observabilidad (Prometheus/Grafana) ni Docker Compose.

## 1. Requisitos Previos

*   **Python 3.12 o superior** instalado.
*   **uv** instalado (`pip install uv`).
*   Clave de API de Google Gemini (`GEMINI_API_KEY`).

## 2. Configuración del Entorno Local

1.  **Navega a la raíz del proyecto:**
    Asegúrate de estar en el directorio raíz del proyecto.

2.  **Crea y activa el entorno virtual:**

    *   **Windows (PowerShell):**
        ```powershell
        .venv\Scripts\activate
        ```

    *   **Linux / macOS (Bash/Zsh):**
        ```bash
        source .venv/bin/activate
        ```

3.  **Instala las dependencias:**
    ```bash
    uv sync
    ```

## 3. Ejecución de la Aplicación

Para iniciar el servidor de la aplicación, utiliza el siguiente comando:

*   **Windows (PowerShell):**
    ```powershell
    $env:GEMINI_API_KEY="TU_GEMINI_API_KEY"; uv run uvicorn app.backend.main:app --port 8000 --reload
    ```

*   **Linux / macOS (Bash/Zsh):**
    ```bash
    GEMINI_API_KEY="TU_GEMINI_API_KEY" uv run uvicorn app.backend.main:app --port 8000 --reload
    ```

*Sustituye `TU_GEMINI_API_KEY` por tu clave real.*

## 4. Verificación del Funcionamiento

Una vez que el servidor esté activo (verás un mensaje de "Application startup complete"), puedes verificar su estado:

1.  **Endpoint de salud:**
    Abre en tu navegador: `http://localhost:8000/health`
    *   Deberías recibir la respuesta: `{"status": "ok"}`

2.  **Interfaz principal:**
    Abre en tu navegador: `http://localhost:8000/`
    *   Deberías ver la interfaz de usuario de DocQuery.

---

## Opción Alternativa: Ejecución con Docker Individual

Si prefieres ejecutar solo la aplicación usando un contenedor Docker (sin Compose):

1.  **Construye la imagen:**
    ```bash
    docker build -t docquery -f deployment/Dockerfile .
    ```

2.  **Ejecuta el contenedor:**

    *   **Windows (PowerShell):**
        ```powershell
        $env:GEMINI_API_KEY="TU_GEMINI_API_KEY"; docker run --rm -p 8000:8000 -e GEMINI_API_KEY=$env:GEMINI_API_KEY docquery
        ```

    *   **Linux / macOS (Bash/Zsh):**
        ```bash
        docker run --rm -p 8000:8000 -e GEMINI_API_KEY="TU_GEMINI_API_KEY" docquery
        ```
    *Puedes verificar el funcionamiento en `http://localhost:8000/health` de la misma manera.*
