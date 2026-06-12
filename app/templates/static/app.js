document.addEventListener('DOMContentLoaded', () => {
    /* ── State ── */
    const docs = [];
    let config = { 
        generation_model: localStorage.getItem('gen_model') || '', 
        embedding_model: localStorage.getItem('emb_model') || '' 
    };

    /* ── Settings Management ── */
    const btnOpenSettings  = document.getElementById('btnOpenSettings');
    const btnCloseSettings = document.getElementById('btnCloseSettings');
    const modalSettings    = document.getElementById('modalSettings');
    const btnSaveSettings  = document.getElementById('btnSaveSettings');
    const selectGenModel   = document.getElementById('selectGenModel');
    const selectEmbModel   = document.getElementById('selectEmbModel');
    const currentGenModel  = document.getElementById('currentGenModel');
    const currentEmbModel  = document.getElementById('currentEmbModel');

    btnOpenSettings.addEventListener('click', () => modalSettings.classList.add('active'));
    btnCloseSettings.addEventListener('click', () => modalSettings.classList.remove('active'));
    modalSettings.addEventListener('click', (e) => { if(e.target === modalSettings) modalSettings.classList.remove('active'); });

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
            console.log('Config data received:', data);
            
            // Populate select options
            if (data.models && data.models.generation && data.models.generation.options) {
                selectGenModel.innerHTML = data.models.generation.options.map(opt => 
                    `<option value="${opt.name}">${opt.name} (${opt.cost})</option>`
                ).join('');
            }
            
            if (data.models && data.models.embeddings && data.models.embeddings.options) {
                selectEmbModel.innerHTML = data.models.embeddings.options.map(opt => 
                    `<option value="${opt.name}">${opt.name}</option>`
                ).join('');
            }

            // Set defaults if not in localStorage
            if (!config.generation_model && data.models && data.models.generation) 
                config.generation_model = data.models.generation.default;
            if (!config.embedding_model && data.models && data.models.embeddings) 
                config.embedding_model = data.models.embeddings.default;

            updateSettingsUI();
        } catch (err) {
            console.error('Error loading config:', err);
        }
    }

    function updateSettingsUI() {
        currentGenModel.textContent = config.generation_model;
        currentEmbModel.textContent = config.embedding_model;
        
        const headerGenModel = document.getElementById('headerGenModel');
        if (headerGenModel) headerGenModel.textContent = config.generation_model;

        // Update selects if they were changed elsewhere
        selectGenModel.value = config.generation_model;
        selectEmbModel.value = config.embedding_model;
    }

    btnSaveSettings.addEventListener('click', () => {
        config.generation_model = selectGenModel.value;
        config.embedding_model = selectEmbModel.value;
        localStorage.setItem('gen_model', config.generation_model);
        localStorage.setItem('emb_model', config.embedding_model);
        updateSettingsUI();
        modalSettings.classList.remove('active');
    });

    loadSettings();

    /* ── Upload ── */
    const fileInput  = document.getElementById('fileInput');
    const btnUpload  = document.getElementById('btnUpload');
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
                    updateDocStatus(docId, 'ready');
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
        const list   = document.getElementById('docList');
        const empty  = document.getElementById('emptyState');
        if (!docs.length) { empty.style.display = ''; return; }
        empty.style.display = 'none';

        // Keep empty state node, re-render items
        list.querySelectorAll('.doc-item').forEach(n => n.remove());

        docs.forEach(doc => {
            const statusLabel = { ready: 'Listo', processing: 'Procesando…', error: 'Error' }[doc.status];
            const sizeLabel   = doc.size ? formatBytes(doc.size) : '';

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
                <button class="btn-delete" title="Eliminar" onclick="removeDoc(${doc.id})">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            `;
            list.appendChild(item);
        });
    }

    window.removeDoc = async function(id) {
        const idx = docs.findIndex(d => d.id === id);
        if (idx === -1) {
            console.warn('Doc not found in local array:', id);
            return;
        }

        const doc = docs[idx];
        console.log('Attempting to delete:', doc.name, 'with id:', id);

        try {
            const res = await fetch(`/documents/${encodeURIComponent(doc.name)}`, { method: 'DELETE' });
            if (res.ok) {
                console.log('Doc deleted on server, removing from DOM');

                // Remove from local array
                docs.splice(idx, 1);

                // Direct DOM manipulation
                const docItem = document.querySelector(`.doc-item[data-id="${id}"]`);
                if (docItem) {
                    docItem.remove();
                    console.log('DOM element removed');
                } else {
                    console.error('DOM element not found for id:', id);
                }

                // Re-check empty state
                if (docs.length === 0) {
                    document.getElementById('emptyState').style.display = '';
                }
            } else {
                console.error('Server failed to delete:', res.statusText);
                alert('Error al eliminar el documento en servidor');
            }
        } catch (e) {
            console.error('Delete error:', e);
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
    const chatEmpty    = document.getElementById('chatEmpty');
    const chatInput    = document.getElementById('chatInput');
    const btnSend      = document.getElementById('btnSend');

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
        const question = chatInput.value.trim();
        if (!question) return;

        // Hide empty state
        chatEmpty.style.display = 'none';

        // Hide suggestions after first message
        document.getElementById('suggestions').style.display = 'none';

        appendMessage('user', question);
        chatInput.value = '';
        chatInput.style.height = 'auto';
        btnSend.disabled = true;

        // Typing indicator
        const typingEl = appendTyping();

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    question, 
                    generation_model: config.generation_model 
                })
            });
            const data = await res.json();
            typingEl.remove();
            
            // Render markdown
            const botMessage = document.createElement('div');
            botMessage.className = 'message bot';
            botMessage.innerHTML = `
                <div class="message-avatar">AI</div>
                <div class="message-bubble">${marked.parse(data.answer || 'Sin respuesta.')}</div>
            `;
            chatMessages.appendChild(botMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } catch {
            typingEl.remove();
            appendMessage('bot', 'Error de conexión. Intenta de nuevo.');
        }

        btnSend.disabled = false;
        chatMessages.scrollTop = chatMessages.scrollHeight;
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

    window.setQuery = function(q) {
        chatInput.value = q;
        chatInput.focus();
        chatInput.dispatchEvent(new Event('input'));
    };

    function escHtml(str) {
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }
});
