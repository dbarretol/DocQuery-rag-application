document.addEventListener('DOMContentLoaded', () => {
    /* ── State ── */
    // docs is keyed by filename to avoid duplicates across sessions
    const docs = [];
    let config = {
        generation_model: localStorage.getItem('gen_model') || '',
        embedding_model: localStorage.getItem('emb_model') || '',
        language: localStorage.getItem('language') || 'Spanish'
    };
    let abortController = null;

    /* ── Settings Management ── */
    const btnOpenSettings = document.getElementById('btnOpenSettings');
    const btnCloseSettings = document.getElementById('btnCloseSettings');
    const modalSettings = document.getElementById('modalSettings');
    const btnSaveSettings = document.getElementById('btnSaveSettings');
    const selectGenModel = document.getElementById('selectGenModel');
    const selectEmbModel = document.getElementById('selectEmbModel');
    const selectLanguage = document.getElementById('selectLanguage');
    const currentGenModel = document.getElementById('currentGenModel');
    const currentEmbModel = document.getElementById('currentEmbModel');
    const currentLanguage = document.getElementById('currentLanguage');

    /* ── Passage Modal ── */
    const modalPassage = document.getElementById('modalPassage');
    const btnClosePassage = document.getElementById('btnClosePassage');
    const passageContent = document.getElementById('passageContent');
    const passageMeta = document.getElementById('passageMeta');

    btnClosePassage.addEventListener('click', () => modalPassage.classList.remove('active'));
    modalPassage.addEventListener('click', (e) => { if (e.target === modalPassage) modalPassage.classList.remove('active'); });

    btnOpenSettings.addEventListener('click', () => modalSettings.classList.add('active'));
    btnCloseSettings.addEventListener('click', () => modalSettings.classList.remove('active'));
    modalSettings.addEventListener('click', (e) => { if (e.target === modalSettings) modalSettings.classList.remove('active'); });

    /* ── GCS Sync Modal ── */
    const modalGcsSync = document.getElementById('modalGcsSync');
    const btnOpenGCS = document.getElementById('btnOpenGCS');
    const btnCloseGcs = document.getElementById('btnCloseGcs');
    const btnDownloadGcs = document.getElementById('btnDownloadGcs');
    const btnUploadGcs = document.getElementById('btnUploadGcs');
    const inputGcsBucket = document.getElementById('inputGcsBucket');

    btnOpenGCS.addEventListener('click', () => modalGcsSync.classList.add('active'));
    btnCloseGcs.addEventListener('click', () => modalGcsSync.classList.remove('active'));
    modalGcsSync.addEventListener('click', (e) => { if(e.target === modalGcsSync) modalGcsSync.classList.remove('active'); });

    async function syncGCS(endpoint) {
        const bucketName = inputGcsBucket.value.trim();
        if (!bucketName) { alert('Ingresa un bucket name'); return; }

        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bucket_name: bucketName })
            });
            const data = await res.json();
            alert(data.message);
            if (res.ok) modalGcsSync.classList.remove('active');
        } catch (e) {
            console.error('Sync error:', e);
            alert('Error en la sincronización');
        }
    }

    btnDownloadGcs.addEventListener('click', () => syncGCS('/sync/download'));
    btnUploadGcs.addEventListener('click', () => syncGCS('/sync/upload'));

    let modelsConfig = {}; // Store config locally

    async function loadSettings() {
        console.log('Fetching config...');
        try {
            const res = await fetch('/config');
            console.log('Config response status:', res.status);
            if (!res.ok) {
                console.error('Config fetch failed:', res.statusText);
                return;
            }
            const data = await res.json();
            modelsConfig = data.models;
            console.log('Config data received:', data);

            // Populate select options
            if (modelsConfig && modelsConfig.generation && modelsConfig.generation.options) {
                selectGenModel.innerHTML = modelsConfig.generation.options.map(opt =>
                    `<option value="${opt.name}">${opt.name} (${opt.cost})</option>`
                ).join('');
            }

            if (modelsConfig && modelsConfig.embeddings && modelsConfig.embeddings.options) {
                selectEmbModel.innerHTML = modelsConfig.embeddings.options.map(opt =>
                    `<option value="${opt.name}">${opt.name}</option>`
                ).join('');
            }

            // Set defaults if not in localStorage
            if (!config.generation_model && modelsConfig && modelsConfig.generation)
                config.generation_model = modelsConfig.generation.default;
            if (!config.embedding_model && modelsConfig && modelsConfig.embeddings)
                config.embedding_model = modelsConfig.embeddings.default;

            updateSettingsUI();
        } catch (err) {
            console.error('Error loading config:', err);
        }
    }

    function updateSettingsUI() {
        currentGenModel.textContent = config.generation_model;
        currentEmbModel.textContent = config.embedding_model;
        currentLanguage.textContent = config.language;

        // Header
        const headerGenModel = document.getElementById('headerGenModel');
        const headerModelDesc = document.getElementById('headerModelDesc');
        if (headerGenModel) headerGenModel.textContent = config.generation_model;

        if (headerModelDesc && modelsConfig.generation && modelsConfig.generation.options) {
            const modelOpt = modelsConfig.generation.options.find(o => o.name === config.generation_model);
            headerModelDesc.textContent = modelOpt ? modelOpt.description : '';
        }

        // Sidebar Embeddings
        const sidebarEmbModel = document.getElementById('sidebarEmbModel');
        const sidebarEmbModelDesc = document.getElementById('sidebarEmbModelDesc');

        if (sidebarEmbModel) sidebarEmbModel.textContent = config.embedding_model;

        if (sidebarEmbModelDesc && modelsConfig.embeddings && modelsConfig.embeddings.options) {
            const embOpt = modelsConfig.embeddings.options.find(o => o.name === config.embedding_model);
            sidebarEmbModelDesc.textContent = embOpt ? embOpt.description : '';
        }

        // Update selects if they were changed elsewhere
        selectGenModel.value = config.generation_model;
        selectEmbModel.value = config.embedding_model;
        selectLanguage.value = config.language;
    }

    btnSaveSettings.addEventListener('click', () => {
        config.generation_model = selectGenModel.value;
        config.embedding_model = selectEmbModel.value;
        config.language = selectLanguage.value;
        localStorage.setItem('gen_model', config.generation_model);
        localStorage.setItem('emb_model', config.embedding_model);
        localStorage.setItem('language', config.language);
        updateSettingsUI();
        modalSettings.classList.remove('active');
    });

    loadSettings();
    loadSidebarDocs(); // Hydrate sidebar from persistent ChromaDB on startup

    /* ── Sidebar Persistence: bidirectional sync with ChromaDB ── */
    async function loadSidebarDocs() {
        console.log('[loadSidebarDocs] START — docs array before fetch:', docs.map(d => d.name));
        try {
            const res = await fetch('/knowledge-base');
            if (!res.ok) {
                console.error('[loadSidebarDocs] /knowledge-base returned', res.status);
                return;
            }
            const data = await res.json();
            const kbNames = new Set(data.documents.map(d => d.filename));
            console.log('[loadSidebarDocs] KB returned:', [...kbNames]);
            console.log('[loadSidebarDocs] docs array at resolution time:', docs.map(d => d.name));

            // ── STEP 1: Remove 'ready' docs that are no longer in ChromaDB ──
            // Iterate backwards so splices don't shift unvisited indices.
            for (let i = docs.length - 1; i >= 0; i--) {
                if (docs[i].status === 'ready' && !kbNames.has(docs[i].name)) {
                    console.log('[loadSidebarDocs] Removing stale entry from sidebar:', docs[i].name);
                    docs.splice(i, 1);
                }
            }

            // ── STEP 2: Add KB docs not yet in the local array ──
            const existingNames = new Set(docs.map(d => d.name));
            data.documents.forEach(doc => {
                if (!existingNames.has(doc.filename)) {
                    console.log('[loadSidebarDocs] Adding new entry to sidebar:', doc.filename);
                    docs.push({
                        id: doc.filename,
                        name: doc.filename,
                        status: 'ready',
                        size: null
                    });
                }
            });

            console.log('[loadSidebarDocs] END — docs array after sync:', docs.map(d => d.name));
            renderDocList();
        } catch (e) {
            console.error('[loadSidebarDocs] Error:', e);
        }
    }

    /* ── Knowledge Base Management ── */
    const btnOpenKB = document.getElementById('btnOpenKB');
    const btnCloseKB = document.getElementById('btnCloseKB');
    const modalKB = document.getElementById('modalKB');
    const kbList = document.getElementById('kbList');

    btnOpenKB.addEventListener('click', async () => {
        modalKB.classList.add('active');
        await loadKnowledgeBase();
    });
    btnCloseKB.addEventListener('click', () => modalKB.classList.remove('active'));
    modalKB.addEventListener('click', (e) => { if(e.target === modalKB) modalKB.classList.remove('active'); });

    async function loadKnowledgeBase() {
        kbList.innerHTML = '<div style="padding: 20px; text-align: center;">Cargando...</div>';
        try {
            const res = await fetch('/knowledge-base');
            const data = await res.json();
            
            if (data.documents.length === 0) {
                kbList.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-lo);">No hay documentos en la base de conocimientos.</div>';
                return;
            }
            
            kbList.innerHTML = data.documents.map(doc => `
                <div class="doc-item">
                    <div class="doc-item-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <div class="doc-item-info">
                        <div class="doc-item-name">${escHtml(doc.filename)}</div>
                    </div>
                    <button class="btn-delete" title="Eliminar" onclick="deleteDocFromKB('${encodeURIComponent(doc.filename)}')">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            `).join('');
        } catch (e) {
            console.error('Error loading KB:', e);
            kbList.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--danger);">Error al cargar.</div>';
        }
    }

    window.deleteDocFromKB = async function(filename) {
        if (!confirm(`¿Estás seguro de eliminar ${decodeURIComponent(filename)}?`)) return;
        
        try {
            const res = await fetch(`/documents/${filename}`, { method: 'DELETE' });
            if (res.ok) {
                await loadKnowledgeBase();
            } else {
                alert('Error al eliminar.');
            }
        } catch (e) {
            console.error('Delete error:', e);
        }
    };
    const fileInput = document.getElementById('fileInput');
    const btnUpload = document.getElementById('btnUpload');
    const uploadZone = document.getElementById('uploadZone');
    const uploadStatus = document.getElementById('uploadStatus');

    fileInput.addEventListener('change', () => {
        btnUpload.disabled = !fileInput.files.length;
        if (fileInput.files.length) {
            uploadZone.querySelector('p').innerHTML =
                `<strong>${fileInput.files[0].name}</strong>`;
        }
    });

    // Drag-and-drop
    uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
    uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
    uploadZone.addEventListener('drop', e => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });

    btnUpload.addEventListener('click', uploadFile);

    async function uploadFile() {
        const file = fileInput.files[0];
        if (!file) return;

        setUploadStatus('Subiendo…', '');
        btnUpload.disabled = true;

        // Add to list as "processing"
        const docId = Date.now();
        addDocToList({ id: docId, name: file.name, status: 'processing', size: file.size });

        const formData = new FormData();
        formData.append('file', file);
        if (config.generation_model) formData.append('generation_model', config.generation_model);
        if (config.embedding_model) formData.append('embedding_model', config.embedding_model);

        console.log('Sending upload with:', {
            gen: config.generation_model,
            emb: config.embedding_model
        });

        try {
            const res = await fetch('/upload', { method: 'POST', body: formData });
            if (res.ok) {
                setUploadStatus('Documento subido. Indexando...', 'success');
                // Start polling
                pollDocumentStatus(docId, file.name);
            } else {
                setUploadStatus('Error al subir.', 'error');
                updateDocStatus(docId, 'error');
            }
        } catch {
            setUploadStatus('Sin conexión.', 'error');
            updateDocStatus(docId, 'error');
        }

        // Reset
        fileInput.value = '';
        uploadZone.querySelector('p').innerHTML = '<strong>Arrastra un archivo</strong><br>o haz clic para seleccionar';
        btnUpload.disabled = true;
    }

    async function pollDocumentStatus(docId, filename) {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/document-status/${encodeURIComponent(filename)}`);
                const data = await res.json();

                if (data.status === 'INDEXED') {
                    clearInterval(interval);
                    // Remove the temporary in-session entry and reload from KB
                    // to ensure filename-based deduplication and correct stable IDs
                    const idx = docs.findIndex(d => d.id === docId);
                    if (idx !== -1) docs.splice(idx, 1);
                    await loadSidebarDocs();
                    setUploadStatus('Documento indexado.', 'success');
                } else if (data.status.startsWith('ERROR')) {
                    clearInterval(interval);
                    updateDocStatus(docId, 'error');
                    setUploadStatus(data.status, 'error');
                    console.error('Indexing failed:', data.status);
                }
            } catch (e) {
                console.error('Polling error:', e);
            }
        }, 2000); // Poll every 2 seconds
    }

    function setUploadStatus(msg, type) {
        uploadStatus.textContent = msg;
        uploadStatus.className = 'upload-status' + (type ? ' ' + type : '');
        if (type === 'success') setTimeout(() => { uploadStatus.textContent = ''; }, 3000);
    }

    function addDocToList(doc) {
        docs.push(doc);
        renderDocList();
    }

    function updateDocStatus(id, status) {
        const doc = docs.find(d => d.id === id);
        if (doc) { doc.status = status; renderDocList(); }
    }

    function renderDocList() {
        const list = document.getElementById('docList');
        const empty = document.getElementById('emptyState');

        // Always remove stale DOM items FIRST — before any early return.
        // Without this, the last item's element persists as a ghost when docs empties.
        list.querySelectorAll('.doc-item').forEach(n => n.remove());

        if (!docs.length) { empty.style.display = ''; return; }
        empty.style.display = 'none';

        // Re-render from current docs array
        docs.forEach(doc => {
            const statusLabel = { ready: 'Listo', processing: 'Procesando…', error: 'Error' }[doc.status];
            const sizeLabel = doc.size ? formatBytes(doc.size) : '';

            const item = document.createElement('div');
            item.className = 'doc-item';
            item.dataset.id = doc.id;
            item.innerHTML = `
                <div class="doc-item-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                </div>
                <div class="doc-item-info">
                    <div class="doc-item-name">${escHtml(doc.name)}</div>
                    <div class="doc-item-meta">${statusLabel}${sizeLabel ? ' · ' + sizeLabel : ''}</div>
                </div>
                <span class="status-dot ${doc.status}"></span>
                <button class="btn-delete" title="Eliminar" onclick="removeDoc('${String(doc.id).replace(/'/g, "\\'")}')">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            `;
            list.appendChild(item);
        });
    }

    window.removeDoc = async function (id) {
        const docEntry = docs.find(d => String(d.id) === String(id));
        if (!docEntry) {
            console.warn('[removeDoc] Doc not found in local array for id:', id,
                         '| Current docs:', docs.map(d => d.name));
            return;
        }

        const docName = docEntry.name;
        console.log('[removeDoc] Starting delete for:', docName,
                    '| docs before splice:', docs.map(d => d.name));

        try {
            const res = await fetch(`/documents/${encodeURIComponent(docName)}`, { method: 'DELETE' });
            if (res.ok) {
                // Re-find index AFTER the await — concurrent deletes may have shifted positions.
                const currentIdx = docs.findIndex(d => d.name === docName);
                console.log('[removeDoc] DELETE 200 OK for:', docName,
                            '| re-found idx:', currentIdx,
                            '| docs at resolution:', docs.map(d => d.name));
                if (currentIdx !== -1) docs.splice(currentIdx, 1);
                console.log('[removeDoc] docs after splice:', docs.map(d => d.name));

                // Full bidirectional sync — handles any race where KB was already
                // updated or still has the doc in-flight.
                await loadSidebarDocs();
            } else {
                console.error('[removeDoc] Server DELETE failed:', res.status, res.statusText);
                alert('Error al eliminar el documento en servidor');
            }
        } catch (e) {
            console.error('[removeDoc] Network error:', e);
            alert('Error de conexión al eliminar');
        }
    };


    function formatBytes(b) {
        if (b < 1024) return b + ' B';
        if (b < 1048576) return (b / 1024).toFixed(0) + ' KB';
        return (b / 1048576).toFixed(1) + ' MB';
    }

    /* ── Chat ── */
    const chatMessages = document.getElementById('chatMessages');
    const chatEmpty = document.getElementById('chatEmpty');
    const chatInput = document.getElementById('chatInput');
    const btnSend = document.getElementById('btnSend');

    // Auto-grow textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    // Send on Enter (Shift+Enter = newline)
    chatInput.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });

    btnSend.addEventListener('click', sendMessage);

    async function sendMessage() {
        if (abortController) {
            abortController.abort();
            abortController = null;
            btnSend.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>`;
            return;
        }

        const question = chatInput.value.trim();
        if (!question) return;

        // Hide empty state
        chatEmpty.style.display = 'none';

        // Hide suggestions after first message
        document.getElementById('suggestions').style.display = 'none';

        appendMessage('user', question);
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Show cancel state (square/stop icon)
        btnSend.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <rect x="6" y="6" width="12" height="12" fill="currentColor" transform="rotate(-45 12 12)" />
</svg>`;

        abortController = new AbortController();

        // Typing indicator
        const typingEl = appendTyping();

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question,
                    generation_model: config.generation_model,
                    language: config.language
                }),
                signal: abortController.signal
            });
            const data = await res.json();
            typingEl.remove();

            // Render markdown with sequential citation re-mapping
            const botMessage = document.createElement('div');
            botMessage.className = 'message bot';
            
            let originalAnswer = data.answer || 'Sin respuesta.';
            
            // 1. Identify used original indices
            const citedOriginalIndices = new Set();
            const citationRegex = /\[([\d,\s]+)\]/g;
            let match;
            while ((match = citationRegex.exec(originalAnswer)) !== null) {
                match[1].split(',').forEach(n => {
                    const idx = parseInt(n.trim()) - 1;
                    if (data.sources && data.sources[idx]) {
                        citedOriginalIndices.add(idx);
                    }
                });
            }

            // 2. Create sequential mapping
            const sortedOriginalIndices = Array.from(citedOriginalIndices).sort((a, b) => a - b);
            const indexMap = {}; // originalIdx -> sequentialIndex (1-based)
            const mappedSources = sortedOriginalIndices.map((origIdx, i) => {
                indexMap[origIdx] = i + 1;
                return data.sources[origIdx];
            });

            // 3. Replace in the answer text using the new mapping
            let processedAnswer = originalAnswer.replace(/\[([\d,\s]+)\]/g, (match, group) => {
                const numbers = group.split(',').map(n => n.trim());
                const mappedNumbers = numbers.map(n => {
                    const origIdx = parseInt(n) - 1;
                    return indexMap[origIdx] || n;
                });
                return `[${mappedNumbers.join(', ')}]`;
            });

            let answerHtml = marked.parse(processedAnswer);
            
            // 4. Convert citations to interactive links
            answerHtml = answerHtml.replace(/\[([\d,\s]+)\]/g, (match, group) => {
                const numbers = group.split(',').map(n => n.trim());
                const links = numbers.map(n => {
                    const seqIdx = parseInt(n);
                    const source = mappedSources[seqIdx - 1];
                    if (source) {
                        return `<a class="citation-link" onclick="openPassageModal('${source.id}')">${n}</a>`;
                    }
                    return n;
                });
                return `[${links.join(', ')}]`;
            });

            botMessage.innerHTML = `
                <div class="message-avatar">AI</div>
                <div class="message-bubble">
                    <div class="message-content">${answerHtml}</div>
                    ${renderSources(mappedSources)}
                </div>
            `;
            chatMessages.appendChild(botMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Fetch and show dynamic suggestions
            fetchDynamicSuggestions(question, data.answer);
        } catch (err) {
            typingEl.remove();
            if (err.name === 'AbortError') {
                appendMessage('bot', 'Consulta cancelada.');
            } else {
                appendMessage('bot', 'Error de conexión. Intenta de nuevo.');
            }
        }

        // Reset button
        abortController = null;
        btnSend.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function renderSources(mappedSources) {
        if (!mappedSources || mappedSources.length === 0) return '';
        
        const sourceChips = mappedSources.map((s, i) => `
            <button class="source-chip" onclick="openPassageModal('${s.id}')">
                [${i + 1}] ${escHtml(s.filename)}${s.page !== 'Unknown' ? ' (pág. ' + s.page + ')' : ''}
            </button>
        `).join('');
        
        return `<div class="source-list">${sourceChips}</div>`;
    }

    window.openPassageModal = async function(passageId) {
        passageMeta.textContent = 'Cargando...';
        passageContent.innerHTML = '<div style="text-align:center; padding: 20px;">Cargando contenido del pasaje...</div>';
        modalPassage.classList.add('active');
        
        try {
            const res = await fetch(`/passage/${passageId}`);
            const data = await res.json();
            
            if (data.error) {
                passageMeta.textContent = 'Error';
                passageContent.textContent = data.error;
                return;
            }
            
            passageMeta.textContent = `${data.metadata.filename}${data.metadata.page !== 'Unknown' ? ' · Página ' + data.metadata.page : ''}`;
            
            if (data.type === 'image') {
                // Image descriptions are stored as text, but we might want to show them specially
                passageContent.innerHTML = `<div style="margin-bottom: 12px; font-weight: 600; color: var(--indigo);">Descripción de Imagen:</div>` + marked.parse(data.content);
            } else {
                passageContent.innerHTML = marked.parse(data.content);
            }
        } catch (e) {
            console.error('Error opening passage:', e);
            passageMeta.textContent = 'Error';
            passageContent.textContent = 'No se pudo cargar el pasaje.';
        }
    };

    async function fetchDynamicSuggestions(question, answer) {
        const suggestionsContainer = document.getElementById('suggestions');
        suggestionsContainer.style.display = 'none'; // Temporarily hide while loading

        try {
            const res = await fetch('/chat/suggestions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question,
                    answer,
                    language: config.language
                })
            });
            const data = await res.json();

            if (data.suggestions && data.suggestions.length > 0) {
                suggestionsContainer.innerHTML = data.suggestions.map(s => 
                    `<button class="suggestion-chip" onclick="setQuery('${s.replace(/'/g, "\\'")}')">${s}</button>`
                ).join('');
                suggestionsContainer.style.display = 'flex';
            }
        } catch (err) {
            console.error('Error fetching suggestions:', err);
        }
    }
    function appendMessage(role, text) {
        const isUser = role === 'user';
        const msg = document.createElement('div');
        msg.className = `message ${role}`;
        msg.innerHTML = `
            <div class="message-avatar">${isUser ? 'Tú' : 'AI'}</div>
            <div class="message-bubble">${escHtml(text)}</div>
        `;
        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msg;
    }

    function appendTyping() {
        const msg = document.createElement('div');
        msg.className = 'message bot';
        msg.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-bubble">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msg;
    }

    window.setQuery = function (q) {
        chatInput.value = q;
        chatInput.focus();
        chatInput.dispatchEvent(new Event('input'));
    };

    function escHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
});
