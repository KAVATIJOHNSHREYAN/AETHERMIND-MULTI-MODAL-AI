/**
 * AETHERMIND MULTIMODAL AI — OFFICIAL FIREBASE AUTHENTICATION ENGINE
 * Firebase Auth SDK v10 Integration (Email/Password, Google OAuth with Popup & Redirect Fallback)
 */

document.addEventListener("DOMContentLoaded", async () => {
    // Views
    const views = {
        splash: document.getElementById("view-splash"),
        login: document.getElementById("view-login"),
        register: document.getElementById("view-register"),
        forgot: document.getElementById("view-forgot-password"),
        otp: document.getElementById("view-otp-2fa"),
        loading: document.getElementById("view-loading-screen"),
        logout: document.getElementById("view-logout"),
    };

    function showView(targetKey) {
        Object.keys(views).forEach(key => {
            if (views[key]) {
                if (key === targetKey) {
                    views[key].classList.remove("hidden");
                } else {
                    views[key].classList.add("hidden");
                }
            }
        });
    }

    function showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        if (!container) return;
        const toast = document.createElement("div");
        toast.className = `p-3.5 rounded-xl text-xs font-semibold shadow-xl border backdrop-blur-md flex items-center space-x-2 transition-all duration-300 transform translate-y-2 opacity-0 ${
            type === "error" ? "bg-red-500/20 border-red-500/40 text-red-300" :
            type === "success" ? "bg-[#22C55E]/20 border-[#22C55E]/40 text-emerald-300" :
            "bg-[#3ABEFF]/20 border-[#3ABEFF]/40 text-cyan-300"
        }`;
        toast.innerHTML = `<span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => { toast.classList.remove("translate-y-2", "opacity-0"); }, 50);
        setTimeout(() => {
            toast.classList.add("opacity-0", "-translate-y-2");
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // 1. Initialize Firebase App, Auth & GoogleAuthProvider
    const firebaseConfig = {
        apiKey: "AIzaSyCdemmCjPLZpOjyi9kahAE19TmKmkpFABs",
        authDomain: "aethermind-multi-modal-ai.firebaseapp.com",
        projectId: "aethermind-multi-modal-ai",
        storageBucket: "aethermind-multi-modal-ai.firebasestorage.app",
        messagingSenderId: "471859893946",
        appId: "1:471859893946:web:561069de250f2606ec9483",
        measurementId: "G-BWG2NJMMFK"
    };

    let firebaseAuth = null;
    let googleAuthProvider = null;

    if (window.firebase) {
        try {
            if (!window.firebase.apps.length) {
                window.firebase.initializeApp(firebaseConfig);
            }
            firebaseAuth = window.firebase.auth();
            googleAuthProvider = new window.firebase.auth.GoogleAuthProvider();
            googleAuthProvider.addScope("email");
            googleAuthProvider.addScope("profile");
        } catch (e) {
            console.error("Firebase Auth init error:", e);
        }
    }

    // Splash Screen Auto-Transition
    const splashProgress = document.getElementById("splash-progress");
    const splashStatus = document.getElementById("splash-status-text");

    const urlParams = new URLSearchParams(window.location.search);
    const isLogoutPage = window.location.pathname.includes("/logout") || urlParams.get("view") === "logout";

    if (isLogoutPage) {
        // Enforce session revocation on logout
        document.cookie = "aethermind_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;";
        document.cookie = "aethermind_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;";
        localStorage.removeItem("aethermind_active_chat");
        localStorage.removeItem("aethermind_user_email");
        localStorage.removeItem("aethermind_user_name");
        if (firebaseAuth) {
            firebaseAuth.signOut().catch(() => {});
        }
    }

    if (splashProgress) {
        splashProgress.style.width = "50%";
        setTimeout(() => {
            splashProgress.style.width = "100%";
            if (splashStatus) {
                splashStatus.textContent = isLogoutPage ? "Session Revocation Complete" : "Firebase Authentication Engine Ready";
            }
        }, 300);
    }

    // Check Firebase Auth Redirect Result (for signInWithRedirect)
    if (firebaseAuth && !isLogoutPage) {
        firebaseAuth.getRedirectResult().then(async (result) => {
            if (result && result.user) {
                const token = await result.user.getIdToken();
                document.cookie = `aethermind_token=${token}; path=/; max-age=604800; SameSite=Lax`;
                localStorage.setItem("aethermind_user_email", result.user.email || "");
                localStorage.setItem("aethermind_user_name", result.user.displayName || (result.user.email ? result.user.email.split('@')[0] : "Google User"));
                showToast("Firebase Google Sign-In Successful!", "success");
                runWorkspaceLoadingSequence();
            }
        }).catch((error) => {
            console.error("Firebase redirect result error:", error);
            const loginErrorBox = document.getElementById("login-error-box");
            if (loginErrorBox) {
                loginErrorBox.textContent = `Firebase Auth Error: ${error.message || "Google Sign-In failed."}`;
                loginErrorBox.classList.remove("hidden");
            }
            showToast(error.message || "Google Sign-In failed", "error");
        });

        // Auth state listener
        firebaseAuth.onAuthStateChanged(async (user) => {
            if (user) {
                try {
                    const token = await user.getIdToken();
                    document.cookie = `aethermind_token=${token}; path=/; max-age=604800; SameSite=Lax`;
                    localStorage.setItem("aethermind_user_email", user.email || "");
                    localStorage.setItem("aethermind_user_name", user.displayName || (user.email ? user.email.split('@')[0] : "Authenticated User"));
                } catch (err) {
                    console.error("Error setting Firebase ID token:", err);
                }
            }
        });
    }

    setTimeout(() => {
        showView(isLogoutPage ? "logout" : "login");
    }, 500);

    // 2. Navigation Triggers
    document.getElementById("btn-goto-register")?.addEventListener("click", () => showView("register"));
    document.getElementById("btn-goto-login")?.addEventListener("click", () => showView("login"));
    document.getElementById("btn-goto-forgot")?.addEventListener("click", () => showView("forgot"));
    document.getElementById("btn-forgot-back")?.addEventListener("click", () => showView("login"));
    document.getElementById("btn-logout-relogin")?.addEventListener("click", () => showView("login"));
    document.getElementById("btn-logout-register")?.addEventListener("click", () => showView("register"));

    // Password Visibility Toggle
    const togglePassBtn = document.getElementById("toggle-login-password");
    const loginPassInput = document.getElementById("login-password");
    if (togglePassBtn && loginPassInput) {
        togglePassBtn.addEventListener("click", () => {
            const isPass = loginPassInput.type === "password";
            loginPassInput.type = isPass ? "text" : "password";
            togglePassBtn.textContent = isPass ? "Hide" : "Show";
        });
    }

    // Official Firebase Google Authentication Handler
    const btnOauthGoogle = document.getElementById("btn-oauth-google");

    async function handleGoogleSignIn() {
        const loginErrorBox = document.getElementById("login-error-box");
        if (loginErrorBox) loginErrorBox.classList.add("hidden");

        if (!firebaseAuth) {
            const errMsg = "Firebase Authentication SDK failed to initialize.";
            showToast(errMsg, "error");
            if (loginErrorBox) {
                loginErrorBox.textContent = `Firebase Auth Error: ${errMsg}`;
                loginErrorBox.classList.remove("hidden");
            }
            return;
        }

        showToast("Connecting to Google via Firebase Auth...", "info");

        try {
            const provider = googleAuthProvider || new window.firebase.auth.GoogleAuthProvider();
            // Step 1: Call official Firebase signInWithPopup
            const result = await firebaseAuth.signInWithPopup(provider);
            if (result && result.user) {
                const token = await result.user.getIdToken();
                document.cookie = `aethermind_token=${token}; path=/; max-age=604800; SameSite=Lax`;
                localStorage.setItem("aethermind_user_email", result.user.email || "");
                localStorage.setItem("aethermind_user_name", result.user.displayName || (result.user.email ? result.user.email.split('@')[0] : "Google User"));
                showToast("Firebase Google Sign-In Successful!", "success");
                runWorkspaceLoadingSequence();
            } else {
                throw new Error("No user returned from Firebase Google Sign-In.");
            }
        } catch (popupErr) {
            console.warn("signInWithPopup warning or popup blocked, attempting signInWithRedirect fallback:", popupErr);
            // Step 2: Automatic fallback to signInWithRedirect if popup is blocked, closed, or unsupported
            if (
                popupErr.code === 'auth/popup-blocked' ||
                popupErr.code === 'auth/popup-closed-by-user' ||
                popupErr.code === 'auth/operation-not-supported-in-this-environment' ||
                popupErr.code === 'auth/cancelled-popup-request'
            ) {
                try {
                    const provider = googleAuthProvider || new window.firebase.auth.GoogleAuthProvider();
                    await firebaseAuth.signInWithRedirect(provider);
                    return; // Browser will redirect to Google authentication
                } catch (redirectErr) {
                    console.error("Firebase signInWithRedirect error:", redirectErr);
                    const errMsg = redirectErr.message || "Google Authentication failed.";
                    if (loginErrorBox) {
                        loginErrorBox.textContent = `Firebase Auth Error: ${errMsg}`;
                        loginErrorBox.classList.remove("hidden");
                    }
                    showToast(errMsg, "error");
                }
            } else {
                console.error("Firebase Google Auth Error:", popupErr);
                const errMsg = popupErr.message || "Google Authentication failed.";
                if (loginErrorBox) {
                    loginErrorBox.textContent = `Firebase Auth Error: ${errMsg}`;
                    loginErrorBox.classList.remove("hidden");
                }
                showToast(errMsg, "error");
            }
            // CRITICAL REQUIREMENT: Stay on login page if authentication fails. NEVER navigate manually!
        }
    }

    btnOauthGoogle?.addEventListener("click", handleGoogleSignIn);

    // 3. Official Firebase Email & Password Sign In
    const formLogin = document.getElementById("form-login");
    const loginErrorBox = document.getElementById("login-error-box");
    const btnLoginSubmit = document.getElementById("btn-login-submit");

    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email")?.value.trim();
            const password = document.getElementById("login-password")?.value;

            if (!email || !password) return;
            if (loginErrorBox) loginErrorBox.classList.add("hidden");
            if (btnLoginSubmit) {
                btnLoginSubmit.disabled = true;
                btnLoginSubmit.textContent = "Authenticating with Firebase...";
            }

            try {
                if (!firebaseAuth) {
                    throw new Error("Firebase Authentication SDK not initialized.");
                }
                const userCred = await firebaseAuth.signInWithEmailAndPassword(email, password);
                if (userCred && userCred.user) {
                    const token = await userCred.user.getIdToken();
                    document.cookie = `aethermind_token=${token}; path=/; max-age=604800; SameSite=Lax`;
                    localStorage.setItem("aethermind_user_email", userCred.user.email || email);
                    localStorage.setItem("aethermind_user_name", userCred.user.displayName || email.split('@')[0]);
                    showToast("Firebase Authentication Successful!", "success");
                    runWorkspaceLoadingSequence();
                } else {
                    throw new Error("Invalid response from Firebase Authentication.");
                }
            } catch (err) {
                console.error("Firebase Login Error:", err);
                const errorMsg = err.message || "Invalid email or password.";
                if (loginErrorBox) {
                    loginErrorBox.textContent = `Firebase Auth Error: ${errorMsg}`;
                    loginErrorBox.classList.remove("hidden");
                }
                showToast(errorMsg, "error");
            } finally {
                if (btnLoginSubmit) {
                    btnLoginSubmit.disabled = false;
                    btnLoginSubmit.textContent = "Sign In with Firebase";
                }
            }
        });
    }

    // 4. Official Firebase Email Registration Execution
    const formRegister = document.getElementById("form-register");
    const regErrorBox = document.getElementById("register-error-box");
    const regPassInput = document.getElementById("reg-password");
    const passStrengthBar = document.getElementById("pass-strength-bar");
    const passStrengthLabel = document.getElementById("pass-strength-label");

    if (regPassInput) {
        regPassInput.addEventListener("input", () => {
            const val = regPassInput.value;
            let score = 0;
            if (val.length >= 8) score++;
            if (/[A-Z]/.test(val)) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;

            if (score <= 1) {
                passStrengthBar.className = "bg-red-500 h-full w-1/4 transition-all duration-300";
                passStrengthLabel.textContent = "Weak";
                passStrengthLabel.className = "font-bold text-red-400";
            } else if (score <= 3) {
                passStrengthBar.className = "bg-yellow-500 h-full w-2/4 transition-all duration-300";
                passStrengthLabel.textContent = "Medium";
                passStrengthLabel.className = "font-bold text-yellow-400";
            } else {
                passStrengthBar.className = "bg-emerald-500 h-full w-full transition-all duration-300";
                passStrengthLabel.textContent = "Strong";
                passStrengthLabel.className = "font-bold text-emerald-400";
            }
        });
    }

    if (formRegister) {
        formRegister.addEventListener("submit", async (e) => {
            e.preventDefault();
            const firstName = document.getElementById("reg-fname")?.value.trim();
            const lastName = document.getElementById("reg-lname")?.value.trim();
            const email = document.getElementById("reg-email")?.value.trim();
            const password = regPassInput?.value;
            const confirmPass = document.getElementById("reg-password-confirm")?.value;

            if (password !== confirmPass) {
                if (regErrorBox) {
                    regErrorBox.textContent = "Passwords do not match.";
                    regErrorBox.classList.remove("hidden");
                }
                return;
            }

            if (regErrorBox) regErrorBox.classList.add("hidden");

            try {
                if (!firebaseAuth) {
                    throw new Error("Firebase Authentication SDK not initialized.");
                }
                const userCred = await firebaseAuth.createUserWithEmailAndPassword(email, password);
                if (userCred && userCred.user) {
                    await userCred.user.updateProfile({
                        displayName: `${firstName} ${lastName}`.trim()
                    });
                    showToast("Firebase Account Created! Redirecting to sign in...", "success");
                    showView("login");
                }
            } catch (err) {
                console.error("Firebase Registration Error:", err);
                const errorMsg = err.message || "Registration failed.";
                if (regErrorBox) {
                    regErrorBox.textContent = `Firebase Auth Error: ${errorMsg}`;
                    regErrorBox.classList.remove("hidden");
                }
                showToast(errorMsg, "error");
            }
        });
    }

    // 5. Password Reset Handler
    const formForgot = document.getElementById("form-forgot");
    const forgotErrorBox = document.getElementById("forgot-error-box");
    const btnForgotSubmit = document.getElementById("btn-forgot-submit");

    if (formForgot) {
        formForgot.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("forgot-email")?.value.trim();
            if (!email) return;

            if (forgotErrorBox) forgotErrorBox.classList.add("hidden");
            if (btnForgotSubmit) {
                btnForgotSubmit.disabled = true;
                btnForgotSubmit.textContent = "Sending Reset Email...";
            }

            try {
                if (!firebaseAuth) {
                    throw new Error("Firebase Authentication SDK not initialized.");
                }
                await firebaseAuth.sendPasswordResetEmail(email);
                showToast("Password reset email sent via Firebase! Check your inbox.", "success");
                showView("login");
            } catch (err) {
                console.error("Password reset error:", err);
                const errorMsg = err.message || "Unable to send password reset email.";
                if (forgotErrorBox) {
                    forgotErrorBox.textContent = `Firebase Auth Error: ${errorMsg}`;
                    forgotErrorBox.classList.remove("hidden");
                }
                showToast(errorMsg, "error");
            } finally {
                if (btnForgotSubmit) {
                    btnForgotSubmit.disabled = false;
                    btnForgotSubmit.textContent = "Send Reset Link";
                }
            }
        });
    }

    // 6. Workspace Loading Sequence (Only Executed Post-Authentication)
    function runWorkspaceLoadingSequence() {
        showView("loading");
        const bar = document.getElementById("workspace-load-bar");
        const statusText = document.getElementById("loading-stage-text");

        const stages = [
            { text: "Verifying Firebase Authentication Token...", progress: "25%" },
            { text: "Loading Multimodal AI Engine & Models...", progress: "55%" },
            { text: "Connecting to Qdrant Memory Pipeline...", progress: "80%" },
            { text: "Launching Workspace...", progress: "100%" },
        ];

        let index = 0;
        const interval = setInterval(() => {
            if (index < stages.length) {
                if (statusText) statusText.textContent = stages[index].text;
                if (bar) bar.style.width = stages[index].progress;
                index++;
            } else {
                clearInterval(interval);
                setTimeout(() => {
                    window.location.href = "/";
                }, 400);
            }
        }, 350);
    }
});
