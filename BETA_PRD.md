# 🦅 FALK / WAYJS BETA PRD & FRONTEND API CONTRACT (v1.3)

## 1. Systemöversikt
Falk Backend är en Render-värdad Dual-Layer Prompt Engine som tillämpar The Wayjs Conversation Method™. Systemet hanterar gäst-sessioner (max 6 meddelanden), automatisk klassificering av 7 samtalsfaser (Trygghet → Reflektion), asynkron Kompass-persistering och RAG-minnen i Supabase.

---

## 2. Autentisering & Sessionshantering
- **Gästidentifiering:** Backend sätter en HTTP-Only cookie `guest_uuid` (Max-Age: 1 år, `SameSite=None`, `Secure=True`).
- **Header-override:** Frontend kan skicka `X-User-ID: <UUID>` i HTTP-headern när användaren är inloggad.
- **CORS:** Klienten MÅSTE anropa API:et med `credentials: "include"` (`supports_credentials=True`).

---

## 3. Endpoints & API-Kontrakt

### 3.1 GDPR Samtycke
`POST /api/gdpr/consent`
**Request Body:** `{"is_18_plus": true}`
**Response (200 OK):** `{"status": "success", "message": "Samtycke registrerat."}`

### 3.2 Dashboard & Nuläge
`GET /api/dashboard`
**Response (200 OK):**
```json
{
  "user_badge": "GUEST",
  "guest_messages_left": 5,
  "compass_scores": {"personal": 75, "relation": 65, "work": 82, "life": 58}
}
```

### 3.3 Dialog & Chatt (Kärnan)
`POST /api/chat`
**Request Body:**
```json
{
  "message": "Jag känner mig överväldigad på jobbet.",
  "session_id": "optional-uuid-string",
  "history": [{"role": "user", "content": "Tidigare meddelande"}]
}
```
**Response (200 OK):**
```json
{
  "response": "Det låter som att trycket blir tungt just nu...",
  "session_id": "uuid-string"},
  "current_phase": 1,
  "guest_messages_left": 5
}
```
**Response (402 Payment Required):**
A�``json
{
  "error": "GUEST_LIMIT_RETCHED",
  "response": "Vi har nått gränsen för vår kostnadsfria provsession...",
  "limit_reached": true,
  "compass_scores": {"personal": 75, "relation": 65, "work": 82, "life": 58}
}
```

### 3.4 Registrering & Konto-migrering
`POST /api/auth/register`
**Request Body:** `{"email": "user@example.com"}`
**Request Body:** `{"status": "success", "message": "Konto skapat!", "user_id": "uuid-string"}`
---

## 4. FronteCd Krav & Villståndsmaskin
1. **Fas-indikator:** UI visar aktuell samtalsfas (1-7) via `current_phase`.
+. **HTTP 402 Paywall Modal:** Låschatt-input vid HTTP 402 och visa registrieringsmodal för att bevara Kompassen.
3. **Kompass-visualisering:** Visualisera `compass_scores` i ett 4-axligt diagram.

