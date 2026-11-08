import os

print("=== DEPLOYAR OCH SANERAR BIFOGAD INDEX_2.HTML FÖR LANSERING ===")

# Läser in innehållet från din bifogade fil till templates/index.html
if os.path.exists("index_2.html"):
    with open("index_2.html", "r", encoding="utf-8") as src:
        content = src.read()
    with open(os.path.join("templates", "index.html"), "w", encoding="utf-8") as dst:
        dst.write(content)

index_path = os.path.join("templates", "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Byt lokala JS-sökvägar mot stabila CDN:er
code = code.replace('<script src="/js/purify.min.js"></script>', '<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.0.6/purify.min.js"></script>')
code = code.replace('<script src="/js/marked.min.js"></script>', '<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>')
code = code.replace('<script src="/js/supabase.js"></script>', '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>')

# 2. Dölj overlay som standard för gästläge
code = code.replace('<div id="auth-overlay" class="auth-overlay-screen">', '<div id="auth-overlay" class="auth-overlay-screen hidden">')

# 3. Gör initAuthCheck gästvänlig (tvinga inte overlay)
old_auth_check = '''async function initAuthCheck() {
            const { data: { session } } = await supabaseClient.auth.getSession().catch(() => ({ data: { session: null } }));
            const overlay = document.getElementById("auth-overlay");
            if (!session) {
                overlay.classList.remove("hidden", "dismissing");
            } else {
                overlay.classList.add("hidden");
            }
        }'''

new_auth_check = '''async function initAuthCheck() {
            if (!supabaseClient) return;
            const { data: { session } } = await supabaseClient.auth.getSession().catch(() => ({ data: { session: null } }));
            // Session-kontroll utförd utan att tvinga fram overlay för gäster
        }'''

code = code.replace(old_auth_check, new_auth_check)

# 4. Tillåt gäster att skicka meddelanden utan att krascha på saknad session
old_send_auth = '''const { data: { session } } = await supabaseClient.auth.getSession().catch(() => ({ data: { session: null } }));
                if (!session) throw new Error("Ingen aktiv session");'''

new_send_auth = '''let authToken = "";
                let userId = "guest_user";
                if (supabaseClient) {
                    const { data: { session } } = await supabaseClient.auth.getSession().catch(() => ({ data: { session: null } }));
                    if (session) {
                        authToken = session.access_token;
                        userId = session.user.id;
                    }
                }'''

code = code.replace(old_send_auth, new_send_auth)
code = code.replace('"Authorization": `Bearer ${session.access_token}`', '"Authorization": `Bearer ${authToken}`')
code = code.replace('user_id: session.user.id', 'user_id: userId')

with open(index_path, "w", encoding="utf-8") as f:
    f.write(code)

print("-> [SUCCESS] index_2.html är nu sanerad, säkrad med CDN:er och helt öppen för gäst- och chattester!")
