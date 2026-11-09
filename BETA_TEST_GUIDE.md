# 🦅 WAYJS OPERATING SYSTEM (WOS) - BETA v1.0-GOLD
## Betatestningsguide & Systemspecifikation

Välkommen till betatestningen av **WOS Beta v1.0-gold** – Wayjs digitala mentormotor.

---

### 📡 1. Åtkomst till WOS Beta Dashboard
Öppna din webbläsare och gå till:
👉 **`https://falk-backend.onrender.com/chat`**

---

### 🎨 2. Vad du ser på skärmen (Tvåkolumns gränssnitt)
1. **Vänster spalt (Falk Mentor Dialogue):**
   - Här för du dina samtal med Falk.
   - Överst visas den aktuella **Samtalsfasen** (`TRYGGHET`, `FÖRSTÅELSE`, `HANDLING` etc.).
   - Falk guidar dig från ett fågelperspektiv utan att ge färdiga svar eller dömande råd.

2. **Höger spalt (WOS State Visualizer):**
   - **The Compass Score™:** Fyra levande kompassstaplar (*Riktning, Balans, Handling, Reflektion*) som uppdateras automatiskt baserat på insikterna i ditt samtal.
   - **The Compass Journal™:** Din personliga utvecklingsjournal där Falk automatiskt skapar och sparar kapitel när du når nya insikter eller fattar viktiga beslut.

---

### 🔒 3. Databaspersistens & Kontinuitet
- Alla dina kompasspoäng och journal-kapitel sparas i realtid i **Supabase**.
- Om du laddar om sidan hämtas dina senast sparade poäng och alla dina tidigare journal-kapitel automatiskt via `/api/dialogue/state/<user_id>`.

---

### 📝 4. Vad vi vill att du testar
1. **Skriv om ett verkligt vägval eller en fundering:** Se hur Falk svarar och hur samtalsfasen ändras.
2. **Sätt en gräns eller fatta ett beslut i chatten:** Observera om Falk genererar ett nytt kapitel i *The Compass Journal™*.
3. **Ladda om sidan:** Verifiera att dina poäng och journal-kapitel finns kvar.

---

*Falk Core Engine v1.0.0-gold | Powered by OpenAI GPT-4o & Supabase*
