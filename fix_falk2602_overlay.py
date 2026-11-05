import os

print("=== DEAKTIVERAR AUTOMATISK AUTH-OVERLAY PÅ FALK2602 ===")

index_path = os.path.join("templates", "index.html")

with open(index_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Dölj overlay-diven från start
code = code.replace('<div id="auth-overlay" class="auth-overlay-screen">', '<div id="auth-overlay" class="auth-overlay-screen hidden">')

# 2. Inaktivera att initAuthCheck tvingar fram overlayen vid sidinläsning
old_init = '''async function initAuthCheck() {
            const { data: { session } } = await supabaseClient.auth.getSession().catch(() => ({ data: { session: null } }));
            const overlay = document.getElementById("auth-overlay");
            if (!session) {
                overlay.classList.remove("hidden", "dismissing");
            } else {
                overlay.classList.add("hidden");
            }
        }'''

new_init = '''async function initAuthCheck() {
            // FALK2602: Automatisk auth-pop-up inaktiverad så att appen laddas direkt
            const { data: { session } } = await supabaseClient.auth.getSession().catch(() => ({ data: { session: null } }));
        }'''

if old_init in code:
    code = code.replace(old_init, new_init)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(code)

print("-> [SUCCESS] FALK2602 laddas nu direkt på startsidan utan inloggningsruta!")
