/* === FALK HIGH-END SAND & BEIGE AESTHETIC CHAT ENGINE === */

function getChatMessagesContainer() {
    let container = document.getElementById("chat-messages");
    if (!container) {
        container = document.createElement("div");
        container.id = "chat-messages";
        const main = document.querySelector("main") || document.body;
        main.appendChild(container);
    }
    
    container.className = "flex flex-col gap-4 p-4 overflow-y-auto flex-1 w-full max-w-2xl mx-auto";
    container.setAttribute("style", "display: flex !important; flex-direction: column !important; gap: 16px !important; padding-top: 80px !important; padding-bottom: 110px !important; box-sizing: border-box !important;");
    return container;
}

function showThinkingIndicator() {
    removeThinkingIndicator();
    const container = getChatMessagesContainer();

    const thinkingDiv = document.createElement("div");
    thinkingDiv.id = "thinking-indicator";
    thinkingDiv.setAttribute("style", "padding: 12px 18px; margin-bottom: 8px; background-color: #FAF7F2; border: 1px solid rgba(0,0,0,0.12); border-radius: 18px 18px 18px 4px; max-width: 180px; color: #000000; font-size: 13px; font-weight: 500; box-shadow: 0 2px 8px rgba(0,0,0,0.03);");
    thinkingDiv.innerHTML = `<div style="display:flex; align-items:center; gap:8px;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#000000; animation: pulse 1s infinite;"></span> FALK tänker...</div>`;

    container.appendChild(thinkingDiv);
    container.scrollTop = container.scrollHeight;
}

function removeThinkingIndicator() {
    const el = document.getElementById("thinking-indicator");
    if (el) el.remove();
}

function appendMessage(sender, text) {
    if (!text) return;
    removeThinkingIndicator();

    const container = getChatMessagesContainer();

    const msgDiv = document.createElement("div");
    const isUser = (sender === "user" || sender === "du" || sender === "gäst");

    if (isUser) {
        msgDiv.setAttribute("style", 
            "margin-left: auto !important; " +
            "background-color: #E8DCC4 !important; " +
            "color: #000000 !important; " +
            "padding: 12px 20px !important; " +
            "border-radius: 18px 18px 4px 18px !important; " +
            "margin-bottom: 10px !important; " +
            "max-width: 75% !important; " +
            "min-width: 48px !important; " +
            "text-align: right !important; " +
            "font-size: 14px !important; " +
            "line-height: 1.5 !important; " +
            "font-weight: 600 !important; " +
            "box-shadow: 0 2px 6px rgba(120, 53, 15, 0.08) !important;"
        );
        msgDiv.innerHTML = `<div style="white-space: pre-wrap;">${text}</div>`;
    } else {
        msgDiv.setAttribute("style", 
            "margin-right: auto !important; " +
            "background-color: #FAF7F2 !important; " +
            "border: 1px solid rgba(0,0,0,0.12) !important; " +
            "color: #1c1917 !important; " +
            "padding: 16px 22px !important; " +
            "border-radius: 18px 18px 18px 4px !important; " +
            "margin-bottom: 10px !important; " +
            "max-width: 82% !important; " +
            "font-size: 14.5px !important; " +
            "line-height: 1.6 !important; " +
            "box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;"
        );
        msgDiv.innerHTML = `
            <div style="font-size: 10px; font-weight: 800; color: #2d4a3e; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">FALK</div>
            <div style="white-space: pre-wrap;">${text}</div>
        `;
    }

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function renderPaywallCard() {
    removeThinkingIndicator();
    const container = getChatMessagesContainer();

    const paywallDiv = document.createElement("div");
    paywallDiv.setAttribute("style", 
        "margin: 20px auto !important; " +
        "background-color: #FAF7F2 !important; " +
        "border: 1px solid rgba(120, 53, 15, 0.2) !important; " +
        "border-radius: 20px !important; " +
        "padding: 24px 28px !important; " +
        "max-width: 480px !important; " +
        "width: 90% !important; " +
        "box-shadow: 0 12px 32px rgba(28, 25, 23, 0.12) !important; " +
        "text-align: center !important;"
    );

    paywallDiv.innerHTML = `
        <div style="display: inline-block; background-color: #E8DCC4; color: #000000; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 20px; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 12px;">
            FALK Premium · 199 kr/mån
        </div>
        <h3 style="font-size: 20px; font-weight: 800; color: #2d4a3e; margin: 0 0 8px 0; letter-spacing: -0.01em;" style="color: #000000 !important; font-size: 16px !important; font-weight: 700 !important;" style="color: #000000 !important; font-size: 16px !important; font-weight: 700 !important;" style="color: #000000 !important; font-size: 16px !important; font-weight: 700 !important; margin-bottom: 4px !important;">
            Du har nått gränsen för gratismeddelanden
        </h3>
        <p style="font-size: 13.5px; color: #44403c; line-height: 1.5; margin: 0 0 20px 0;" style="color: #2D2D2D !important; font-size: 15px !important; font-style: italic !important;" style="color: #2D2D2D !important; font-size: 15px !important; font-style: italic !important;" style="color: #2D2D2D !important; font-size: 15px !important; font-style: italic !important; font-family: Georgia, serif !important; margin: 0 !important;">
            Skapa ett konto eller logga in för att låsa upp obegränsat antal samtal, djupa insikter och din personliga utvecklingsresa.
        </p>
        <button onclick="if(window.openAuthModal) window.openAuthModal(); else alert('Inloggning öppnas...');" style="background-color: #2d4a3e; color: #ffffff; border: none; padding: 12px 28px; border-radius: 30px; font-weight: 700; font-size: 14px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(45, 74, 62, 0.25);">
            Logga in / Skapa konto
        </button>
    `;

    container.appendChild(paywallDiv);
    container.scrollTop = container.scrollHeight;
}

async function sendPromptText(textToSend) {
    if (!textToSend) return;

    // Dölj onboarding-kort
    const promptGrids = document.querySelectorAll("#prompt-grid, #onboarding-cards-wrapper, .prompt-grid");
    promptGrids.forEach(el => el.style.setProperty("display", "none", "important"));

    // 1. Visa användarens meddelande
    appendMessage("user", textToSend);

    // 2. Visa tänk-indikator
    showThinkingIndicator();

    // 3. Anropa Flask backend
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: textToSend })
        });

        const data = await response.json();
        removeThinkingIndicator();

        if (data && data.limit_reached) {
            renderPaywallCard();
        } else if (data && (data.response || data.reply)) {
            appendMessage("bot", data.response || data.reply);
        } else {
            appendMessage("bot", "Jag hör vad du säger. Låt oss fördjupa oss i det.");
        }
    } catch (err) {
        console.error("Chat error:", err);
        removeThinkingIndicator();
        appendMessage("bot", "Tack för dina tankar. Låt oss utforska detta vidare.");
    }
}

// Global Event Delegation för alla onboarding-kort
document.addEventListener("click", function(e) {
    const card = e.target.closest("#prompt-grid > div, .prompt-card, [class*='prompt-card']");
    if (card) {
        const textNode = card.querySelector("p, i, em, span, h3, h4") || card;
        let txt = textNode.textContent.trim();
        txt = txt.replace(/^["'”«]+|["'”»]+$/g, '').trim();

        if (txt && txt.length > 2 && !txt.includes("Skriv till mig")) {
            e.preventDefault();
            e.stopPropagation();
            sendPromptText(txt);
        }
    }
});

// Globala alias
window.sendPromptText = sendPromptText;
window.sendMessage = sendPromptText;
window.selectPrompt = sendPromptText;
window.sendPromptToChat = sendPromptText;
window.appendMessage = appendMessage;
window.renderPaywallCard = renderPaywallCard;


/* === FALK ONBOARDING CARD CLICK DELEGATION === */
document.addEventListener("DOMContentLoaded", () => {
  const promptGrid = document.getElementById("prompt-grid");
  const chatMessages = document.getElementById("chat-messages");

  if (promptGrid) {
    promptGrid.addEventListener("click", (e) => {
      const card = e.target.closest(".prompt-card");
      if (!card) return;

      const promptText = card.getAttribute("data-prompt") || card.innerText;
      
      // Dölj onboarding-grid
      promptGrid.style.display = "none";
      
      // Visa chat-ytan om den var dold
      if (chatMessages) {
        chatMessages.style.display = "block";
      }

      // Om det finns en global sendPrompt-funktion, anropa den
      if (typeof window.sendPromptText === "function") {
        window.sendPromptText(promptText);
      } else if (typeof sendMessage === "function") {
        sendMessage(promptText);
      } else {
        const inputField = document.getElementById("chat-input");
        const sendBtn = document.getElementById("send-btn");
        if (inputField && sendBtn) {
          inputField.value = promptText;
          sendBtn.click();
        }
      }
    });
  }
});


/* === FALK CLICK DELEGATION FOR ALL 9 CARDS === */
document.addEventListener("DOMContentLoaded", () => {
  const promptGrid = document.getElementById("prompt-grid");
  if (promptGrid) {
    promptGrid.addEventListener("click", (e) => {
      const card = e.target.closest(".prompt-card, [data-prompt], div[class*='border']");
      if (!card) return;

      const text = card.getAttribute("data-prompt") || card.innerText;
      promptGrid.style.display = "none";
      
      const chatMessages = document.getElementById("chat-messages");
      if (chatMessages) chatMessages.style.display = "block";

      const input = document.getElementById("chat-input");
      const btn = document.getElementById("send-btn");
      if (input && btn) {
        input.value = text.replace(/"/g, '').trim();
        btn.click();
      }
    });
  }
});


/* === STRIKT KLICK-LYSSNARE FÖR STATISKA HTML-KORT === */
document.addEventListener("DOMContentLoaded", () => {
  const promptGrid = document.getElementById("prompt-grid");
  if (promptGrid) {
    promptGrid.addEventListener("click", (e) => {
      const card = e.target.closest(".prompt-card");
      if (!card) return;

      const promptText = card.getAttribute("data-prompt") || card.innerText;
      
      // Dölj kort-grid, visa chatt
      promptGrid.style.display = "none";
      const chatMessages = document.getElementById("chat-messages");
      if (chatMessages) chatMessages.style.display = "block";

      // Skicka texten
      const inputField = document.getElementById("chat-input");
      const sendBtn = document.getElementById("send-btn");
      if (inputField && sendBtn) {
        inputField.value = promptText.replace(/^\s*["'“]?|["'”]?\s*$/g, '').trim();
        sendBtn.click();
      }
    });
  }
});


/* === FALK CHAT INPUT & SEND BUTTON BINDINGS === */
document.addEventListener("DOMContentLoaded", function() {
  const inputField = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const chatForm = document.getElementById("chat-form") || (inputField ? inputField.closest("form") : null);

  function triggerSend(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    if (!inputField) return;
    const text = inputField.value.trim();
    if (!text) return;

    // Kör gästkontroll om den finns
    if (typeof window.checkGuestAccess === "function" && !window.checkGuestAccess()) {
      return;
    }

    // Anropa den existerande sendMessage-funktionen
    if (typeof window.sendMessage === "function") {
      window.sendMessage(text);
    } else if (typeof sendMessage === "function") {
      sendMessage(text);
    } else {
      console.error("[FALK Error] sendMessage-funktionen hittades inte!");
    }
  }

  // 1. Bind skicka-knappen
  if (sendBtn) {
    sendBtn.onclick = triggerSend;
  }

  // 2. Bind formuläret om det finns
  if (chatForm) {
    chatForm.onsubmit = triggerSend;
  }

  // 3. Bind Enter-tangenten i textarea/input (Shift+Enter ger ny rad)
  if (inputField) {
    inputField.addEventListener("keydown", function(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        triggerSend(e);
      }
    });
  }
});


/* === FALK UNBEATABLE CHAT & INPUT ENGINE === */
(function() {
  // 1. Funktion för att växla från Startsida till Chattvy
  window.showChatView = function() {
    const wrapper = document.getElementById("onboarding-cards-wrapper");
    const grid = document.getElementById("prompt-grid");
    const chatMessages = document.getElementById("chat-messages");
    const chatContainer = document.getElementById("chat-container");

    if (wrapper) {
      wrapper.style.display = "none";
      wrapper.classList.add("hidden");
    }
    if (grid) {
      grid.style.display = "none";
      grid.classList.add("hidden");
    }
    if (chatMessages) {
      chatMessages.style.display = "block";
      chatMessages.classList.remove("hidden");
    }
    if (chatContainer) {
      chatContainer.style.display = "block";
      chatContainer.classList.add("is-active");
    }
    document.body.classList.add("is-chat-active");
  };

  // 2. Den centrala sendMessage-funktionen
  window.sendMessage = function(textOverride) {
    const inputEl = document.getElementById("chat-input") || document.querySelector("textarea") || document.querySelector("input[type='text']");
    const text = (typeof textOverride === "string" ? textOverride : (inputEl ? inputEl.value : "")).trim();
    
    if (!text) return;

    // Kör gästkontroll om den finns
    if (typeof window.checkGuestAccess === "function" && !window.checkGuestAccess()) {
      return;
    }

    // Växla vy direkt på skärmen
    window.showChatView();

    // Rensa inputfältet
    if (inputEl) {
      inputEl.value = "";
    }

    // Öka gästräknaren
    if (typeof window.incrementGuestMessageCount === "function" && !window.FALK_USER_LOGGED_IN) {
      window.incrementGuestMessageCount();
    }

    // Rendera användarens meddelandebubbla i DOM
    const chatMsgs = document.getElementById("chat-messages");
    if (chatMsgs) {
      const userDiv = document.createElement("div");
      userDiv.className = "user-message my-3 p-4 bg-[#E8DCC4] text-stone-900 rounded-2xl max-w-[85%] ml-auto shadow-sm text-base font-medium";
      userDiv.textContent = text;
      chatMsgs.appendChild(userDiv);
      chatMsgs.scrollTop = chatMsgs.scrollHeight;
    }

    // Anropa backend API
    if (typeof window.fetchAIResponse === "function") {
      window.fetchAIResponse(text);
    } else if (typeof window.streamResponse === "function") {
      window.streamResponse(text);
    }
  };

  // 3. Koppla om window.selectPrompt så att kortklick använder samma motor
  window.selectPrompt = function(promptText) {
    window.sendMessage(promptText);
  };

  // 4. Global Capture-Phase Event Delegation för Inmatning
  // Enter-tangent i skrivfältet
  document.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      const active = document.activeElement;
      if (active && (active.id === "chat-input" || active.tagName === "TEXTAREA" || active.tagName === "INPUT")) {
        e.preventDefault();
        e.stopPropagation();
        window.sendMessage();
      }
    }
  }, true);

  // Klick på Skicka-knapp
  document.addEventListener("click", function(e) {
    const target = e.target;
    if (!target) return;

    const sendBtn = target.closest("#send-btn, [id*='send'], button[type='submit'], .send-btn");
    if (sendBtn) {
      e.preventDefault();
      e.stopPropagation();
      window.sendMessage();
    }
  }, true);

  // Formulär-submit
  document.addEventListener("submit", function(e) {
    e.preventDefault();
    e.stopPropagation();
    window.sendMessage();
  }, true);
})();


/* === UNIFIED FALK CHAT ENGINE (CARDS + INPUT + BACKEND) === */
(function() {
  window.sendMessage = async function(textOverride) {
    const inputEl = document.getElementById("chat-input") || document.querySelector("textarea") || document.querySelector("input[type='text']");
    const text = (typeof textOverride === "string" ? textOverride : (inputEl ? inputEl.value : "")).trim();
    
    if (!text) return;

    // 1. Kontrollera gästspärren (Max 6)
    if (typeof window.checkGuestAccess === "function" && !window.checkGuestAccess()) {
      return;
    }

    // 2. Dölj startsidan / onboarding-korten och visa chattytan
    const wrapper = document.getElementById("onboarding-cards-wrapper");
    const grid = document.getElementById("prompt-grid");
    const chatMsgs = document.getElementById("chat-messages");
    const chatContainer = document.getElementById("chat-container");

    if (wrapper) wrapper.style.setProperty("display", "none", "important");
    if (grid) grid.style.setProperty("display", "none", "important");
    if (chatMsgs) chatMsgs.style.setProperty("display", "block", "important");
    if (chatContainer) chatContainer.classList.add("is-active");
    document.body.classList.add("is-chat-active");

    // 3. Rensa skrivfältet
    if (inputEl) inputEl.value = "";

    // 4. Rendera användarens meddelandebubbla i DOM
    if (chatMsgs) {
      const userDiv = document.createElement("div");
      userDiv.className = "user-message my-3 p-4 bg-[#E8DCC4] text-stone-900 rounded-2xl max-w-[85%] ml-auto shadow-sm text-base font-medium";
      userDiv.textContent = text;
      chatMsgs.appendChild(userDiv);

      // 5. Skapa en temporär laddningsbubbla för FALK
      const falkDiv = document.createElement("div");
      falkDiv.className = "falk-message my-3 p-4 bg-[#FAF7F2] border border-[rgba(0,0,0,0.08)] text-stone-900 rounded-2xl max-w-[85%] mr-auto shadow-sm text-base font-normal";
      falkDiv.textContent = "FALK tänker...";
      chatMsgs.appendChild(falkDiv);
      chatMsgs.scrollTop = chatMsgs.scrollHeight;

      // 6. Öka gästräknaren i localStorage
      if (typeof window.incrementGuestMessageCount === "function" && !window.FALK_USER_LOGGED_IN) {
        window.incrementGuestMessageCount();
      }

      // 7. Skicka anrop till backend (/chat)
      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, prompt: text })
        });

        if (!response.ok) {
          throw new Error("Backend svarade med status " + response.status);
        }

        const data = await response.json();
        const replyText = data.response || data.message || data.reply || (typeof data === "string" ? data : "Ett svar mottogs från FALK.");
        falkDiv.textContent = replyText;
      } catch (err) {
        console.error("[FALK API Error]:", err);
        falkDiv.textContent = "Kunde inte ansluta till FALK-motorn. Kontrollera att backend körs.";
      }
      chatMsgs.scrollTop = chatMsgs.scrollHeight;
    }
  };

  // Koppla globalt för kortklick
  window.selectPrompt = function(promptText) {
    window.sendMessage(promptText);
  };
})();
