# Guía de Docker — DocQuery

Esta guía explica cómo construir, probar y publicar la imagen de la aplicación.

## 1. Construcción de la Imagen
Para construir la imagen de la aplicación desde el `Dockerfile` situado en la carpeta `deployment/`:

```powershell
docker build -t docquery -f deployment/Dockerfile .
```

*   `-t docquery`: Asigna el nombre "docquery" a la imagen.
*   `-f deployment/Dockerfile`: Especifica la ruta del archivo Dockerfile.

## 2. Probar la Aplicación Independientemente
Una vez construida la imagen, puedes probarla rápidamente ejecutando el siguiente comando:

Sustituye `TU_GEMINI_API_KEY` por tu clave real:

```powershell
$env:GEMINI_API_KEY="TU_GEMINI_API_KEY"; docker run --rm -p 8000:8000 -e GEMINI_API_KEY=$env:GEMINI_API_KEY docquery
```

### Explicación del comando:
- `--rm`: Elimina el contenedor automáticamente al detenerlo.
- `-p 8000:8000`: Mapea el puerto 8000.
- `-e GEMINI_API_KEY=...`: Inyecta la API Key.

## 3. Publicación en GHCR (GitHub Container Registry)

Para publicar la imagen y hacerla accesible a otros:

1. **Etiquetar la imagen:**
   ```powershell
   docker tag docquery ghcr.io/TU_USUARIO_GITHUB/docquery:latest
   ```

2. **Autenticarse en GHCR:**
   Necesitas un Personal Access Token (PAT) con permisos de `write:packages`.
   ```powershell
   echo $env:GH_TOKEN | docker login ghcr.io -u TU_USUARIO_GITHUB --password-stdin
   ```

3. **Subir la imagen:**
   ```powershell
   docker push ghcr.io/TU_USUARIO_GITHUB/docquery:latest
   ```
