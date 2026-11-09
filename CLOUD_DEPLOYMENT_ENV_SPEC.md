# 🦅 WOS v1.6 CLOUD DEPLOYMENT SPECIFICATION

## 1. BACKEND DEPLOYMENT (RENDER / FLY.IO)
- **Root Directory:** `falk-backend`
- **Build Command:** Dockerfile (Auto-detected)
- **Port:** `5001`
- **Environment Variables Required:**
  - `PORT` = `5001`
  - `OPENAI_API_KEY` = `<din_skarpa_openai_nyckel>`
  - `SUPABASE_URL` = `<din_supabase_url>`
  - `SUPABASE_SERVICE_KEY` = `<din_supabase_service_role_nyckel>`

## 2. FRONTEND DEPLOYMENT (VERCEL)
- **Root Directory:** `falk-frontend`
- **Framework Preset:** Next.js
- **Environment Variables Required:**
  - `NEXT_PUBLIC_BACKEND_URL` = `https://<ditt-render-backend-namn>.onrender.com`
  - `NEXT_PUBLIC_SUPABASE_URL` = `<din_supabase_url>`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` = `<din_supabase_anon_nyckel>`
