# ─────── FIREBASE AUTHENTICATION SETUP GUIDE ───────
## AetherMind Multimodal AI — Enterprise Identity Configuration Guide

This guide walks you step-by-step through setting up **Firebase Authentication** for your AetherMind Multimodal AI platform on both your local environment and live Streamlit Cloud deployment (`https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app`).

---

### 📋 STEP 1: Enable Firebase Authentication Engine

1. Open your Firebase Console:
   👉 [Firebase Console Authentication Setup](https://console.firebase.google.com/u/0/project/aethermind-multi-modal-ai/authentication)
2. On the **Authentication** landing page (shown in your screenshot), click the **"Get started"** button.

---

### 🔐 STEP 2: Configure Sign-In Methods (Providers)

Once initialized, navigate to the **Sign-in method** tab inside Authentication:

#### 1. Email / Password Authentication
- Click **Email/Password** from the Native providers list.
- Toggle **Enable** to `ON`.
- *(Optional)* Enable Email link (passwordless sign-in).
- Click **Save**.

#### 2. Anonymous / Instant Guest Mode Sign-In
- Click **Anonymous** from the Additional providers list.
- Toggle **Enable** to `ON`.
- Click **Save**.
- *This powers 1-click guest access without requiring account creation.*

#### 3. Google OAuth 2.0
- Click **Google** under Social providers.
- Toggle **Enable** to `ON`.
- Select your **Project support email** from the dropdown.
- Click **Save**.

#### 4. GitHub OAuth 2.0
- Click **GitHub** under Social providers.
- Toggle **Enable** to `ON`.
- Copy the **Authorization callback URL** provided by Firebase (e.g., `https://aethermind-multi-modal-ai.firebaseapp.com/__/auth/handler`).
- Open [GitHub Developer Settings → OAuth Apps](https://github.com/settings/developers).
- Click **New OAuth App**:
  - Application name: `AetherMind Multimodal AI`
  - Homepage URL: `https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app`
  - Authorization callback URL: *Paste the Firebase callback URL copied above*.
- Click **Register application**, generate a Client Secret, and paste the **Client ID** and **Client Secret** back into Firebase.
- Click **Save**.

---

### 🌐 STEP 3: Add Authorized Domains

To allow authentication calls from your Streamlit Cloud app and local server:

1. In the Firebase Authentication section, select the **Settings** tab.
2. Click **Authorized domains**.
3. Verify or click **Add domain**:
   - Add: `aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app`
   - Add: `localhost`
   - Add: `127.0.0.1`
4. Click **Save**.

---

### 🔑 STEP 4: Retrieve & Update Firebase API Keys

1. Click the **Gear Icon (⚙️)** next to *Project Overview* in the top left sidebar and select **Project Settings**.
2. Scroll down to the **Your apps** section.
3. Click the **Web icon (`</>`)** to register a Web app if you haven't already:
   - App nickname: `AetherMind Web OS`
   - Click **Register app**.
4. Copy the `firebaseConfig` JavaScript snippet:
   ```javascript
   const firebaseConfig = {
     apiKey: "YOUR_FIREBASE_API_KEY",
     authDomain: "aethermind-multi-modal-ai.firebaseapp.com",
     projectId: "aethermind-multi-modal-ai",
     storageBucket: "aethermind-multi-modal-ai.appspot.com",
     messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
     appId: "YOUR_APP_ID"
   };
   ```
5. Update `firebaseConfig` in [`app/static/js/auth.js`](file:///c:/Users/johns/Documents/AETHERMIND%20MULTIMODAL%20AI/app/static/js/auth.js) or set the environment variables in `.env`.

---

### 🚀 STEP 5: Testing Login, Logout & Session Management

- **Direct Full-Screen Login Page**:
  Visit `/login` or `/auth` to view the 2-column cyberpunk login portal.
- **Direct Full-Screen Logout Page**:
  Visit `/logout` to trigger session destruction and view the signed-out portal.
- **In-App Login Modal**:
  Clicking **Logout** in the top bar or profile menu now opens the **Firebase Authentication Modal Card** directly on screen, allowing instant sign-in via Email, Guest mode, Google, or GitHub.

---
*AetherMind Multimodal AI — Enterprise Cyberpunk OS v4.0*
