# Guía de Despliegue — DocQuery

Esta guía detalla los pasos necesarios para desplegar la aplicación DocQuery junto con su stack de observabilidad.

## 1. Requisitos Previos
- **Docker** y **Docker Compose** instalados.
- Iniciar **Docker Desktop**.
- Clave de API de Google Gemini (`API_KEY`).

## 2. Configuración de Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`:

```bash
# .env
API_KEY=tu_api_key_aqui
```

## 3. Despliegue de la Aplicación y Observabilidad
Utilizamos Docker Compose para orquestar la aplicación, Prometheus y Grafana.

Ejecuta el siguiente comando en la raíz:

```bash
docker-compose up --build
```

### Servicios iniciados:
| Servicio | Puerto | Descripción |
| :--- | :--- | :--- |
| **App** | `8000` | Interfaz y API de DocQuery. |
| **Prometheus** | `9090` | Recopilación de métricas. |
| **Grafana** | `3000` | Visualización (admin/admin). |

## 4. Configuración de Observabilidad
Para ver las métricas en Grafana:

1. Accede a `http://localhost:3000` e inicia sesión con `admin/admin`.
2. Ve a **Connections** > **Data sources**.
3. Añade **Prometheus**.
4. En URL, introduce: `http://prometheus:9090`.
5. Haz clic en **Save & test**.
6. Crea un nuevo **Dashboard** y añade paneles consultando las métricas disponibles (ej. `http_requests_total`).

## 5. Resolución de Problemas
- **Logs de construcción:** Revisa la salida de `docker-compose up --build`. Se han añadido logs explícitos en el Dockerfile para identificar fallos durante `uv sync`.
- **Logs de la aplicación:** La aplicación escribe logs en el volumen montado en `./logs/`.
- **Acceso:** Si `app` no arranca, verifica que la `API_KEY` sea válida y no tenga espacios.
