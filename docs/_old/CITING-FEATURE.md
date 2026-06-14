# Funcionalidad de Citas Contextuales Interactivas

## Contexto y Objetivo
Se buscó implementar una funcionalidad para permitir que los usuarios visualizaran el pasaje original (texto o descripción de imagen) desde el cual el bot extrajo una respuesta. El objetivo era aumentar la confianza y auditabilidad de las respuestas del modelo.

## Plan Original de Implementación

### 1. Backend: Endpoint de Recuperación
- Crear `GET /passage/{passage_id}` en `app/backend/main.py`.
- El endpoint consultará ChromaDB por el `passage_id`.
- Devolverá un JSON con `type` ("text" o "image") y `content` (texto crudo o la imagen procesada/codificada para visualización).

### 2. Frontend: Interfaz de Usuario
- **Modal**: Actualizar la estructura HTML del modal para que pueda mostrar dinámicamente un `p` (para texto) o un `img` (para imágenes).
- **Lógica**: Modificar la función que renderiza las citas en `app.js` para que el modal se adapte según el tipo de contenido recibido del backend.

### 3. Integración
- Asegurar que la respuesta del bot contenga los `ids` necesarios de ChromaDB para consultar los pasajes correctamente.

## Aprendizajes Clave

### 1. Estrategia de Chunking
- La aplicación utiliza una estrategia de segmentación por tamaño fijo de caracteres (`chunk_text` en `app/backend/rag/ingest.py`).
- Se concluyó que reducir el `chunk_size` de 500 a 250 sin implementar técnicas de solapamiento (overlap) incrementaría el riesgo de fragmentación semántica, resultando en respuestas incompletas o incoherentes.

### 2. Implementación de Citas
- **Estructura de Metadatos**: El sistema ya almacena suficiente metadatos (`filename`, `page`, `content_type`, etc.) para identificar la fuente original sin necesidad de cambiar la estrategia de chunking.
- **Flujo de Recuperación**: El enfoque más robusto consiste en:
  - Recuperar el `passage_id` (o la combinación de metadatos) junto con la respuesta.
  - Implementar un endpoint en el backend (`GET /passage/{passage_id}`) para recuperar el contenido exacto del chunk.
  - Renderizar en el frontend mediante un modal interactivo.
- **Soporte de Imágenes**: La descripción de imágenes se almacena como texto en ChromaDB; para visualizar la imagen real se requeriría un endpoint adicional que sirva los bytes de la imagen original.

### 3. Consideraciones de UX y UI
- **Citas en el texto**: El uso de citas completas textuales ("filename.pdf, pág. 1") dentro del cuerpo del mensaje interrumpe el flujo de lectura. Se recomendó el uso de referencias numéricas compactas `[1]`, `[2]` en el texto, desplazando la información detallada a una sección de "Fuentes" al final.
- **Renderizado en Modal**: Para mostrar descripciones de imágenes en el modal, es necesario aplicar `marked.parse()` en el frontend antes de inyectar el contenido, para asegurar que los elementos Markdown (negritas, listas) se rendericen correctamente y no como texto plano.

## Retos Técnicos Identificados
- La integración de citas interactivas requiere una sincronización precisa entre el formato de respuesta del LLM, la estructura de datos que recibe el frontend y la lógica de renderizado Markdown.
- Cambios complejos en prompts o lógica de renderizado pueden romper funcionalidades existentes (como los `suggestion-chips`) si no se manejan con cuidado en el frontend.

Plan: Citas Contextuales Interactivas

  Objetivo
  Permitir que el usuario haga clic en las fuentes citadas dentro de las respuestas del bot para visualizar el pasaje original del documento en una ventana
  modal, mejorando la confianza y auditabilidad.

  Archivos Clave
   - app/backend/main.py: Nuevo endpoint para recuperar el contenido del pasaje.
   - app/templates/index.html: Estructura del modal para mostrar el pasaje.
   - app/templates/static/app.js: Lógica para manejar clics en citas y mostrar el modal.
   - app/templates/static/styles.css: Estilos para el modal y los elementos citados.

  Pasos de Implementación

  1. Backend: Endpoint de Recuperación de Pasaje
   - Crear un nuevo endpoint GET /passage/{passage_id} en app/backend/main.py.
   - Este endpoint buscará en la colección de ChromaDB el documento asociado al passage_id (o la combinación filename + page + chunk) y devolverá su
     contenido.

  2. Frontend: Interfaz de Usuario
   - Modal: Añadir una estructura de div en app/templates/index.html para la ventana modal (con estilos en app/templates/static/styles.css).
   - Renderización de citas:
       - Modificar la lógica en app/templates/static/app.js (o en la parte de renderizado Markdown) para detectar las referencias a fuentes (ej. [filename
         (page X)]) y convertirlas en botones/enlaces clicables.
       - Al hacer clic, invocar el modal y cargar el contenido mediante fetch al nuevo endpoint.

  3. Integración
   - Asegurar que la respuesta del bot en el chat contenga los identificadores necesarios (passage_id o similar) para que el frontend sepa qué pasaje
     solicitar.

  Verificación
   - Realizar una pregunta que genere citas.
   - Verificar que las citas aparezcan como elementos interactivos.
   - Hacer clic en una cita y confirmar que se abre el modal con el contenido correcto del documento.

  ¿Estás de acuerdo con este plan? Si es así, procederé a solicitar la aprobación formal para comenzar la implementación.

Plan: Citas Contextuales Interactivas

  Objetivo
  Permitir que el usuario haga clic en las fuentes citadas (texto o imágenes) dentro de las respuestas del bot para visualizar el pasaje o la imagen
  original en una ventana modal.

  Archivos Clave
   - app/backend/main.py: Nuevo endpoint para recuperar el contenido del pasaje o la imagen.
   - app/templates/index.html: Estructura del modal mejorada para soportar contenido dinámico (texto o imágenes).
   - app/templates/static/app.js: Lógica para manejar clics, determinar el tipo de contenido y mostrar el modal.
   - app/templates/static/styles.css: Estilos para el modal y los elementos citados.

  Pasos de Implementación

  1. Backend: Endpoint de Recuperación
   - Crear GET /passage/{passage_id} en app/backend/main.py.
   - El endpoint consultará ChromaDB por el passage_id.
   - Devolverá un JSON con type ("text" o "image") y content (texto crudo o la imagen procesada/codificada para visualización).

  2. Frontend: Interfaz de Usuario
   - Modal: Actualizar la estructura HTML del modal para que pueda mostrar dinámicamente un p (para texto) o un img (para imágenes).
   - Lógica: Modificar la función que renderiza las citas en app.js para que el modal se adapte según el tipo de contenido recibido del backend.

  3. Integración
   - Asegurar que la respuesta del bot contenga los ids necesarios de ChromaDB para consultar los pasajes correctamente.

  Verificación
   - Realizar consultas que generen citas de texto y de imágenes.
   - Verificar que el modal se abre y renderiza correctamente tanto el texto como la imagen asociada a la cita.

   Para finalizar, necesitarías ajustar la lógica que renderiza la respuesta del bot para incluir los passage_id (o la capacidad de extraerlos) y convertir
  las citas de texto en elementos interactivos que llamen a openPassageModal(passageId). Actualmente, la estructura del frontend está preparada para recibir
  y mostrar la información.

   Ahora, cuando el bot genera una respuesta, las fuentes se muestran debajo del mensaje como botones clicables. Al hacer clic en una fuente:

   1. Se abre una ventana modal (modalPassage).
   2. El frontend realiza una petición al nuevo endpoint /passage/{passage_id}.
   3. El modal muestra el contenido original (texto o descripción de imagen) correspondiente a esa cita.

  Resumen de cambios:
   * Backend (app/backend/main.py): Se añadió GET /passage/{passage_id} para recuperar el contenido y los metadatos de un pasaje de la base de datos Chroma.
   * Backend (app/backend/rag/generation.py): Se actualizó la estructura de la respuesta para incluir los IDs de las fuentes necesarias para la
     interactividad.
   * Frontend (app/templates/index.html y app/templates/static/styles.css): Se integró la estructura HTML y los estilos del nuevo modal para visualización
     dinámica.
   * Frontend (app/templates/static/app.js): Se integró la lógica para renderizar las fuentes citadas como botones y gestionar la apertura del modal y la
     carga de contenido.