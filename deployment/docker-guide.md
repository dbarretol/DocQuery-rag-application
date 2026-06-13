# Guía de Docker — DocQuery

Esta guía explica cómo construir y probar la imagen de la aplicación de forma independiente, sin necesidad de ejecutar el stack completo de observabilidad (Prometheus/Grafana).

## 1. Construcción de la Imagen
Para construir la imagen de la aplicación desde el `Dockerfile` situado en la carpeta `deployment/`:

```powershell
docker build -t docquery -f deployment/Dockerfile .
```

*   `-t docquery`: Asigna el nombre "docquery" a la imagen.
*   `-f deployment/Dockerfile`: Especifica la ruta del archivo Dockerfile.

## 2. Probar la Aplicación Independientemente
Una vez construida la imagen, puedes probarla rápidamente ejecutando el siguiente comando. Este enfoque inyecta la variable de entorno en tiempo de ejecución, cumpliendo con los requisitos de seguridad.

Sustituye `TU_GEMINI_API_KEY` por tu clave real:

```powershell
$env:GEMINI_API_KEY="TU_GEMINI_API_KEY"; docker run --rm -p 8000:8000 -e GEMINI_API_KEY=$env:GEMINI_API_KEY docquery
```

### Explicación del comando:
- `--rm`: Elimina el contenedor automáticamente al detenerlo, manteniendo tu sistema limpio.
- `-p 8000:8000`: Mapea el puerto 8000 de tu máquina local al puerto 8000 del contenedor.
- `-e GEMINI_API_KEY=...`: Inyecta la API Key requerida por la aplicación para funcionar con Gemini.

Una vez ejecutado, la aplicación estará accesible en: `http://localhost:8000`.
