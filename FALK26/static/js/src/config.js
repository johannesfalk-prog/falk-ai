// Config Module - Bulletproof Supabase Client Init
const supabaseUrl = window.SUPABASE_URL || '';
const supabaseAnonKey = window.SUPABASE_ANON_KEY || '';

if (supabaseUrl && supabaseAnonKey && (supabaseUrl.startsWith('http://') || supabaseUrl.startsWith('https://'))) {
    try {
        if (typeof supabase !== 'undefined' && supabase.createClient) {
            window.supabaseClient = supabase.createClient(supabaseUrl, supabaseAnonKey);
            console.log('[FALK Config] Supabase-klient initierad i window.supabaseClient');
        }
    } catch (err) {
        console.error('[FALK Config] Fel vid skapande av Supabase-klient:', err);
    }
} else {
    console.warn('[FALK Config] Supabase URL/KEY saknas eller är ogiltig. Mottagen URL:', supabaseUrl);
}
