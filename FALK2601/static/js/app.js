// --- Extracted Script Block --- 
window.ensureProgressRendered = function() {
    const container = document.getElementById('progress-drawer-content') || document.querySelector('#progress-drawer .drawer-body') || document.getElementById('progress-drawer');
    if (!container) return;
    
    // Om container saknar reellt innehåll eller bara har tomma noder, injecta strukturen
    if (container.children.length <= 1 || container.innerText.trim() === "") {
        container.innerHTML = `
            <div class="p-6 space-y-6 text-stone-800">
                <div class="border-b border-stone-200 pb-4">
                    <h3 class="text-sm font-bold text-stone-500 uppercase tracking-wider">Reflektioner</h3>
                    <p class="text-xs text-stone-600 mt-1">Dina sparade insikter, påminnelser och personliga mönster.</p>
                </div>
                
                <div id="journal-list" class="space-y-3">
                    <div class="p-4 bg-stone-100/80 rounded-xl text-xs text-stone-600 italic border border-stone-200/60">
                        Inga tidigare reflektioner sparade ännu. Dina framsteg och sparade insikter visas här automatiskt under dina samtal med FALK.
                    </div>
                </div>
            </div>
        `;
    }
    if (typeof loadJournal === 'function') loadJournal();
    if (typeof fetchProgressData === 'function') fetchProgressData();
};


window.ensureSettingsRendered = function() {
    const container = document.getElementById('settings-drawer-content') || document.querySelector('#settings-drawer .drawer-body') || document.getElementById('settings-drawer');
    if (!container) return;

    if (container.children.length <= 1 || container.innerText.trim() === "") {
        container.innerHTML = `
            <div class="p-6 space-y-6 text-stone-800">
                <div class="border-b border-stone-200 pb-4">
                    <h3 class="text-sm font-bold text-stone-500 uppercase tracking-wider">Inställningar & Dataskydd</h3>
                    <p class="text-xs text-stone-600 mt-1">Hantera ditt konto, sekretess och sparade data.</p>
                </div>

                <div class="space-y-4 text-xs">
                    <div class="p-4 bg-white border border-stone-200 rounded-xl space-y-3 shadow-sm">
                        <div class="font-bold text-stone-700">Konto & Medlemskap</div>
                        <div class="flex justify-between items-center text-stone-600">
                            <span>KONTOTYP</span>
                            <span class="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">GÄST</span>
                        </div>
                    </div>

                    <div class="p-4 bg-white border border-stone-200 rounded-xl space-y-3 shadow-sm">
                        <div class="font-bold text-stone-700">Dataskydd & Integritet (GDPR)</div>
                        <p class="text-stone-500 leading-relaxed">Dina samtal krypteras och delas aldrig med tredje part. Du kan när som helst radera din historik.</p>
                        <button type="button" onclick="if(confirm('Är du säker på att du vill rensa din lokala samtalshistorik?')) { localStorage.clear(); location.reload(); }" class="w-full py-2 bg-rose-50 text-rose-700 border border-rose-200 rounded-lg hover:bg-rose-100 transition font-medium">
                            Rensa lokal historik
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
};



window.ensureProgressRendered = function() {
    const container = document.getElementById('progress-drawer-content') || document.querySelector('#progress-drawer .drawer-body') || document.getElementById('progress-drawer');
    if (!container) return;
    
    // Om container saknar reellt innehåll eller bara har tomma noder, injecta strukturen
    if (container.children.length <= 1 || container.innerText.trim() === "") {
        container.innerHTML = `
            <div class="p-6 space-y-6 text-stone-800">
                <div class="border-b border-stone-200 pb-4">
                    <h3 class="text-sm font-bold text-stone-500 uppercase tracking-wider">Reflektioner</h3>
                    <p class="text-xs text-stone-600 mt-1">Dina sparade insikter, påminnelser och personliga mönster.</p>
                </div>
                
                <div id="journal-list" class="space-y-3">
                    <div class="p-4 bg-stone-100/80 rounded-xl text-xs text-stone-600 italic border border-stone-200/60">
                        Inga tidigare reflektioner sparade ännu. Dina framsteg och sparade insikter visas här automatiskt under dina samtal med FALK.
                    </div>
                </div>
            </div>
        `;
    }
    if (typeof loadJournal === 'function') loadJournal();
    if (typeof fetchProgressData === 'function') fetchProgressData();
};


window.ensureSettingsRendered = function() {
    const container = document.getElementById('settings-drawer-content') || document.querySelector('#settings-drawer .drawer-body') || document.getElementById('settings-drawer');
    if (!container) return;

    if (container.children.length <= 1 || container.innerText.trim() === "") {
        container.innerHTML = `
            <div class="p-6 space-y-6 text-stone-800">
                <div class="border-b border-stone-200 pb-4">
                    <h3 class="text-sm font-bold text-stone-500 uppercase tracking-wider">Inställningar & Dataskydd</h3>
                    <p class="text-xs text-stone-600 mt-1">Hantera ditt konto, sekretess och sparade data.</p>
                </div>

                <div class="space-y-4 text-xs">
                    <div class="p-4 bg-white border border-stone-200 rounded-xl space-y-3 shadow-sm">
                        <div class="font-bold text-stone-700">Konto & Medlemskap</div>
                        <div class="flex justify-between items-center text-stone-600">
                            <span>KONTOTYP</span>
                            <span class="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">GÄST</span>
                        </div>
                    </div>

                    <div class="p-4 bg-white border border-stone-200 rounded-xl space-y-3 shadow-sm">
                        <div class="font-bold text-stone-700">Dataskydd & Integritet (GDPR)</div>
                        <p class="text-stone-500 leading-relaxed">Dina samtal krypteras och delas aldrig med tredje part. Du kan när som helst radera din historik.</p>
                        <button type="button" onclick="if(confirm('Är du säker på att du vill rensa din lokala samtalshistorik?')) { localStorage.clear(); location.reload(); }" class="w-full py-2 bg-rose-50 text-rose-700 border border-rose-200 rounded-lg hover:bg-rose-100 transition font-medium">
                            Rensa lokal historik
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
};



// Global Paywall Override: Släpp alltid igenom inloggade användare
window.handleLockedFeature = function(feature) {
    const isLoggedIn = !!(userToken || document.body.classList.contains('is-logged-in') || localStorage.getItem('sb-falk-auth-token'));
    if (isLoggedIn) return false;
    if (typeof openPaywallModal === 'function') openPaywallModal(feature || 'limit');
    return true;
};

window.handleLogin = async function(e) {
    
  // [Orphaned login block purged]

  const email = emailEl.value.trim();
  const password = passEl.value;

  if (!email || !password) {
    alert("Fyll i både e-post och lösenord.");
    return false;
  }

  const sb = window.supabase || window.supabaseClient;
  if (!sb || !sb.auth) {
    alert("Supabase-klienten är inte redo.");
    return false;
  }

  try {
    const { data, error } = await sb.auth.signInWithPassword({ email, password });
    if (error) {
      alert("Inloggningsfel: " + error.message);
      return false;
    }

    if (data && data.session) {
      window.userToken = data.session.access_token;
      
      // REAKTIV UI-UPPDATERING DIREKT I DOM:EN (INGEN F5 KRÄVS)
      if (typeof updateAuthUI === 'function') {
        updateAuthUI(data.user);
      } else {
        const emailDisp = document.getElementById('user-email-display');
        if (emailDisp) emailDisp.innerText = data.user.email;
        
        const loggedInBox = document.getElementById('user-profile-logged-in');
        const loggedOutBox = document.getElementById('user-profile-logged-out');
        if (loggedInBox) loggedInBox.classList.remove('hidden');
        if (loggedOutBox) loggedOutBox.classList.add('hidden');

        document.querySelectorAll('.guest-badge, #user-status-badge, #user-tier-badge').forEach(el => {
          el.innerText = 'PREMIUM';
          el.classList.remove('bg-stone-200', 'text-stone-600');
          el.classList.add('bg-[#2C3E35]', 'text-white');
        });
      }

      // Dölj auth-modalen
      const authModal = document.getElementById('auth-modal');
      if (authModal) authModal.classList.add('hidden');

      // Omdirigera om användaren klickat på dashboarden innan login
      if (window.pendingViewAfterAuth === 'dashboard') {
        window.pendingViewAfterAuth = null;
        openDashboardView();
      }
    }
  } catch (err) {
    console.error("Login exception:", err);
    alert("Ett oväntat fel uppstod vid inloggning.");
  }

  return false;

// --- Extracted Script Block --- 
document.addEventListener('DOMContentLoaded', async () => {
    if (typeof supabase !== 'undefined' && supabase.auth) {
        try {
            const { data: { session } } = await supabase.auth.getSession();
            if (session && session.user) {
                if (typeof window.setUserTier === 'function') {
                    window.setUserTier('PREMIUM');
                } else {
                    window.userTier = 'PREMIUM';
                }
            } else {
                if (typeof window.setUserTier === 'function') {
                    window.setUserTier('GUEST');
                } else {
                    window.userTier = 'GUEST';
                }
            }
        } catch (e) {
            console.error('[AUTH HYDRATION ERROR]:', e);
        }
    }
});

    if (typeof e.preventDefault === 'function') e.preventDefault();
    if (typeof e.stopPropagation === 'function') e.stopPropagation();
  }


  const email = emailEl.value.trim();
  const password = passEl.value;

  if (!email || !password) {
  }

  const sb = window.supabase || window.supabaseClient;
  if (!sb || !sb.auth) {
  }

  try {
    if (error) {
      alert("Inloggningsfel: " + error.message);
    }

    if (data && data.session) {
      
      // REAKTIV UI-UPPDATERING DIREKT I DOM:EN (INGEN F5 KRÄVS)
      if (typeof updateAuthUI === 'function') {
        updateAuthUI(data.user);
      } else {
        const emailDisp = document.getElementById('user-email-display');
        if (emailDisp) emailDisp.innerText = data.user.email;
        
        const loggedInBox = document.getElementById('user-profile-logged-in');
        const loggedOutBox = document.getElementById('user-profile-logged-out');
        if (loggedInBox) loggedInBox.classList.remove('hidden');
        if (loggedOutBox) loggedOutBox.classList.add('hidden');

        document.querySelectorAll('.guest-badge, #user-status-badge, #user-tier-badge').forEach(el => {
          el.innerText = 'PREMIUM';
          el.classList.remove('bg-stone-200', 'text-stone-600');
          el.classList.add('bg-[#2C3E35]', 'text-white');
        });
      }

      // Dölj auth-modalen
      const authModal = document.getElementById('auth-modal');
      if (authModal) authModal.classList.add('hidden');

// --- Extracted Script Block --- 
const SUPABASE_URL = window.FALK_CONFIG?.SUPABASE_URL || "";
        const SUPABASE_ANON_KEY = window.FALK_CONFIG?.SUPABASE_ANON_KEY || "";
        
        let supabaseClient = null;
        if (typeof window.supabase !== 'undefined' && window.supabase.createClient) {
            supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        }

        let userToken = null;
        let activeSessionId = null;
        let selectedMood = 3;
        let userProfile = null;
        let currentAuthMode = 'login';
        let pendingReminderText = '';
        let confirmResolver = null;

        window.isSendingMessage = false;
let focusState = { confidence: 50, stress: 50, action: 50, boundaries: 50, motivation: 50 };
        let pinnedSessions = JSON.parse(localStorage.getItem('falk_pinned_sessions') || '[]');

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
        function openTermsModal() {
            openPrivacyPolicyModal();
            setLegalTab('terms');
        }

        function customConfirm(msg, title = "Bekräfta åtgärd") {
            return new Promise((resolve) => {
                document.getElementById('confirm-title').textContent = title;
                document.getElementById('confirm-msg').textContent = msg;
                document.getElementById('confirm-modal').classList.remove('hidden');
                confirmResolver = resolve;
            });
        }

        function closeConfirmModal(result) {
            document.getElementById('confirm-modal').classList.add('hidden');
            if (confirmResolver) {
                confirmResolver(result);
                confirmResolver = null;
            }
        }

        function initDisclaimer() {
            const lang = (navigator.language || 'sv').toLowerCase();
            const el = document.getElementById('disclaimer-text');
            if (!el) return;
            if (lang.startsWith('sv')) {
                el.textContent = "FALK är ett AI-baserat verktyg för självhjälp och personlig utveckling. Ej sjukvård. Vid akuta kriser, ring 112 eller 90101 (MIND).";
            } else {
                el.textContent = "FALK is an AI self-help & personal development tool (not medical care). In acute crisis, contact your local emergency service (112/911).";
            }
        }

        function checkForCrisisKeywords(text) {
            const lower = text.toLowerCase();
            const crisisWords = ['suicid', 'ta mitt liv', 'skada mig', 'kill myself', 'end my life', 'suicide', 'self harm'];
            for (let word of crisisWords) {
                if (lower.includes(word)) {
                    showAlert("Om du befinner dig i kris, sök hjälp direkt. Ring 112 eller 90101 (MIND Självmordslinjen).");
                    break;
                }
            }
        }

        function showAlert(msg) {
            const msgEl = document.getElementById('custom-alert-msg');
            if (msgEl) msgEl.textContent = msg;
            const modal = document.getElementById('custom-alert-modal');
            if (modal) modal.classList.remove('hidden');
        }

        function closeCustomAlert() {
            const modal = document.getElementById('custom-alert-modal');
            if (modal) modal.classList.add('hidden');
        }

        async function initAuth() {
            initDisclaimer();
            loadJournal();
            if (!supabaseClient) return;

            const { data: { session } } = await supabaseClient.auth.getSession();
            await updateAuthUI(session);

            supabaseClient.auth.onAuthStateChange(async (_event, session) => {
                await updateAuthUI(session);
            });
        }

        async function updateAuthUI(session) {
            const userDisplayBottom = document.getElementById('user-display-bottom');
            const logoutBtnBottom = document.getElementById('logout-btn-bottom');
            const loginBtnBottom = document.getElementById('login-btn-bottom');
            // Tier badge update refactored
            const settingsTier = document.getElementById('settings-tier');

            if (session) {
                if (session.user && !session.user.email_confirmed_at) {
                    await supabaseClient.auth.signOut();
                    userToken = null;
                    showAuthError("E-postadressen har inte bekräftats ännu. Kontrollera din inkorg eller begär en ny länk.");
                    openAuthModal();
                    return;
                }
                userToken = session.access_token;
                await fetchProfile();
                const displayName = (userProfile && userProfile.username) ? userProfile.username : session.user.email;
                if (userDisplayBottom) userDisplayBottom.textContent = displayName;
                if (logoutBtnBottom) logoutBtnBottom.classList.remove('hidden');
                if (loginBtnBottom) loginBtnBottom.classList.add('hidden');
                const badges = document.querySelectorAll('.tier-badge-element');
        const settingsTiers = document.querySelectorAll('.settings-tier-element');
        const isProUser = !!session;
        const text = isProUser ? "PREMIUM" : "GÄST";
        const badgeClasses = isProUser 
            ? 'tier-badge-element text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-800 border border-amber-500/30 transition'
            : 'tier-badge-element text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-stone-200 text-stone-600 transition';
        
        badges.forEach(b => {
            b.textContent = text;
            b.className = badgeClasses;
        });
        settingsTiers.forEach(s => s.textContent = text);
                if (settingsTier) settingsTier.textContent = "PREMIUM";
                loadSessions();
                loadJournal();
            } else {
                userToken = null;
                userProfile = null;
                if (userDisplayBottom) userDisplayBottom.textContent = "Gäst";
                if (logoutBtnBottom) logoutBtnBottom.classList.add('hidden');
                if (loginBtnBottom) loginBtnBottom.classList.remove('hidden');
                if (tierBadge) tierBadge.textContent = "GÄST";
                if (settingsTier) settingsTier.textContent = "GÄST";
                document.getElementById('session-list').innerHTML = `<p class="p-2 text-stone-600 italic">Logga in för samtalshistorik</p>`;
                loadJournal();
            }
        }

        async function fetchProfile() {
            if (!userToken) return;
            try {
                const res = await fetch('/api/profile', { headers: { 'Authorization': `Bearer ${userToken}` } });
                userProfile = await res.json();
            } catch (err) { console.error("Profile fetch fail", err); }
        }

        function closeAllDrawers() {
            document.getElementById('sidebar-drawer').classList.add('-translate-x-full');
            document.getElementById('progress-drawer').classList.add('translate-x-full');
            document.getElementById('sidebar-overlay').classList.add('hidden');
        }

        function toggleSidebar() {
            const drawer = document.getElementById('sidebar-drawer');
            const overlay = document.getElementById('sidebar-overlay');
            if (drawer.classList.contains('-translate-x-full')) {
                closeAllDrawers();
                drawer.classList.remove('-translate-x-full');
                overlay.classList.remove('hidden');
            } else closeAllDrawers();
        }

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

        
function switchTab(tab) {
    if (tab === 'journal' || tab === 'progress') {
        if (typeof closeAllDrawers === 'function') closeAllDrawers();
        if (typeof toggleProgressDrawer === 'function') toggleProgressDrawer();
        return;
    }
    console.log("Navigerar till vy:", tab);
    try {
        if (typeof closeAllDrawers === 'function') closeAllDrawers();
        
        // Dölj alla kända vyer säkert
        const allViews = ['view-chat', 'view-journal', 'view-library', 'view-settings'];
        allViews.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.add('hidden');
        });

        // Bestäm mål-ID
        let targetId = 'view-chat';
        if (tab === 'library') targetId = 'view-library';
        else if (tab === 'settings') targetId = 'view-settings';
        else if (tab === 'journal') targetId = 'view-journal';
        else if (tab === 'chat') targetId = 'view-chat';
        else if (tab) targetId = 'view-' + tab;

        const targetEl = document.getElementById(targetId);
        if (targetEl) {
            targetEl.classList.remove('hidden');
            console.log("Framgångsrikt visade vy:", targetId);
        } else {
            console.warn("Vy hittades inte för targetId:", targetId, "- Kör fallback till view-chat");
            const defaultView = document.getElementById('view-chat');
            if (defaultView) defaultView.classList.remove('hidden');
        }

        // Om vi växlar till inställningar, hämta profil
        if (targetId === 'view-settings' && typeof fetchProfile === 'function') {
            fetchProfile();
        }
    } catch (err) {
        console.error("Fel i switchTab, återgår säkert till chatten:", err);
        const defaultView = document.getElementById('view-chat');
        if (defaultView) defaultView.classList.remove('hidden');
    }
}


        function hidePrompts() {
            const cards = document.getElementById('onboarding-cards');
            if (cards) cards.classList.add('hidden');
            const checkin = document.getElementById('daily-checkin-card');
            if (checkin) checkin.classList.add('hidden');
        }

        function selectOnboarding(text) {
            hidePrompts();
            const input = document.getElementById('message-input');
            if (input) input.value = text;
            sendMessage(new Event('submit'));
        }

        function launchProtocol(promptText) {
            switchTab('chat');
            const input = document.getElementById('message-input');
            if (input) input.value = promptText;
            sendMessage(new Event('submit'));
        }

       async function loadSessions() {
            if (!userToken) return;
            let sessions = [];
            try {
                const res = await fetch('/api/sessions', { headers: { 'Authorization': `Bearer ${userToken}` } });
                if (!res.ok) throw new Error(`API returnerade status ${res.status}`);
                sessions = await res.json();
            } catch (err) {
                console.error("[NETWORK ERROR] Misslyckades att hämta sessioner:", err);
                sessions = []; // Fallback för att förhindra krasch i gränssnittet
            }
            const list = document.getElementById('session-list');
            if (!list) return;
            list.innerHTML = '';

            if (!Array.isArray(sessions)) return;
            // Om användaren har en aktiv chatt i DOM men saknar session-ID, skapa en ny session för användaren
            const hasMessages = document.getElementById('chat-messages-list')?.children.length > 0;
            if (hasMessages && !activeSessionId) {
                try {
                    const createRes = await fetch('/api/sessions', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${userToken}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title: "Samtal från gästsession" })
                    });
                    if (createRes.ok) {
                        const newSess = await createRes.json();
                        activeSessionId = newSess.id;
                        sessions.unshift(newSess);
                    }
                } catch (e) {
                    console.error("Kunde inte migrera gästsession:", e);
                }
            }
        sessions.sort((a, b) => {
                const isAPinned = pinnedSessions.includes(a.id);
                const isBPinned = pinnedSessions.includes(b.id);
                if (isAPinned && !isBPinned) return -1;
                if (!isAPinned && isBPinned) return 1;
                return 0;
            });

            sessions.forEach(s => {
                const isPinned = pinnedSessions.includes(s.id);
                const item = document.createElement('div');
                item.className = `group flex items-center justify-between p-2 rounded-lg text-xs transition ${activeSessionId === s.id ? 'bg-stone-200 text-deep-olive font-bold' : 'hover:bg-stone-200/50 text-stone-700'}`;
                
                const titleBtn = document.createElement('button');
                titleBtn.className = "truncate flex-1 text-left flex items-center space-x-1.5";
                titleBtn.innerHTML = `${isPinned ? '<span class="text-terracotta">📌</span>' : ''}<span class="truncate">${s.title}</span>`;
                titleBtn.onclick = () => selectSession(s.id);

                const actionsDiv = document.createElement('div');
                actionsDiv.className = "flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition";

                const pinBtn = document.createElement('button');
                pinBtn.className = "p-1 hover:text-terracotta text-stone-600 transition";
                pinBtn.title = isPinned ? "Lossa samtal" : "Nåla samtal";
                pinBtn.innerHTML = `<svg class="w-3.5 h-3.5" fill="${isPinned ? 'currentColor' : 'none'}" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M5 5h14l-4 4v6l2 2v1H7v-1l2-2V9L5 5z"/></svg>`;
                pinBtn.onclick = (e) => { e.stopPropagation(); togglePinSession(s.id); };

                const delBtn = document.createElement('button');
                delBtn.className = "p-1 hover:text-rose-600 text-stone-600 transition";
                delBtn.title = "Radera samtal";
                delBtn.innerHTML = `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>`;
                delBtn.onclick = (e) => { e.stopPropagation(); deleteSession(s.id); };

                actionsDiv.appendChild(pinBtn);
                actionsDiv.appendChild(delBtn);
                item.appendChild(titleBtn);
                item.appendChild(actionsDiv);
                list.appendChild(item);
            });
        }

        function togglePinSession(id) {
            if (pinnedSessions.includes(id)) pinnedSessions = pinnedSessions.filter(item => item !== id);
            else pinnedSessions.push(id);
            localStorage.setItem('falk_pinned_sessions', JSON.stringify(pinnedSessions));
            loadSessions();
        }

        async function deleteSession(id) {
            const confirmed = await customConfirm("Vill du radera detta samtal permanent?", "Radera samtal");
            if (!confirmed) return;
            if (userToken) {
                await fetch(`/api/sessions/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${userToken}` } });
            }
            if (activeSessionId === id) {
                activeSessionId = null;
                document.getElementById('chat-messages-list').innerHTML = '';
            }
            loadSessions();
        }

        async function createNewSession() {
    closeAllDrawers();
    if (typeof switchTab === 'function') switchTab('chat');
            if (!userToken) return openAuthModal();
            const res = await fetch('/api/sessions', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${userToken}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: "Nytt samtalsrum" })
            });
            const s = await res.json();
            if (s.id) {
                activeSessionId = s.id;
                document.getElementById('chat-messages-list').innerHTML = '';
                const cards = document.getElementById('onboarding-cards');
                if (cards) cards.classList.remove('hidden');
                switchTab('chat');
                loadSessions();
            }
        }

        async function selectSession(id) {
            activeSessionId = id;
            loadSessions();
            closeAllDrawers();
            hidePrompts();

            const res = await fetch(`/api/sessions/${id}/messages`, { headers: { 'Authorization': `Bearer ${userToken}` } });
            const messages = await res.json();
            const list = document.getElementById('chat-messages-list');
            if (!list) return;
            list.innerHTML = '';
            
            if (messages.length > 0) hidePrompts();
            messages.forEach(m => appendMessage(m.sender === 'user' ? 'Du' : 'FALK', m.content, m.sender));
        }

        let isRecording = false;
        let recognition = null;

        function toggleSpeechRecognition() {
            const micBtn = document.getElementById('mic-btn');
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                return showAlert("Tal-till-text stöds inte i din webbläsare.");
            }

            if (isRecording) {
                if (recognition) recognition.stop();
                isRecording = false;
                micBtn.classList.remove('text-rose-600', 'animate-pulse');
                micBtn.classList.add('text-stone-600');
            } else {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.lang = 'sv-SE';
                recognition.onstart = function() {
                    isRecording = true;
                    micBtn.classList.remove('text-stone-600');
                    micBtn.classList.add('text-rose-600', 'animate-pulse');
                };
                recognition.onresult = function(event) {
                    document.getElementById('message-input').value += event.results[0][0].transcript;
                };
                recognition.onend = function() {
                    isRecording = false;
                    micBtn.classList.remove('text-rose-600', 'animate-pulse');
                    micBtn.classList.add('text-stone-600');
                };
                recognition.start();
            }
        }

        function updateFocusVal(key) {
            const val = document.getElementById(`slider-${key}`).value;
            focusState[key] = parseInt(val);
            document.getElementById(`val-${key}`).textContent = `${val}%`;
            const prog = document.getElementById(`prog-${key}`);
            const bar = document.getElementById(`bar-${key}`);
            if (prog) prog.textContent = `${val}%`;
            if (bar) bar.style.width = `${val}%`;
        }

        function resetFocusSliders() {
            ['confidence', 'stress', 'action', 'boundaries', 'motivation'].forEach(k => {
                document.getElementById(`slider-${k}`).value = 50;
                updateFocusVal(k);
            });
        }

        function openFocusModal() { document.getElementById('focus-modal').classList.remove('hidden'); }
        function closeFocusModal() { document.getElementById('focus-modal').classList.add('hidden'); }

        async function sendMessage(e) {
    if (e && typeof e.preventDefault === 'function') e.preventDefault();
    if (window.isSendingMessage) return;

    const input = document.getElementById('message-input');
    const btn = document.getElementById('send-btn');
    const message = input ? input.value.trim() : '';

    if (!message) return;

    window.isSendingMessage = true;
            checkForCrisisKeywords(message);
            hidePrompts();

            if (!activeSessionId && userToken) {
                try {
                    await createNewSession();
                } catch (err) {
                    console.error("Fel vid skapande av session:", err);
                }
            }

            appendMessage('Du', message, 'user');
            if (input) input.value = '';
            if (btn) btn.disabled = true;

            const thinkingId = showThinkingIndicator();

            try {
                const headers = { 'Content-Type': 'application/json' };
                if (userToken) headers['Authorization'] = `Bearer ${userToken}`;

                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ 
                        message: message, 
                        session_id: activeSessionId,
                        focus: focusState
                    })
                });
                if (res.status === 403 || res.status === 429) {
                    window.isSendingMessage = false;
                    if (typeof removeThinkingIndicator === 'function' && typeof thinkingId !== 'undefined') {
                        removeThinkingIndicator(thinkingId);
                    }
                    if (typeof openPaywallModal === 'function') openPaywallModal();
                    else {
                        const pm = document.getElementById('paywall-modal');
                        if (pm) pm.classList.remove('hidden');
                    }
                    return;
                }

                removeThinkingIndicator(thinkingId);

                if (res.status === 403) {
                    if (typeof window.openPaywallModal === 'function') window.openPaywallModal('limit');
                    return;
                }

                if (!res.ok) { console.error('Session API Error:', res.status); return; }
                const data = await res.json();

                if (res.ok) {
                    appendMessage('FALK', data.response, 'bot');
                    loadSessions();
                } else {
                    appendMessage('FALK', data.error || 'Ett fel uppstod.', 'error');
                }
            } catch (err) {
                removeThinkingIndicator(thinkingId);
                appendMessage('FALK', 'Kunde inte ansluta till servern.', 'error');
            } finally {
                window.isSendingMessage = false;
                if (btn) btn.disabled = false;
            }
        }

        function showThinkingIndicator() {
            const list = document.getElementById('chat-messages-list');
            if (!list) return null;
            const id = 'thinking-' + Math.random().toString(36).substr(2, 9);
            const container = document.createElement('div');
            container.id = id;
            container.className = "flex flex-col items-start space-y-1.5 my-2";
            container.innerHTML = `<div class="bg-white/90 border border-stone-200/80 px-4 py-3 rounded-2xl text-xs text-stone-600 shadow-sm flex items-center space-x-2"><span class="w-2 h-2 bg-deep-olive rounded-full animate-pulse"></span><span class="italic">FALK tänker...</span></div>`;
            list.appendChild(container);
            const containerBox = document.getElementById('chat-container');
            if (containerBox) containerBox.scrollTop = containerBox.scrollHeight;
            return id;
        }

        function removeThinkingIndicator(id) {
            if (!id) return;
            const el = document.getElementById(id);
            if (el) el.remove();
        }

        function appendMessage(sender, text, type) {
            const list = document.getElementById('chat-messages-list');
            if (!list) return;
            hidePrompts();

            const container = document.createElement('div');
            if (type === 'user') {
                container.className = "flex justify-end";
                container.innerHTML = `<div class="bg-bubble-user text-amber-50 px-4 py-3 rounded-2xl max-w-[85%] text-xs shadow-sm">${text}</div>`;
            } else {
                container.className = "flex flex-col items-start space-y-1.5";
                const msgId = 'msg-' + Math.random().toString(36).substr(2, 9);
                container.innerHTML = `
                    <div class="bg-white/90 border border-stone-200/80 text-stone-800 px-4 py-3 rounded-2xl max-w-[90%] text-xs shadow-sm leading-relaxed" id="${msgId}">${text}</div>
                    <div class="icon-bar ${ (userToken || document.body.classList.contains('is-logged-in')) ? 'flex' : 'hidden'} items-center space-x-1 mt-1.5 px-1 py-0.5 text-stone-600">
                <!-- 1. Högtalare -->
                <button type="button" onclick="speakText('${msgId}')" class="p-1 hover:text-stone-700 transition flex items-center justify-center text-stone-600" title="Läs upp meddelande">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5 5 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.414 0-.75-.336-.75-.75V9c0-.414.336-.75.75-.75h2.24z"/></svg>
                </button>
                <!-- 2. Generera nytt -->
                <button type="button" onclick="regenerateLastMessage()" class="p-1 hover:text-stone-700 transition flex items-center justify-center text-stone-600" title="Generera nytt svar">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/></svg>
                </button>
                <!-- 3. Tumme upp -->
                <button type="button" onclick="rateResponse('${msgId}', 'up', this)" class="btn-thumb-up p-1 hover:text-stone-700 transition flex items-center justify-center text-stone-600" title="Bra svar">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6.633 10.5c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 01.75-.75A2.25 2.25 0 0116.5 4.5c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.128 1.2-.083 2.408-.52 3.518l-1.572 3.93a2.25 2.25 0 01-2.09 1.414H9.728c-.538 0-1.054-.195-1.458-.55L5.25 16.5M6.633 10.55V18a2.25 2.25 0 01-2.25 2.25H3.75A2.25 2.25 0 011.5 18v-5.25c0-1.243 1.007-2.25 2.25-2.25h2.883z"/></svg>
                </button>
                <!-- 4. Tumme ner -->
                <button type="button" onclick="rateResponse('${msgId}', 'down', this)" class="btn-thumb-down p-1 hover:text-stone-700 transition flex items-center justify-center text-stone-600" title="Mindre bra svar">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17.367 13.5c-.806 0-1.533.446-2.031 1.08a9.041 9.041 0 01-2.861 2.4c-.723.384-1.35.956-1.653 1.715a4.498 4.498 0 00-.322 1.672V21a.75.75 0 01-.75.75A2.25 2.25 0 017.5 19.5c0-1.152.26-2.243.723-3.218.266-.558-.107-1.282-.725-1.282H4.372c-1.026 0-1.945-.694-2.054-1.715a12.137 12.137 0 01.52-3.518l1.572-3.93a2.25 2.25 0 012.09-1.414h7.901c.538 0 1.054.195 1.458.55l3.02 2.55M17.367 13.45V6a2.25 2.25 0 012.25-2.25h.375A2.25 2.25 0 0122.5 6v5.25c0 1.243-1.007 2.25-2.25 2.25h-2.883z"/></svg>
                </button>
                <!-- 5. Minus -->
                <button type="button" onclick="adjustLastResponse('minus')" class="p-1 hover:text-stone-700 transition flex items-center justify-center text-stone-600" title="Gör svaret mer kortfattat">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12h-15"/></svg>
                </button>
                <!-- 6. Plus -->
                <button type="button" onclick="adjustLastResponse('plus')" class="p-1 hover:text-stone-700 transition flex items-center justify-center text-stone-600" title="Fördjupa svaret">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
                </button>
                <!-- 7. Påminnelse -->
                <button type="button" onclick="openReminderModal('${msgId}')" class="p-1 hover:text-stone-700 transition flex items-center justify-center text-stone-600" title="Skapa påminnelse">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                </button>
            </div>`;
            }
            list.appendChild(container);
            const containerBox = document.getElementById('chat-container');
            if (containerBox) containerBox.scrollTop = containerBox.scrollHeight;
        }

        function speakText(id) {
            const el = document.getElementById(id);
            if (!el) return;
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(el.textContent);
                utterance.lang = 'sv-SE';
                window.speechSynthesis.speak(utterance);
            }
        }

        function openReminderModal(textOrId) {
            const el = document.getElementById(textOrId);
            pendingReminderText = el ? el.textContent.trim() : textOrId;
            const input = document.getElementById('reminder-quote-input');
            if (input) input.value = pendingReminderText;
            document.getElementById('reminder-modal').classList.remove('hidden');
        }

        function closeReminderModal() { document.getElementById('reminder-modal').classList.add('hidden'); }

        async function saveReminderModalSubmit() {
            const quoteInput = document.getElementById('reminder-quote-input');
            const customText = quoteInput ? quoteInput.value.trim() : pendingReminderText;
            const timeVal = document.getElementById('reminder-time').value;
            const freqVal = document.getElementById('reminder-freq').value;
            const saveJournal = document.getElementById('reminder-save-journal').checked;

            if (saveJournal) await saveJournalEntryDirect(4, `Påminnelse [${freqVal} kl ${timeVal}]: ${customText}`);
            closeReminderModal();
            showAlert(`Påminnelse sparad klockan ${timeVal}!`);
        }

        function setMood(score) {
            selectedMood = score;
            document.querySelectorAll('.mood-btn').forEach(btn => btn.className = "mood-btn flex-1 py-2 bg-stone-100 border border-stone-300 rounded-xl text-sm font-semibold text-stone-800 transition");
            const activeBtn = document.querySelector(`.mood-btn[data-score="${score}"]`);
            if (activeBtn) activeBtn.className = "mood-btn flex-1 py-2 bg-deep-olive text-amber-50 border border-deep-olive rounded-xl text-sm font-bold transition shadow-sm";
        }

        async function saveJournalEntry(e) {
            if (e && e.preventDefault) e.preventDefault();
            const input = document.getElementById('journal-text');
            const text = input ? input.value.trim() : '';
            if (!text) return;
            await saveJournalEntryDirect(selectedMood, text);
            if (input) input.value = '';
        }

        async function saveJournalEntryDirect(score, text) {
            if (userToken) {
                try {
                    await fetch('/api/journal', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${userToken}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ mood_score: score, entry_text: text })
                    });
                } catch (err) { console.error("Kunde inte spara till backend", err); }
            }
            let localEntries = JSON.parse(localStorage.getItem('falk_guest_journal') || '[]');
            localEntries.unshift({ id: 'local-' + Math.random().toString(36).substr(2, 9), mood_score: score, entry_text: text, created_at: new Date().toISOString() });
            localStorage.setItem('falk_guest_journal', JSON.stringify(localEntries));
            loadJournal();
        }

        async function loadJournal() {
            let entries = [];
            if (userToken) {
                try {
                    const res = await fetch('/api/journal', { headers: { 'Authorization': `Bearer ${userToken}` } });
                    if (res.ok) {
                        entries = await res.json();
                    } else {
                        console.error('Journal API Error:', res.status);
                    }
                } catch (err) { console.error("API error", err); }
            }
            if (!entries || entries.length === 0) entries = JSON.parse(localStorage.getItem('falk_guest_journal') || '[]');
            if (Array.isArray(entries)) { renderJournalList(entries); }
        }

        function renderJournalList(entries) {
            const list = document.getElementById('journal-list') || document.getElementById('journal-entries-list');
            if (!list) return;
            list.innerHTML = '';
            
            const statCount = document.getElementById('stat-entries-count');
            if (statCount) statCount.textContent = entries.length;
            
            if (entries.length === 0) { 
                list.innerHTML = `<p class="text-stone-600 text-xs italic">Inga reflektioner sparade ännu.</p>`; 
                return; 
            }

            const moodEmojis = ['', '😞', '😐', '🙂', '😊', '🤩'];
            entries.forEach(e => {
                const div = document.createElement('div');
                div.className = "bg-white p-3.5 rounded-xl border border-stone-200 text-xs space-y-1 shadow-sm flex justify-between items-start";
                
                // 1. Bygg det ofarliga skelettet utan användardata
                div.innerHTML = `
                    <div class="space-y-1 flex-1 pr-2">
                        <div class="flex justify-between items-center font-bold text-stone-500">
                            <span>Status: ${moodEmojis[e.mood_score] || '🙂'} (${e.mood_score}/5)</span>
                            <span>${new Date(e.created_at).toLocaleDateString('sv-SE')}</span>
                        </div>
                        <p class="entry-text-container text-stone-800 leading-relaxed whitespace-pre-wrap"></p>
                    </div>
                    <div class="flex items-center space-x-1">
                        <button type="button" class="reminder-btn p-1 hover:text-deep-olive text-stone-600 transition" title="Sätt påminnelse">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        </button>
                        <button type="button" class="delete-btn p-1 hover:text-rose-600 text-stone-600 transition" title="Radera reflektion">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                        </button>
                    </div>
                `;

                // 2. Injicera farlig text säkert via textContent (neutraliserar HTML/XSS)
                div.querySelector('.entry-text-container').textContent = e.entry_text;

                // 3. Koppla händelser programmatiskt (immunt mot citattecken och radbrytningar)
                div.querySelector('.reminder-btn').addEventListener('click', () => openReminderModal(e.entry_text));
                div.querySelector('.delete-btn').addEventListener('click', () => deleteJournalEntry(e.id));

                list.appendChild(div);
            });
        }

        async function deleteJournalEntry(id) {
            const confirmed = await customConfirm("Vill du radera denna reflektion permanent?", "Radera reflektion");
            if (!confirmed) return;
            if (userToken && !id.startsWith('local-')) {
                await fetch(`/api/journal/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${userToken}` } });
            }
            let localEntries = JSON.parse(localStorage.getItem('falk_guest_journal') || '[]');
            localEntries = localEntries.filter(e => e.id !== id);
            localStorage.setItem('falk_guest_journal', JSON.stringify(localEntries));
            loadJournal();
        }

        async function exportMyData() {
            if (!userToken) return openAuthModal();
            try {
                const res = await fetch('/api/export-user-data', { headers: { 'Authorization': `Bearer ${userToken}` } });
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `falk_userdata_${new Date().toISOString().slice(0, 10)}.json`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } catch (err) { showAlert("Nätverksfel vid export."); }
        }

        async function deleteMyData() {
            const confirmed = await customConfirm("Är du helt säker? Detta raderar permanent ditt konto och all din samtalshistorik.", "Radera konto");
            if (!confirmed) return;
            if (userToken) {
                await fetch('/delete-user-data', { method: 'DELETE', headers: { 'Authorization': `Bearer ${userToken}` } });
            }
            localStorage.clear();
            location.reload();
        }

        function openAuthModal() { document.getElementById('auth-modal').classList.remove('hidden'); }
        function closeAuthModal() { document.getElementById('auth-modal').classList.add('hidden'); }
        function openPrivacyPolicyModal() { document.getElementById('privacy-modal').classList.remove('hidden'); }
        function closePrivacyPolicyModal() { document.getElementById('privacy-modal').classList.add('hidden'); }

        async function resendVerificationEmail(btnEl) {
            const email = document.getElementById('auth-identifier')?.value.trim();
            if (!email) return showAuthError("Ange din e-postadress i fältet ovan.");
            
            if (btnEl) {
                btnEl.disabled = true;
                btnEl.textContent = "Skickar nytt mail...";
            }
            
            try {
                const redirectUrl = window.location.origin;
                const res = await supabaseClient.auth.resend({
                    type: 'signup',
                    email: email,
                    options: { emailRedirectTo: redirectUrl }
                });
                
                if (res.error) {
                    let errStr = res.error.message;
                    if (errStr.includes("rate limit")) errStr = "Du måste vänta en stund innan du skickar igen.";
                    showAuthError("Kunde inte skicka: " + errStr);
                } else {
                    showAlert("Ett nytt bekräftelsemail har skickats till " + email);
                    if (btnEl) btnEl.textContent = "Bekräftelsemail skickat!";
                }
            } catch (err) {
                showAuthError("Ett fel uppstod vid utskick av bekräftelsemail.");
            } finally {
                if (btnEl && !btnEl.textContent.includes("skickat")) {
                    btnEl.disabled = false;
                    btnEl.textContent = "Skicka nytt bekräftelsemail";
                }
            }
        }

        function showAuthError(msg) {
            const errBox = document.getElementById('auth-error-msg');
            if (errBox) {
                let friendlyMsg = msg;
                let showResend = false;
                if (msg.includes("Invalid login credentials")) {
                    friendlyMsg = "Felaktig e-postadress eller lösenord.";
                } else if (msg.includes("User already registered")) {
                    friendlyMsg = "E-postadressen är redan registrerad.";
                } else if (msg.includes("Password should be at least")) {
                    friendlyMsg = "Lösenordet måste vara minst 6 tecken.";
                } else if (msg.includes("Email not confirmed")) {
                    friendlyMsg = "E-postadressen har inte bekräftats ännu.";
                    showResend = true;
                }
                
                if (showResend) {
                    errBox.innerHTML = `<div>${friendlyMsg}</div><button type="button" onclick="resendVerificationEmail(this)" class="underline font-bold mt-1.5 text-amber-900 hover:text-stone-900 block text-xs">Skicka nytt bekräftelsemail</button><div id="resend-status-msg" class="text-[11px] text-rose-700 font-normal mt-1 hidden"></div>`;
                } else {
                    errBox.textContent = friendlyMsg;
                }
                errBox.classList.remove('hidden');
            }
        }

        function clearAuthError() {
            const errBox = document.getElementById('auth-error-msg');
            if (errBox) {
                errBox.textContent = '';
                errBox.classList.add('hidden');
            }
        }

        async function submitAuth() {
            clearAuthError();
            const identifier = document.getElementById('auth-identifier').value.trim();
            const password = document.getElementById('auth-password').value.trim();
            if (!identifier || !password) return showAuthError("Fyll i alla fält.");

            if (currentAuthMode === 'signup') {
                const username = document.getElementById('auth-username').value.trim();
                const gdprCheck = document.getElementById('auth-gdpr-check').checked;
                if (!username || !gdprCheck) return showAuthError("Godkänn villkoren och fyll i användarnamn.");

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

        async function logout() {
            if (supabaseClient) await supabaseClient.auth.signOut();
            localStorage.clear();
            location.reload();
        }

        try {
            initAuth();
        } catch (err) {
            console.error("[BOOT ERROR] initAuth failed:", err);
        }
    

      // Omdirigera om användaren klickat på dashboarden innan login
      if (window.pendingViewAfterAuth === 'dashboard') {
        window.pendingViewAfterAuth = null;
// --- Extracted Script Block --- 
// ==========================================
// UNIFIERAD OCH SKOTTSÄKER AKTIONS-MOTOR
// ==========================================

let activeTTSUtterance = null;
let activeTTSBtn = null;

// 1. HÖGTALARE (speakText) - MED SÄKER TOGGLE-BROMS
window.speakText = function(msgId) {
    if (!('speechSynthesis' in window)) {
        alert("Text-till-tal stöds inte i din webbläsare.");
        return;
    }

    const btn = (typeof event !== 'undefined' && event) ? (event.currentTarget || event.target) : null;

    // Om ljud spelas: STOPPA OMEDELBART
    if (window.speechSynthesis.speaking || window.speechSynthesis.pending) {
        window.speechSynthesis.cancel();
        if (activeTTSBtn) {
            activeTTSBtn.classList.remove('text-amber-600', 'animate-pulse');
            activeTTSBtn.classList.add('text-stone-600');
        }
        // Klick på samma knapp igen = tystnad
        if (activeTTSBtn === btn) {
            activeTTSBtn = null;
            return;
        }
    }

    // Hämta text ur chattbubbla eller fallback till sista bot-meddelandet
    let text = "";
    const msgContainer = document.getElementById(`msg-${msgId}`) || document.querySelector(`[data-id="${msgId}"]`);
    if (msgContainer) {
        text = msgContainer.innerText || msgContainer.textContent;
    } else {
        const botMsgs = document.querySelectorAll('.bot-message, .assistant-message, [data-sender="bot"]');
        if (botMsgs.length > 0) {
            text = botMsgs[botMsgs.length - 1].innerText;
        }
    }

    if (!text.trim()) {
        console.warn("Hittade ingen text att läsa upp.");
        return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text.trim());
    utterance.lang = 'sv-SE';
    utterance.rate = 0.95;

    activeTTSBtn = btn;
    if (btn) {
        btn.classList.remove('text-stone-600');
        btn.classList.add('text-amber-600', 'animate-pulse');
    }

    utterance.onend = utterance.onerror = function() {
        if (btn) {
            btn.classList.remove('text-amber-600', 'animate-pulse');
            btn.classList.add('text-stone-600');
        }
        activeTTSBtn = null;
    };

    window.speechSynthesis.speak(utterance);
};

// 2. PLUS / MINUS (adjustLastResponse) - KOPPLAD MOT message-input OCH send-btn
window.adjustLastResponse = function(action) {
    let promptText = "";
    if (action === 'minus') {
        promptText = "Gör ditt förra svar kortare och mer koncist.";
    } else if (action === 'plus') {
        promptText = "Utveckla ditt förra svar lite djupare och ge mer kontext.";
    } else {
        promptText = action;
    }

    const inputField = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    if (inputField && sendBtn) {
        inputField.value = promptText;
        sendBtn.click();
    } else {
        console.error("DOM Error: Hittade inte #message-input eller #send-btn");
    }
};

// 3. REGENERERA (regenerateLastMessage)
window.regenerateLastMessage = function() {
    window.adjustLastResponse("Formulera om ditt förra svar på ett nytt sätt.");
};

// 4. BETYG (rateResponse)
window.rateResponse = function(msgId, direction, btnElement) {
    if (btnElement) {
        btnElement.classList.toggle('text-amber-600');
    }
    fetch('/api/feedback', {
        method: 'POST',
        headers: (function() {
        const h = { 'Content-Type': 'application/json' };
        if (typeof userToken !== 'undefined' && userToken) {
          h['Authorization'] = 'Bearer ' + userToken;
        } else if (window.supabaseClient && window.supabaseClient.auth) {
          const session = typeof supabaseClient.auth.session === 'function' ? supabaseClient.auth.session() : null;
          if (session && session.access_token) h['Authorization'] = 'Bearer ' + session.access_token;
        }
        return h;
      })(),
        body: JSON.stringify({ message_id: msgId, direction: direction })
          el.classList.add('bg-[#2C3E35]', 'text-white');
        });
      }

      // Dölj auth-modalen
      const authModal = document.getElementById('auth-modal');
      if (authModal) authModal.classList.add('hidden');

      // Omdirigera om användaren klickat på dashboarden innan login
      if (window.pendingViewAfterAuth === 'dashboard') {
        window.pendingViewAfterAuth = null;
        openDashboardView();
      }
    }
  } catch (err) {
    console.error("Login exception:", err);
    alert("Ett oväntat fel uppstod vid inloggning.");
  }

  return false;

// --- Extracted Script Block --- 
// ==========================================
// IN-PLACE VERSIONERING OCH PAGINERINGS-MOTOR
// ==========================================

window.msgStore = window.msgStore || {};
window.lastBotMsgId = null;

// 1. REFFA APPENDMESSAGE FÖR ATT SPÅRA VERSIONER
// appendMessage hanteras i Block #5

// 2. TYST BAKGRUNDSANROP FÖR PLUS / MINUS / REGENERERA
window.adjustLastResponse = async function(action) {
    const msgId = window.lastBotMsgId;
    if (!msgId || !window.msgStore[msgId]) {
        console.warn("Inget giltigt bot-meddelande att justera.");
        return;
    }

    const msgElem = document.getElementById(msgId);
    if (!msgElem) return;

    const contentDiv = msgElem.querySelector('.msg-content') || msgElem;
    const store = window.msgStore[msgId];
    const currentVersionCount = store.versions.length; // 1 = original, 2 = 1:a fördjupning, etc.

    let instruction = "";
    if (action === 'minus') {
        instruction = "[SYSTEM-INSTRUKTION: Ge ett mycket kortare, mer direkt och kärnfullt Sokratiskt svar (max 100 ord). AVSLUTA ALLTID din sista mening helt. Kommentera ELLER bekräfta INTE denna instruktion.]";
    } else if (action === 'plus') {
        if (currentVersionCount <= 1) {
            // NIVÅ 1 FÖRDJUPNING (~300-400 tokens / 200-250 ord)
            instruction = "[SYSTEM-INSTRUKTION: Fördjupa resonemanget med måttlig detaljrikedom (ca 200-250 ord). Belys underliggande antaganden och ge ett fylligare perspektiv. VIKTIGT: Du MÅSTE avsluta din sista mening helt med punkt eller frågetecken. Klipp ALDRIG av en mening mitt i. Gå direkt in i reflektionen utan meta-kommentarer.]";
        } else {
            // NIVÅ 2 FÖRDJUPNING (~500-600 tokens / 350-400 ord)
            instruction = "[SYSTEM-INSTRUKTION: Ge en maximalt djup och heltäckande Sokratisk analys (ca 350-400 ord). Utforska målkonflikter, blinda fläckar och handlingsvägar i grunden. VIKTIGT: Du MÅSTE avsluta din sista mening helt med punkt eller frågetecken. Klipp ALDRIG av en mening mitt i. Gå direkt in i reflektionen utan meta-kommentarer.]";
        }
    } else {
        instruction = action;
    }

    const originalText = contentDiv.innerHTML;
    contentDiv.innerHTML = `<span class="animate-pulse text-stone-600">FALK tänker...</span>`;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: (function() {
        const h = { 'Content-Type': 'application/json' };
        if (typeof userToken !== 'undefined' && userToken) {
          h['Authorization'] = 'Bearer ' + userToken;
        } else if (window.supabaseClient && window.supabaseClient.auth) {
          const session = typeof supabaseClient.auth.session === 'function' ? supabaseClient.auth.session() : null;
          if (session && session.access_token) h['Authorization'] = 'Bearer ' + session.access_token;
        }
        return h;
      })(),
            body: JSON.stringify({ message: instruction })
        });

        if (response.status === 403) {
            if (typeof window.openPaywallModal === 'function') window.openPaywallModal('limit');
            contentDiv.innerHTML = originalText;
            return;
        }
        if (!response.ok) {
            console.error("Session API Error:", response.status);
            contentDiv.innerHTML = originalText;
            return;
        }

        const data = await response.json();
        const newReply = data.response || data.reply || "Kunde inte generera variant.";

        store.versions.push(newReply);
        store.currentIndex = store.versions.length - 1;

        window.renderMessageVersion(msgId);
    } catch (err) {
        console.error("Fel vid skapande av variant:", err);
        contentDiv.innerHTML = originalText;
    }
};

// 3. RENDERING AV SPECIFIK VERSION OCH PAGINERING
window.renderMessageVersion = function(msgId) {
    const store = window.msgStore[msgId];
    if (!store) return;

    const msgElem = document.getElementById(msgId);
    if (!msgElem) return;

    const contentDiv = msgElem.querySelector('.msg-content') || msgElem;
    contentDiv.innerText = store.versions[store.currentIndex];

    // Uppdatera pagineringselementet
    const pageControls = document.getElementById(`page-controls-${msgId}`);
    if (pageControls && store.versions.length > 1) {
        pageControls.classList.remove('hidden');
        pageControls.innerHTML = `
            <button type="button" onclick="window.navigateVersion('${msgId}', -1)" class="hover:text-stone-900 px-0.5 ${store.currentIndex === 0 ? 'opacity-30 cursor-default' : ''}">&lt;</button>
            <span>${store.currentIndex + 1}/${store.versions.length}</span>
            <button type="button" onclick="window.navigateVersion('${msgId}', 1)" class="hover:text-stone-900 px-0.5 ${store.currentIndex === store.versions.length - 1 ? 'opacity-30 cursor-default' : ''}">&gt;</button>
        `;
    }
};

// 4. NAVIGERA MELLAN VERSIONER
window.navigateVersion = function(msgId, direction) {
    const store = window.msgStore[msgId];
    if (!store) return;

    const newIndex = store.currentIndex + direction;
    if (newIndex >= 0 && newIndex < store.versions.length) {
        store.currentIndex = newIndex;
        window.renderMessageVersion(msgId);
    }
};

  // [Orphaned login block purged]

  const email = emailEl.value.trim();
  const password = passEl.value;

  if (!email || !password) {
    alert("Fyll i både e-post och lösenord.");
    return false;
  }

  const sb = window.supabase || window.supabaseClient;
  if (!sb || !sb.auth) {
    alert("Supabase-klienten är inte redo.");
    return false;
  }

  try {
    const { data, error } = await sb.auth.signInWithPassword({ email, password });
    if (error) {
      alert("Inloggningsfel: " + error.message);
      return false;
    }

    if (data && data.session) {
      window.userToken = data.session.access_token;
      
      // REAKTIV UI-UPPDATERING DIREKT I DOM:EN (INGEN F5 KRÄVS)
      if (typeof updateAuthUI === 'function') {
        updateAuthUI(data.user);
      } else {
        const emailDisp = document.getElementById('user-email-display');
        if (emailDisp) emailDisp.innerText = data.user.email;
        
        const loggedInBox = document.getElementById('user-profile-logged-in');
        const loggedOutBox = document.getElementById('user-profile-logged-out');
        if (loggedInBox) loggedInBox.classList.remove('hidden');
        if (loggedOutBox) loggedOutBox.classList.add('hidden');

        document.querySelectorAll('.guest-badge, #user-status-badge, #user-tier-badge').forEach(el => {
          el.innerText = 'PREMIUM';
          el.classList.remove('bg-stone-200', 'text-stone-600');
          el.classList.add('bg-[#2C3E35]', 'text-white');
        });
      }

      // Dölj auth-modalen
      const authModal = document.getElementById('auth-modal');
      if (authModal) authModal.classList.add('hidden');

      // Omdirigera om användaren klickat på dashboarden innan login
      if (window.pendingViewAfterAuth === 'dashboard') {
        window.pendingViewAfterAuth = null;
        openDashboardView();
      }
    }
  } catch (err) {
    console.error("Login exception:", err);
    alert("Ett oväntat fel uppstod vid inloggning.");
  }

  return false;

// --- Extracted Script Block --- 
// Global user context
window.userTier = window.userTier || 'GUEST';


window.removeThinkingIndicator = function() {
    const thinkingEl = document.getElementById('falk-thinking') || document.querySelector('.falk-thinking');
    if (thinkingEl) thinkingEl.remove();
    document.querySelectorAll('div, p, span').forEach(el => {
        if (el.children.length === 0 && el.textContent.includes('FALK tänker...')) {
            const flexParent = el.closest('.flex');
            if (flexParent) flexParent.remove();
            else el.remove();
        }
    });
};

window.setUserTier = function(tier) {
    const normalizedTier = (tier || '').toUpperCase() === 'PREMIUM' ? 'PREMIUM' : 'GÄST';
    const badges = document.querySelectorAll('.tier-badge-element');
    badges.forEach(badge => {
        badge.textContent = normalizedTier;
        if (normalizedTier === 'PREMIUM') {
            badge.className = 'text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-800 border border-amber-500/30 transition';
        } else {
            badge.className = 'text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-stone-200 text-stone-600 transition';
        }
    });

    window.userTier = normalizedTier;
    document.querySelectorAll('.icon-bar').forEach(el => {
        if (normalizedTier === 'PREMIUM') {
            el.classList.add('pro-mode');
        } else {
            el.classList.remove('pro-mode');
        }
    });
};
    // Uppdatera alla befintliga ikonrader i chatt-historiken
    document.querySelectorAll('.icon-bar').forEach(el => {
        if (tier === 'PREMIUM') {
            el.classList.add('pro-mode');
        }
            el.classList.remove('hidden');
        } else {
            el.classList.add('hidden');
    // Om användaren blev PRO, stäng ev. öppen paywall
    if (tier === 'PREMIUM') {
        document.getElementById('paywall-modal')?.remove();
    }


// Lock menu / dev links for guests

window.handlePaywallAuth = function(mode, event) {
    if (event) event.preventDefault();
    const modal = document.getElementById('paywall-modal');
    if (modal) modal.remove();
    if (typeof openAuthModal === 'function') {
        openAuthModal(mode || 'login');
    } else if (typeof toggleAuthModal === 'function') {
        toggleAuthModal();
    }
    return false;
};

window.handleLockedFeature = function(featureName) {
    if (window.userTier !== 'PREMIUM') {
        window.openPaywallModal(featureName);
        return true;
    }
    return false;
};

window.openPaywallModal = function(reason) {
    let modal = document.getElementById('paywall-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'paywall-modal';
        modal.className = 'fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4';
        modal.innerHTML = `
            <div class="falk-modal-card rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl relative text-center">
                <button type="button" onclick="document.getElementById('paywall-modal').classList.add('hidden')" class="absolute top-4 right-4 text-stone-300 hover:text-white text-xl font-bold p-1">&times;</button>
                <div class="space-y-2">
                    <span class="falk-gold-badge-styled px-4 py-1.5 rounded-full text-xs uppercase inline-block mb-2">FALK Premium</span>
                    <h3 class="text-xl font-bold text-white">Lås upp FALK Premium</h3>
                    <p class="text-xs text-stone-200 leading-relaxed px-2">För att få tillgång till djupgående analyser, obegränsade samtal, minnesfunktioner och utvecklingsmenyn behöver du ett konto.</p>
                </div>
                <div class="space-y-3 pt-2">
                    <a href="#" onclick="window.handlePaywallAuth('signup', event); return false;" class="falk-paywall-btn">Skaffa Premium</a>
                    <a href="#" onclick="window.handlePaywallAuth('login', event); return false;" class="falk-paywall-btn">Logga in</a>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    } else {
        modal.classList.remove('hidden');
    }
};

  // [Orphaned login block purged]

  const email = emailEl.value.trim();
  const password = passEl.value;

  if (!email || !password) {
    alert("Fyll i både e-post och lösenord.");
    return false;
  }

  const sb = window.supabase || window.supabaseClient;
  if (!sb || !sb.auth) {
    alert("Supabase-klienten är inte redo.");
    return false;
  }

  try {
    const { data, error } = await sb.auth.signInWithPassword({ email, password });
    if (error) {
      alert("Inloggningsfel: " + error.message);
      return false;
    }

    if (data && data.session) {
      window.userToken = data.session.access_token;
      
      // REAKTIV UI-UPPDATERING DIREKT I DOM:EN (INGEN F5 KRÄVS)
      if (typeof updateAuthUI === 'function') {
        updateAuthUI(data.user);
      } else {
        const emailDisp = document.getElementById('user-email-display');
        if (emailDisp) emailDisp.innerText = data.user.email;
        
        const loggedInBox = document.getElementById('user-profile-logged-in');
        const loggedOutBox = document.getElementById('user-profile-logged-out');
        if (loggedInBox) loggedInBox.classList.remove('hidden');
        if (loggedOutBox) loggedOutBox.classList.add('hidden');

        document.querySelectorAll('.guest-badge, #user-status-badge, #user-tier-badge').forEach(el => {
          el.innerText = 'PREMIUM';
          el.classList.remove('bg-stone-200', 'text-stone-600');
          el.classList.add('bg-[#2C3E35]', 'text-white');
        });
      }

      // Dölj auth-modalen
      const authModal = document.getElementById('auth-modal');
      if (authModal) authModal.classList.add('hidden');

      // Omdirigera om användaren klickat på dashboarden innan login
      if (window.pendingViewAfterAuth === 'dashboard') {
        window.pendingViewAfterAuth = null;
        openDashboardView();
      }
    }
  } catch (err) {
    console.error("Login exception:", err);
    alert("Ett oväntat fel uppstod vid inloggning.");
  }

  return false;

// --- Extracted Script Block --- 
// === FALK DASHBOARD CONTROLLER ===
let falkRadarChartInstance = null;


// Fail-safe funktion för att alltid hämta giltig userToken från minne, Supabase eller localStorage
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

// Skriv över openDashboardView med fail-safe token-kontroll

async function openDashboardView(e) {
  if (e) {
    if (typeof e.preventDefault === 'function') e.preventDefault();
    if (typeof e.stopPropagation === 'function') e.stopPropagation();
  }

  // AUTO-STÄNG SIDOMENYN OCH BACKDROP PÅ MOBIL OCH DESKTOP
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (sidebar) sidebar.classList.add('-translate-x-full');
  if (backdrop) backdrop.classList.add('hidden');
  if (typeof closeSidebar === 'function') closeSidebar();

  // Stäng reflektionspanelen om den är öppen
  const refPanel = document.getElementById('reflections-panel');
  if (refPanel) refPanel.classList.add('translate-x-full');

  const token = await getOrHydrateUserToken();
  if (!token) {
    window.pendingViewAfterAuth = 'dashboard';
    if (typeof openAuthModal === 'function') openAuthModal('login');
    return false;
  }

  // DÖLJ CHATT & VISA DASHBOARD
  document.querySelectorAll('#main-chat-view, #chat-view, .chat-container').forEach(el => el.classList.add('hidden'));
  const dashView = document.getElementById('dashboard-view');
  if (dashView) {
    dashView.classList.remove('hidden');
    dashView.style.display = 'block';
  }

  try {
    await fetchAndRenderDashboardData();
  } catch (err) {
    console.error("Dashboard error caught safely:", err);
  }

  return false;
}



function filterDashboardCategory(cat) {
  document.querySelectorAll('.dash-filter-btn').forEach(btn => {
    btn.classList.remove('bg-[#2C3E35]', 'text-white');
    btn.classList.add('bg-white', 'text-stone-600');
  });
  if (event && event.target) {
    event.target.classList.remove('bg-white', 'text-stone-600');
    event.target.classList.add('bg-[#2C3E35]', 'text-white');
  }
  
  // Filtrera kort baserat på vald kategori
  document.querySelectorAll('.insight-card, .metric-card').forEach(card => {
    if (cat === 'all' || card.dataset.category === cat) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

function updateAuthUI(user) {
  const loggedInBox = document.getElementById('user-profile-logged-in');
  const loggedOutBox = document.getElementById('user-profile-logged-out');
  const emailDisplay = document.getElementById('user-email-display');
  const avatar = document.getElementById('user-avatar');

  if (user && user.email) {
    if (loggedInBox) loggedInBox.classList.remove('hidden');
    if (loggedOutBox) loggedOutBox.classList.add('hidden');
    if (emailDisplay) emailDisplay.innerText = user.email;
    if (avatar) avatar.innerText = user.email.charAt(0).toUpperCase();
  } else {
    if (loggedInBox) loggedInBox.classList.add('hidden');
    if (loggedOutBox) loggedOutBox.classList.remove('hidden');
  }
}

function showChatView() {
  const mainChatView = document.getElementById('main-chat-view') || document.getElementById('chat-view');
  const dashView = document.getElementById('dashboard-view');
  if (dashView) dashView.classList.add('hidden');
  if (mainChatView) mainChatView.classList.remove('hidden');
}

function closeDashboardView() {
  const mainChatView = document.getElementById('chat-container') || document.querySelector('main');
  const dashView = document.getElementById('dashboard-view');
  if (dashView) dashView.classList.add('hidden');
  if (mainChatView) mainChatView.classList.remove('hidden');
}

async function fetchAndRenderDashboardData() {
  try {
    const res = await fetch('/api/dashboard-data', {
      headers: {
        'Authorization': `Bearer ${userToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (res.status === 403) {
      if (window.handlePaywallAuth) window.handlePaywallAuth('signup');
      closeDashboardView();
      return;
    }

    if (!res.ok) throw new Error('Dashboard API error: ' + res.status);

    const data = await res.json();
    
    // 1. Render Radar Chart
    window.latestUserScores = data.scores || { mindset: 50, halsa: 50, relationer: 50, produktivitet: 50, sjalvkannedom: 50 };
    renderRadarChart(window.latestUserScores);

    // 2. Render Habits List
    renderHabitsList(data.habits || []);

    // 3. Render Insights List
    renderInsightsList(data.insights || []);

  } catch (err) {
    console.error('Failed to load dashboard data:', err);
  }
}

function renderRadarChart(scores) {
  const ctx = document.getElementById('falkRadarChart');
  if (!ctx) return;

  if (falkRadarChartInstance) {
    falkRadarChartInstance.destroy();
  }

  falkRadarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Mindset', 'Hälsa', 'Relationer', 'Produktivitet', 'Självkännedom'],
      datasets: [{
        label: 'Utveckling %',
        data: [
          scores.mindset || 50,
          scores.halsa || 50,
          scores.relationer || 50,
          scores.produktivitet || 50,
          scores.sjalvkannedom || 50
        ],
        backgroundColor: 'rgba(44, 62, 53, 0.2)',
        borderColor: '#2C3E35',
        pointBackgroundColor: '#D97706',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { display: false },
          grid: { color: '#E5E2D9' }
        }
      },
      plugins: { legend: { display: false } }
    }
  });
}

function renderHabitsList(habits) {
  const container = document.getElementById('habits-list-container');
  if (!container) return;

  if (habits.length === 0) {
    container.innerHTML = '<p class="text-stone-400 italic">Inga vanor registrerade ännu.</p>';
    return;
  }

  container.innerHTML = habits.map(h => `
    <div class="flex items-center justify-between p-2 rounded-lg bg-stone-50 border border-stone-200">
      <span class="font-medium text-stone-800">${h.title}</span>
      <span class="font-bold text-[#2C3E35]">${h.rate}%</span>
    </div>
  `).join('');
}

function renderInsightsList(insights) {
  const container = document.getElementById('insights-list-container');
  if (!container) return;

  if (insights.length === 0) {
    container.innerHTML = '<p class="text-stone-400 italic">Inga insikter ännu.</p>';
    return;
  }

  container.innerHTML = insights.map(i => `
    <div class="p-2.5 rounded-lg bg-stone-50 border border-stone-200 text-stone-700">
      💡 ${i}
    </div>
  `).join('');
}

// Header Filter Controls
function toggleDashCard(cardId, isChecked) {
  const card = document.getElementById(cardId);
  if (card) {
    if (isChecked) card.classList.remove('hidden');
    else card.classList.add('hidden');
  }
}

function toggleDashboardSection(mode) {
  if (mode === 'all') {
    ['scores-card', 'habits-card', 'insights-card'].forEach(id => {
      const card = document.getElementById(id);
      if (card) card.classList.remove('hidden');
    });
    document.querySelectorAll('.dash-filter-btn').forEach(btn => btn.classList.add('active'));
    document.querySelectorAll('#dashboard-view input[type="checkbox"]').forEach(cb => cb.checked = true);
  }
}

  // [Orphaned login block purged]

  const email = emailEl.value.trim();
  const password = passEl.value;

  if (!email || !password) {
    alert("Fyll i både e-post och lösenord.");
    return false;
  }

  const sb = window.supabase || window.supabaseClient;
  if (!sb || !sb.auth) {
    alert("Supabase-klienten är inte redo.");
    return false;
  }

  try {
    const { data, error } = await sb.auth.signInWithPassword({ email, password });
    if (error) {
      alert("Inloggningsfel: " + error.message);
      return false;
    }

    if (data && data.session) {
      window.userToken = data.session.access_token;
      
      // REAKTIV UI-UPPDATERING DIREKT I DOM:EN (INGEN F5 KRÄVS)
      if (typeof updateAuthUI === 'function') {
        updateAuthUI(data.user);
      } else {
        const emailDisp = document.getElementById('user-email-display');
        if (emailDisp) emailDisp.innerText = data.user.email;
        
        const loggedInBox = document.getElementById('user-profile-logged-in');
        const loggedOutBox = document.getElementById('user-profile-logged-out');
        if (loggedInBox) loggedInBox.classList.remove('hidden');
        if (loggedOutBox) loggedOutBox.classList.add('hidden');

        document.querySelectorAll('.guest-badge, #user-status-badge, #user-tier-badge').forEach(el => {
          el.innerText = 'PREMIUM';
          el.classList.remove('bg-stone-200', 'text-stone-600');
          el.classList.add('bg-[#2C3E35]', 'text-white');
        });
      }

      // Dölj auth-modalen
      const authModal = document.getElementById('auth-modal');
      if (authModal) authModal.classList.add('hidden');

      // Omdirigera om användaren klickat på dashboarden innan login
      if (window.pendingViewAfterAuth === 'dashboard') {
        window.pendingViewAfterAuth = null;
        openDashboardView();
      }
    }
  } catch (err) {
    console.error("Login exception:", err);
    alert("Ett oväntat fel uppstod vid inloggning.");
  }

  return false;
