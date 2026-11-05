import { supabaseClient } from './config.js';

export function initUI() { console.log('🎨 UI Module Fully Loaded'); }

function closeAllDrawers() {
            document.getElementById('sidebar-drawer').classList.add('-translate-x-full');
            document.getElementById('progress-drawer').classList.add('translate-x-full');
            document.getElementById('sidebar-overlay').classList.add('hidden');
        }
window.closeAllDrawers = closeAllDrawers;

function closeConfirmModal(result) {
            document.getElementById('confirm-modal').classList.add('hidden');
            if (confirmResolver) {
                confirmResolver(result);
                confirmResolver = null;
            }
        }
window.closeConfirmModal = closeConfirmModal;

function closeCustomAlert() {
            const modal = document.getElementById('custom-alert-modal');
            if (modal) modal.classList.add('hidden');
        }
window.closeCustomAlert = closeCustomAlert;

function closeFocusModal() { document.getElementById('focus-modal').classList.add('hidden'); }
window.closeFocusModal = closeFocusModal;

function closePrivacyPolicyModal() { document.getElementById('privacy-modal').classList.add('hidden'); }
window.closePrivacyPolicyModal = closePrivacyPolicyModal;

function closeReminderModal() { document.getElementById('reminder-modal').classList.add('hidden'); }
window.closeReminderModal = closeReminderModal;

function ensureProgressRendered() { console.warn('ensureProgressRendered missing'); }
window.ensureProgressRendered = ensureProgressRendered;

function openPrivacyPolicyModal() { document.getElementById('privacy-modal').classList.remove('hidden'); }
window.openPrivacyPolicyModal = openPrivacyPolicyModal;

function openTermsModal() {
            openPrivacyPolicyModal();
            setLegalTab('terms');
        }
window.openTermsModal = openTermsModal;

function setLegalTab(tab) {
            const btnPrivacy = document.getElementById('legal-tab-privacy');
            const btnTerms = document.getElementById('legal-tab-terms');
            const contentPrivacy = document.getElementById('legal-content-privacy');
            const contentTerms = document.getElementById('legal-content-terms');

            if (tab === 'privacy') {
                btnPrivacy.className = "flex-1 text-center font-bold text-xs text-deep-olive border-b-2 border-deep-olive pb-1";
                btnTerms.className = "flex-1 text-center font-bold text-xs text-stone-600 border-b-2 border-transparent pb-1 hover:text-stone-600";
                contentPrivacy.classList.remove('hidden');
                contentTerms.classList.add('hidden');
            } else {
                btnTerms.className = "flex-1 text-center font-bold text-xs text-deep-olive border-b-2 border-deep-olive pb-1";
                btnPrivacy.className = "flex-1 text-center font-bold text-xs text-stone-600 border-b-2 border-transparent pb-1 hover:text-stone-600";
                contentTerms.classList.remove('hidden');
                contentPrivacy.classList.add('hidden');
            }
        }
window.setLegalTab = setLegalTab;

function toggleProgressDrawer() {
            const drawer = document.getElementById('progress-drawer');
            const overlay = document.getElementById('sidebar-overlay');
            if (drawer.classList.contains('translate-x-full')) {
                window.ensureProgressRendered();
                window.ensureProgressRendered();
                closeAllDrawers();
                drawer.classList.remove('translate-x-full');
                overlay.classList.remove('hidden');
                // Trigga datarendering för utveckling/reflektion om funktionen finns
                if (typeof renderProgressContent === 'function') renderProgressContent();
                if (typeof loadJournal === 'function') loadJournal();
            } else closeAllDrawers();
        }
window.toggleProgressDrawer = toggleProgressDrawer;

function toggleReflectionsPanel() { console.warn('toggleReflectionsPanel missing'); }
window.toggleReflectionsPanel = toggleReflectionsPanel;

function toggleSidebar() {
            const drawer = document.getElementById('sidebar-drawer');
            const overlay = document.getElementById('sidebar-overlay');
            if (drawer.classList.contains('-translate-x-full')) {
                closeAllDrawers();
                drawer.classList.remove('-translate-x-full');
                overlay.classList.remove('hidden');
            } else closeAllDrawers();
        }
window.toggleSidebar = toggleSidebar;



export function setAppState(state) {
    console.log('[FALK UI Engine] Symmetriskt tillståndsskifte till:', state);
    
    const onboardingEl = document.getElementById('onboarding-cards-wrapper');
    const chatEl = document.getElementById('chat-container');
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
                   
    // Stäng sidomenyn genom transform – ALDRIG genom 'hidden' på sidebar
    if (sidebar) {
        sidebar.classList.remove('translate-x-0');
        sidebar.classList.add('-translate-x-full');
        sidebar.classList.remove('hidden'); // Säkerställ att hidden aldrig ligger kvar
    }
    if (backdrop) {
        backdrop.classList.add('hidden');
    }

    if (state === 'chat') {
        if (onboardingEl) onboardingEl.classList.add('hidden-force');
        if (chatEl) chatEl.classList.remove('hidden-force');
    } else if (state === 'page1' || state === 'home' || state === 'onboarding') {
        if (onboardingEl) onboardingEl.classList.remove('hidden-force');
        if (chatEl) {
            chatEl.classList.add('hidden-force');
            const msgs = document.getElementById('messages');
            if (msgs) msgs.innerHTML = '';
        }
    }
}
if (typeof window !== 'undefined') {
    window.setAppState = setAppState;
}
if (typeof window !== 'undefined') {
    window.setAppState = setAppState;
}
window.setAppState = setAppState;

if (typeof window !== 'undefined') {
    window.setAppState = setAppState;
}
if (typeof window !== 'undefined') {
    window.setAppState = setAppState;
}

window.setAppState = setAppState;

export function switchTab(tabName) {
    console.log('[FALK UI] switchTab anropad med:', tabName);
    if (tabName === 'page1' || tabName === 'home' || tabName === 'onboarding' || !tabName) {
        if (typeof window.startNewChat === 'function') {
            window.startNewChat();
        } else if (typeof setAppState === 'function') {
            setAppState('page1');
        }
    } else {
        if (typeof setAppState === 'function') {
            setAppState(tabName);
        } else if (typeof window.setAppState === 'function') {
            window.setAppState(tabName);
        }
    }
}
if (typeof window !== 'undefined') {
    window.switchTab = switchTab;
}
if (typeof window !== 'undefined') {
    window.switchTab = switchTab;
}

if (typeof window !== 'undefined') {
    window.switchTab = switchTab;
}

export function toggleMenu() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (!sidebar || !backdrop) {
        console.warn('[FALK UI] Meny-element saknas i DOM.');
        return;
    }

    // Ta bort eventuell felaktig hidden-klass på sidebar
    sidebar.classList.remove('hidden');

    const isHidden = sidebar.classList.contains('-translate-x-full');
    if (isHidden) {
        sidebar.classList.remove('-translate-x-full');
        sidebar.classList.add('translate-x-0');
        backdrop.classList.remove('hidden');
    } else {
        sidebar.classList.remove('translate-x-0');
        sidebar.classList.add('-translate-x-full');
        backdrop.classList.add('hidden');
    }
}
if (typeof window !== 'undefined') {
    window.toggleMenu = toggleMenu;
}
if (typeof window !== 'undefined') {
    window.toggleMenu = toggleMenu;
}

if (typeof window !== 'undefined') {
    window.toggleMenu = toggleMenu;
}

export function openAuthModal() {
    console.log('[FALK Auth UI] Öppnar Auth Modal.');
    const modal = document.getElementById('auth-modal');
    const backdrop = document.getElementById('auth-modal-backdrop');
    if (modal) modal.classList.remove('hidden');
    if (backdrop) backdrop.classList.remove('hidden');
}

export function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    const backdrop = document.getElementById('auth-modal-backdrop');
    if (modal) modal.classList.add('hidden');
    if (backdrop) backdrop.classList.add('hidden');
}

if (typeof window !== 'undefined') {
    window.openAuthModal = openAuthModal;
    window.closeAuthModal = closeAuthModal;
}

if (typeof window !== 'undefined' && !window.handleAuthSubmit) { window.handleAuthSubmit = function(){ console.warn('Auth module loading...'); }; }


/* === FALK OPTION A: NEW CHAT RESET & STREAM ABORT === */
window.activeAbortController = window.activeAbortController || null;

window.resetToHome = function() {
  // 1. Avbryt pågående AI-respons om den strömmar
  if (window.activeAbortController) {
    try {
      window.activeAbortController.abort();
    } catch(e) {}
    window.activeAbortController = null;
  }

  // 2. Dölj chatt och nollställ meddelande-ytan i DOM
  const chatMessages = document.getElementById("chat-messages");
  const chatContainer = document.getElementById("chat-container");
  if (chatMessages) {
    chatMessages.innerHTML = "";
    chatMessages.style.display = "none";
  }
  if (chatContainer) {
    chatContainer.classList.remove("is-active");
  }
  document.body.classList.remove("is-chat-active");

  // 3. Visa startsidan och onboarding-korten (ÖVERRÖR EJ CSS/DESIGN)
  const wrapper = document.getElementById("onboarding-cards-wrapper");
  const grid = document.getElementById("prompt-grid");
  if (wrapper) {
    wrapper.style.display = "block";
    wrapper.classList.remove("hidden");
  }
  if (grid) {
    grid.style.display = "flex";
    grid.classList.remove("hidden");
  }

  // 4. Rensa inmatningsfältet
  const input = document.getElementById("chat-input");
  if (input) {
    input.value = "";
    input.style.height = "auto";
  }

  // 5. Mjuk scroll till toppen
  window.scrollTo({ top: 0, behavior: 'smooth' });
};


/* === FALK BULLETPROOF HEADER CLICK DELEGATION (OPTION A) === */
window.resetToHome = function() {
  // 1. Dölj chattytan och töm alla meddelandebubblor
  const chatMessages = document.getElementById("chat-messages");
  const chatContainer = document.getElementById("chat-container");
  
  if (chatMessages) {
    chatMessages.style.display = "none";
    chatMessages.innerHTML = ""; 
  }
  if (chatContainer) {
    chatContainer.classList.remove("is-active");
    chatContainer.style.display = "none";
  }
  document.body.classList.remove("is-chat-active");

  // 2. Nollställ konversationshistorik i JS (utan att rör gästräknaren)
  if (window.conversationHistory && Array.isArray(window.conversationHistory)) {
    window.conversationHistory = [];
  }

  // 3. Visa onboarding-cards-wrapper
  const wrapper = document.getElementById("onboarding-cards-wrapper");
  const grid = document.getElementById("prompt-grid");
  
  if (wrapper) {
    wrapper.style.display = "block";
    wrapper.classList.remove("hidden");
  }
  if (grid) {
    grid.style.display = "flex";
    grid.classList.remove("hidden");
  }

  // 4. Rensa skrivfältet
  const input = document.getElementById("chat-input");
  if (input) {
    input.value = "";
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// Global Capture-Phase Listener: Fångar ALLA klick på logga eller plusknapp
document.addEventListener("click", function(e) {
  const target = e.target;
  if (!target) return;

  // Kontrollera om klicket skedde i eller på headern
  const header = target.closest("header, nav, .header, [class*='header'], div[class*='top']");
  
  const isFalkLogo = (header && target.textContent && target.textContent.includes("FALK")) ||
                     target.closest("[data-action='home'], .logo, #logo");

  const isPlusBtn = (header && (target.textContent.trim() === "+" || target.innerHTML.includes("+"))) ||
                    target.closest("#new-chat-btn, .new-chat, [data-action='new-chat']");

  if (isFalkLogo || isPlusBtn) {
    e.preventDefault();
    e.stopPropagation();
    window.resetToHome();
  }
}, true); // true = capture phase (prioriteras över alla andra skript)


// Force cursor pointer on FALK text elements at runtime
document.addEventListener("DOMContentLoaded", function() {
  const allElements = document.querySelectorAll("body *");
  allElements.forEach(el => {
    if (el.children.length === 0 && el.textContent.trim() === "FALK") {
      el.style.setProperty("cursor", "pointer", "important");
      if (el.parentElement) el.parentElement.style.setProperty("cursor", "pointer", "important");
    }
  });
});
