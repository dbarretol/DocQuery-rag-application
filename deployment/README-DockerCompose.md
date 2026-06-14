# Guía de Despliegue con Docker Compose

Esta guía detalla los pasos para ejecutar la aplicación **DocQuery** junto con su stack completo de observabilidad (Prometheus y Grafana) utilizando **Docker Compose**.

## 1. Requisitos Previos

*   **Docker** y **Docker Compose** instalados y en ejecución.
*   Clave de API de Google Gemini (`GEMINI_API_KEY`).
*   Acceso a internet para descargar las imágenes desde Docker Hub y GitHub Container Registry (GHCR).

## 2. Ejecución del Stack

Para iniciar todos los servicios (App, Prometheus y Grafana), utiliza los siguientes comandos en la raíz del proyecto, reemplazando `TU_GEMINI_API_KEY` por tu clave real:

*   **Windows (PowerShell):**
    ```powershell
    $env:GEMINI_API_KEY="TU_GEMINI_API_KEY"; docker compose up -d
    ```

*   **Linux / macOS (Bash/Zsh):**
    ```bash
    GEMINI_API_KEY="TU_GEMINI_API_KEY" docker compose up -d
    ```

## 3. Verificación del Despliegue

### A. Verificar que los servicios están activos
Ejecuta:
```bash
docker compose ps
```
Deberías ver que los servicios `app`, `prometheus` y `grafana` tienen el estado **Up**.

### B. Verificar los logs de la aplicación
Para asegurar que la app ha iniciado correctamente:
```bash
docker compose logs app -f
```
Busca la línea: `"Application startup complete."`

## 4. Acceso a los Servicios

| Servicio | URL | Credenciales |
| :--- | :--- | :--- |
| **DocQuery App** | `http://localhost:8000` | N/A |
| **Prometheus** | `http://localhost:9090` | N/A |
| **Grafana** | `http://localhost:3000` | admin / admin |

## 5. Configuración de Observabilidad en Grafana

1.  Inicia sesión en Grafana (`http://localhost:3000`) con `admin` / `admin`.
2.  Ve a **Connections** > **Data sources** > **Add data source** > **Prometheus**.
3.  En **URL**, introduce: `http://prometheus:9090`.
4.  Haz clic en **Save & test**.
5.  ¡Ya puedes crear tus Dashboards consultando las métricas! (ej. `rag_retrieval_latency_seconds`).

---

## 6. Detención del Stack
Para detener y eliminar todos los contenedores:
```bash
docker compose down
```
