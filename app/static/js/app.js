/* ==========================================================================
   AETHERMIND MULTIMODAL AI — UNIFIED FRONTEND ENGINE (PHASE 8)
   Multimodal Chat, Document Intelligence, Vision AI, Text-to-Image, Audio,
   Long-Term Memory Dashboard, Knowledge Base & Hybrid Qdrant RAG Search Lab.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 AetherMind Multimodal AI Phase 8 Engine Initialized.");

    // State Variables
    let activeChatId = null;
    let pendingAttachments = [];
    let mediaRecorder = null;
    let audioChunks = [];
    let recordStartTime = 0;
    let recordTimerInterval = null;
    let currentLightboxZoom = 1.0;
    let currentDocumentPages = [];
    let currentDocumentPageIdx = 0;
    let currentDocumentId = null;
    let currentMemoryFilter = "all";

    // Main DOM Elements
    const messagesContainer = document.getElementById("messages-container");
    const welcomeHero = document.getElementById("welcome-hero");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const attachmentTray = document.getElementById("attachment-tray");
    const fileUploadInput = document.getElementById("file-upload-input");
    const dropzoneOverlay = document.getElementById("dropzone-overlay");
    const modelSelect = document.getElementById("model-select");
    const conversationList = document.getElementById("conversation-list");

    // Action Buttons
    const btnAttachFile = document.getElementById("btn-attach-file");
    const btnOpenCamera = document.getElementById("btn-open-camera");
    const btnOpenImageGen = document.getElementById("btn-open-image-gen");
    const btnRecordVoice = document.getElementById("btn-record-voice");
    const btnNewChat = document.getElementById("btn-new-chat");
    const btnClearChat = document.getElementById("btn-clear-chat");
    const btnCompressMemory = document.getElementById("btn-compress-memory");

    // Navigation Buttons for Modals
    const openKnowledgeBtn = document.getElementById("open-knowledge-btn");
    const openMemoryBtn = document.getElementById("open-memory-btn");
    const openSearchBtn = document.getElementById("open-search-btn");
    const openSettingsBtn = document.getElementById("open-settings-btn");

    // Modals
    const modalSettings = document.getElementById("modal-settings");
    const closeSettingsBtn = document.getElementById("close-settings-btn");
    const modalDocumentViewer = document.getElementById("modal-document-viewer");
    const closeDocViewerBtn = document.getElementById("close-doc-viewer-btn");
    const modalImagePreview = document.getElementById("modal-image-preview");
    const closeImgPreviewBtn = document.getElementById("close-img-preview-btn");
    const modalImageGen = document.getElementById("modal-image-gen");
    const closeImageGenBtn = document.getElementById("close-image-gen-btn");
    const modalCamera = document.getElementById("modal-camera");
    const closeCameraBtn = document.getElementById("close-camera-btn");
    const btnCaptureSnapshot = document.getElementById("btn-capture-snapshot");
    const webcamVideo = document.getElementById("webcam-video");
    const modalVoiceRecorder = document.getElementById("modal-voice-recorder");
    const closeVoiceBtn = document.getElementById("close-voice-btn");
    const btnStopVoice = document.getElementById("btn-stop-voice");

    // Phase 8 Modals
    const modalKnowledgeBase = document.getElementById("modal-knowledge-base");
    const closeKnowledgeBtn = document.getElementById("close-knowledge-btn");
    const formCreateCollection = document.getElementById("form-create-collection");
    const formIngestDoc = document.getElementById("form-ingest-doc");
    const knowledgeCollectionsList = document.getElementById("knowledge-collections-list");
    const ingestColSelect = document.getElementById("ingest-col-select");

    const modalMemoryDashboard = document.getElementById("modal-memory-dashboard");
    const closeMemoryBtn = document.getElementById("close-memory-btn");
    const formAddMemory = document.getElementById("form-add-memory");
    const memoryItemsList = document.getElementById("memory-items-list");

    const modalSemanticSearch = document.getElementById("modal-semantic-search");
    const closeSearchBtn = document.getElementById("close-search-btn");
    const formSemanticSearch = document.getElementById("form-semantic-search");
    const searchResultsOutput = document.getElementById("search-results-output");

    // Toast Notification System
    window.showToast = (message, type = "info") => {
        const container = document.getElementById("toast-container");
        if (!container) return;

        const toast = document.createElement("div");
        const bgColors = {
            success: "bg-emerald-950/90 border-emerald-500/40 text-emerald-200",
            error: "bg-rose-950/90 border-rose-500/40 text-rose-200",
            info: "bg-cyan-950/90 border-cyan-500/40 text-cyan-200",
        };
        const icons = { success: "✓", error: "✕", info: "ℹ" };

        toast.className = `p-4 rounded-xl border backdrop-blur-xl shadow-2xl text-xs font-medium flex items-center space-x-3 pointer-events-auto transition-all transform translate-y-2 opacity-0 ${bgColors[type] || bgColors.info}`;
        toast.innerHTML = `<span class="font-bold text-sm">${icons[type] || "ℹ"}</span><span>${message}</span>`;

        container.appendChild(toast);
        setTimeout(() => toast.classList.remove("translate-y-2", "opacity-0"), 10);
        setTimeout(() => {
            toast.classList.add("opacity-0", "translate-y-2");
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };

    // Phase 9 Modals & Workspace Elements
    const modalWorkspaceDashboard = document.getElementById("modal-workspace-dashboard");
    const closeWorkspaceDashboardBtn = document.getElementById("close-workspace-dashboard-btn");
    const openDashboardBtn = document.getElementById("open-dashboard-btn");

    const modalProjectsWorkspace = document.getElementById("modal-projects-workspace");
    const closeProjectsBtn = document.getElementById("close-projects-btn");
    const openProjectsBtn = document.getElementById("open-projects-btn");
    const formCreateProject = document.getElementById("form-create-project");
    const projectsGrid = document.getElementById("projects-grid");

    const modalMediaGallery = document.getElementById("modal-media-gallery");
    const closeMediaBtn = document.getElementById("close-media-btn");
    const openMediaBtn = document.getElementById("open-media-btn");
    const mediaGalleryGrid = document.getElementById("media-gallery-grid");
    const mediaTypeFilter = document.getElementById("media-type-filter");

    const modalDocLibrary = document.getElementById("modal-doc-library");
    const closeDocsBtn = document.getElementById("close-docs-btn");
    const openDocsBtn = document.getElementById("open-docs-btn");
    const docLibraryList = document.getElementById("doc-library-list");

    const modalAudioLibrary = document.getElementById("modal-audio-library");
    const closeAudioBtn = document.getElementById("close-audio-btn");
    const openAudioBtn = document.getElementById("open-audio-btn");
    const audioLibraryList = document.getElementById("audio-library-list");

    const modalRecycleBin = document.getElementById("modal-recycle-bin");
    const closeRecycleBinBtn = document.getElementById("close-recycle-bin-btn");
    const openRecycleBinBtn = document.getElementById("open-recycle-bin-btn");
    const recycleBinList = document.getElementById("recycle-bin-list");
    const btnEmptyRecycleBin = document.getElementById("btn-empty-recycle-bin");

    const modalGlobalSearch = document.getElementById("modal-global-search");
    const closeGlobalSearchBtn = document.getElementById("close-global-search-btn");
    const openGlobalSearchBtn = document.getElementById("open-global-search-btn");
    const formWorkspaceSearch = document.getElementById("form-workspace-search");
    const workspaceSearchResults = document.getElementById("workspace-search-results");

    // Modal Display Helpers
    const hideAllModals = () => {
        [
            modalSettings, modalDocumentViewer, modalImagePreview, modalImageGen, modalCamera, modalVoiceRecorder,
            modalKnowledgeBase, modalMemoryDashboard, modalSemanticSearch,
            modalWorkspaceDashboard, modalProjectsWorkspace, modalMediaGallery, modalDocLibrary, modalAudioLibrary, modalRecycleBin, modalGlobalSearch
        ].forEach(m => m && m.classList.add("hidden"));
        if (webcamVideo.srcObject) {
            webcamVideo.srcObject.getTracks().forEach(t => t.stop());
            webcamVideo.srcObject = null;
        }
    };

    closeSettingsBtn?.addEventListener("click", hideAllModals);
    closeDocViewerBtn?.addEventListener("click", hideAllModals);
    closeImgPreviewBtn?.addEventListener("click", hideAllModals);
    closeImageGenBtn?.addEventListener("click", hideAllModals);
    closeCameraBtn?.addEventListener("click", hideAllModals);
    closeVoiceBtn?.addEventListener("click", hideAllModals);
    closeKnowledgeBtn?.addEventListener("click", hideAllModals);
    closeMemoryBtn?.addEventListener("click", hideAllModals);
    closeSearchBtn?.addEventListener("click", hideAllModals);

    closeWorkspaceDashboardBtn?.addEventListener("click", hideAllModals);
    closeProjectsBtn?.addEventListener("click", hideAllModals);
    closeMediaBtn?.addEventListener("click", hideAllModals);
    closeDocsBtn?.addEventListener("click", hideAllModals);
    closeAudioBtn?.addEventListener("click", hideAllModals);
    closeRecycleBinBtn?.addEventListener("click", hideAllModals);
    closeGlobalSearchBtn?.addEventListener("click", hideAllModals);

    openSettingsBtn?.addEventListener("click", () => { hideAllModals(); modalSettings.classList.remove("hidden"); });
    openKnowledgeBtn?.addEventListener("click", () => { hideAllModals(); modalKnowledgeBase.classList.remove("hidden"); loadKnowledgeCollections(); });
    openMemoryBtn?.addEventListener("click", () => { hideAllModals(); modalMemoryDashboard.classList.remove("hidden"); loadMemories(); });
    openSearchBtn?.addEventListener("click", () => { hideAllModals(); modalSemanticSearch.classList.remove("hidden"); });

    openDashboardBtn?.addEventListener("click", () => { hideAllModals(); modalWorkspaceDashboard.classList.remove("hidden"); loadWorkspaceDashboard(); });
    openProjectsBtn?.addEventListener("click", () => { hideAllModals(); modalProjectsWorkspace.classList.remove("hidden"); loadProjects(); });
    openMediaBtn?.addEventListener("click", () => { hideAllModals(); modalMediaGallery.classList.remove("hidden"); loadMediaGallery(); });
    openDocsBtn?.addEventListener("click", () => { hideAllModals(); modalDocLibrary.classList.remove("hidden"); loadDocLibrary(); });
    openAudioBtn?.addEventListener("click", () => { hideAllModals(); modalAudioLibrary.classList.remove("hidden"); loadAudioLibrary(); });
    openRecycleBinBtn?.addEventListener("click", () => { hideAllModals(); modalRecycleBin.classList.remove("hidden"); loadRecycleBin(); });
    openGlobalSearchBtn?.addEventListener("click", () => { hideAllModals(); modalGlobalSearch.classList.remove("hidden"); });

    // Quick Actions Trigger from Hero
    window.triggerQuickAction = (action) => {
        hideAllModals();
        if (action === "document" || action === "image") {
            fileUploadInput.click();
        } else if (action === "knowledge") {
            modalKnowledgeBase.classList.remove("hidden");
            loadKnowledgeCollections();
        } else if (action === "memory") {
            modalMemoryDashboard.classList.remove("hidden");
            loadMemories();
        } else if (action === "search") {
            modalSemanticSearch.classList.remove("hidden");
        }
    };

    // =========================================================================
    // 1. DRAG AND DROP & ATTACHMENTS SYSTEM
    // =========================================================================
    window.addEventListener("dragover", (e) => {
        e.preventDefault();
        if (dropzoneOverlay) dropzoneOverlay.classList.remove("hidden");
    });

    if (dropzoneOverlay) {
        dropzoneOverlay.addEventListener("dragleave", (e) => {
            e.preventDefault();
            dropzoneOverlay.classList.add("hidden");
        });

        dropzoneOverlay.addEventListener("drop", async (e) => {
            e.preventDefault();
            dropzoneOverlay.classList.add("hidden");
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                await handleFileSelection(e.dataTransfer.files);
            }
        });
    }

    if (btnAttachFile) btnAttachFile.addEventListener("click", () => fileUploadInput.click());

    if (fileUploadInput) {
        fileUploadInput.addEventListener("change", async (e) => {
            if (e.target.files && e.target.files.length > 0) {
                await handleFileSelection(e.target.files);
                fileUploadInput.value = "";
            }
        });
    }

    const handleFileSelection = async (fileList) => {
        for (let i = 0; i < fileList.length; i++) {
            await uploadFileToApi(fileList[i]);
        }
    };

    const uploadFileToApi = async (file) => {
        const formData = new FormData();
        formData.append("file", file);
        if (activeChatId) formData.append("chat_id", activeChatId);

        const tempId = "temp_" + Date.now();
        renderPendingChip({ id: tempId, filename: file.name, file_type: getCategoryFromMime(file.type, file.name), uploading: true });

        try {
            const res = await fetch("/api/v1/upload", { method: "POST", body: formData });
            const data = await res.json();
            removePendingChip(tempId);
            if (data.success && data.data) {
                pendingAttachments.push(data.data);
                renderPendingTray();
                showToast(`Attached ${file.name}`, "success");
            } else {
                showToast(data.detail || `Upload failed`, "error");
            }
        } catch (err) {
            removePendingChip(tempId);
            showToast(`Error uploading ${file.name}`, "error");
        }
    };

    const getCategoryFromMime = (mime, filename) => {
        const name = filename.toLowerCase();
        if (mime.includes("image") || name.endsWith(".png") || name.endsWith(".jpg") || name.endsWith(".jpeg") || name.endsWith(".webp") || name.endsWith(".svg")) return "image";
        if (mime.includes("audio") || name.endsWith(".mp3") || name.endsWith(".wav") || name.endsWith(".m4a") || name.endsWith(".flac")) return "audio";
        return "document";
    };

    const renderPendingTray = () => {
        if (!attachmentTray) return;
        attachmentTray.innerHTML = "";
        if (pendingAttachments.length === 0) {
            attachmentTray.classList.add("hidden");
            return;
        }
        attachmentTray.classList.remove("hidden");
        pendingAttachments.forEach((att) => renderPendingChip(att));
    };

    const renderPendingChip = (att) => {
        if (!attachmentTray) return;
        attachmentTray.classList.remove("hidden");
        const chip = document.createElement("div");
        chip.id = `att_chip_${att.id}`;
        chip.className = "px-3 py-1.5 rounded-xl bg-white/5 border border-white/15 flex items-center space-x-2 text-xs text-slate-200 animate-fade-in";
        const icons = { document: "📄", image: "🖼️", audio: "🎙️" };

        if (att.uploading) {
            chip.innerHTML = `<span class="animate-spin text-cyan-400">⏳</span><span class="truncate max-w-[120px]">${att.filename}</span>`;
        } else {
            chip.innerHTML = `
                <span>${icons[att.file_type] || "📁"}</span>
                <span class="truncate max-w-[140px]">${att.filename}</span>
                <button type="button" class="text-slate-400 hover:text-rose-400 ml-1" onclick="removeAttachment('${att.id}')">✕</button>
            `;
        }
        attachmentTray.appendChild(chip);
    };

    const removePendingChip = (id) => {
        const elem = document.getElementById(`att_chip_${id}`);
        if (elem) elem.remove();
    };

    window.removeAttachment = (id) => {
        pendingAttachments = pendingAttachments.filter(a => a.id !== id);
        renderPendingTray();
    };

    // =========================================================================
    // 2. CHAT & RAG CONTEXT COMPLETIONS
    // =========================================================================
    if (chatForm) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const prompt = chatInput.value.trim();
            if (!prompt && pendingAttachments.length === 0) return;

            const selectedModel = modelSelect.value || "gemini-2.5-flash";
            const attachmentIds = pendingAttachments.map(a => a.id);
            const currentAtts = [...pendingAttachments];

            chatInput.value = "";
            pendingAttachments = [];
            renderPendingTray();

            if (welcomeHero) welcomeHero.classList.add("hidden");

            renderMessage({ role: "user", content: prompt, attachments: currentAtts, created_at: new Date().toISOString() });

            const typingId = "asst_" + Date.now();
            renderAssistantTyping(typingId, selectedModel);

            try {
                const res = await fetch("/api/v1/chat/completions", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt, chat_id: activeChatId, model: selectedModel, attachment_ids: attachmentIds })
                });
                const data = await res.json();
                removeAssistantTyping(typingId);

                if (data.success && data.data) {
                    activeChatId = data.data.chat_id;
                    renderMessage({ role: "assistant", content: data.data.content, model_name: selectedModel, created_at: data.data.created_at });
                    loadConversationsHistory();
                } else {
                    renderMessage({ role: "assistant", content: `⚠️ Error: ${data.detail || "Completion failed"}` });
                }
            } catch (err) {
                removeAssistantTyping(typingId);
                renderMessage({ role: "assistant", content: "⚠️ Network completion error." });
            }
        });
    }

    const renderMessage = (msg) => {
        const msgDiv = document.createElement("div");
        const isUser = msg.role === "user";
        msgDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`;

        let attachmentsHtml = "";
        if (msg.attachments && msg.attachments.length > 0) {
            attachmentsHtml = `<div class="flex flex-wrap gap-2 mb-2">`;
            msg.attachments.forEach(att => {
                if (att.file_type === "image") {
                    attachmentsHtml += `
                        <div class="relative group cursor-pointer overflow-hidden rounded-xl border border-white/15 max-w-[200px]" onclick="openImagePreview('${att.public_url}', '${att.filename}')">
                            <img src="${att.public_url}" class="w-full h-32 object-cover group-hover:scale-105 transition">
                        </div>
                    `;
                } else {
                    attachmentsHtml += `
                        <button type="button" class="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-200 text-xs flex items-center space-x-2" onclick="openDocumentViewer('${att.id}', '${att.filename}')">
                            <span>📄</span>
                            <span class="font-medium truncate max-w-[150px]">${att.filename}</span>
                        </button>
                    `;
                }
            });
            attachmentsHtml += `</div>`;
        }

        msgDiv.innerHTML = `
            <div class="flex space-x-3 max-w-2xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}">
                <div class="w-8 h-8 rounded-xl ${isUser ? 'bg-gradient-to-tr from-cyan-500 to-indigo-600' : 'bg-gradient-to-tr from-indigo-600 to-purple-600'} flex items-center justify-center text-white text-xs font-bold shrink-0 shadow-lg">
                    ${isUser ? '👤' : 'Æ'}
                </div>
                <div class="space-y-1">
                    <div class="p-4 rounded-2xl ${isUser ? 'bg-indigo-600/30 border border-indigo-500/30 text-slate-100 rounded-tr-none' : 'bg-[#0e131f]/90 border border-white/10 text-slate-200 rounded-tl-none'} shadow-xl text-sm leading-relaxed whitespace-pre-wrap">
                        ${attachmentsHtml}
                        <div>${escapeHtml(msg.content)}</div>
                    </div>
                </div>
            </div>
        `;
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    const renderAssistantTyping = (id, model) => {
        const div = document.createElement("div");
        div.id = id;
        div.className = "flex justify-start animate-fade-in";
        div.innerHTML = `
            <div class="flex space-x-3 max-w-2xl">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white text-xs font-bold shrink-0">Æ</div>
                <div class="p-4 rounded-2xl bg-[#0e131f]/90 border border-white/10 text-slate-300 flex items-center space-x-2">
                    <span class="text-xs font-mono text-cyan-400">${model} Qdrant RAG processing</span>
                    <span class="typing-dot"></span><span class="typing-dot"></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    const removeAssistantTyping = (id) => {
        const elem = document.getElementById(id);
        if (elem) elem.remove();
    };

    const escapeHtml = (str) => str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";

    // =========================================================================
    // 3. PHASE 8: KNOWLEDGE BASE & COLLECTIONS
    // =========================================================================
    if (formCreateCollection) {
        formCreateCollection.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("col-name-input").value;
            const description = document.getElementById("col-desc-input").value;
            const tags = document.getElementById("col-tags-input").value.split(",").map(t => t.strip ? t.strip() : t);

            try {
                const res = await fetch("/api/v1/knowledge/collections", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, description, tags })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Knowledge Collection '${name}' created!`, "success");
                    document.getElementById("col-name-input").value = "";
                    document.getElementById("col-desc-input").value = "";
                    loadKnowledgeCollections();
                }
            } catch (err) {
                showToast("Failed to create collection", "error");
            }
        });
    }

    if (formIngestDoc) {
        formIngestDoc.addEventListener("submit", async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById("ingest-file-input");
            if (!fileInput.files || fileInput.files.length === 0) return;

            const formData = new FormData();
            formData.append("file", fileInput.files[0]);
            formData.append("collection_id", ingestColSelect.value || "default");

            showToast("Ingesting & embedding document into Qdrant...", "info");

            try {
                const res = await fetch("/api/v1/knowledge/ingest", { method: "POST", body: formData });
                const data = await res.json();
                if (data.success) {
                    showToast(`Ingested ${fileInput.files[0].name} (${data.data.chunk_count} chunks)`, "success");
                    fileInput.value = "";
                    loadKnowledgeCollections();
                }
            } catch (err) {
                showToast("Document ingestion failed", "error");
            }
        });
    }

    const loadKnowledgeCollections = async () => {
        if (!knowledgeCollectionsList) return;
        try {
            const res = await fetch("/api/v1/knowledge/collections");
            const data = await res.json();
            if (data.success && data.data) {
                renderKnowledgeCollections(data.data);
                populateIngestColSelect(data.data);
            }
        } catch (e) {}
    };

    const populateIngestColSelect = (cols) => {
        if (!ingestColSelect) return;
        ingestColSelect.innerHTML = `<option value="">Default Collection</option>`;
        cols.forEach(c => {
            ingestColSelect.innerHTML += `<option value="${c.id}">${c.name} (${c.doc_count} docs)</option>`;
        });
    };

    const renderKnowledgeCollections = (cols) => {
        knowledgeCollectionsList.innerHTML = "";
        if (cols.length === 0) {
            knowledgeCollectionsList.innerHTML = `<div class="text-slate-400 col-span-2 text-center py-4">No knowledge collections created yet.</div>`;
            return;
        }

        cols.forEach(c => {
            const div = document.createElement("div");
            div.className = "p-4 rounded-xl bg-white/5 border border-white/10 space-y-2";
            div.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="font-bold text-white text-sm">📚 ${escapeHtml(c.name)}</div>
                    <span class="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono text-[10px]">${c.doc_count} docs</span>
                </div>
                <div class="text-slate-400 text-xs">${escapeHtml(c.description || "No description")}</div>
                <div class="text-[10px] font-mono text-slate-500">Qdrant Collection: ${c.qdrant_collection_name}</div>
            `;
            knowledgeCollectionsList.appendChild(div);
        });
    };

    // =========================================================================
    // 4. PHASE 8: LONG-TERM MEMORY DASHBOARD
    // =========================================================================
    if (formAddMemory) {
        formAddMemory.addEventListener("submit", async (e) => {
            e.preventDefault();
            const memory_key = document.getElementById("mem-key-input").value;
            const memory_value = document.getElementById("mem-val-input").value;
            const memory_type = document.getElementById("mem-type-select").value;
            const category = document.getElementById("mem-cat-input").value || "general";

            try {
                const res = await fetch("/api/v1/memory", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ memory_key, memory_value, memory_type, category })
                });
                const data = await res.json();
                if (data.success) {
                    showToast("Memory stored & vector indexed", "success");
                    document.getElementById("mem-key-input").value = "";
                    document.getElementById("mem-val-input").value = "";
                    loadMemories();
                }
            } catch (err) {
                showToast("Failed to add memory", "error");
            }
        });
    }

    if (btnCompressMemory) {
        btnCompressMemory.addEventListener("click", async () => {
            if (!activeChatId) {
                showToast("No active conversation to compress", "info");
                return;
            }
            try {
                const res = await fetch(`/api/v1/memory/compress/${activeChatId}`, { method: "POST" });
                const data = await res.json();
                if (data.success) {
                    showToast("Conversation compressed into long-term memory", "success");
                }
            } catch (e) {
                showToast("Compression failed", "error");
            }
        });
    }

    const loadMemories = async () => {
        if (!memoryItemsList) return;
        try {
            const url = currentMemoryFilter === "all" ? "/api/v1/memory" : `/api/v1/memory?memory_type=${currentMemoryFilter}`;
            const res = await fetch(url);
            const data = await res.json();
            if (data.success && data.data) {
                renderMemoryItems(data.data);
            }
        } catch (e) {}
    };

    const renderMemoryItems = (items) => {
        memoryItemsList.innerHTML = "";
        if (items.length === 0) {
            memoryItemsList.innerHTML = `<div class="text-slate-400 col-span-2 text-center py-4">No memories stored.</div>`;
            return;
        }

        items.forEach(m => {
            const div = document.createElement("div");
            div.className = "p-3.5 rounded-xl bg-white/5 border border-white/10 space-y-1.5 relative group";
            div.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="font-bold text-white text-xs truncate max-w-[200px]">📌 ${escapeHtml(m.memory_key)}</div>
                    <span class="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono text-[9px] uppercase">${m.memory_type}</span>
                </div>
                <div class="text-slate-300 text-xs">${escapeHtml(m.memory_value)}</div>
                <div class="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                    <span>Category: ${m.category}</span>
                    <button class="text-rose-400 hover:underline" onclick="deleteMemoryItem('${m.id}')">Delete</button>
                </div>
            `;
            memoryItemsList.appendChild(div);
        });
    };

    window.filterMemories = (type) => {
        currentMemoryFilter = type;
        loadMemories();
    };

    window.deleteMemoryItem = async (memId) => {
        try {
            await fetch(`/api/v1/memory/${memId}`, { method: "DELETE" });
            loadMemories();
            showToast("Memory item deleted", "info");
        } catch (e) {}
    };

    // =========================================================================
    // 5. PHASE 8: HYBRID & SEMANTIC SEARCH LAB
    // =========================================================================
    if (formSemanticSearch) {
        formSemanticSearch.addEventListener("submit", async (e) => {
            e.preventDefault();
            const query = document.getElementById("search-query-input").value.trim();
            const search_type = document.getElementById("search-type-select").value;
            if (!query) return;

            searchResultsOutput.innerHTML = `<div class="text-slate-400 text-center py-4">Searching Qdrant Vector DB & Knowledge Base...</div>`;

            try {
                const res = await fetch("/api/v1/search", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query, search_type, limit: 10 })
                });
                const data = await res.json();
                if (data.success && data.data) {
                    renderSearchResults(data.data.results || []);
                }
            } catch (err) {
                searchResultsOutput.innerHTML = `<div class="text-rose-400 text-center py-4">Search execution failed.</div>`;
            }
        });
    }

    const renderSearchResults = (results) => {
        searchResultsOutput.innerHTML = "";
        if (results.length === 0) {
            searchResultsOutput.innerHTML = `<div class="text-slate-400 text-center py-4">No matching vectors or knowledge chunks found.</div>`;
            return;
        }

        results.forEach(r => {
            const div = document.createElement("div");
            div.className = "p-4 rounded-xl bg-white/5 border border-white/10 space-y-2";
            div.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="font-bold text-cyan-300 text-xs">${escapeHtml(r.title)}</div>
                    <span class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono text-[10px]">Score: ${r.score}</span>
                </div>
                <div class="text-slate-200 text-xs font-mono whitespace-pre-wrap">${escapeHtml(r.content)}</div>
            `;
            searchResultsOutput.appendChild(div);
        });
    };

    // Conversations Load & Switch
    const loadConversationsHistory = async () => {
        if (!conversationList) return;
        try {
            const res = await fetch("/api/v1/chat/conversations");
            const data = await res.json();
            if (data.success && data.data) renderConversationsList(data.data);
        } catch (e) {}
    };

    const renderConversationsList = (chats) => {
        conversationList.innerHTML = "";
        chats.forEach(c => {
            const btn = document.createElement("button");
            const isActive = c.id === activeChatId;
            btn.className = `w-full py-2.5 px-3 rounded-lg text-xs font-medium flex items-center justify-between transition ${isActive ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-300 hover:bg-white/5'}`;
            btn.innerHTML = `
                <div class="flex items-center space-x-2 truncate">
                    <span>💬</span>
                    <span class="truncate">${escapeHtml(c.title)}</span>
                </div>
                <button class="text-slate-500 hover:text-rose-400 p-1" onclick="deleteConversation('${c.id}', event)">✕</button>
            `;
            btn.addEventListener("click", () => switchConversation(c.id));
            conversationList.appendChild(btn);
        });
    };

    window.switchConversation = async (chatId) => {
        activeChatId = chatId;
        messagesContainer.innerHTML = "";
        try {
            const res = await fetch(`/api/v1/chat/conversations/${chatId}`);
            const data = await res.json();
            if (data.success && data.data) {
                (data.data.messages || []).forEach(m => renderMessage(m));
                if (welcomeHero) welcomeHero.classList.add("hidden");
            }
        } catch (e) {}
    };

    window.deleteConversation = async (chatId, event) => {
        if (event) event.stopPropagation();
        try {
            await fetch(`/api/v1/chat/conversations/${chatId}`, { method: "DELETE" });
            if (activeChatId === chatId) {
                activeChatId = null;
                messagesContainer.innerHTML = "";
                if (welcomeHero) messagesContainer.classList.remove("hidden");
            }
            loadConversationsHistory();
        } catch (e) {}
    };

    if (btnNewChat) {
        btnNewChat.addEventListener("click", () => {
            activeChatId = null;
            messagesContainer.innerHTML = "";
            if (welcomeHero) messagesContainer.appendChild(welcomeHero);
            if (welcomeHero) welcomeHero.classList.remove("hidden");
            pendingAttachments = [];
            renderPendingTray();
        });
    }

    if (btnClearChat) {
        btnClearChat.addEventListener("click", () => {
            messagesContainer.innerHTML = "";
            if (welcomeHero) messagesContainer.appendChild(welcomeHero);
            if (welcomeHero) welcomeHero.classList.remove("hidden");
        });
    }

    // =========================================================================
    // 6. PHASE 9: CLOUD WORKSPACE & PRODUCTIVITY SYSTEM
    // =========================================================================

    // A. WORKSPACE DASHBOARD OVERVIEW
    const loadWorkspaceDashboard = async () => {
        try {
            const res = await fetch("/api/v1/dashboard/overview");
            const data = await res.json();
            if (data.success && data.data) {
                const stats = data.data.overview || data.data.stats || {};
                const storage = data.data.storage || data.data.storage_breakdown || {};
                const recent_uploads = data.data.recent_uploads || [];

                document.getElementById("dash-total-files").textContent = stats.total_files || 0;
                document.getElementById("dash-total-storage").textContent = storage.used_mb ? `${storage.used_mb} MB / ${storage.quota_gb || 50} GB (${storage.used_percentage || 0}%)` : "0 B";
                document.getElementById("dash-total-projects").textContent = stats.total_projects || 0;
                document.getElementById("dash-total-chats").textContent = stats.total_conversations || stats.total_chats || 0;

                const imgElem = document.getElementById("dash-storage-images");
                const docElem = document.getElementById("dash-storage-docs");
                const audElem = document.getElementById("dash-storage-audio");

                if (imgElem) imgElem.textContent = storage.breakdown?.image?.count ? `${storage.breakdown.image.count} files` : "0 files";
                if (docElem) docElem.textContent = storage.breakdown?.document?.count ? `${storage.breakdown.document.count} files` : "0 files";
                if (audElem) audElem.textContent = storage.breakdown?.audio?.count ? `${storage.breakdown.audio.count} files` : "0 files";

                const timelineContainer = document.getElementById("dash-activity-timeline");
                if (timelineContainer) {
                    timelineContainer.innerHTML = "";
                    if (timeline.length === 0) {
                        timelineContainer.innerHTML = `<div class="text-slate-400 text-xs py-2">No recent workspace activities logged.</div>`;
                    } else {
                        timeline.forEach(item => {
                            const div = document.createElement("div");
                            div.className = "flex items-start space-x-3 text-xs p-2.5 rounded-lg bg-white/5 border border-white/5";
                            div.innerHTML = `
                                <div class="text-cyan-400 font-bold shrink-0">⚡</div>
                                <div class="flex-1 min-w-0">
                                    <div class="text-slate-200 font-medium truncate">${escapeHtml(item.action)}: ${escapeHtml(item.target_name || item.entity_type)}</div>
                                    <div class="text-[10px] text-slate-400">${item.timestamp ? new Date(item.timestamp).toLocaleString() : ''}</div>
                                </div>
                            `;
                            timelineContainer.appendChild(div);
                        });
                    }
                }
            }
        } catch (err) {
            showToast("Failed to load workspace dashboard", "error");
        }
    };

    // B. PROJECTS MANAGEMENT
    if (formCreateProject) {
        formCreateProject.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("project-name-input").value.trim();
            const description = document.getElementById("project-desc-input").value.trim();
            const color = document.getElementById("project-color-input")?.value || "#3b82f6";
            if (!name) return;

            try {
                const res = await fetch("/api/v1/projects", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, description, color })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Project '${name}' created successfully`, "success");
                    document.getElementById("project-name-input").value = "";
                    document.getElementById("project-desc-input").value = "";
                    loadProjects();
                } else {
                    showToast(data.detail || "Failed to create project", "error");
                }
            } catch (e) {
                showToast("Error creating project", "error");
            }
        });
    }

    const loadProjects = async () => {
        if (!projectsGrid) return;
        try {
            const res = await fetch("/api/v1/projects");
            const data = await res.json();
            if (data.success && data.data) {
                renderProjectsList(data.data);
            }
        } catch (e) {}
    };

    const renderProjectsList = (projects) => {
        projectsGrid.innerHTML = "";
        if (projects.length === 0) {
            projectsGrid.innerHTML = `<div class="text-slate-400 col-span-3 text-center py-6">No projects created yet. Create a project above!</div>`;
            return;
        }

        projects.forEach(p => {
            const card = document.createElement("div");
            card.className = "p-4 rounded-xl bg-white/5 border border-white/10 space-y-3 flex flex-col justify-between group hover:border-cyan-500/40 transition";
            card.innerHTML = `
                <div>
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <span class="w-3 h-3 rounded-full" style="background-color: ${p.color || '#3b82f6'}"></span>
                            <h4 class="font-bold text-white text-sm truncate">${escapeHtml(p.name)}</h4>
                        </div>
                        <span class="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono text-[10px]">${p.file_count || 0} files</span>
                    </div>
                    <p class="text-slate-400 text-xs mt-2 line-clamp-2">${escapeHtml(p.description || "No project details")}</p>
                </div>
                <div class="flex items-center justify-between text-[11px] pt-2 border-t border-white/5">
                    <span class="text-slate-500">${p.chat_count || 0} chats</span>
                    <button type="button" class="text-rose-400 hover:underline" onclick="deleteProject('${p.id}')">Delete</button>
                </div>
            `;
            projectsGrid.appendChild(card);
        });
    };

    window.deleteProject = async (projectId) => {
        try {
            const res = await fetch(`/api/v1/projects/${projectId}`, { method: "DELETE" });
            const data = await res.json();
            if (data.success) {
                showToast("Project deleted", "info");
                loadProjects();
            }
        } catch (e) {}
    };

    // C. MEDIA GALLERY
    if (mediaTypeFilter) {
        mediaTypeFilter.addEventListener("change", () => loadMediaGallery());
    }

    const loadMediaGallery = async () => {
        if (!mediaGalleryGrid) return;
        const cat = mediaTypeFilter ? mediaTypeFilter.value : "all";
        try {
            const res = await fetch(`/api/v1/workspace/media-gallery?category=${cat}`);
            const data = await res.json();
            if (data.success && data.data) {
                renderMediaGallery(data.data);
            }
        } catch (e) {}
    };

    const renderMediaGallery = (items) => {
        mediaGalleryGrid.innerHTML = "";
        if (items.length === 0) {
            mediaGalleryGrid.innerHTML = `<div class="text-slate-400 col-span-3 text-center py-6">No images found in gallery.</div>`;
            return;
        }

        items.forEach(item => {
            const card = document.createElement("div");
            card.className = "group relative rounded-xl border border-white/10 overflow-hidden bg-black/40 flex flex-col";
            card.innerHTML = `
                <div class="relative h-36 overflow-hidden cursor-pointer" onclick="openImagePreview('${item.public_url}', '${escapeHtml(item.filename)}')">
                    <img src="${item.public_url}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" />
                </div>
                <div class="p-2.5 bg-[#0e131f] flex items-center justify-between text-xs">
                    <span class="font-medium text-slate-200 truncate max-w-[120px]" title="${escapeHtml(item.filename)}">${escapeHtml(item.filename)}</span>
                    <div class="flex items-center space-x-1">
                        <button type="button" class="text-yellow-400 hover:text-yellow-300" onclick="toggleStarFile('${item.id}', event)">${item.is_starred ? '★' : '☆'}</button>
                        <button type="button" class="text-rose-400 hover:text-rose-300" onclick="softDeleteFile('${item.id}', event)">🗑️</button>
                    </div>
                </div>
            `;
            mediaGalleryGrid.appendChild(card);
        });
    };

    // D. DOCUMENT LIBRARY
    const loadDocLibrary = async () => {
        if (!docLibraryList) return;
        try {
            const res = await fetch("/api/v1/workspace/doc-library");
            const data = await res.json();
            if (data.success && data.data) {
                renderDocLibrary(data.data);
            }
        } catch (e) {}
    };

    const renderDocLibrary = (items) => {
        docLibraryList.innerHTML = "";
        if (items.length === 0) {
            docLibraryList.innerHTML = `<div class="text-slate-400 text-center py-6">No documents found in library.</div>`;
            return;
        }

        items.forEach(item => {
            const div = document.createElement("div");
            div.className = "p-3 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between text-xs hover:border-cyan-500/30 transition";
            div.innerHTML = `
                <div class="flex items-center space-x-3 truncate">
                    <span class="text-cyan-400 text-base">📄</span>
                    <div>
                        <div class="font-semibold text-white truncate max-w-[240px]">${escapeHtml(item.filename)}</div>
                        <div class="text-[10px] text-slate-400">${item.size_formatted} • ${item.chunk_count ? item.chunk_count + ' indexed chunks' : 'Uploaded doc'}</div>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <button type="button" class="px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 font-medium hover:bg-cyan-500/30" onclick="openDocumentViewer('${item.id}', '${escapeHtml(item.filename)}')">View</button>
                    <button type="button" class="text-yellow-400 hover:text-yellow-300 p-1" onclick="toggleStarFile('${item.id}', event)">${item.is_starred ? '★' : '☆'}</button>
                    <button type="button" class="text-rose-400 hover:text-rose-300 p-1" onclick="softDeleteFile('${item.id}', event)">🗑️</button>
                </div>
            `;
            docLibraryList.appendChild(div);
        });
    };

    // E. AUDIO LIBRARY
    const loadAudioLibrary = async () => {
        if (!audioLibraryList) return;
        try {
            const res = await fetch("/api/v1/workspace/audio-library");
            const data = await res.json();
            if (data.success && data.data) {
                renderAudioLibrary(data.data);
            }
        } catch (e) {}
    };

    const renderAudioLibrary = (items) => {
        audioLibraryList.innerHTML = "";
        if (items.length === 0) {
            audioLibraryList.innerHTML = `<div class="text-slate-400 text-center py-6">No audio recordings or uploads found.</div>`;
            return;
        }

        items.forEach(item => {
            const div = document.createElement("div");
            div.className = "p-3 rounded-xl bg-white/5 border border-white/10 space-y-2 text-xs";
            div.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="font-semibold text-white truncate max-w-[200px]">🎙️ ${escapeHtml(item.filename)}</div>
                    <div class="flex items-center space-x-1">
                        <span class="text-[10px] text-slate-400">${item.size_formatted}</span>
                        <button type="button" class="text-rose-400 hover:text-rose-300 p-1" onclick="softDeleteFile('${item.id}', event)">🗑️</button>
                    </div>
                </div>
                <audio controls src="${item.public_url}" class="w-full h-8 rounded-lg bg-slate-900"></audio>
            `;
            audioLibraryList.appendChild(div);
        });
    };

    // F. RECYCLE BIN MANAGEMENT
    const loadRecycleBin = async () => {
        if (!recycleBinList) return;
        try {
            const res = await fetch("/api/v1/workspace/recycle-bin");
            const data = await res.json();
            if (data.success && data.data) {
                renderRecycleBin(data.data);
            }
        } catch (e) {}
    };

    const renderRecycleBin = (items) => {
        recycleBinList.innerHTML = "";
        if (items.length === 0) {
            recycleBinList.innerHTML = `<div class="text-slate-400 text-center py-6">Recycle bin is completely empty.</div>`;
            return;
        }

        items.forEach(item => {
            const div = document.createElement("div");
            div.className = "p-3 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between text-xs";
            div.innerHTML = `
                <div class="flex items-center space-x-3 truncate">
                    <span class="text-rose-400 text-base">🗑️</span>
                    <div>
                        <div class="font-medium text-slate-200 truncate max-w-[220px]">${escapeHtml(item.filename)}</div>
                        <div class="text-[10px] text-slate-400">Deleted ${item.deleted_at ? new Date(item.deleted_at).toLocaleString() : ''}</div>
                    </div>
                </div>
                <button type="button" class="px-3 py-1 rounded-lg bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 font-medium hover:bg-emerald-500/30" onclick="restoreFromRecycleBin('${item.id}')">Restore</button>
            `;
            recycleBinList.appendChild(div);
        });
    };

    if (btnEmptyRecycleBin) {
        btnEmptyRecycleBin.addEventListener("click", async () => {
            try {
                const res = await fetch("/api/v1/workspace/recycle-bin/empty", { method: "POST" });
                const data = await res.json();
                if (data.success) {
                    showToast("Recycle bin emptied", "info");
                    loadRecycleBin();
                }
            } catch (e) {}
        });
    }

    window.restoreFromRecycleBin = async (fileId) => {
        try {
            const res = await fetch(`/api/v1/workspace/recycle-bin/restore/${fileId}`, { method: "POST" });
            const data = await res.json();
            if (data.success) {
                showToast("File restored successfully", "success");
                loadRecycleBin();
            }
        } catch (e) {}
    };

    // G. GLOBAL WORKSPACE SEARCH
    if (formWorkspaceSearch) {
        formWorkspaceSearch.addEventListener("submit", async (e) => {
            e.preventDefault();
            const query = document.getElementById("workspace-search-input").value.trim();
            const entity_type = document.getElementById("workspace-search-type").value;
            if (!query) return;

            workspaceSearchResults.innerHTML = `<div class="text-slate-400 text-center py-4">Searching workspace entities...</div>`;

            try {
                const res = await fetch("/api/v1/workspace/search", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query, entity_type, limit: 15 })
                });
                const data = await res.json();
                if (data.success && data.data) {
                    renderWorkspaceSearchResults(data.data.results || []);
                }
            } catch (err) {
                workspaceSearchResults.innerHTML = `<div class="text-rose-400 text-center py-4">Workspace search failed.</div>`;
            }
        });
    }

    const renderWorkspaceSearchResults = (results) => {
        workspaceSearchResults.innerHTML = "";
        if (results.length === 0) {
            workspaceSearchResults.innerHTML = `<div class="text-slate-400 text-center py-4">No matching workspace items found.</div>`;
            return;
        }

        results.forEach(r => {
            const div = document.createElement("div");
            div.className = "p-3.5 rounded-xl bg-white/5 border border-white/10 space-y-1 text-xs hover:border-cyan-500/40 transition";
            const icons = { chat: "💬", file: "📁", project: "📁", memory: "🧠", knowledge: "📚" };
            div.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="font-bold text-cyan-300 flex items-center space-x-2">
                        <span>${icons[r.entity_type] || '🔍'}</span>
                        <span>${escapeHtml(r.title)}</span>
                    </div>
                    <span class="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono text-[9px] uppercase">${r.entity_type}</span>
                </div>
                <div class="text-slate-300 text-xs">${escapeHtml(r.snippet)}</div>
            `;
            workspaceSearchResults.appendChild(div);
        });
    };

    // H. FILE OPERATIONS HELPERS
    window.toggleStarFile = async (fileId, event) => {
        if (event) event.stopPropagation();
        try {
            const res = await fetch(`/api/v1/files/${fileId}/star`, { method: "POST" });
            const data = await res.json();
            if (data.success) {
                showToast(data.data.is_starred ? "File starred" : "File unstarred", "info");
                loadMediaGallery();
                loadDocLibrary();
            }
        } catch (e) {}
    };

    window.softDeleteFile = async (fileId, event) => {
        if (event) event.stopPropagation();
        try {
            const res = await fetch(`/api/v1/files/${fileId}/delete`, { method: "POST" });
            const data = await res.json();
            if (data.success) {
                showToast("File moved to Recycle Bin", "info");
                loadMediaGallery();
                loadDocLibrary();
                loadAudioLibrary();
            }
        } catch (e) {}
    };

    // Sidebar Toggle
    const sidebar = document.getElementById("sidebar");
    const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("w-72");
            sidebar.classList.toggle("w-20");
        });
    }

    // Initial Load
    loadConversationsHistory();
});

