from typing import List, Dict, Any

def generate_session_pdf_html(session_id: str, messages: List[Dict[str, Any]]) -> str:
    """Genererar en stilren, utskriftsvänlig HTML/PDF-vy för en Falk-session."""
    
    rows_html = ""
    for msg in messages:
        role_label = "FALK (Mentor)" if msg["role"] == "assistant" else "DU (Användare)"
        bg_color = "#DFD2B7" if msg["role"] == "assistant" else "#1e293b"
        text_color = "#232B22" if msg["role"] == "assistant" else "#F4EFE6"
        border = "border-left: 4px solid #C57B57;" if msg["role"] == "assistant" else ""

        rows_html += f"""
        <div style="margin-bottom: 20px; padding: 16px; background-color: {bg_color}; color: {text_color}; border-radius: 8px; {border}">
            <div style="font-weight: bold; font-size: 0.85rem; margin-bottom: 6px; opacity: 0.8;">{role_label}</div>
            <div style="line-height: 1.6; white-space: pre-wrap;">{msg['content']}</div>
        </div>
        """

    html_doc = f"""
    <!DOCTYPE html>
    <html lang="sv">
    <head>
        <meta charset="UTF-8">
        <title>FALK Mentorsession - {session_id}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #E8DCC4;
                color: #232B22;
                padding: 40px;
                max-width: 800px;
                margin: 0 auto;
            }}
            .header {{
                border-bottom: 2px solid #4E5C4B;
                padding-bottom: 20px;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .logo {{ font-size: 1.8rem; font-weight: 800; color: #4E5C4B; letter-spacing: 2px; }}
            .disclaimer {{
                font-size: 0.8rem;
                color: #4E5C4B;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid rgba(78, 92, 75, 0.3);
                text-align: center;
            }}
            @media print {{
                body {{ background-color: #ffffff; color: #000000; padding: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="no-print" style="margin-bottom: 20px; text-align: right;">
            <button onclick="window.print()" style="background:#C57B57; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; cursor:pointer;">
                🖨️ Skriv ut / Spara som PDF
            </button>
        </div>
        <div class="header">
            <div>
                <div class="logo">FALK</div>
                <div style="font-size: 0.9rem; color: #4E5C4B;">WAYJS Cognitive Engine™ - Samtalsutskrift</div>
            </div>
            <div style="text-align: right; font-size: 0.85rem; color: #4E5C4B;">
                Session: <strong>{session_id}</strong>
            </div>
        </div>

        <div class="messages">
            {rows_html}
        </div>

        <div class="disclaimer">
            Falk hjälper dig att tänka klarare, inte att tänka åt dig. Det här dokumentet innehåller dina egna reflekterade insikter.
        </div>
    </body>
    </html>
    """
    return html_doc
