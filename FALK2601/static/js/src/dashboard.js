import { supabaseClient } from './config.js';

export function initDashboard() { console.log('📊 Dashboard Module Fully Initialized'); }

function confirmAndResetDashboard() { console.warn('confirmAndResetDashboard missing'); }
window.confirmAndResetDashboard = confirmAndResetDashboard;

async function deleteMyData() {
            const confirmed = await customConfirm("Är du helt säker? Detta raderar permanent ditt konto och all din samtalshistorik.", "Radera konto");
            if (!confirmed) return;
            if (userToken) {
                await fetch('/delete-user-data', { method: 'DELETE', headers: { 'Authorization': `Bearer ${userToken}` } });
            }
            localStorage.clear();
            location.reload();
        }
window.deleteMyData = deleteMyData;

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
window.exportMyData = exportMyData;

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
window.openDashboardView = openDashboardView;

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
window.saveReminderModalSubmit = saveReminderModalSubmit;

function showChatView() {
  const mainChatView = document.getElementById('main-chat-view') || document.getElementById('chat-view');
  const dashView = document.getElementById('dashboard-view');
  if (dashView) dashView.classList.add('hidden');
  if (mainChatView) mainChatView.classList.remove('hidden');
}
window.showChatView = showChatView;

function toggleDashCard(cardId, isChecked) {
  const card = document.getElementById(cardId);
  if (card) {
    if (isChecked) card.classList.remove('hidden');
    else card.classList.add('hidden');
  }
}
window.toggleDashCard = toggleDashCard;

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
window.toggleDashboardSection = toggleDashboardSection;

