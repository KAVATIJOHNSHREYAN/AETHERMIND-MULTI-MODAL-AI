/* ==========================================================================
   AETHERMIND MULTIMODAL AI — INTERACTIVE FRONTEND APPLICATION CONTROLLER
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 AetherMind Multimodal AI UI Engine Initialized.");

    // Element Selectors
    const sidebar = document.getElementById("sidebar");
    const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    const modalSettings = document.getElementById("modal-settings");
    const openSettingsBtn = document.getElementById("open-settings-btn");
    const closeSettingsBtn = document.getElementById("close-settings-btn");
    const modalVoice = document.getElementById("modal-voice");
    const openVoiceBtn = document.getElementById("open-voice-btn");
    const closeVoiceBtn = document.getElementById("close-voice-btn");
    const modalImageViewer = document.getElementById("modal-image-viewer");
    const closeImageViewerBtn = document.getElementById("close-image-viewer-btn");
    const fileUploadOverlay = document.getElementById("file-upload-overlay");

    // Sidebar Toggle
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
            sidebar.classList.toggle("-translate-x-full");
        });
    }

    // Theme Switcher (Dark / Light)
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = document.body.getAttribute("data-theme") || "dark";
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            document.body.setAttribute("data-theme", newTheme);
            themeToggleBtn.innerText = newTheme === "dark" ? "🌙 Dark" : "☀️ Light";
        });
    }

    // Settings Modal
    if (openSettingsBtn && modalSettings) {
        openSettingsBtn.addEventListener("click", () => modalSettings.classList.remove("hidden"));
    }
    if (closeSettingsBtn && modalSettings) {
        closeSettingsBtn.addEventListener("click", () => modalSettings.classList.add("hidden"));
    }

    // Voice Modal
    if (openVoiceBtn && modalVoice) {
        openVoiceBtn.addEventListener("click", () => modalVoice.classList.remove("hidden"));
    }
    if (closeVoiceBtn && modalVoice) {
        closeVoiceBtn.addEventListener("click", () => modalVoice.classList.add("hidden"));
    }

    // Image Viewer Modal
    if (closeImageViewerBtn && modalImageViewer) {
        closeImageViewerBtn.addEventListener("click", () => modalImageViewer.classList.add("hidden"));
    }

    // Settings Modal Tab Switcher
    const settingTabs = document.querySelectorAll(".settings-tab");
    const settingPanes = document.querySelectorAll(".settings-pane");

    settingTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            settingTabs.forEach(t => t.classList.remove("active", "border-cyan-500", "text-cyan-400"));
            settingPanes.forEach(p => p.classList.add("hidden"));

            tab.classList.add("active", "border-cyan-500", "text-cyan-400");
            const paneId = tab.getAttribute("data-tab");
            const targetPane = document.getElementById(`pane-${paneId}`);
            if (targetPane) targetPane.classList.remove("hidden");
        });
    });

    // Auto-expanding textarea input
    const promptInput = document.getElementById("prompt-input");
    if (promptInput) {
        promptInput.addEventListener("input", function() {
            this.style.height = "auto";
            this.style.height = (this.scrollHeight > 180 ? 180 : this.scrollHeight) + "px";
        });
    }
});
