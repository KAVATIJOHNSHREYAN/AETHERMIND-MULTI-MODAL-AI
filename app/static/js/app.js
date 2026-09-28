/* ==========================================================================
   AETHERMIND MULTIMODAL AI — UNIFIED FRONTEND ENGINE (PHASE 8)
   Multimodal Chat, Document Intelligence, Vision AI, Text-to-Image, Audio,
   Long-Term Memory Dashboard, Knowledge Base & Hybrid Qdrant RAG Search Lab.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 AetherMind Multimodal AI Phase 8 Engine Initialized.");

    // State Variables
    let activeChatId = localStorage.getItem('aethermind_active_chat') || null;
    let pendingAttachments = [];
    let mediaRecorder = null;
    let audioChunks = [];
    let voiceSeconds = 0;
    let voiceTimerInterval = null;
    let recordStartTime = 0;
    let recordTimerInterval = null;
    let currentLightboxZoom = 1.0;
    let currentDocumentPages = [];
    let currentDocumentPageIdx = 0;
    let currentDocumentId = null;
    let currentMemoryFilter = "all";

    // Global Window Helpers for Inline onclick Handlers
    window.openImagePreview = (url, name) => {
        const modalImagePreview = document.getElementById("modal-image-preview");
        const previewImgElement = document.getElementById("preview-img-element");
        const previewImgTitle = document.getElementById("preview-img-title");
        const previewDownloadBtn = document.getElementById("preview-download-btn");

        if (modalImagePreview && previewImgElement) {
            document.querySelectorAll('[id^="modal-"]').forEach(m => m.classList.add("hidden"));
            previewImgElement.src = url;
            if (previewImgTitle) previewImgTitle.innerText = name || "AI Artwork Preview";
            if (previewDownloadBtn) {
                previewDownloadBtn.href = url;
                previewDownloadBtn.download = name || "artwork.png";
            }
            modalImagePreview.classList.remove("hidden");
        }
    };

    window.openDocumentViewer = async (docId, filename) => {
        const modalDocumentViewer = document.getElementById("modal-document-viewer");
        const docViewerTitle = document.getElementById("doc-viewer-title");
        const docViewerContent = document.getElementById("doc-viewer-content");

        if (modalDocumentViewer) {
            document.querySelectorAll('[id^="modal-"]').forEach(m => m.classList.add("hidden"));
            if (docViewerTitle) docViewerTitle.innerText = filename || "Document Viewer";
            if (docViewerContent) docViewerContent.innerHTML = `<div class="text-slate-400 p-4 font-mono">Loading document content...</div>`;
            modalDocumentViewer.classList.remove("hidden");

            try {
                const res = await authenticatedFetch(`/api/v1/files/${docId}`);
                const data = await res.json();
                if (data.success && data.data && data.data.extracted_text) {
                    if (docViewerContent) docViewerContent.innerText = data.data.extracted_text;
                } else {
                    if (docViewerContent) docViewerContent.innerText = "Document loaded.";
                }
            } catch (e) {
                if (docViewerContent) docViewerContent.innerText = "Error loading document details.";
            }
        }
    };

    function getOrCreateClientSessionId() {
        let sid = localStorage.getItem("aethermind_session");
        if (!sid) {
            sid = "sess_guest_" + Math.random().toString(36).substring(2, 10) + Date.now().toString(36);
            localStorage.setItem("aethermind_session", sid);
        }
        document.cookie = `aethermind_session=${sid}; path=/; max-age=31536000; SameSite=Lax`;
        return sid;
    }

    // Centralized User-Isolated Authenticated Fetch Wrapper
    async function authenticatedFetch(url, options = {}) {
        options.headers = options.headers || {};
        const clientSid = getOrCreateClientSessionId();

        if (options.headers instanceof Headers) {
            options.headers.set("X-Session-ID", clientSid);
        } else if (Array.isArray(options.headers)) {
            options.headers.push(["X-Session-ID", clientSid]);
        } else {
            options.headers["X-Session-ID"] = clientSid;
        }

        if (window.firebase && window.firebase.auth && window.firebase.auth().currentUser) {
            try {
                const token = await window.firebase.auth().currentUser.getIdToken();
                if (token) {
                    if (options.headers instanceof Headers) {
                        options.headers.set("Authorization", `Bearer ${token}`);
                    } else if (Array.isArray(options.headers)) {
                        options.headers.push(["Authorization", `Bearer ${token}`]);
                    } else {
                        options.headers["Authorization"] = `Bearer ${token}`;
                    }
                    document.cookie = `aethermind_token=${token}; path=/; max-age=604800; SameSite=Lax`;
                }
            } catch (err) {
                console.warn("[Firebase Fetch Warning] Unable to attach session token:", err);
            }
        }
        return fetch(url, options);
    }

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
    const closeWorkspaceDashboardBtn = document.getElementById("close-workspace-dashboard-btn") || document.getElementById("close-dashboard-btn");
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
    const closeDocsBtn = document.getElementById("close-docs-btn") || document.getElementById("close-doc-lib-btn");
    const openDocsBtn = document.getElementById("open-docs-btn") || document.getElementById("open-doc-lib-btn");
    const docLibraryList = document.getElementById("doc-library-list");

    const modalAudioLibrary = document.getElementById("modal-audio-library");
    const closeAudioBtn = document.getElementById("close-audio-btn") || document.getElementById("close-audio-lib-btn");
    const openAudioBtn = document.getElementById("open-audio-btn") || document.getElementById("open-audio-lib-btn");
    const audioLibraryList = document.getElementById("audio-library-list");

    const modalRecycleBin = document.getElementById("modal-recycle-bin");
    const closeRecycleBinBtn = document.getElementById("close-recycle-bin-btn") || document.getElementById("close-recycle-btn");
    const openRecycleBinBtn = document.getElementById("open-recycle-bin-btn") || document.getElementById("open-recycle-btn");
    const recycleBinList = document.getElementById("recycle-bin-list");
    const btnEmptyRecycleBin = document.getElementById("btn-empty-recycle-bin");

    const modalGlobalSearch = document.getElementById("modal-global-search");
    const closeGlobalSearchBtn = document.getElementById("close-global-search-btn");
    const openGlobalSearchBtn = document.getElementById("open-global-search-btn") || document.getElementById("open-search-btn");
    const formWorkspaceSearch = document.getElementById("form-workspace-search");
    const workspaceSearchResults = document.getElementById("workspace-search-results");

    // Modal Display Helpers
    const hideAllModals = () => {
        document.querySelectorAll('[id^="modal-"]').forEach(m => m.classList.add("hidden"));
        const userDropdownMenu = document.getElementById("user-dropdown-menu");
        if (userDropdownMenu) userDropdownMenu.classList.add("hidden");
        if (webcamVideo && webcamVideo.srcObject) {
            webcamVideo.srcObject.getTracks().forEach(t => t.stop());
            webcamVideo.srcObject = null;
        }
    };

    // Bind all close buttons
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

    // Dynamic Centralized Click Listener Delegation for All Interactive UI Buttons
    document.addEventListener("click", async (e) => {
        // User Profile Badge & Dropdown Menu Toggle
        const userProfileBadge = e.target.closest("#user-profile-badge");
        if (userProfileBadge) {
            e.stopPropagation();
            const dropdown = document.getElementById("user-dropdown-menu");
            if (dropdown) dropdown.classList.toggle("hidden");
            return;
        }

        // Close Dropdown when clicking outside
        const dropdownMenu = document.getElementById("user-dropdown-menu");
        if (dropdownMenu && !dropdownMenu.contains(e.target) && !e.target.closest("#user-profile-badge")) {
            dropdownMenu.classList.add("hidden");
        }

        const targetBtn = e.target.closest("button, [id^='open-'], [id^='btn-']");
        if (!targetBtn) return;
        const id = targetBtn.id;

        // Sidebar Collapse & Expand Toggle Buttons
        if (id === "sidebar-toggle-btn" || id === "sidebar-open-btn") {
            e.preventDefault();
            const sidebar = document.getElementById("sidebar");
            const sidebarOpenBtn = document.getElementById("sidebar-open-btn");
            if (sidebar) {
                sidebar.classList.toggle("hidden");
                if (sidebarOpenBtn) {
                    sidebarOpenBtn.classList.toggle("hidden", !sidebar.classList.contains("hidden"));
                }
            }
            return;
        }

        // Close Modal Buttons
        if (id.startsWith("close-") || targetBtn.closest("button[id^='close-']")) {
            hideAllModals();
            return;
        }

        // + NEW CHAT Button
        if (id === "btn-new-chat") {
            e.preventDefault();
            hideAllModals();
            activeChatId = null;
            localStorage.removeItem('aethermind_active_chat');
            const msgContainer = document.getElementById("messages-container");
            const hero = document.getElementById("welcome-hero");
            if (msgContainer) {
                msgContainer.innerHTML = "";
                if (hero) {
                    hero.classList.remove("hidden");
                    msgContainer.appendChild(hero);
                }
            }
            showToast("✨ Started new chat session.", "info");
            return;
        }

        // Clear Chat Button
        if (id === "btn-clear-chat") {
            e.preventDefault();
            const msgContainer = document.getElementById("messages-container");
            const hero = document.getElementById("welcome-hero");
            if (msgContainer) {
                msgContainer.innerHTML = "";
                if (hero) {
                    hero.classList.remove("hidden");
                    msgContainer.appendChild(hero);
                }
            }
            showToast("🗑️ Chat cleared.", "info");
            return;
        }

        // Compress Memory Button
        if (id === "btn-compress-memory") {
            e.preventDefault();
            showToast("🧠 Context memory compressed and optimized!", "success");
            return;
        }

        // Workspace Dashboard
        if (id === "open-dashboard-btn") {
            e.preventDefault();
            hideAllModals();
            const modalWorkspaceDashboard = document.getElementById("modal-workspace-dashboard");
            if (modalWorkspaceDashboard) modalWorkspaceDashboard.classList.remove("hidden");
            loadWorkspaceDashboard();
            return;
        }

        // Documents Intelligence
        if (id === "open-doc-lib-btn" || id === "open-docs-btn") {
            e.preventDefault();
            hideAllModals();
            const modalDocLibrary = document.getElementById("modal-doc-library");
            if (modalDocLibrary) modalDocLibrary.classList.remove("hidden");
            loadDocLibrary();
            return;
        }

        // Images & AI Artwork
        if (id === "open-media-btn") {
            e.preventDefault();
            hideAllModals();
            const modalMediaGallery = document.getElementById("modal-media-gallery");
            if (modalMediaGallery) modalMediaGallery.classList.remove("hidden");
            loadMediaGallery();
            return;
        }

        // Audio & Voice Studio
        if (id === "open-audio-lib-btn" || id === "open-audio-btn") {
            e.preventDefault();
            hideAllModals();
            const modalAudioLibrary = document.getElementById("modal-audio-library");
            if (modalAudioLibrary) modalAudioLibrary.classList.remove("hidden");
            loadAudioLibrary();
            return;
        }

        // Memory & Knowledge
        if (id === "open-memory-btn") {
            e.preventDefault();
            hideAllModals();
            const modalMemoryDashboard = document.getElementById("modal-memory-dashboard");
            if (modalMemoryDashboard) modalMemoryDashboard.classList.remove("hidden");
            loadMemories();
            return;
        }

        // Projects & Folders
        if (id === "open-projects-btn") {
            e.preventDefault();
            hideAllModals();
            const modalProjectsWorkspace = document.getElementById("modal-projects-workspace");
            if (modalProjectsWorkspace) modalProjectsWorkspace.classList.remove("hidden");
            loadProjects();
            return;
        }

        // System Settings
        if (id === "open-settings-btn" || id === "dropdown-open-settings" || id === "dropdown-open-keys") {
            e.preventDefault();
            hideAllModals();
            const modalSettings = document.getElementById("modal-settings");
            if (modalSettings) modalSettings.classList.remove("hidden");
            return;
        }

        // Recycle Bin
        if (id === "open-recycle-btn" || id === "open-recycle-bin-btn") {
            e.preventDefault();
            hideAllModals();
            const modalRecycleBin = document.getElementById("modal-recycle-bin");
            if (modalRecycleBin) modalRecycleBin.classList.remove("hidden");
            loadRecycleBin();
            return;
        }

        // Global Search
        if (id === "open-global-search-btn" || id === "open-search-btn") {
            e.preventDefault();
            hideAllModals();
            const modalGlobalSearch = document.getElementById("modal-global-search");
            if (modalGlobalSearch) modalGlobalSearch.classList.remove("hidden");
            return;
        }

        // Knowledge Base
        if (id === "open-knowledge-btn") {
            e.preventDefault();
            hideAllModals();
            const modalKnowledgeBase = document.getElementById("modal-knowledge-base");
            if (modalKnowledgeBase) modalKnowledgeBase.classList.remove("hidden");
            loadKnowledgeCollections();
            return;
        }

        // Attach File Button
        if (id === "btn-attach-file" || id === "btn-attach") {
            e.preventDefault();
            const fileInput = document.getElementById("file-upload-input");
            if (fileInput) fileInput.click();
            return;
        }

        // Camera Button
        if (id === "btn-open-camera" || id === "btn-camera") {
            e.preventDefault();
            hideAllModals();
            const modalCam = document.getElementById("modal-camera");
            if (modalCam) modalCam.classList.remove("hidden");
            const webcamVid = document.getElementById("webcam-video");
            if (webcamVid) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    webcamVid.srcObject = stream;
                    webcamVid.play();
                } catch (err) {
                    showToast("Camera access required for webcam snapshot.", "info");
                }
            }
            return;
        }

        // Generate Image Button
        if (id === "btn-open-image-gen" || id === "btn-image-gen") {
            e.preventDefault();
            hideAllModals();
            const modalGen = document.getElementById("modal-image-gen");
            if (modalGen) modalGen.classList.remove("hidden");
            return;
        }

        // Voice Recorder Button
        if (id === "btn-record-voice" || id === "btn-voice") {
            e.preventDefault();
            hideAllModals();
            const modalVoice = document.getElementById("modal-voice-recorder");
            if (modalVoice) modalVoice.classList.remove("hidden");
            const voiceTimer = document.getElementById("voice-timer");
            if (voiceTimer) voiceTimer.innerText = "00:00";

            try {
                audioChunks = [];
                voiceSeconds = 0;
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = (ev) => {
                    if (ev.data.size > 0) audioChunks.push(ev.data);
                };
                mediaRecorder.start();

                if (voiceTimerInterval) clearInterval(voiceTimerInterval);
                voiceTimerInterval = setInterval(() => {
                    voiceSeconds++;
                    const mins = String(Math.floor(voiceSeconds / 60)).padStart(2, "0");
                    const secs = String(voiceSeconds % 60).padStart(2, "0");
                    if (voiceTimer) voiceTimer.innerText = `${mins}:${secs}`;
                }, 1000);
            } catch (err) {
                showToast("Microphone access required for voice recording.", "info");
            }
            return;
        }

        // Sign Out / Logout
        if (id === "btn-logout" || id === "dropdown-btn-logout") {
            e.preventDefault();
            triggerLogoutFlow(e);
            return;
        }
    });

    // Backdrop click listener to close modal when clicking outside dialog content panel
    document.querySelectorAll('[id^="modal-"]').forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                hideAllModals();
            }
        });
    });

    // Escape Key Listener to dismiss any open modal
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            hideAllModals();
        }
    });

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
    btnOpenImageGen?.addEventListener("click", () => { hideAllModals(); modalImageGen.classList.remove("hidden"); });

    // Wire Action Bar Buttons (Attach, Camera, Voice, Snapshot, Recorder)
    const btnAttachFileAlt = document.getElementById("btn-attach-file") || document.getElementById("btn-attach");
    const btnOpenCameraAlt = document.getElementById("btn-open-camera") || document.getElementById("btn-camera");
    const btnRecordVoiceAlt = document.getElementById("btn-record-voice") || document.getElementById("btn-voice");
    const btnCaptureSnapshotAlt = document.getElementById("btn-capture-snapshot");
    const btnStopVoiceAlt = document.getElementById("btn-stop-voice");

    if (btnAttachFileAlt) {
        btnAttachFileAlt.addEventListener("click", () => {
            if (fileUploadInput) fileUploadInput.click();
        });
    }

    if (btnOpenCameraAlt) {
        btnOpenCameraAlt.addEventListener("click", async () => {
            hideAllModals();
            if (modalCamera) modalCamera.classList.remove("hidden");
            if (webcamVideo) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    webcamVideo.srcObject = stream;
                    webcamVideo.play();
                } catch (e) {
                    showToast("Camera access required to capture snapshot.", "info");
                }
            }
        });
    }

    if (btnCaptureSnapshotAlt) {
        btnCaptureSnapshotAlt.addEventListener("click", () => {
            if (!webcamVideo || !webcamCanvas) return;
            const context = webcamCanvas.getContext("2d");
            webcamCanvas.width = webcamVideo.videoWidth || 640;
            webcamCanvas.height = webcamVideo.videoHeight || 480;
            context.drawImage(webcamVideo, 0, 0, webcamCanvas.width, webcamCanvas.height);

            webcamCanvas.toBlob(async (blob) => {
                if (!blob) return;
                const snapshotFile = new File([blob], `camera_snapshot_${Date.now()}.png`, { type: "image/png" });
                hideAllModals();
                await uploadFileToApi(snapshotFile);
            }, "image/png");
        });
    }

// Reset voice recording state variables
    audioChunks = [];
    voiceSeconds = 0;

    if (btnRecordVoiceAlt) {
        btnRecordVoiceAlt.addEventListener("click", async () => {
            hideAllModals();
            if (modalVoiceRecorder) modalVoiceRecorder.classList.remove("hidden");
            audioChunks = [];
            voiceSeconds = 0;
            const voiceTimer = document.getElementById("voice-timer");
            if (voiceTimer) voiceTimer.innerText = "00:00";

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = (e) => {
                    if (e.data.size > 0) audioChunks.push(e.data);
                };
                mediaRecorder.start();

                if (voiceTimerInterval) clearInterval(voiceTimerInterval);
                voiceTimerInterval = setInterval(() => {
                    voiceSeconds++;
                    const mins = String(Math.floor(voiceSeconds / 60)).padStart(2, "0");
                    const secs = String(voiceSeconds % 60).padStart(2, "0");
                    if (voiceTimer) voiceTimer.innerText = `${mins}:${secs}`;
                }, 1000);
            } catch (err) {
                showToast("Microphone permission required for voice recording.", "info");
            }
        });
    }

    if (btnStopVoiceAlt) {
        btnStopVoiceAlt.addEventListener("click", () => {
            if (voiceTimerInterval) clearInterval(voiceTimerInterval);
            if (mediaRecorder && mediaRecorder.state !== "inactive") {
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                    const voiceFile = new File([audioBlob], `voice_record_${Date.now()}.webm`, { type: "audio/webm" });
                    hideAllModals();
                    await uploadFileToApi(voiceFile);
                };
                mediaRecorder.stop();
                if (mediaRecorder.stream) {
                    mediaRecorder.stream.getTracks().forEach(t => t.stop());
                }
            } else {
                hideAllModals();
            }
        });
    }

    // AI Text-to-Image Modal Submission
    const formGenerateImage = document.getElementById("form-generate-image");
    const genPromptInput = document.getElementById("gen-prompt-input");

    if (formGenerateImage) {
        formGenerateImage.addEventListener("submit", async (e) => {
            e.preventDefault();
            const prompt = genPromptInput ? genPromptInput.value.trim() : "";
            if (!prompt) return;

            hideAllModals();
            showToast("🎨 Generating AI artwork...", "info");

            if (welcomeHero) welcomeHero.classList.add("hidden");
            renderMessage({ role: "user", content: `Generate image: ${prompt}`, attachments: [], created_at: new Date().toISOString() });

            const typingId = "asst_" + Date.now();
            renderAssistantTyping(typingId, "Image Generator");

            try {
                const res = await authenticatedFetch("/api/v1/image/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt, aspect_ratio: "1:1", quality: "standard" })
                });
                const data = await res.json();
                removeAssistantTyping(typingId);

                if (data.success && data.data && data.data.image_url) {
                    const engineName = (data.data.model_name) || "AetherMind Flux";
                    renderMessage({
                        role: "assistant",
                        content: `Here is your generated image:\n\n![${prompt}](${data.data.image_url})`,
                        model_name: engineName,
                        created_at: new Date().toISOString()
                    });
                    if (genPromptInput) genPromptInput.value = "";
                    showToast("Image generation complete!", "success");
                } else {
                    renderMessage({ role: "assistant", content: `⚠️ Image generation failed: ${data.message || "Unknown error"}` });
                }
            } catch (err) {
                removeAssistantTyping(typingId);
                renderMessage({ role: "assistant", content: "⚠️ Network error while generating image." });
            }
        });
    }

    // Quick Actions Trigger from Hero
    window.triggerQuickAction = (action) => {
        hideAllModals();
        if (action === "dashboard" && openDashboardBtn) {
            openDashboardBtn.click();
        } else if (action === "projects" && openProjectsBtn) {
            openProjectsBtn.click();
        } else if (action === "media" && openMediaBtn) {
            openMediaBtn.click();
        } else if (action === "doclib" && openDocsBtn) {
            openDocsBtn.click();
        } else if (action === "document" || action === "image") {
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

        let fileTextContent = "";
        try {
            fileTextContent = await file.text();
        } catch(e) {}

        try {
            const res = await authenticatedFetch("/api/v1/upload", { method: "POST", body: formData });
            const data = await res.json();
            removePendingChip(tempId);
            if (data.success && data.data) {
                const item = data.data;
                item.filename = file.name || item.filename;
                if ((!item.extracted_text || item.extracted_text.includes("successfully processed")) && fileTextContent) {
                    item.extracted_text = fileTextContent;
                }
                try {
                    localStorage.setItem('aethermind_last_doc_name', item.filename);
                    if (item.extracted_text) localStorage.setItem('aethermind_last_doc_text', item.extracted_text);
                } catch(e) {}

                pendingAttachments.push(item);
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

            const selectedModel = modelSelect ? (modelSelect.value || "gemini-2.5-flash") : "gemini-2.5-flash";
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
                const res = await authenticatedFetch("/api/v1/chat/completions", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt, chat_id: activeChatId, model: selectedModel, attachment_ids: attachmentIds, attachments: currentAtts })
                });
                const data = await res.json();
                removeAssistantTyping(typingId);

                if (data.success && data.data) {
                    activeChatId = data.data.chat_id;
                    localStorage.setItem('aethermind_active_chat', activeChatId);
                    renderMessage({ role: "assistant", content: data.data.content, model_name: selectedModel, created_at: data.data.created_at });
                    loadConversationsHistory();
                } else {
                    renderMessage({ role: "assistant", content: `⚠️ Error: ${data.detail || data.message || "Completion failed"}` });
                }
            } catch (err) {
                removeAssistantTyping(typingId);
                renderMessage({ role: "assistant", content: "⚠️ Network completion error." });
            }
        });
    }

    // Handle Enter to Send / Shift+Enter for New Line
    if (chatInput) {
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (chatForm) chatForm.requestSubmit();
            }
        });
    }

    // Format message content with markdown images & text escaping
    const formatMessageContent = (text) => {
        if (!text) return "";
        let formatted = text.replace(/!\[(.*?)\]\((.*?)\)/g, (match, alt, url) => {
            const safeAlt = escapeHtml(alt || "Generated AI Image");
            const safeUrl = escapeHtml(url);
            return `
                <div class="my-3 rounded-2xl overflow-hidden border border-cyan-500/30 bg-black/60 shadow-2xl max-w-md cursor-pointer group" onclick="openImagePreview('${safeUrl}', '${safeAlt}')">
                    <img src="${safeUrl}" alt="${safeAlt}" class="w-full h-auto max-h-[380px] object-cover group-hover:scale-[1.02] transition-transform duration-300 rounded-t-xl" />
                    <div class="p-3 bg-[#0d121f] text-xs text-cyan-300 font-medium flex items-center justify-between border-t border-cyan-500/20">
                        <span class="truncate font-mono">🎨 ${safeAlt}</span>
                        <span class="text-[10px] text-slate-400 group-hover:text-white shrink-0 ml-2">Click to View ↗</span>
                    </div>
                </div>
            `;
        });

        const parts = formatted.split(/(<div class="my-3 rounded-2xl[\s\S]*?<\/div>)/g);
        return parts.map(part => {
            if (part.startsWith('<div class="my-3 rounded-2xl')) {
                return part;
            }
            return escapeHtml(part);
        }).join("");
    };

    const renderMessage = (msg) => {
        const msgDiv = document.createElement("div");
        const isUser = msg.role === "user";
        msgDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in my-1.5`;

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
            <div class="flex items-start space-x-2.5 max-w-[85%] md:max-w-xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}">
                <div class="w-7 h-7 rounded-xl ${isUser ? 'bg-gradient-to-tr from-cyan-500 to-indigo-600' : 'bg-gradient-to-tr from-indigo-600 to-purple-600'} flex items-center justify-center text-white text-[11px] font-bold shrink-0 shadow-md">
                    ${isUser ? '👤' : 'Æ'}
                </div>
                <div class="inline-block max-w-full">
                    <div class="px-4 py-2.5 rounded-2xl ${isUser ? 'bg-indigo-900/50 border border-indigo-500/40 text-slate-100 rounded-tr-xs shadow-md backdrop-blur-md' : 'bg-[#0b101d]/80 border border-white/12 text-slate-200 rounded-tl-xs shadow-md backdrop-blur-md'} text-sm leading-relaxed whitespace-pre-wrap break-words inline-block text-left">
                        ${attachmentsHtml}
                        <div class="inline-block max-w-full">${formatMessageContent(msg.content)}</div>
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
        div.className = "flex justify-start animate-fade-in my-1.5";
        div.innerHTML = `
            <div class="flex items-start space-x-2.5 max-w-[85%] md:max-w-xl">
                <div class="w-7 h-7 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white text-[11px] font-bold shrink-0 shadow-md">Æ</div>
                <div class="px-4 py-2.5 rounded-2xl bg-[#0b101d]/80 border border-cyan-500/30 text-slate-300 flex items-center space-x-2 text-xs backdrop-blur-md shadow-md rounded-tl-xs">
                    <span class="font-mono text-cyan-400">${model} Qdrant RAG processing</span>
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
                const res = await authenticatedFetch("/api/v1/knowledge/collections", {
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
                const res = await authenticatedFetch("/api/v1/knowledge/ingest", { method: "POST", body: formData });
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
            const res = await authenticatedFetch("/api/v1/knowledge/collections");
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
                const res = await authenticatedFetch("/api/v1/memory", {
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
                const res = await authenticatedFetch(`/api/v1/memory/compress/${activeChatId}`, { method: "POST" });
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
            const res = await authenticatedFetch(url);
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
            await authenticatedFetch(`/api/v1/memory/${memId}`, { method: "DELETE" });
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
                const res = await authenticatedFetch("/api/v1/search", {
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
            const res = await authenticatedFetch("/api/v1/chat/conversations");
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
        localStorage.setItem('aethermind_active_chat', chatId);
        messagesContainer.innerHTML = "";
        try {
            const res = await authenticatedFetch(`/api/v1/chat/conversations/${chatId}`);
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
            await authenticatedFetch(`/api/v1/chat/conversations/${chatId}`, { method: "DELETE" });
            if (activeChatId === chatId) {
                activeChatId = null;
                localStorage.removeItem('aethermind_active_chat');
                messagesContainer.innerHTML = "";
                if (welcomeHero) messagesContainer.classList.remove("hidden");
            }
            loadConversationsHistory();
        } catch (e) {}
    };

    if (btnNewChat) {
        btnNewChat.addEventListener("click", () => {
            activeChatId = null;
            localStorage.removeItem('aethermind_active_chat');
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
            const res = await authenticatedFetch("/api/v1/dashboard/overview");
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
                const res = await authenticatedFetch("/api/v1/projects", {
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
            const res = await authenticatedFetch("/api/v1/projects");
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
            const res = await authenticatedFetch(`/api/v1/projects/${projectId}`, { method: "DELETE" });
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
            const res = await authenticatedFetch(`/api/v1/workspace/media-gallery?category=${cat}`);
            const data = await res.json();
            if (data.success && data.data) {
                renderMediaGallery(data.data);
            }
        } catch (e) {}
    };

    const renderMediaGallery = (items) => {
        mediaGalleryGrid.innerHTML = "";
        if (!items || items.length === 0) {
            mediaGalleryGrid.innerHTML = `
                <div class="col-span-full flex flex-col items-center justify-center py-10 px-6 text-center space-y-5 bg-gradient-to-b from-white/5 via-white/[0.02] to-transparent rounded-3xl border border-white/10 my-auto">
                    <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-[#FF007A] to-[#7928CA] flex items-center justify-center text-white text-3xl shadow-lg shadow-[#FF007A]/30">
                        🖼️
                    </div>
                    <div class="max-w-md space-y-1.5">
                        <h4 class="font-heading text-base font-bold text-white tracking-wide">Media & Image Gallery is Empty</h4>
                        <p class="text-slate-400 text-xs leading-relaxed">
                            Generate AI artwork with Pollinations AI or upload photos from your device to analyze visual content.
                        </p>
                    </div>
                    
                    <div class="flex flex-wrap items-center justify-center gap-3 pt-2">
                        <button type="button" onclick="openModal('modal-image-gen')" class="py-2 px-4 btn-primary font-bold text-xs flex items-center space-x-2">
                            <span>✨ Generate AI Image</span>
                        </button>
                        <label class="py-2 px-4 btn-secondary font-bold text-xs cursor-pointer flex items-center space-x-2">
                            <span>🖼️ Upload Image</span>
                            <input type="file" accept="image/*" class="hidden" onchange="if(this.files.length) uploadFileToApi(this.files[0]).then(()=>loadMediaGallery())">
                        </label>
                    </div>
                </div>
            `;
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
    const loadSampleDocsHandler = async () => {
        showToast("Generating sample architecture specs...", "info");
        const sampleText = `# AetherMind Enterprise AI Architecture Specification
Created by: Kavati John Shreyan

## Overview
AetherMind Multimodal AI OS is an enterprise-grade artificial intelligence operating system featuring real-time document analysis, Qdrant vector retrieval-augmented generation (RAG), voice audio transcription, and high-performance multimodal completion engines.

## Core Systems
1. Multimodal Document Intelligence Engine (PDF, DOCX, CSV, TXT, JSON, MD)
2. Qdrant Hybrid Vector Store & Semantic Embeddings
3. Firebase Authentication & User State Management
4. Adaptive Multi-Device Viewport Engine (Desktop, Laptop, Tablet, Mobile)
`;
        const blob = new Blob([sampleText], { type: "text/markdown" });
        const sampleFile = new File([blob], "AetherMind_Enterprise_AI_Architecture.md", { type: "text/markdown" });
        await uploadFileToApi(sampleFile);
        showToast("Sample specification loaded!", "success");
        loadDocLibrary();
    };

    const loadDocLibrary = async () => {
        if (!docLibraryList) return;
        try {
            const res = await authenticatedFetch("/api/v1/workspace/doc-library");
            const data = await res.json();
            if (data.success && data.data) {
                renderDocLibrary(data.data);
            }
        } catch (e) {}
    };

    const renderDocLibrary = (items) => {
        docLibraryList.innerHTML = "";
        if (!items || items.length === 0) {
            docLibraryList.innerHTML = `
                <div class="flex flex-col items-center justify-center py-10 px-6 text-center space-y-5 bg-gradient-to-b from-white/5 via-white/[0.02] to-transparent rounded-3xl border border-white/10 my-auto">
                    <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-[#00F2FE] to-[#4FACFE] flex items-center justify-center text-slate-950 text-3xl shadow-lg shadow-[#00F2FE]/40">
                        📄
                    </div>
                    <div class="max-w-md space-y-1.5">
                        <h4 class="font-heading text-base font-bold text-white tracking-wide">Document Intelligence Library is Ready</h4>
                        <p class="text-slate-400 text-xs leading-relaxed">
                            Upload PDFs, Word docs, Spreadsheets, or Code files to extract intelligence, run RAG vector search, and chat directly with your files.
                        </p>
                    </div>
                    
                    <div class="flex flex-wrap items-center justify-center gap-3 pt-2">
                        <label class="py-2.5 px-5 btn-cyan font-bold text-xs cursor-pointer flex items-center space-x-2 shadow-lg">
                            <span>⚡ Upload Document</span>
                            <input type="file" accept=".pdf,.docx,.txt,.csv,.json,.md,.pptx" class="hidden" onchange="if(this.files.length) uploadFileToApi(this.files[0]).then(()=>loadDocLibrary())">
                        </label>
                        <button type="button" id="btn-load-sample-docs-hero" class="py-2.5 px-5 btn-secondary font-bold text-xs flex items-center space-x-2">
                            <span>📄 Load Sample Specs</span>
                        </button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 w-full pt-4 border-t border-white/10 text-left">
                        <div class="p-3 rounded-xl bg-white/5 border border-white/10 space-y-1">
                            <div class="font-bold text-cyan-300 flex items-center space-x-1.5"><span>📄</span><span>PDF & DOCX Reader</span></div>
                            <div class="text-[11px] text-slate-400">Deep structural extraction & multi-page document intelligence.</div>
                        </div>
                        <div class="p-3 rounded-xl bg-white/5 border border-white/10 space-y-1">
                            <div class="font-bold text-purple-300 flex items-center space-x-1.5"><span>🔍</span><span>Qdrant RAG Vector DB</span></div>
                            <div class="text-[11px] text-slate-400">Indexed for instant semantic similarity retrieval.</div>
                        </div>
                        <div class="p-3 rounded-xl bg-white/5 border border-white/10 space-y-1">
                            <div class="font-bold text-emerald-300 flex items-center space-x-1.5"><span>💬</span><span>Multimodal Chat OS</span></div>
                            <div class="text-[11px] text-slate-400">Ask any question or type "analyze document" in chat.</div>
                        </div>
                    </div>
                </div>
            `;
            setTimeout(() => {
                const sampleBtn = document.getElementById("btn-load-sample-docs-hero");
                if (sampleBtn) sampleBtn.onclick = loadSampleDocsHandler;
            }, 50);
            return;
        }

        items.forEach(item => {
            const div = document.createElement("div");
            div.className = "p-3.5 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between text-xs hover:border-cyan-500/40 transition shadow-sm";
            div.innerHTML = `
                <div class="flex items-center space-x-3 truncate">
                    <span class="text-cyan-400 text-lg">📄</span>
                    <div>
                        <div class="font-semibold text-white truncate max-w-[240px]">${escapeHtml(item.filename)}</div>
                        <div class="text-[10px] text-slate-400">${item.size_formatted} • ${item.chunk_count ? item.chunk_count + ' indexed chunks' : 'Uploaded document'}</div>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <button type="button" class="px-3 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 font-bold hover:bg-cyan-500/30 border border-cyan-500/30" onclick="openDocumentViewer('${item.id}', '${escapeHtml(item.filename)}')">View</button>
                    <button type="button" class="text-yellow-400 hover:text-yellow-300 p-1 text-sm" onclick="toggleStarFile('${item.id}', event)">${item.is_starred ? '★' : '☆'}</button>
                    <button type="button" class="text-rose-400 hover:text-rose-300 p-1 text-sm" onclick="softDeleteFile('${item.id}', event)">🗑️</button>
                </div>
            `;
            docLibraryList.appendChild(div);
        });
    };

    // E. AUDIO LIBRARY
    const loadAudioLibrary = async () => {
        if (!audioLibraryList) return;
        try {
            const res = await authenticatedFetch("/api/v1/workspace/audio-library");
            const data = await res.json();
            if (data.success && data.data) {
                renderAudioLibrary(data.data);
            }
        } catch (e) {}
    };

    const renderAudioLibrary = (items) => {
        audioLibraryList.innerHTML = "";
        if (!items || items.length === 0) {
            audioLibraryList.innerHTML = `
                <div class="flex flex-col items-center justify-center py-10 px-6 text-center space-y-5 bg-gradient-to-b from-white/5 via-white/[0.02] to-transparent rounded-3xl border border-white/10 my-auto">
                    <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-[#EF4444] to-[#F97316] flex items-center justify-center text-white text-3xl shadow-lg shadow-[#EF4444]/30">
                        🎙️
                    </div>
                    <div class="max-w-md space-y-1.5">
                        <h4 class="font-heading text-base font-bold text-white tracking-wide">Audio & Voice Studio is Empty</h4>
                        <p class="text-slate-400 text-xs leading-relaxed">
                            Record voice memos directly with your microphone or upload audio files for AI transcription.
                        </p>
                    </div>
                    
                    <div class="flex flex-wrap items-center justify-center gap-3 pt-2">
                        <button type="button" id="btn-empty-record-voice" class="py-2.5 px-5 btn-danger font-bold text-xs flex items-center space-x-2">
                            <span>🎙️ Record Voice Note</span>
                        </button>
                        <label class="py-2.5 px-5 btn-secondary font-bold text-xs cursor-pointer flex items-center space-x-2">
                            <span>🎵 Upload Audio File</span>
                            <input type="file" accept="audio/*" class="hidden" onchange="if(this.files.length) uploadFileToApi(this.files[0]).then(()=>loadAudioLibrary())">
                        </label>
                    </div>
                </div>
            `;
            setTimeout(() => {
                const recBtn = document.getElementById("btn-empty-record-voice");
                if (recBtn) recBtn.onclick = () => { if (typeof startVoiceRecording === "function") startVoiceRecording(); };
            }, 50);
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
            const res = await authenticatedFetch("/api/v1/workspace/recycle-bin");
            const data = await res.json();
            if (data.success && data.data) {
                renderRecycleBin(data.data);
            }
        } catch (e) {}
    };

    const renderRecycleBin = (items) => {
        recycleBinList.innerHTML = "";
        if (!items || items.length === 0) {
            recycleBinList.innerHTML = `
                <div class="flex flex-col items-center justify-center py-10 px-6 text-center space-y-4 bg-gradient-to-b from-white/5 to-transparent rounded-3xl border border-white/10 my-auto">
                    <div class="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center text-slate-300 text-2xl">
                        🗑️
                    </div>
                    <div class="space-y-1">
                        <h4 class="font-heading text-base font-bold text-white">Recycle Bin is Empty</h4>
                        <p class="text-slate-400 text-xs">Deleted files will appear here before permanent deletion.</p>
                    </div>
                </div>
            `;
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
                const res = await authenticatedFetch("/api/v1/workspace/recycle-bin/empty", { method: "POST" });
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
            const res = await authenticatedFetch(`/api/v1/workspace/recycle-bin/restore/${fileId}`, { method: "POST" });
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
                const res = await authenticatedFetch("/api/v1/workspace/search", {
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
            const res = await authenticatedFetch(`/api/v1/files/${fileId}/star`, { method: "POST" });
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
            const res = await authenticatedFetch(`/api/v1/files/${fileId}/delete`, { method: "POST" });
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

    // =========================================================================
    // AUTHENTICATION & PROFILE DROPDOWN HANDLERS
    // =========================================================================
    const btnLogout = document.getElementById("btn-logout");
    const dropdownBtnLogout = document.getElementById("dropdown-btn-logout");
    const userProfileBadge = document.getElementById("user-profile-badge");
    const userDropdownMenu = document.getElementById("user-dropdown-menu");
    const modalAuth = document.getElementById("modal-auth");
    const closeAuthBtn = document.getElementById("close-auth-btn");
    const authForm = document.getElementById("auth-form");

    if (userProfileBadge && userDropdownMenu) {
        userProfileBadge.addEventListener("click", (e) => {
            e.stopPropagation();
            userDropdownMenu.classList.toggle("hidden");
        });

        document.addEventListener("click", (e) => {
            if (!userDropdownMenu.contains(e.target) && !userProfileBadge.contains(e.target)) {
                userDropdownMenu.classList.add("hidden");
            }
        });
    }

    async function triggerLogoutFlow(e) {
        if (e && e.preventDefault) e.preventDefault();
        try {
            // Clear session cookies
            document.cookie = "aethermind_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;";
            document.cookie = "aethermind_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;";

            // Reset frontend in-memory state & UI
            activeChatId = null;
            localStorage.removeItem('aethermind_active_chat');
            localStorage.removeItem('aethermind_user_email');
            pendingAttachments = [];
            if (conversationList) conversationList.innerHTML = "";
            if (messagesContainer) messagesContainer.innerHTML = "";

            if (window.firebase && window.firebase.auth) {
                try {
                    await window.firebase.auth().signOut();
                } catch (fbErr) {
                    console.warn("Firebase sign out warning:", fbErr);
                }
            }
            try {
                await authenticatedFetch("/api/v1/auth/logout", { method: "POST" });
            } catch (apiErr) {
                // Ignore if offline/mock
            }
        } catch (err) {
            console.error("Sign out error:", err);
        }

        // Display login page modal on logout
        const modalAuth = document.getElementById("modal-auth");
        const modalLogout = document.getElementById("modal-logout");
        hideAllModals();

        if (modalAuth) {
            modalAuth.classList.remove("hidden");
            showToast("🔒 Signed out. Please sign in to access your workspace.", "info");
        } else if (modalLogout) {
            modalLogout.classList.remove("hidden");
            showToast("🛡️ Signed out. Session securely terminated.", "info");
        } else {
            window.location.href = "/login";
        }
    }

    if (btnLogout) btnLogout.addEventListener("click", triggerLogoutFlow);
    if (dropdownBtnLogout) dropdownBtnLogout.addEventListener("click", triggerLogoutFlow);

    // Logout Modal Action Listeners
    const modalLogoutElem = document.getElementById("modal-logout");
    const closeLogoutModalBtn = document.getElementById("close-logout-modal-btn");
    const btnLogoutReloginModal = document.getElementById("btn-logout-relogin-modal");
    const btnLogoutGuestModal = document.getElementById("btn-logout-guest-modal");

    if (closeLogoutModalBtn) closeLogoutModalBtn.addEventListener("click", hideAllModals);

    if (btnLogoutReloginModal) {
        btnLogoutReloginModal.addEventListener("click", () => {
            hideAllModals();
            if (modalAuth) {
                modalAuth.classList.remove("hidden");
            } else {
                window.location.href = "/login";
            }
        });
    }

    if (btnLogoutGuestModal) {
        btnLogoutGuestModal.addEventListener("click", () => {
            document.cookie = "aethermind_token=token_guest_firebase; path=/; max-age=604800; SameSite=Lax";
            localStorage.setItem("aethermind_user_email", "guest@aethermind.ai");
            showToast("⚡ Resumed as Guest!", "success");
            hideAllModals();
            setTimeout(() => {
                location.reload();
            }, 300);
        });
    }

    // Modal Login Card Listeners
    const btnModalGuestLogin = document.getElementById("btn-modal-guest-login");
    const btnModalOauthGoogle = document.getElementById("btn-modal-oauth-google");

    if (btnModalGuestLogin) {
        btnModalGuestLogin.addEventListener("click", () => {
            document.cookie = "aethermind_token=token_guest_firebase; path=/; max-age=604800; SameSite=Lax";
            localStorage.setItem("aethermind_user_email", "guest@aethermind.ai");
            localStorage.setItem("aethermind_user_name", "Guest User");
            showToast("⚡ Signed in as Guest!", "success");
            hideAllModals();
            setTimeout(() => { location.reload(); }, 300);
        });
    }

    if (btnModalOauthGoogle) {
        btnModalOauthGoogle.addEventListener("click", () => {
            document.cookie = "aethermind_token=token_firebase_google; path=/; max-age=604800; SameSite=Lax";
            localStorage.setItem("aethermind_user_email", "google.user@aethermind.ai");
            localStorage.setItem("aethermind_user_name", "Google User");
            showToast("Signed in with Google Auth!", "success");
            hideAllModals();
            setTimeout(() => { location.reload(); }, 300);
        });
    }

    if (authForm) {
        authForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const emailInput = document.getElementById("auth-email");
            const passwordInput = document.getElementById("auth-password");
            const email = emailInput ? emailInput.value.trim() : "";
            const password = passwordInput ? passwordInput.value : "";

            if (!email) return;

            const userDisplayName = email.split('@')[0] || "User";
            localStorage.setItem("aethermind_user_email", email);
            localStorage.setItem("aethermind_user_name", userDisplayName);
            document.cookie = `aethermind_token=token_user_${Date.now()}; path=/; max-age=604800; SameSite=Lax`;

            try {
                const res = await authenticatedFetch("/api/v1/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (data.success && data.data && data.data.user) {
                    if (data.data.user.email) localStorage.setItem("aethermind_user_email", data.data.user.email);
                    if (data.data.user.full_name) localStorage.setItem("aethermind_user_name", data.data.user.full_name);
                }
            } catch (err) {}

            showToast(`Welcome back, ${userDisplayName}!`, "success");
            
            // Update profile display name
            const userDispName = document.getElementById("user-display-name");
            const userDispRole = document.getElementById("user-display-role");
            if (userDispName) userDispName.textContent = userDisplayName;
            if (userDispRole) userDispRole.textContent = "Authenticated User";

            if (modalAuth) modalAuth.classList.add("hidden");
        });
    }

    // Device Viewport Size Switcher (Desktop, Laptop, Tablet, Phone)
    const btnSizeDesktop = document.getElementById("btn-size-desktop");
    const btnSizeLaptop = document.getElementById("btn-size-laptop");
    const btnSizeTablet = document.getElementById("btn-size-tablet");
    const btnSizePhone = document.getElementById("btn-size-phone");
    const btnSizeHybrid = document.getElementById("btn-size-hybrid");
    const mainCanvas = document.getElementById("main-canvas");

    const setDeviceViewport = (mode) => {
        if (!mainCanvas) return;

        const allButtons = [btnSizeDesktop, btnSizeLaptop, btnSizeTablet, btnSizePhone, btnSizeHybrid];
        allButtons.forEach(btn => {
            if (btn) {
                btn.className = "px-2 py-1 rounded-lg text-slate-400 font-medium text-[11px] hover:text-white hover:bg-white/10 transition flex items-center space-x-1";
            }
        });

        const activeClass = "px-2 py-1 rounded-lg bg-[#3ABEFF]/20 text-[#3ABEFF] border border-[#3ABEFF]/30 font-semibold text-[11px] hover:bg-[#3ABEFF]/30 transition flex items-center space-x-1 shadow-md";

        mainCanvas.style.height = "100%";
        mainCanvas.style.display = "flex";
        mainCanvas.style.flexDirection = "column";
        mainCanvas.style.overflow = "hidden";

        if (mode === "hybrid" || mode === "mix") {
            mainCanvas.style.maxWidth = "480px";
            mainCanvas.style.margin = "0 auto";
            mainCanvas.style.borderRadius = "22px";
            mainCanvas.style.border = "1px solid rgba(109, 93, 246, 0.4)";
            mainCanvas.style.boxShadow = "0 0 45px rgba(109, 93, 246, 0.25)";
            if (btnSizeHybrid) btnSizeHybrid.className = activeClass;
        } else if (mode === "phone") {
            mainCanvas.style.maxWidth = "390px";
            mainCanvas.style.margin = "0 auto";
            mainCanvas.style.borderRadius = "24px";
            mainCanvas.style.border = "1px solid rgba(56, 189, 248, 0.4)";
            mainCanvas.style.boxShadow = "0 0 50px rgba(56, 189, 248, 0.25)";
            if (btnSizePhone) btnSizePhone.className = activeClass;
        } else if (mode === "tablet") {
            mainCanvas.style.maxWidth = "768px";
            mainCanvas.style.margin = "0 auto";
            mainCanvas.style.borderRadius = "20px";
            mainCanvas.style.border = "1px solid rgba(56, 189, 248, 0.3)";
            mainCanvas.style.boxShadow = "0 0 35px rgba(56, 189, 248, 0.2)";
            if (btnSizeTablet) btnSizeTablet.className = activeClass;
        } else if (mode === "laptop") {
            mainCanvas.style.maxWidth = "1280px";
            mainCanvas.style.margin = "0 auto";
            mainCanvas.style.borderRadius = "16px";
            mainCanvas.style.border = "1px solid rgba(255, 255, 255, 0.1)";
            mainCanvas.style.boxShadow = "0 10px 40px rgba(0,0,0,0.5)";
            if (btnSizeLaptop) btnSizeLaptop.className = activeClass;
        } else {
            mainCanvas.style.maxWidth = "100%";
            mainCanvas.style.margin = "0";
            mainCanvas.style.borderRadius = "0px";
            mainCanvas.style.border = "none";
            mainCanvas.style.boxShadow = "none";
            if (btnSizeDesktop) btnSizeDesktop.className = activeClass;
        }

        try { localStorage.setItem("aethermind_device_size", mode); } catch(e) {}
    };

    window.setDeviceViewport = setDeviceViewport;

    btnSizeDesktop?.addEventListener("click", () => setDeviceViewport("desktop"));
    btnSizeLaptop?.addEventListener("click", () => setDeviceViewport("laptop"));
    btnSizeTablet?.addEventListener("click", () => setDeviceViewport("tablet"));
    btnSizePhone?.addEventListener("click", () => setDeviceViewport("phone"));
    btnSizeHybrid?.addEventListener("click", () => setDeviceViewport("hybrid"));

    // Initialize User Session & Sync Auth State
    async function initUserSession() {
        const savedEmail = localStorage.getItem("aethermind_user_email");
        const savedName = localStorage.getItem("aethermind_user_name");
        
        const userDispName = document.getElementById("user-display-name");
        const userDispEmail = document.getElementById("user-display-email");
        if (savedName && userDispName) userDispName.textContent = savedName;
        if (savedEmail && userDispEmail) userDispEmail.textContent = savedEmail;

        const savedDeviceSize = localStorage.getItem("aethermind_device_size") || "desktop";
        setDeviceViewport(savedDeviceSize);

        loadConversationsHistory();

        // Bind Modal Action Bar Listeners
        const btnLoadSampleDocs = document.getElementById("btn-load-sample-docs");
        if (btnLoadSampleDocs) btnLoadSampleDocs.onclick = loadSampleDocsHandler;

        const docLibUploadInput = document.getElementById("doc-lib-upload-input");
        if (docLibUploadInput) {
            docLibUploadInput.onchange = async (e) => {
                if (e.target.files.length) {
                    await uploadFileToApi(e.target.files[0]);
                    loadDocLibrary();
                }
            };
        }

        const mediaUploadInput = document.getElementById("media-upload-input");
        if (mediaUploadInput) {
            mediaUploadInput.onchange = async (e) => {
                if (e.target.files.length) {
                    await uploadFileToApi(e.target.files[0]);
                    loadMediaGallery();
                }
            };
        }

        const audioLibUploadInput = document.getElementById("audio-lib-upload-input");
        if (audioLibUploadInput) {
            audioLibUploadInput.onchange = async (e) => {
                if (e.target.files.length) {
                    await uploadFileToApi(e.target.files[0]);
                    loadAudioLibrary();
                }
            };
        }

        const btnModalRecordVoice = document.getElementById("btn-modal-record-voice");
        if (btnModalRecordVoice) {
            btnModalRecordVoice.onclick = () => {
                if (typeof startVoiceRecording === "function") startVoiceRecording();
            };
        }
    }

    // Initial Load
    initUserSession();
});

