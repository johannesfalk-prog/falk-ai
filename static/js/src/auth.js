
function updateAuthModalUI(mode) {
    const termsContainer = document.getElementById("terms-container");
    const rememberMeContainer = document.getElementById("auth-remember-me")?.closest("label");
    if (termsContainer) {
        if (mode === "signup") {
            termsContainer.classList.remove("hidden");
        } else {
            termsContainer.classList.add("hidden");
        }
    }
}

import { supabaseClient } from './config.js';

export function initAuth() { console.log('🔒 Auth Module Fully Initialized'); }

function closeAuthModal() { document.getElementById('auth-modal').classList.add('hidden'); }
window.closeAuthModal = closeAuthModal;

async function getOrHydrateUserToken() {
  if (window.userToken && window.userToken.length > 20) return window.userToken;

  // 1. Testa globala Supabase-klienter
  const sb = window.supabase || window.supabaseClient;
  if (sb && sb.auth) {
    try {
      const { data: { session } } = await sb.auth.getSession();
      if (session && session.access_token) {
        window.userToken = session.access_token;
        if (typeof updateAuthUI === 'function') updateAuthUI(session.user);
        return window.userToken;
      }
    } catch (e) { console.warn("Supabase session check exception:", e); }
  }

  // 2. Failsafe: Direkt inspektion av localStorage om Supabase-klienten inte svarat än
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && (key.includes('auth-token') || key.startsWith('sb-'))) {
      try {
        const parsed = JSON.parse(localStorage.getItem(key));
        if (parsed && parsed.access_token) {
          window.userToken = parsed.access_token;
          if (parsed.user && typeof updateAuthUI === 'function') updateAuthUI(parsed.user);
          return window.userToken;
        }
      } catch(err) {}
    }
  }

  return null;
}
window.getOrHydrateUserToken = getOrHydrateUserToken;

function handleLogout() { console.warn('handleLogout missing'); }
window.handleLogout = handleLogout;

async function logout() {
            if (supabaseClient) await supabaseClient.auth.signOut();
            localStorage.clear();
            location.reload();
        }
window.logout = logout;

function openAuthModal() { document.getElementById('auth-modal').classList.remove('hidden'); }
window.openAuthModal = openAuthModal;

function setAuthTab(mode) {
            currentAuthMode = mode;
            if (mode === 'login') {
                document.getElementById('wrap-username').classList.add('hidden');
                document.getElementById('wrap-gdpr').classList.add('hidden');
                document.getElementById('auth-submit-btn').textContent = "Logga in";
            } else {
                document.getElementById('wrap-username').classList.remove('hidden');
                document.getElementById('wrap-gdpr').classList.remove('hidden');
                document.getElementById('auth-submit-btn').textContent = "Skapa konto";
            }
        }
window.setAuthTab = setAuthTab;

async function submitAuth() {
            clearAuthError();
            const identifier = document.getElementById('auth-identifier').value.trim();
            const password = document.getElementById('auth-password').value.trim();
            if (!identifier || !password) return showAuthError("Fyll i alla fält.");

            if (currentAuthMode === 'signup') {
                const username = document.getElementById('auth-username').value.trim();
                const gdprCheck = document.getElementById('auth-gdpr-check').checked;
                if (!username || !gdprCheck) return showAuthError("Godkänn villkoren och fyll i användarnamn.");

                const termsCheck = document.getElementById("auth-terms-accept");
        if (currentAuthMode === "signup" && termsCheck && !termsCheck.checked) {
            alert("Du måste godkänna användarvillkoren och integritetspolicyn för att skapa ett konto.");
            return;
        }
        let res = await supabaseClient.auth.signUp({ email: identifier, password });
                if (res.error) return showAuthError("Fel: " + res.error.message);
                await supabaseClient.auth.signOut();
                userToken = null;
                document.body.classList.remove('is-logged-in');
                showAlert("Konto skapat! Ett bekräftelsemail har skickats till " + identifier + ". Du MÅSTE klicka på länken i mailet för att aktivera kontot innan du kan logga in.");
                setAuthTab('login');
                return;
                if (res.error) return showAuthError("Fel: " + res.error.message);
                // Tvinga urloggning omedelbart för att förhindra auto-login innan e-post är verifierad
                await supabaseClient.auth.signOut();
                userToken = null;
                showAlert("Konto skapat! Ett bekräftelsemail har skickats till " + identifier + ". Du MÅSTE klicka på länken i mailet för att aktivera kontot innan du kan logga in.");
                setAuthTab('login');
            } else {
                document.cookie = "falk_guest_count=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                let res = await supabaseClient.auth.signInWithPassword({ email: identifier, password });
                if (res.error) showAuthError("Fel: " + res.error.message);
                else closeAuthModal();
            }
        }
window.submitAuth = submitAuth;


export async function handleAuthSubmit() {
    const emailEl = document.getElementById('auth-email');
    const passwordEl = document.getElementById('auth-password');
    const statusEl = document.getElementById('auth-status-msg');

    if (!emailEl || !passwordEl) return;

    const email = emailEl.value.trim();
    const password = passwordEl.value.trim();

    if (!email || !password) {
        if (statusEl) {
            statusEl.innerText = "Vänligen ange både e-post och lösenord.";
            statusEl.className = "mt-3 text-xs text-center font-serif italic text-red-600 block";
        }
        return;
    }

    if (statusEl) {
        statusEl.innerText = "Verifierar med Supabase...";
        statusEl.className = "mt-3 text-xs text-center font-serif italic text-[#4E5C4B] block";
    }

    try {
        // Kontrollera om supabase-klienten finns på window
        const client = window.supabaseClient || window.supabase;
        
        if (!client || !client.auth) {
            console.warn('[FALK Auth] Supabase-klient ej hittad. Kör lokal fallback/mock-session.');
            // Fallback om Supabase inte är inställt i lokala miljöfaktorer ännu
            localStorage.setItem('falk_user_logged_in', 'true');
            localStorage.setItem('falk_user_email', email);
            finalizeLogin(email);
            return;
        }

        // 1. Försök logga in
        let { data, error } = await client.auth.signInWithPassword({ email, password });

        // 2. Om kontot inte finns, registrera nytt konto
        if (error && (error.message.includes('Invalid login credentials') || error.status === 400)) {
            if (statusEl) statusEl.innerText = "Skapar nytt konto...";
            const signUpRes = await client.auth.signUp({ email, password });
            data = signUpRes.data;
            error = signUpRes.error;
        }

        if (error) {
            if (statusEl) {
                statusEl.innerText = "Inloggningsfel: " + error.message;
                statusEl.className = "mt-3 text-xs text-center font-serif italic text-red-600 block";
            }
            return;
        }

        // Framgångsrik inloggning
        const userEmail = data?.user?.email || email;
        localStorage.setItem('falk_user_logged_in', 'true');
        localStorage.setItem('falk_user_email', userEmail);
        
        finalizeLogin(userEmail);

    } catch (err) {
        console.error('[FALK Auth Error]:', err);
        if (statusEl) {
            statusEl.innerText = "Ett oväntat fel uppstod vid inloggning.";
            statusEl.className = "mt-3 text-xs text-center font-serif italic text-red-600 block";
        }
    }
}

function finalizeLogin(userEmail) {
    console.log('[FALK Auth] Inloggning genomförd för:', userEmail);
    
    // Uppdatera UI-märkning i headern
    const guestBadges = document.querySelectorAll('header span, aside span');
    guestBadges.forEach(el => {
        if (el.innerText.includes('GÄST') || el.innerText.includes('Gäst')) {
            el.innerText = 'INLOGGAD';
            el.classList.remove('bg-[#A8BFA1]/30');
            el.classList.add('bg-[#C57B57]', 'text-white');
        }
    });

    // Stäng Auth-modal
    if (typeof window.closeAuthModal === 'function') {
        window.closeAuthModal();
    }

    // Ta bort eventuell Paywall-varning ur chatten och lås upp input
    const paywallDivs = document.querySelectorAll('div[class*="bg-[#C57B57]/15"]');
    paywallDivs.forEach(div => div.remove());

    const inputEl = document.getElementById('chat-input');
    if (inputEl) {
        inputEl.disabled = false;
        inputEl.classList.remove('opacity-60', 'cursor-not-allowed');
        inputEl.placeholder = "Skriv till mig...";
        inputEl.focus();
    }
}

if (typeof window !== 'undefined') {
    window.handleAuthSubmit = handleAuthSubmit;
}


/* === FALK GUEST LIMIT & AUTH WALL (MAX 6 MESSAGES) === */
window.FALK_GUEST_LIMIT = 6;

window.getGuestMessageCount = function() {
  return parseInt(localStorage.getItem("falk_guest_msg_count") || "0", 10);
};

window.incrementGuestMessageCount = function() {
  const current = window.getGuestMessageCount();
  const updated = current + 1;
  localStorage.setItem("falk_guest_msg_count", updated.toString());
  return updated;
};

window.checkGuestAccess = function() {
  // Om användaren är inloggad (har session/token) -> tillåt alltid
  if (window.FALK_USER_LOGGED_IN === true) return true;

  const count = window.getGuestMessageCount();
  if (count >= window.FALK_GUEST_LIMIT) {
    window.triggerAuthModal("Du har nått gränsen på 6 gratis meddelanden som gäst. Skapa ett konto för att fortsätta.");
    return false;
  }
  return true;
};

window.triggerAuthModal = function(reasonMessage) {
  const modal = document.getElementById("auth-modal") || document.getElementById("login-modal");
  const modalText = document.getElementById("auth-modal-reason");
  
  if (modalText && reasonMessage) {
    modalText.innerText = reasonMessage;
  }
  if (modal) {
    modal.classList.remove("hidden");
    modal.style.display = "flex";
  } else {
    alert(reasonMessage || "Skapa ett konto för att fortsätta samtala med FALK.");
  }
};
