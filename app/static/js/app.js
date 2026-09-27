/* ==========================================================================
   AETHERMIND MULTIMODAL AI — FRONTEND AUTHENTICATION & USER ENGINE
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 AetherMind Multimodal AI Phase 4 Auth Engine Initialized.");

    // Element Selectors
    const modalLogin = document.getElementById("modal-auth-login");
    const modalRegister = document.getElementById("modal-auth-register");
    const modalForgot = document.getElementById("modal-auth-forgot");
    const modalVerify = document.getElementById("modal-verify-email");
    const modalProfile = document.getElementById("modal-profile-settings");

    const openLoginBtn = document.getElementById("open-login-modal-btn");
    const headerLoginBtn = document.getElementById("header-login-btn");
    const headerRegisterBtn = document.getElementById("header-register-btn");
    const logoutBtn = document.getElementById("logout-btn");

    const formLogin = document.getElementById("form-login");
    const formRegister = document.getElementById("form-register");
    const formForgot = document.getElementById("form-forgot");
    const formResetConfirm = document.getElementById("form-reset-confirm");
    const formVerifyEmail = document.getElementById("form-verify-email");
    const formUpdateProfile = document.getElementById("form-update-profile");
    const formUpdatePreferences = document.getElementById("form-update-preferences");

    const loginErrorMsg = document.getElementById("login-error-msg");
    const registerErrorMsg = document.getElementById("register-error-msg");
    const forgotResultMsg = document.getElementById("forgot-result-msg");
    const verifyErrorMsg = document.getElementById("verify-error-msg");
    const resetTokenBox = document.getElementById("reset-token-box");

    // UI User Card & Header Badges
    const headerStatusBadge = document.getElementById("header-status-badge");
    const userAvatar = document.getElementById("user-avatar");
    const userNameDisplay = document.getElementById("user-name-display");
    const userEmailDisplay = document.getElementById("user-email-display");
    const userDetailsCard = document.getElementById("user-details-card");

    const cardAvatarDisplay = document.getElementById("card-avatar-display");
    const cardUserName = document.getElementById("card-user-name");
    const cardUserEmail = document.getElementById("card-user-email");
    const cardUserId = document.getElementById("card-user-id");
    const cardUserProvider = document.getElementById("card-user-provider");
    const cardUserClerkId = document.getElementById("card-user-clerkid");
    const cardUserCreated = document.getElementById("card-user-created");
    const badgeUserRole = document.getElementById("badge-user-role");
    const badgeUserVerified = document.getElementById("badge-user-verified");

    // Toast Notification Utility
    const showToast = (message, type = "info") => {
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
        setTimeout(() => {
            toast.classList.remove("translate-y-2", "opacity-0");
        }, 10);

        setTimeout(() => {
            toast.classList.add("opacity-0", "translate-y-2");
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };

    // Modal Visibility Helpers
    const hideAllModals = () => {
        [modalLogin, modalRegister, modalForgot, modalVerify, modalProfile].forEach(m => m && m.classList.add("hidden"));
    };

    const showModal = (modal) => {
        hideAllModals();
        if (modal) modal.classList.remove("hidden");
    };

    // Close Button Listeners
    document.getElementById("close-login-btn")?.addEventListener("click", hideAllModals);
    document.getElementById("close-register-btn")?.addEventListener("click", hideAllModals);
    document.getElementById("close-forgot-btn")?.addEventListener("click", hideAllModals);
    document.getElementById("close-verify-btn")?.addEventListener("click", hideAllModals);
    document.getElementById("close-profile-modal-btn")?.addEventListener("click", hideAllModals);

    document.getElementById("switch-to-register")?.addEventListener("click", () => showModal(modalRegister));
    document.getElementById("switch-to-login")?.addEventListener("click", () => showModal(modalLogin));
    document.getElementById("link-forgot-pass")?.addEventListener("click", () => showModal(modalForgot));

    if (openLoginBtn) openLoginBtn.addEventListener("click", () => showModal(modalLogin));
    if (headerLoginBtn) headerLoginBtn.addEventListener("click", () => showModal(modalLogin));
    if (headerRegisterBtn) headerRegisterBtn.addEventListener("click", () => showModal(modalRegister));

    // Nav Bar Buttons
    document.getElementById("nav-btn-profile")?.addEventListener("click", () => {
        openProfileModal("profile");
    });
    document.getElementById("nav-btn-settings")?.addEventListener("click", () => {
        openProfileModal("preferences");
    });
    document.getElementById("nav-btn-verify-email")?.addEventListener("click", () => showModal(modalVerify));
    document.getElementById("btn-open-profile-card")?.addEventListener("click", () => openProfileModal("profile"));

    // Profile Modal Tabs Switcher
    const tabBtnProfile = document.getElementById("tab-btn-profile");
    const tabBtnPreferences = document.getElementById("tab-btn-preferences");
    const tabContentProfile = document.getElementById("tab-content-profile");
    const tabContentPreferences = document.getElementById("tab-content-preferences");

    const switchTab = (tab) => {
        if (tab === "profile") {
            tabBtnProfile.className = "text-sm font-bold text-cyan-400 border-b-2 border-cyan-400 pb-1";
            tabBtnPreferences.className = "text-sm font-bold text-slate-400 hover:text-white pb-1";
            tabContentProfile.classList.remove("hidden");
            tabContentPreferences.classList.add("hidden");
        } else {
            tabBtnPreferences.className = "text-sm font-bold text-indigo-400 border-b-2 border-indigo-400 pb-1";
            tabBtnProfile.className = "text-sm font-bold text-slate-400 hover:text-white pb-1";
            tabContentPreferences.classList.remove("hidden");
            tabContentProfile.classList.add("hidden");
        }
    };

    if (tabBtnProfile) tabBtnProfile.addEventListener("click", () => switchTab("profile"));
    if (tabBtnPreferences) tabBtnPreferences.addEventListener("click", () => switchTab("preferences"));

    const openProfileModal = async (tab = "profile") => {
        const token = localStorage.getItem("aethermind_token");
        if (!token) {
            showModal(modalLogin);
            showToast("Please sign in to access your profile", "info");
            return;
        }
        switchTab(tab);
        showModal(modalProfile);
        await loadUserSettings();
    };

    // User State Synchronization UI Handler
    const updateUserUI = (user) => {
        if (user) {
            const displayName = user.full_name || user.email.split("@")[0];
            const firstLetter = displayName.charAt(0).toUpperCase();

            if (userNameDisplay) userNameDisplay.innerText = displayName;
            if (userEmailDisplay) userEmailDisplay.innerText = user.email;
            if (userAvatar) {
                if (user.avatar_url) {
                    userAvatar.innerHTML = `<img src="${user.avatar_url}" class="w-full h-full object-cover rounded-full">`;
                } else {
                    userAvatar.innerText = firstLetter;
                }
            }

            if (headerStatusBadge) {
                headerStatusBadge.innerText = `Authenticated (${user.role.toUpperCase()})`;
                headerStatusBadge.className = "px-3 py-1 rounded-full text-xs font-mono font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30";
            }

            if (openLoginBtn) openLoginBtn.classList.add("hidden");
            if (headerLoginBtn) headerLoginBtn.classList.add("hidden");
            if (headerRegisterBtn) headerRegisterBtn.classList.add("hidden");
            if (logoutBtn) logoutBtn.classList.remove("hidden");

            // Populate Card Details
            if (userDetailsCard) userDetailsCard.classList.remove("hidden");
            if (cardUserName) cardUserName.innerText = displayName;
            if (cardUserEmail) cardUserEmail.innerText = user.email;
            if (cardUserId) cardUserId.innerText = user.id;
            if (cardUserProvider) cardUserProvider.innerText = user.provider_type || "credentials";
            if (cardUserClerkId) cardUserClerkId.innerText = user.clerk_id || "None";
            if (cardUserCreated) cardUserCreated.innerText = user.created_at ? new Date(user.created_at).toLocaleDateString() : "Active";
            if (badgeUserRole) badgeUserRole.innerText = `Role: ${user.role.toUpperCase()}`;
            if (badgeUserVerified) {
                badgeUserVerified.innerText = user.is_verified ? "Verified" : "Unverified";
                badgeUserVerified.className = user.is_verified ?
                    "px-3 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" :
                    "px-3 py-1 rounded-full text-xs font-mono font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30";
            }

            // Populate Profile Modal
            const editName = document.getElementById("edit-full-name");
            const editAvatar = document.getElementById("edit-avatar-url");
            const profileName = document.getElementById("settings-profile-name");
            const profileEmail = document.getElementById("settings-profile-email");
            const avatarImg = document.getElementById("settings-avatar-img");

            if (editName) editName.value = user.full_name || "";
            if (editAvatar) editAvatar.value = user.avatar_url || "";
            if (profileName) profileName.innerText = displayName;
            if (profileEmail) profileEmail.innerText = user.email;
            if (avatarImg) {
                if (user.avatar_url) {
                    avatarImg.innerHTML = `<img src="${user.avatar_url}" class="w-full h-full object-cover rounded-2xl">`;
                } else {
                    avatarImg.innerText = firstLetter;
                }
            }
        } else {
            if (userNameDisplay) userNameDisplay.innerText = "Guest User";
            if (userEmailDisplay) userEmailDisplay.innerText = "Not Logged In";
            if (userAvatar) userAvatar.innerText = "Æ";

            if (headerStatusBadge) {
                headerStatusBadge.innerText = "Anonymous (Guest)";
                headerStatusBadge.className = "px-3 py-1 rounded-full text-xs font-mono font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30";
            }

            if (openLoginBtn) openLoginBtn.classList.remove("hidden");
            if (headerLoginBtn) headerLoginBtn.classList.remove("hidden");
            if (headerRegisterBtn) headerRegisterBtn.classList.remove("hidden");
            if (logoutBtn) logoutBtn.classList.add("hidden");
            if (userDetailsCard) userDetailsCard.classList.add("hidden");
        }
    };

    // Active Session Check API Call
    const checkAuthSession = async () => {
        const token = localStorage.getItem("aethermind_token");
        try {
            const res = await fetch("/api/v1/user/me", {
                headers: token ? { "Authorization": `Bearer ${token}` } : {}
            });
            const data = await res.json();
            if (data.success && data.data) {
                updateUserUI(data.data);
            } else {
                localStorage.removeItem("aethermind_token");
                updateUserUI(null);
            }
        } catch (e) {
            updateUserUI(null);
        }
    };

    // Load User Preferences from API
    const loadUserSettings = async () => {
        const token = localStorage.getItem("aethermind_token");
        if (!token) return;
        try {
            const res = await fetch("/api/v1/user/settings", {
                headers: { "Authorization": `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success && data.data) {
                const pref = data.data;
                if (document.getElementById("pref-theme")) document.getElementById("pref-theme").value = pref.theme || "dark";
                if (document.getElementById("pref-model")) document.getElementById("pref-model").value = pref.default_model || "gemini-2.0-flash";
                if (document.getElementById("pref-voice")) document.getElementById("pref-voice").value = pref.voice_accent || "en-US";
                if (document.getElementById("pref-instructions")) document.getElementById("pref-instructions").value = pref.custom_instructions || "";
            }
        } catch (err) {
            console.error("Error loading settings:", err);
        }
    };

    // Login Form Submit Handler
    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (loginErrorMsg) loginErrorMsg.classList.add("hidden");

            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;
            const remember_me = document.getElementById("login-remember")?.checked || false;

            try {
                const res = await fetch("/api/v1/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password, remember_me })
                });
                const data = await res.json();

                if (data.success && data.data) {
                    localStorage.setItem("aethermind_token", data.data.access_token);
                    await checkAuthSession();
                    hideAllModals();
                    showToast("Signed in successfully!", "success");
                } else {
                    const msg = data.detail || data.message || "Invalid credentials.";
                    if (loginErrorMsg) {
                        loginErrorMsg.innerText = msg;
                        loginErrorMsg.classList.remove("hidden");
                    }
                    showToast(msg, "error");
                }
            } catch (err) {
                showToast("Network error during sign in", "error");
            }
        });
    }

    // Register Form Submit Handler
    if (formRegister) {
        formRegister.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (registerErrorMsg) registerErrorMsg.classList.add("hidden");

            const full_name = document.getElementById("register-fullname").value;
            const email = document.getElementById("register-email").value;
            const password = document.getElementById("register-password").value;

            try {
                const res = await fetch("/api/v1/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ full_name, email, password })
                });
                const data = await res.json();

                if (data.success && data.data) {
                    localStorage.setItem("aethermind_token", data.data.access_token);
                    await checkAuthSession();
                    hideAllModals();
                    showToast("Account created successfully!", "success");
                } else {
                    const msg = data.detail || data.message || "Registration failed.";
                    if (registerErrorMsg) {
                        registerErrorMsg.innerText = msg;
                        registerErrorMsg.classList.remove("hidden");
                    }
                    showToast(msg, "error");
                }
            } catch (err) {
                showToast("Network error during registration", "error");
            }
        });
    }

    // Clerk Auth & Social OAuth Button Handlers
    const handleOAuth = async (provider) => {
        try {
            let endpoint = `/api/v1/auth/oauth/${provider}`;
            let payload = {
                provider,
                id_token: `mock_${provider}_id_token_${Date.now()}`,
                email: `${provider}_user@aethermind.ai`,
                full_name: `${provider.toUpperCase()} Enterprise User`,
                avatar_url: `https://api.dicebear.com/7.x/avataaars/svg?seed=${provider}_user`
            };

            if (provider === "clerk") {
                endpoint = "/api/v1/auth/clerk";
                payload = {
                    token: `clerk_mock_token_${Date.now()}`,
                    email: "clerk_user@aethermind.ai",
                    full_name: "Clerk Enterprise User",
                    avatar_url: "https://api.dicebear.com/7.x/avataaars/svg?seed=clerk"
                };
            }

            const res = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (data.success && data.data) {
                localStorage.setItem("aethermind_token", data.data.access_token);
                await checkAuthSession();
                hideAllModals();
                showToast(`Authenticated via ${provider.toUpperCase()}`, "success");
            } else {
                showToast(`Failed to authenticate via ${provider}`, "error");
            }
        } catch (err) {
            showToast(`OAuth error: ${err}`, "error");
        }
    };

    document.getElementById("btn-oauth-google")?.addEventListener("click", () => handleOAuth("google"));
    document.getElementById("btn-oauth-github")?.addEventListener("click", () => handleOAuth("github"));
    document.getElementById("btn-oauth-microsoft")?.addEventListener("click", () => handleOAuth("microsoft"));
    document.getElementById("btn-oauth-clerk")?.addEventListener("click", () => handleOAuth("clerk"));

    document.getElementById("btn-quick-clerk")?.addEventListener("click", () => handleOAuth("clerk"));
    document.getElementById("btn-quick-google")?.addEventListener("click", () => handleOAuth("google"));
    document.getElementById("btn-quick-github")?.addEventListener("click", () => handleOAuth("github"));
    document.getElementById("btn-quick-ms")?.addEventListener("click", () => handleOAuth("microsoft"));

    // Forgot Password Request Handler
    if (formForgot) {
        formForgot.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("forgot-email").value;
            try {
                const res = await fetch("/api/v1/auth/forgot-password", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email })
                });
                const data = await res.json();
                if (data.success && data.data) {
                    if (forgotResultMsg) {
                        forgotResultMsg.className = "text-xs p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300";
                        forgotResultMsg.innerText = `Reset instructions generated. Token: ${data.data.reset_token || 'Dispatched'}`;
                        forgotResultMsg.classList.remove("hidden");
                    }
                    if (resetTokenBox) resetTokenBox.classList.remove("hidden");
                    showToast("Password reset token generated", "info");
                }
            } catch (err) {
                showToast("Error requesting reset link", "error");
            }
        });
    }

    // Reset Password Confirm Handler
    if (formResetConfirm) {
        formResetConfirm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const token = document.getElementById("reset-token-input").value;
            const new_password = document.getElementById("reset-new-password").value;

            try {
                const res = await fetch("/api/v1/auth/reset-password", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token, new_password })
                });
                const data = await res.json();
                if (data.success) {
                    showToast("Password updated successfully. Please login.", "success");
                    showModal(modalLogin);
                } else {
                    showToast(data.detail || "Reset failed", "error");
                }
            } catch (err) {
                showToast("Error executing password reset", "error");
            }
        });
    }

    // Verify Email Form Handler
    if (formVerifyEmail) {
        formVerifyEmail.addEventListener("submit", async (e) => {
            e.preventDefault();
            const token = document.getElementById("verify-token-input").value;
            try {
                const res = await fetch("/api/v1/auth/verify-email", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token })
                });
                const data = await res.json();
                if (data.success) {
                    showToast("Email verified successfully!", "success");
                    hideAllModals();
                    await checkAuthSession();
                } else {
                    if (verifyErrorMsg) {
                        verifyErrorMsg.innerText = data.detail || "Invalid verification token";
                        verifyErrorMsg.classList.remove("hidden");
                    }
                }
            } catch (err) {
                showToast("Verification request failed", "error");
            }
        });
    }

    // Profile Update Handler
    if (formUpdateProfile) {
        formUpdateProfile.addEventListener("submit", async (e) => {
            e.preventDefault();
            const token = localStorage.getItem("aethermind_token");
            const full_name = document.getElementById("edit-full-name").value;
            const avatar_url = document.getElementById("edit-avatar-url").value;

            try {
                const res = await fetch("/api/v1/user/me", {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({ full_name, avatar_url })
                });
                const data = await res.json();
                if (data.success && data.data) {
                    updateUserUI(data.data);
                    showToast("Profile updated successfully", "success");
                    hideAllModals();
                }
            } catch (err) {
                showToast("Failed to update profile", "error");
            }
        });
    }

    // User Preferences Update Handler
    if (formUpdatePreferences) {
        formUpdatePreferences.addEventListener("submit", async (e) => {
            e.preventDefault();
            const token = localStorage.getItem("aethermind_token");
            const theme = document.getElementById("pref-theme").value;
            const default_model = document.getElementById("pref-model").value;
            const voice_accent = document.getElementById("pref-voice").value;
            const custom_instructions = document.getElementById("pref-instructions").value;

            try {
                const res = await fetch("/api/v1/user/settings", {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify({ theme, default_model, voice_accent, custom_instructions })
                });
                const data = await res.json();
                if (data.success) {
                    showToast("User settings & preferences updated", "success");
                    hideAllModals();
                }
            } catch (err) {
                showToast("Failed to update settings", "error");
            }
        });
    }

    // Logout Handler
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
            const token = localStorage.getItem("aethermind_token");
            try {
                await fetch("/api/v1/auth/logout", {
                    method: "POST",
                    headers: token ? { "Authorization": `Bearer ${token}` } : {}
                });
            } catch (e) {}

            localStorage.removeItem("aethermind_token");
            updateUserUI(null);
            showToast("Logged out successfully. Session destroyed.", "info");
        });
    }

    // Sidebar Collapse Toggle
    const sidebar = document.getElementById("sidebar");
    const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("w-72");
            sidebar.classList.toggle("w-20");
        });
    }

    // Perform initial session check on page load
    checkAuthSession();
});
