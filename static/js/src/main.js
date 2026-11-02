/* === FALK MAIN & ONBOARDING BINDINGS === */

function selectOnboarding(promptText) {
    console.log("[FALK UI] Onboarding valt:", promptText);
    const inputEl = document.querySelector("input[type='text'], textarea, #chat-input");
    if (inputEl) inputEl.value = promptText;

    if (typeof window.sendMessage === "function") {
        window.sendMessage(promptText);
    }
}

function selectPrompt(promptText) {
    selectOnboarding(promptText);
}

window.selectOnboarding = selectOnboarding;
window.selectPrompt = selectPrompt;
