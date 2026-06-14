# Guía de Despliegue — DocQuery

Esta guía detalla los pasos necesarios para desplegar la aplicación DocQuery junto con su stack de observabilidad.

## 1. Requisitos Previos
- **Docker** y **Docker Compose** instalados.
- Iniciar **Docker Desktop** (asegúrate de que el icono de la ballena esté activo).
- Clave de API de Google Gemini (`API_KEY`).

## 2. Configuración y Ejecución
Para evitar problemas con variables de entorno en Windows/PowerShell y asegurar una correcta ejecución:

Ejecuta el siguiente comando en la raíz del proyecto, reemplazando `TU_GEMINI_API_KEY` por tu clave real:

```powershell
$env:GEMINI_API_KEY="TU_GEMINI_API_KEY"; docker compose up --build
```

### Servicios iniciados:
| Servicio | Puerto | Descripción |
| :--- | :--- | :--- |
| **App** | `8000` | Interfaz y API de DocQuery. |
| **Prometheus** | `9090` | Recopilación de métricas. |
| **Grafana** | `3000` | Visualización (admin/admin). |

## 3. Verificación del Despliegue

Para confirmar que todo funciona correctamente:

### A. Verificar estado de los contenedores
```powershell
docker compose ps
```
*   Debes ver que los 3 servicios (`app`, `grafana`, `prometheus`) tengan estado **Up**.

### B. Verificar logs de la aplicación
```powershell
docker compose logs app -f
```
*   Busca confirmación de que Uvicorn ha iniciado: `"Application startup complete."` y observa las peticiones a `/metrics` para confirmar que Prometheus está conectando.

## 4. Configuración de Observabilidad en Grafana
1. Accede a `http://localhost:3000` (usuario/pass: `admin/admin`).
2. Ve a **Connections** > **Data sources** > **Add data source** > **Prometheus**.
3. En **URL**, introduce: `http://prometheus:9090`.
4. Haz clic en **Save & test**.
5. Crea un nuevo **Dashboard** y añade paneles consultando métricas como `http_requests_total`.

## 5. Resolución de Problemas
- **Conflicto de archivos:** Si obtienes un `I/O error` en `.venv`, asegúrate de que `.venv` está excluido en `.dockerignore` y en los volúmenes del `docker-compose.yml`.
- **Logs de construcción:** Si la app falla al arrancar, revisa los logs con `docker compose logs app`.
- **Acceso:** Si no ves la app en `localhost:8000`, comprueba que Docker Desktop está ejecutándose.
