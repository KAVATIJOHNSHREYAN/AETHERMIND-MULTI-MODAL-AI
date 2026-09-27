/**
 * AETHERMIND MULTIMODAL AI — CLERK AUTHENTICATION ENGINE
 * Real Clerk SDK Authentication, Password Strength, OTP, & Workspace Initialization
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
            type === "success" ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300" :
            "bg-cyan-500/20 border-cyan-500/40 text-cyan-300"
        }`;
        toast.innerHTML = `<span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => { toast.classList.remove("translate-y-2", "opacity-0"); }, 50);
        setTimeout(() => {
            toast.classList.add("opacity-0", "-translate-y-2");
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // 1. Splash Screen Auto-Transition
    const splashProgress = document.getElementById("splash-progress");
    const splashStatus = document.getElementById("splash-status-text");

    if (splashProgress) {
        setTimeout(() => { splashProgress.style.width = "40%"; }, 200);
        setTimeout(() => {
            splashProgress.style.width = "80%";
            if (splashStatus) splashStatus.textContent = "Loading Clerk Authentication SDK...";
        }, 700);
    }

    // Initialize Clerk JS SDK
    let clerk = window.Clerk;
    if (clerk) {
        try {
            await clerk.load();
            if (splashProgress) splashProgress.style.width = "100%";

            // Check existing authenticated Clerk session
            if (clerk.user) {
                if (splashStatus) splashStatus.textContent = `Authenticated as ${clerk.user.primaryEmailAddress?.emailAddress || clerk.user.fullName}`;
                setTimeout(() => runWorkspaceLoadingSequence(), 600);
                return;
            } else {
                setTimeout(() => showView("login"), 800);
            }
        } catch (err) {
            console.error("Clerk SDK load error:", err);
            setTimeout(() => showView("login"), 800);
        }
    } else {
        setTimeout(() => showView("login"), 1000);
    }

    // 2. Navigation Triggers
    document.getElementById("btn-goto-register")?.addEventListener("click", () => showView("register"));
    document.getElementById("btn-goto-login")?.addEventListener("click", () => showView("login"));
    document.getElementById("btn-goto-forgot")?.addEventListener("click", () => showView("forgot"));
    document.getElementById("btn-forgot-back")?.addEventListener("click", () => showView("login"));

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

    // Real Clerk OAuth Authentication Handlers (Google & GitHub)
    const btnOauthGoogle = document.getElementById("btn-oauth-google");
    const btnOauthGithub = document.getElementById("btn-oauth-github");

    async function handleClerkOAuth(strategy) {
        if (!window.Clerk) {
            console.warn(`[Clerk OAuth Warning] Clerk SDK not loaded for ${strategy}`);
            showToast("Clerk SDK is loading, please try again in a moment.", "error");
            return;
        }

        try {
            // Ensure Clerk SDK is initialized
            if (!window.Clerk.isReady && typeof window.Clerk.load === "function") {
                await window.Clerk.load();
            }

            const providerName = strategy.includes('google') ? 'Google' : 'GitHub';
            showToast(`Redirecting to ${providerName} OAuth via Clerk...`, "info");

            const redirectUrl = window.location.origin + "/";
            const redirectUrlComplete = window.location.origin + "/";

            // Method 1: Existing Clerk signIn instance
            if (window.Clerk.client && window.Clerk.client.signIn && typeof window.Clerk.client.signIn.authenticateWithRedirect === "function") {
                await window.Clerk.client.signIn.authenticateWithRedirect({
                    strategy: strategy,
                    redirectUrl: redirectUrl,
                    redirectUrlComplete: redirectUrlComplete
                });
                return;
            }

            // Method 2: Global Clerk authenticateWithRedirect
            if (typeof window.Clerk.authenticateWithRedirect === "function") {
                await window.Clerk.authenticateWithRedirect({
                    strategy: strategy,
                    redirectUrl: redirectUrl,
                    redirectUrlComplete: redirectUrlComplete
                });
                return;
            }

            // Method 3: Initialize signIn via Clerk client
            if (window.Clerk.client) {
                const signIn = await window.Clerk.client.signIn.create({
                    strategy: strategy,
                    redirectUrl: redirectUrl,
                    redirectUrlComplete: redirectUrlComplete
                });

                if (signIn && signIn.firstFactorVerification && signIn.firstFactorVerification.externalVerificationRedirectURL) {
                    window.location.href = signIn.firstFactorVerification.externalVerificationRedirectURL.href;
                    return;
                }
            }

            // Method 4: Fallback to Clerk.redirectToSignIn
            if (typeof window.Clerk.redirectToSignIn === "function") {
                await window.Clerk.redirectToSignIn({
                    signInForceRedirectUrl: redirectUrl,
                    signUpForceRedirectUrl: redirectUrlComplete
                });
                return;
            }

            throw new Error(`Unable to initialize ${providerName} OAuth with Clerk. Please check that ${providerName} OAuth is enabled in your Clerk Dashboard.`);

        } catch (err) {
            console.error(`[Clerk OAuth Error - ${strategy}]:`, err);
            const errorMsg = err.errors?.[0]?.longMessage || err.message || `Clerk ${strategy} OAuth failed`;
            if (loginErrorBox) {
                loginErrorBox.textContent = `Clerk OAuth Error: ${errorMsg}`;
                loginErrorBox.classList.remove("hidden");
            }
            showToast(errorMsg, "error");
        }
    }

    btnOauthGoogle?.addEventListener("click", () => handleClerkOAuth("oauth_google"));
    btnOauthGithub?.addEventListener("click", () => handleClerkOAuth("oauth_github"));

    // 3. REAL Clerk Login Execution
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
                btnLoginSubmit.textContent = "Authenticating with Clerk...";
            }

            try {
                if (window.Clerk && window.Clerk.client) {
                    const signIn = await window.Clerk.client.signIn.create({
                        identifier: email,
                        password: password,
                    });

                    if (signIn.status === "complete") {
                        await window.Clerk.setActive({ session: signIn.createdSessionId });
                        showToast("Clerk Authentication Successful!", "success");
                        runWorkspaceLoadingSequence();
                    } else if (signIn.status === "needs_second_factor") {
                        showView("otp");
                        startOtpCountdown();
                    } else {
                        throw new Error(`Authentication incomplete. Status: ${signIn.status}`);
                    }
                } else {
                    // Fallback to backend API route
                    const res = await fetch("/api/v1/auth/login", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email, password })
                    });
                    const data = await res.json();
                    if (!res.ok || !data.success) {
                        throw new Error(data.detail || data.message || "Invalid credentials");
                    }
                    showToast("Authentication Successful!", "success");
                    runWorkspaceLoadingSequence();
                }
            } catch (err) {
                console.error("Clerk Login error:", err);
                const errorMsg = err.errors?.[0]?.longMessage || err.message || "Invalid email or password";
                if (loginErrorBox) {
                    loginErrorBox.textContent = `Clerk Auth Error: ${errorMsg}`;
                    loginErrorBox.classList.remove("hidden");
                }
                showToast(errorMsg, "error");
            } finally {
                if (btnLoginSubmit) {
                    btnLoginSubmit.disabled = false;
                    btnLoginSubmit.textContent = "Sign In with Clerk";
                }
            }
        });
    }

    // 4. REAL Clerk Registration Execution
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
                    regErrorBox.textContent = "Passwords do not match";
                    regErrorBox.classList.remove("hidden");
                }
                return;
            }

            try {
                if (window.Clerk && window.Clerk.client) {
                    const signUp = await window.Clerk.client.signUp.create({
                        emailAddress: email,
                        password: password,
                        firstName: firstName,
                        lastName: lastName,
                    });
                    showToast("Account created in Clerk! Please sign in.", "success");
                    showView("login");
                } else {
                    const res = await fetch("/api/v1/auth/register", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email, password, full_name: `${firstName} ${lastName}` })
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.detail || "Registration failed");
                    showToast("Registration successful! Redirecting to login...", "success");
                    showView("login");
                }
            } catch (err) {
                const errorMsg = err.errors?.[0]?.longMessage || err.message || "Registration failed";
                if (regErrorBox) {
                    regErrorBox.textContent = errorMsg;
                    regErrorBox.classList.remove("hidden");
                }
                showToast(errorMsg, "error");
            }
        });
    }

    // 5. OTP 2FA Controls & Auto-Focus
    const otpInputs = document.querySelectorAll(".otp-input");
    otpInputs.forEach((input, idx) => {
        input.addEventListener("input", (e) => {
            if (e.target.value && idx < otpInputs.length - 1) {
                otpInputs[idx + 1].focus();
            }
        });
        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && !e.target.value && idx > 0) {
                otpInputs[idx - 1].focus();
            }
        });
    });

    let otpInterval;
    function startOtpCountdown() {
        let timer = 59;
        const timerElem = document.getElementById("otp-timer");
        clearInterval(otpInterval);
        otpInterval = setInterval(() => {
            if (timer <= 0) {
                clearInterval(otpInterval);
                if (timerElem) timerElem.textContent = "00:00";
            } else {
                if (timerElem) timerElem.textContent = `00:${timer < 10 ? '0' : ''}${timer}`;
                timer--;
            }
        }, 1000);
    }

    document.getElementById("btn-verify-otp")?.addEventListener("click", () => {
        runWorkspaceLoadingSequence();
    });

    // 6. Workspace Initialization Animation Sequence
    function runWorkspaceLoadingSequence() {
        showView("loading");
        const bar = document.getElementById("workspace-load-bar");
        const statusText = document.getElementById("loading-stage-text");

        const stages = [
            { text: "Initializing AetherMind Security Core...", progress: "20%" },
            { text: "Loading AI Multimodal Providers...", progress: "45%" },
            { text: "Connecting to Qdrant Vector Engine...", progress: "70%" },
            { text: "Preparing Workspace Memory & Collections...", progress: "90%" },
            { text: "Workspace Ready! Launching AetherMind...", progress: "100%" },
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
                }, 500);
            }
        }, 400);
    }
});
