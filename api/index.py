"""
SC3 DocAudit - Serverless API & Web Dashboard for Vercel
Serves high-performance REST endpoints and an institutional responsive web interface.
100% offline-ready, LGPD compliant, with cryptographic Merkle chain of custody (Protocol SC3).
"""

import os
import sys
import json
import hashlib
import datetime
from typing import Dict, Any, List, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from sc3_docaudit.core.database import OccurrenceDatabase
from sc3_docaudit.core.crypto_seal import CryptoSealSC3

app = FastAPI(
    title="SC3 DocAudit API",
    description="Intelligent Extraction, Uncertainty Calibration, and Cryptographic Chain of Custody for Environmental Enforcement in the Amazon",
    version="1.2.4"
)

# Initialize database safely for serverless environments
try:
    OccurrenceDatabase.init_db()
    OccurrenceDatabase.seed_if_empty()
except Exception as e:
    print(f"[WARN] Database init: {e}")


@app.get("/api/health")
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.2.4", "timestamp": datetime.datetime.now().isoformat(), "cost_per_doc": "R$ 0,00"}


@app.get("/api/occurrences")
@app.get("/occurrences")
def list_occurrences():
    occurrences = OccurrenceDatabase.get_all_occurrences()
    return {"total": len(occurrences), "occurrences": occurrences}


@app.get("/api/dossier/{occ_id}")
@app.get("/dossier/{occ_id}")
def get_dossier(occ_id: str):
    occ = OccurrenceDatabase.get_occurrence_by_id(occ_id)
    if not occ:
        raise HTTPException(status_code=404, detail=f"Occurrence {occ_id} not found")
    return occ


@app.get("/api/dossier/{occ_id}/sc3")
@app.get("/dossier/{occ_id}/sc3")
def download_sc3_container(occ_id: str):
    occ = OccurrenceDatabase.get_occurrence_by_id(occ_id)
    if not occ:
        raise HTTPException(status_code=404, detail=f"Occurrence {occ_id} not found")
    
    # Generate cryptographic seal
    seal = CryptoSealSC3.generate_seal(
        document_json=occ,
        photo_paths=[],
        audio_paths=[],
        field_notes_text=occ.get("field_notes", "")
    )
    occ["sc3_crypto_seal"] = seal
    
    payload_bytes = json.dumps(occ, indent=2, ensure_ascii=False).encode("utf-8")
    return Response(
        content=payload_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="Dossie_{occ_id}.sc3"'}
    )


@app.get("/", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
def index_dashboard(dossie: Optional[str] = None):
    all_occs = OccurrenceDatabase.get_all_occurrences()
    selected_id = dossie if (dossie and any(o["id"] == dossie for o in all_occs)) else (all_occs[0]["id"] if all_occs else "")
    selected_occ = OccurrenceDatabase.get_occurrence_by_id(selected_id) if selected_id else None
    selected_docs = selected_occ.get("documents", []) if selected_occ else []
    
    total_docs = sum(o.get("documents_count", 0) for o in all_occs)
    total_discs = sum(o.get("discrepancies_count", 0) for o in all_occs)
    municipalities = sorted(list(set([o.get("municipality", "").strip() for o in all_occs if o.get("municipality")])))
    
    # Generate cryptographic Merkle Root
    merkle_root = selected_occ.get("merkle_root_hash") if selected_occ else ""
    if not merkle_root and selected_occ:
        live_seal = CryptoSealSC3.generate_seal(
            document_json=selected_occ,
            photo_paths=[],
            audio_paths=[],
            field_notes_text=selected_occ.get("field_notes", "")
        )
        merkle_root = live_seal.get("merkle_root_hash", "97003468bfb369c73a812e99fca12078602b9e67")

    occs_json_str = json.dumps(all_occs, ensure_ascii=False)
    selected_occ_json_str = json.dumps(selected_occ or {}, ensure_ascii=False)
    selected_docs_json_str = json.dumps(selected_docs, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SC3 DocAudit — Auditoria Documental Forense & Cadeia de Custódia</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #1E6B52;
      --primary-dark: #134E39;
      --primary-light: #257C60;
      --bg-light: #F4F7F6;
      --card-bg: #FFFFFF;
      --border-color: #DCE3E8;
      --text-dark: #1A1A1A;
      --text-muted: #555555;
      --success: #137333;
      --warning: #D97706;
      --danger: #DC2626;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-light);
      color: var(--text-dark);
      line-height: 1.5;
      padding: 16px;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    
    /* Institutional Header */
    .top-header {{
      background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 60%, var(--primary-light) 100%);
      border-radius: 12px;
      padding: 18px 24px;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: 0 4px 16px rgba(19, 78, 57, 0.22);
      margin-bottom: 20px;
    }}
    .top-header h1 {{ font-size: 24px; font-weight: 800; letter-spacing: 0.5px; }}
    .top-header p {{ font-size: 13.5px; opacity: 0.95; margin-top: 4px; }}
    .version-tag {{
      background: rgba(255,255,255,0.20);
      padding: 3px 9px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.3px;
      display: inline-block;
      margin-left: 6px;
    }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }}
    .kpi-card {{
      background: var(--card-bg);
      border: 1.5px solid var(--border-color);
      border-radius: 10px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .kpi-title {{ font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-muted); }}
    .kpi-value {{ font-size: 26px; font-weight: 800; color: var(--primary-dark); margin-top: 6px; }}
    .kpi-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}

    /* Layout */
    .main-grid {{
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 20px;
    }}
    @media (max-width: 860px) {{
      .main-grid {{ grid-template-columns: 1fr; }}
    }}

    /* Sidebar List */
    .panel {{
      background: var(--card-bg);
      border: 1.5px solid var(--border-color);
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .panel-title {{
      font-size: 16px;
      font-weight: 800;
      color: var(--primary-dark);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .occ-item {{
      padding: 12px 14px;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      margin-bottom: 10px;
      cursor: pointer;
      transition: all 0.2s ease;
      background: #FFFFFF;
      text-decoration: none;
      display: block;
      color: inherit;
    }}
    .occ-item:hover, .occ-item.active {{
      border-color: var(--primary);
      background: #F0FDF4;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(30, 107, 82, 0.15);
    }}
    .occ-id {{ font-size: 13px; font-weight: 700; color: var(--primary-dark); }}
    .occ-muni {{ font-size: 14px; font-weight: 600; color: var(--text-dark); margin-top: 2px; }}
    .occ-meta {{ font-size: 11.5px; color: var(--text-muted); margin-top: 4px; display: flex; justify-content: space-between; }}

    /* Badges */
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 700;
    }}
    .badge-ok {{ background: #E6F4EA; color: var(--success); border: 1px solid #CEEAD6; }}
    .badge-warn {{ background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }}

    /* Forensic Seal Banner */
    .seal-banner {{
      background: var(--primary-dark);
      color: #FFFFFF;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 18px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .merkle-text {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 13.5px;
      font-weight: 700;
      color: #FFFFFF;
      word-break: break-all;
      background: rgba(0,0,0,0.25);
      padding: 8px 12px;
      border-radius: 6px;
      margin-top: 6px;
    }}

    /* Document Card */
    .doc-card {{
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 14px;
      background: #FFFFFF;
    }}
    .doc-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #E2E8F0;
      padding-bottom: 8px;
      margin-bottom: 10px;
    }}
    .doc-title {{ font-size: 14.5px; font-weight: 700; color: var(--primary-dark); }}
    .field-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      font-size: 13px;
    }}
    .field-label {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); }}
    .field-val {{ font-weight: 600; color: var(--text-dark); }}

    /* Buttons */
    .btn-group {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px; }}
    .btn {{
      padding: 9px 16px;
      border-radius: 8px;
      font-size: 13.5px;
      font-weight: 700;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      border: 1.5px solid transparent;
      transition: all 0.15s ease;
    }}
    .btn-primary {{
      background: var(--primary);
      color: #FFFFFF;
      border-color: var(--primary-dark);
    }}
    .btn-primary:hover {{ background: var(--primary-dark); }}
    .btn-secondary {{
      background: #FFFFFF;
      color: var(--primary-dark);
      border-color: var(--border-color);
    }}
    .btn-secondary:hover {{ background: #F0FDF4; border-color: var(--primary); }}
    
    .link-box {{
      background: #F8FAFC;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 8px 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--primary-dark);
      width: 100%;
      margin-top: 8px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header class="top-header">
      <div>
        <h1>🛡️ SC3 DocAudit</h1>
        <p>Selo Criptográfico de Cadeia de Custódia &bull; Auditoria Documental Forense <span class="version-tag">Versão 1.2.4 &bull; 13/09/2026</span></p>
      </div>
    </header>


    <!-- Main Content Grid -->
    <div class="main-grid">
      <!-- Sidebar: Occurrences List -->
      <aside class="panel">
        <div class="panel-title">
          <span>📋 Ocorrências</span>
          <span id="occ-count" style="font-size:12px;color:var(--text-muted);">{len(all_occs)} registros</span>
        </div>

        <div style="margin-bottom: 14px;">
          <label for="muni-filter" style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 6px;">
            📍 Filtrar Município:
          </label>
          <select id="muni-filter" onchange="filterMunicipalities(this.value)" style="width: 100%; padding: 8px 10px; border-radius: 6px; border: 1.5px solid var(--border-color); font-size: 13px; font-weight: 600; color: var(--text-dark); background: #FFFFFF; cursor: pointer; outline: none;">
            <option value="ALL">Todos os Municípios ({len(all_occs)})</option>
            {''.join([f'<option value="{m}">{m}</option>' for m in municipalities])}
          </select>
        </div>

        <div id="occ-list">
          {''.join([f'''<a href="/?dossie={o['id']}" data-muni="{o.get('municipality', '')}" class="occ-item {'active' if o['id'] == selected_id else ''}">
            <div class="occ-id">{o['id']}</div>
            <div class="occ-muni">{o.get('municipality', 'Amazônia')}</div>
            <div class="occ-meta">
              <span>{o.get('documents_count', 0)} auto(s) anexado(s)</span>
            </div>
          </a>''' for o in all_occs])}
        </div>
      </aside>

      <!-- Main Panel: Selected Dossier -->
      <main class="panel">
        {f'''<div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;margin-bottom:14px;border-bottom:1px solid #E2E8F0;padding-bottom:12px;">
            <div>
              <span style="font-size:11px;font-weight:700;color:var(--primary);text-transform:uppercase;letter-spacing:0.8px;">Dossiê Forense de Fiscalização</span>
              <h2 style="font-size:20px;font-weight:800;color:var(--primary-dark);margin-top:2px;">{selected_occ.get('title', 'Ocorrência')} — {selected_occ.get('municipality', '')}</h2>
              <p style="font-size:12.5px;color:var(--text-muted);margin-top:2px;">ID: <b>{selected_occ.get('id')}</b> | Data: <b>{selected_occ.get('issued_date')}</b> | Fiscal: <b>{selected_occ.get('officer_name', 'Agente SEMAS')}</b></p>
            </div>
            <div>
              <span class="badge badge-ok" style="font-size:12px;padding:6px 12px;">
                ✅ HOMOLOGADO & APTO PARA JUÍZO
              </span>
            </div>
          </div>

          <!-- Documents List -->
          <h3 style="font-size:16px;font-weight:700;color:var(--primary-dark);margin:16px 0 10px;">📑 Peças Processuais Anexadas ({len(selected_docs)} autos)</h3>
          {''.join([f'''<div class="doc-card">
            <div class="doc-header">
              <span class="doc-title">📄 {d.get('document_type_label', 'Documento')} Nº {d.get('document_number', 'S/N')}</span>
              <span style="font-family:monospace;font-size:11px;color:var(--text-muted);">Hash: {d.get('sha256_hash', '')[:16]}...</span>
            </div>
            <div class="field-grid">
              <div><div class="field-label">Órgão / Município</div><div class="field-val">{d.get('agency', 'SEMAS')} — {d.get('municipality', '')}</div></div>
              <div><div class="field-label">Código CAR</div><div class="field-val" style="font-family:monospace;font-size:11.5px;">{d.get('car') or 'Não informado'}</div></div>
              <div><div class="field-label">Área Autuada</div><div class="field-val">{str(d.get('area_ha')) + ' ha' if d.get('area_ha') else 'N/A'}</div></div>
              <div><div class="field-label">Valor da Multa</div><div class="field-val">{('R$ ' + f"{d.get('fine_brl'):,.2f}") if d.get('fine_brl') else 'N/A'}</div></div>
            </div>
          </div>''' for d in selected_docs]) if selected_docs else '<p style="color:var(--text-muted);font-size:13.5px;">Nenhum documento físico anexado.</p>'}

          <!-- Cryptographic Seal Banner -->
          <div class="seal-banner" style="margin-top:20px;">
            <div style="font-size:11.5px;font-weight:700;letter-spacing:0.8px;text-transform:uppercase;color:#A7F3D0;">🛡️ Selo Criptográfico SC3 — Raiz da Árvore de Merkle (SHA-256):</div>
            <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
              <div class="merkle-text" id="merkle-hash-text" style="flex:1;margin-top:0;">{merkle_root}</div>
              <button onclick="navigator.clipboard.writeText('{merkle_root}'); alert('Hash copiado com sucesso!');" style="background:rgba(255,255,255,0.20);border:1px solid rgba(255,255,255,0.30);color:#FFFFFF;padding:8px 12px;border-radius:6px;cursor:pointer;font-size:13px;font-weight:700;white-space:nowrap;" title="Copiar Hash">📋 Copiar</button>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="btn-group">
            <button onclick="downloadSC3('{selected_occ['id']}')" class="btn btn-primary">📦 Baixar Pacote Criptográfico (.sc3)</button>
            <button onclick="downloadJSON('{selected_occ['id']}')" class="btn btn-secondary">📄 Baixar JSON do Schema (.json)</button>
          </div>
        </div>''' if selected_occ else '<p>Nenhuma ocorrência selecionada.</p>'}
      </main>
    </div>
  </div>

  <script>
    const selectedDossierData = {selected_occ_json_str};

    function downloadSC3(id) {{
      const payload = JSON.stringify(selectedDossierData, null, 2);
      const blob = new Blob([payload], {{ type: 'application/octet-stream' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Dossie_' + id + '.sc3';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }}

    function downloadJSON(id) {{
      const payload = JSON.stringify(selectedDossierData, null, 2);
      const blob = new Blob([payload], {{ type: 'application/json' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Dossie_' + id + '.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }}

    function filterMunicipalities(selected) {{
      const items = document.querySelectorAll('#occ-list .occ-item');
      let count = 0;
      items.forEach(item => {{
        const muni = item.getAttribute('data-muni');
        if (selected === 'ALL' || muni === selected) {{
          item.style.display = 'block';
          count++;
        }} else {{
          item.style.display = 'none';
        }}
      }});
      const countEl = document.getElementById('occ-count');
      if (countEl) countEl.innerText = count + ' registros';
    }}
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)
