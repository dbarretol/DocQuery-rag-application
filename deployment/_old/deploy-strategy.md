# Estrategia de Despliegue de Producción — DocQuery

Esta estrategia define el flujo de entrega para usuarios finales, permitiendo el despliegue del stack completo (App + Observabilidad) sin necesidad de que el usuario compile el código fuente.

## 1. Flujo de Trabajo (Workflow)

El despliegue se basa en el registro de imágenes **GitHub Container Registry (GHCR)**.

1.  **Construcción (Tú):** Se construye la imagen de la aplicación (`docquery`) a partir del `Dockerfile` y se etiqueta para GHCR.
2.  **Publicación (Tú):** La imagen se sube a GHCR (`ghcr.io/tu-usuario/docquery:latest`).
3.  **Consumo (Usuario):** El usuario recibe únicamente los archivos de configuración (`docker-compose.yml`, `prometheus.yml`). Al ejecutar `docker compose up`, Docker descarga automáticamente la imagen desde GHCR junto con las imágenes oficiales de Prometheus y Grafana.

## 2. Configuración para el Usuario (Paquete de entrega)

El paquete de entrega debe contener únicamente:

- `docker-compose.yml`: Configurado para usar `image: ghcr.io/tu-usuario/docquery:latest`.
- `deployment/prometheus.yml`: Configuración del monitoreo.
- `deployment/deployment-guide.md`: Instrucciones de uso.

### `docker-compose.yml` para el usuario:
```yaml
services:
  app:
    image: ghcr.io/tu-usuario/docquery:latest
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}

  prometheus:
    image: prom/prometheus
    volumes:
      - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

## 3. Comandos de Publicación (Pipeline)

### Construcción y Publicación manual:
```bash
# Etiquetar imagen
docker build -t ghcr.io/tu-usuario/docquery:latest -f deployment/Dockerfile .

# Iniciar sesión en GHCR (requiere Personal Access Token)
echo $GH_TOKEN | docker login ghcr.io -u TU_USUARIO --password-stdin

# Subir imagen
docker push ghcr.io/tu-usuario/docquery:latest
```

*Nota: Se recomienda automatizar este proceso mediante **GitHub Actions** para que se ejecute en cada `git push`.*

## 4. Ventajas
- **Independencia:** El usuario final no necesita herramientas de desarrollo (Python, uv, compiladores).
- **Consistencia:** El usuario ejecuta exactamente la misma imagen que tú has probado.
- **Portabilidad:** Se despliega en cualquier máquina con Docker instalado.
