# DocQuery — Multimodal RAG

## Descripción
Una pequeña aplicación de IA/ML que recibe una entrada (documentos) y permite realizar consultas (RAG) utilizando el modelo Gemini.

## Ejecución

### Requisitos previos
- Tener instalado Docker y Docker Compose.
- Tener una API Key de Google Gemini.

### Correr la aplicación
Para iniciar la aplicación, ejecuta el siguiente comando en la raíz del proyecto (asegúrate de reemplazar `TU_API_KEY` por tu clave real):

```bash
API_KEY=TU_API_KEY docker-compose up --build
```

La aplicación estará disponible en `http://localhost:8000`.

## Observabilidad (Prometheus + Grafana)
Esta aplicación incluye un stack de observabilidad para monitorear métricas.

1. **Inicia el stack:** `API_KEY=TU_API_KEY docker-compose up --build`
2. **Prometheus:** Disponible en `http://localhost:9090`
3. **Grafana:** Disponible en `http://localhost:3000` (usuario/pass por defecto: admin/admin)

Puedes configurar Prometheus como fuente de datos en Grafana usando la URL `http://prometheus:9090`.
