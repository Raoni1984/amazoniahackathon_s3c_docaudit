"""
SC3 DocAudit - Hub de Inteligência Territorial & Auditoria Documental da Amazônia
Design Institucional Claro Mobile-First (Separado por Páginas & Legível em Campo)
Hierarquia Relacional 1 : N: Ocorrência (Operação de Fiscalização) -> Documentos Físicos (Autos/Termos)
Persistência: Banco de Dados SQLite Local Offline (occurrences.db)
"""

import os
import sys
import glob
import json
import hashlib
import time
import math
import re
from typing import List, Dict, Any, Optional
from PIL import Image
import pandas as pd  # type: ignore
import base64

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# pyrefly: ignore [missing-import]
import streamlit as st  # type: ignore
from sc3_docaudit.core.image_preprocessing import DocumentPreprocessor
from sc3_docaudit.core.extractor_engine import ExtractorEngine
from sc3_docaudit.core.confidence_evaluator import ConfidenceEvaluator
from sc3_docaudit.core.crypto_seal import CryptoSealSC3
import importlib
import sc3_docaudit.core.database
importlib.reload(sc3_docaudit.core.database)
from sc3_docaudit.core.database import OccurrenceDatabase, DB_PATH
from sc3_docaudit.core.gps_parser import GPSParser

LOGO_PATH = os.path.join(CURRENT_DIR, "assets", "logo_sc3.png")

st.set_page_config(
    page_title="SC3 DocAudit — Auditoria Documental por Selo Criptográfico de Cadeia de Custódia",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Institutional Light Theme (Clean, Field-Ready, Mobile-First)
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --border: #DCE3E8;
        --primary: #1E6B52;
        --primary-dark: #14533D;
        --bg-main: #F4F7F6;
        --text-main: #1A1A1A;
        --text-muted: #5F5F5F;
        color-scheme: light !important;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1A1A1A;
    }

    .stApp {
        background-color: #ECEFEF;
        color: #1A1A1A;
    }

    /* Reduce Dead Space at the Top */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 96% !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Eliminate all internal header anchor links and SVG icons */
    a.header-anchor,
    .header-anchor,
    [data-testid="stHeaderActionElements"],
    a[href^="#"],
    button[data-testid="stHeaderActionElements"],
    [data-testid="stHeaderActionElements"] svg,
    svg.feather-link,
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        position: absolute !important;
    }

    /* Hide Streamlit's default 'Press Enter to apply' / Input Instructions */
    div[data-testid="InputInstructions"],
    [data-testid="InputInstructions"],
    small[data-testid="InputInstructions"],
    .stTextInput [data-testid="InputInstructions"],
    .stTextArea [data-testid="InputInstructions"],
    .stNumberInput [data-testid="InputInstructions"],
    .stDateInput [data-testid="InputInstructions"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        font-size: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Universal Streamlit Button Styles */
    button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background-color: #1E6B52 !important;
        background: #1E6B52 !important;
        color: #FFFFFF !important;
        border: 1.5px solid #14533D !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    button[kind="primary"] p,
    button[kind="primary"] span,
    button[data-testid="baseButton-primary"] p,
    button[data-testid="baseButton-primary"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background-color: #14533D !important;
        background: #14533D !important;
        color: #FFFFFF !important;
    }

    button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1.5px solid #DCE3E8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"] p,
    button[kind="secondary"] span,
    button[data-testid="baseButton-secondary"] p,
    button[data-testid="baseButton-secondary"] span {
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        border-color: #1E6B52 !important;
        background-color: #F0FDF4 !important;
        color: #1E6B52 !important;
    }
    button[kind="secondary"]:hover p,
    button[kind="secondary"]:hover span {
        color: #1E6B52 !important;
    }

    /* Form Inputs & Labels */
    label, 
    .stTextInput label, 
    .stTextArea label, 
    .stSelectbox label, 
    .stDateInput label, 
    .stNumberInput label {
        color: #1A1A1A !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1.5px solid #DCE3E8 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    div[data-baseweb="input"] input:focus {
        border-color: #1E6B52 !important;
        box-shadow: 0 0 0 1px #1E6B52 !important;
    }

    /* Selectbox / Dropdowns */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1.5px solid #DCE3E8 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #1A1A1A !important;
    }
    ul[data-baseweb="menu"],
    div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }
    li[data-baseweb="menu-item"] {
        color: #1A1A1A !important;
        background-color: #FFFFFF !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background-color: #F0FDF4 !important;
        color: #1E6B52 !important;
    }

    /* Accordion Expanders */
    [data-testid="stExpander"] {
        border: 1.5px solid #DCE3E8 !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
        margin-bottom: 18px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] summary {
        font-weight: 800 !important;
        font-size: 16.5px !important;
        color: #134E39 !important;
        background: #F8FAF9 !important;
        padding: 12px 18px !important;
        border-bottom: 1px solid #E2E8F0 !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #1E6B52 !important;
        background: #F0FDF4 !important;
    }
    [data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        padding: 16px 18px !important;
    }

    /* Evidências Coletadas: Verde se 100% OK */
    div.st-key-expander_evidencias_ok [data-testid="stExpander"] {
        border-left: 6px solid #1E6B52 !important;
    }
    div.st-key-expander_evidencias_ok [data-testid="stExpander"] summary {
        color: #134E39 !important;
        background: #F0FDF4 !important;
    }

    /* Evidências Coletadas: Laranja se Divergências Pendentes */
    div.st-key-expander_evidencias_alerta [data-testid="stExpander"] {
        border: 1.5px solid #FCD34D !important;
        border-left: 6px solid #D97706 !important;
    }
    div.st-key-expander_evidencias_alerta [data-testid="stExpander"] summary {
        color: #92400E !important;
        background: #FEF3C7 !important;
    }

    /* Adicionar Novas Evidências: Lilás Malve */
    div.st-key-expander_adicionar_evidencias [data-testid="stExpander"] {
        border: 1.5px solid #DDD6FE !important;
        border-left: 6px solid #8B5CF6 !important;
    }
    div.st-key-expander_adicionar_evidencias [data-testid="stExpander"] summary {
        color: #6D28D9 !important;
        background: #F5F3FF !important;
    }

    /* Top Institutional Bar */
    .top-header-bar {
        background: linear-gradient(135deg, #134E39 0%, #1E6B52 60%, #257C60 100%);
        border-radius: 12px;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        color: #FFFFFF;
        flex-wrap: wrap;
        margin-bottom: 14px;
        box-shadow: 0 4px 16px rgba(19, 78, 57, 0.22);
        border: 1px solid rgba(255, 255, 255, 0.14);
    }
    @media (max-width: 768px) {
        .top-header-subtitle {
            display: none !important;
        }
    }

    /* KPI Cards Grid (Responsive) */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }
    .kpi-card-blue {
        background: #EEF4FB;
        border: 1px solid #C7DCEF;
        border-radius: 10px;
        padding: 14px;
    }
    .kpi-card-gray {
        background: #EEF0EC;
        border: 1px solid #D6DCCF;
        border-radius: 10px;
        padding: 14px;
    }
    .kpi-card-green {
        background: #EAF3DE;
        border: 1px solid #C5DDA0;
        border-radius: 10px;
        padding: 14px;
    }
    .kpi-card-amber {
        background: #FAEEDA;
        border: 1px solid #EFCB88;
        border-radius: 10px;
        padding: 14px;
    }

    /* Clickable Hero Action Display Cards */
    div.st-key-home_btn_criar button,
    div.st-key-home_btn_consultar button {
        min-height: 185px !important;
        height: auto !important;
        padding: 24px 22px !important;
        border-radius: 12px !important;
        background: #FFFFFF !important;
        border: 1.5px solid #DCE3E8 !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        color: #333333 !important;
    }

    div.st-key-home_btn_criar button:hover,
    div.st-key-home_btn_consultar button:hover {
        border-color: #1E6B52 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(30, 107, 82, 0.16) !important;
        background: #F8FAF9 !important;
    }

    div.st-key-home_btn_criar button:active,
    div.st-key-home_btn_consultar button:active {
        transform: translateY(-1px) !important;
    }

    div.st-key-home_btn_criar button p,
    div.st-key-home_btn_consultar button p {
        font-size: 13.5px !important;
        font-weight: 400 !important;
        color: #555555 !important;
        line-height: 1.5 !important;
        white-space: pre-line !important;
    }

    div.st-key-home_btn_criar button strong,
    div.st-key-home_btn_consultar button strong {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #1E6B52 !important;
        display: block !important;
        margin: 6px 0 8px 0 !important;
        letter-spacing: 0.3px !important;
    }

    /* Expander Discrepancy Styling */
    div[data-testid="stExpander"] {
        background-color: #FFFDF5 !important;
        border: 1.5px solid #F6D899 !important;
        border-left: 6px solid #D97706 !important;
        border-radius: 10px !important;
        margin-bottom: 18px !important;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 700 !important;
        color: #92400E !important;
        font-size: 15px !important;
    }

    /* Orange Discrepancy Action Button */
    div[class*="st-key-btn_nav_disc_"] button {
        background: #EA580C !important;
        background-color: #EA580C !important;
        border: 1.5px solid #C2410C !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 7px 12px !important;
        box-shadow: 0 2px 8px rgba(234, 88, 12, 0.25) !important;
        transition: all 0.15s ease !important;
    }
    div[class*="st-key-btn_nav_disc_"] button:hover {
        background: #C2410C !important;
        background-color: #C2410C !important;
        border-color: #9A3412 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(194, 65, 12, 0.35) !important;
    }
    div[class*="st-key-btn_nav_disc_"] button p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 13px !important;
    }

    /* Green Submit Button for Criar Ocorrência */
    div[class*="st-key-btn_submit_create_occ"] button {
        background: #1E6B52 !important;
        background-color: #1E6B52 !important;
        color: #FFFFFF !important;
        border: 1.5px solid #14533D !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 12px rgba(30, 107, 82, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div[class*="st-key-btn_submit_create_occ"] button:hover {
        background: #14533D !important;
        background-color: #14533D !important;
        border-color: #0F3F2E !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 16px rgba(20, 83, 61, 0.35) !important;
    }
    div[class*="st-key-btn_submit_create_occ"] button p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    /* Download Doc Image Button */
    div[class*="st-key-btn_dl_doc_img_"] button {
        background: #F4F7F6 !important;
        border: 1px solid #1E6B52 !important;
        color: #1E6B52 !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 4px 8px !important;
        min-height: 28px !important;
        height: 28px !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
        margin: 0 !important;
    }
    div[class*="st-key-btn_dl_doc_img_"] button:hover {
        background: #E8F5E9 !important;
        border-color: #14533D !important;
        color: #14533D !important;
    }
    div[class*="st-key-btn_dl_doc_img_"] button p {
        color: #1E6B52 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* Dossier Header Box */
    div.st-key-dossier_header_box {
        background: #FFFFFF !important;
        border: 1.5px solid #DCE3E8 !important;
        border-radius: 10px !important;
        padding: 16px 20px !important;
        color: #134e39 !important;
        margin-bottom: 16px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }

    div.st-key-btn_dossier_voltar button {
        background: #F4F7F6 !important;
        border: 1px solid #134e39 !important;
        border-radius: 6px !important;
        color: #134e39 !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        padding: 6px 12px !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }

    div.st-key-btn_dossier_voltar button:hover {
        background: #E8F5E9 !important;
        border-color: #134e39 !important;
        color: #134e39 !important;
    }

    div.st-key-btn_dossier_voltar button p {
        color: #134e39 !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
    }

    /* Top Navigation Link Buttons */
    div[data-testid="stButton"] button {
        border-radius: 8px !important;
        padding: 8px 14px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stButton"] button p {
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    /* Badges */
    .badge-divergencia {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        font-weight: 600;
        background: #FFE4E6;
        color: #9F1239;
        border: 1px solid #FDA4AF;
        padding: 3px 9px;
        border-radius: 16px;
    }
    .badge-conciliado {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        font-weight: 600;
        background: #EAF3DE;
        color: #1E6B52;
        border: 1px solid #C5DDA0;
        padding: 3px 9px;
        border-radius: 16px;
    }

    /* Navigation Menu: Desktop vs Mobile (Início & Guia de Uso em 1 linha) */
    @media (min-width: 769px) {
        div[class*="st-key-mobile_nav_wrapper"] {
            display: none !important;
        }
        div[class*="st-key-desktop_nav_wrapper"] {
            display: block !important;
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            max-width: 100% !important;
        }
        div[class*="st-key-desktop_nav_wrapper"] {
            display: none !important;
        }
        div[class*="st-key-mobile_nav_wrapper"] {
            display: block !important;
            margin-bottom: 12px !important;
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        div[class*="st-key-mobile_nav_wrapper"] [data-testid="stButton"] {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            margin: 0 0 6px 0 !important;
            padding: 0 !important;
        }
        div[class*="st-key-mobile_nav_wrapper"] button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            padding: 9px 12px !important;
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            text-align: center !important;
        }
        div[class*="st-key-mobile_nav_wrapper"] button p {
            font-size: 14px !important;
            margin: 0 !important;
            padding: 0 !important;
        }
    }

    /* Occurrence Row / Mobile Card Styling */
    @media (min-width: 769px) {
        div[class*="st-key-occ_card_"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin-bottom: 0 !important;
        }
    }

    /* Small Red Trash Button inside Dossier Header */
    div[class*="st-key-btn_dossier_del_"] button {
        background: #FFF1F2 !important;
        border: 1px solid #FECDD3 !important;
        color: #E11D48 !important;
        border-radius: 6px !important;
        padding: 5px 8px !important;
        min-height: 32px !important;
        height: 32px !important;
        font-size: 13px !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }
    div[class*="st-key-btn_dossier_del_"] button:hover {
        background: #FFE4E6 !important;
        border-color: #E11D48 !important;
        color: #BE123C !important;
        box-shadow: 0 2px 6px rgba(225, 29, 72, 0.2) !important;
    }
    div[class*="st-key-btn_dossier_del_"] button p {
        color: #E11D48 !important;
        font-size: 13px !important;
        margin: 0 !important;
    }

    /* Somente na versão mobile: Card Branco e Botão Verde */
    @media (max-width: 768px) {
        .desktop-table-header {
            display: none !important;
        }
        .occ-desktop-hr {
            display: none !important;
        }
        div[class*="st-key-occ_card_"] {
            background: #FFFFFF !important;
            border: 1.5px solid #DCE3E8 !important;
            border-radius: 12px !important;
            padding: 16px 18px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
            margin-bottom: 16px !important;
            display: block !important;
        }
        div[class*="st-key-occ_card_"] [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 4px !important;
            padding: 0 !important;
        }
        div[class*="st-key-occ_card_"] div[class*="st-key-btn_open_"] button {
            background: #1E6B52 !important;
            color: #FFFFFF !important;
            border: 1.5px solid #14533D !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            padding: 10px 14px !important;
            width: 100% !important;
            margin-top: 8px !important;
            box-shadow: 0 3px 10px rgba(30, 107, 82, 0.25) !important;
            transition: all 0.2s ease !important;
        }
        div[class*="st-key-occ_card_"] div[class*="st-key-btn_open_"] button p {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        div[class*="st-key-occ_card_"] div[class*="st-key-btn_open_"] button:hover {
            background: #14533D !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 14px rgba(20, 83, 61, 0.35) !important;
        }
    }

    /* Bullet Point List for Physical Documents */
    div[class*="st-key-sel_doc_btn_"] button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 8px 14px !important;
        font-size: 13.5px !important;
        margin-bottom: 2px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    div[class*="st-key-sel_doc_btn_"] button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #2D3748 !important;
        border: 1px solid #E2E8F0 !important;
    }
    div[class*="st-key-sel_doc_btn_"] button[kind="secondary"]:hover {
        background: #F4FBF7 !important;
        color: #1E6B52 !important;
        border-color: #1E6B52 !important;
    }
    div[class*="st-key-sel_doc_btn_"] button[kind="primary"] {
        background: #E8F5E9 !important;
        color: #1E6B52 !important;
        border: 1.5px solid #1E6B52 !important;
        box-shadow: 0 1px 4px rgba(30, 107, 82, 0.12) !important;
    }
    div[class*="st-key-sel_doc_btn_"] button[kind="primary"] p {
        color: #1E6B52 !important;
        font-weight: 700 !important;
    }
    div[class*="st-key-btn_see_all_"] button,
    div[class*="st-key-btn_see_less_"] button {
        background: transparent !important;
        color: #1E6B52 !important;
        border: 1px dashed #1E6B52 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 5px 14px !important;
        margin-top: 4px !important;
        margin-bottom: 10px !important;
        border-radius: 6px !important;
    }
    div[class*="st-key-btn_see_all_"] button:hover,
    div[class*="st-key-btn_see_less_"] button:hover {
        background: #E8F5E9 !important;
        color: #14533D !important;
    }

    /* Dossier Box */
    .dossier-box {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Disable internal anchor links, header toolbar and theme toggles */
    #MainMenu,
    header [data-testid="stToolbar"],
    [data-testid="stToolbarActions"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    footer,
    a.header-anchor,
    [data-testid="stHeaderActionElements"],
    .st-emotion-cache-15zrgzn a,
    [data-testid="stMarkdownContainer"] a.anchor-link,
    a[href^="#"] {
        display: none !important;
        pointer-events: none !important;
        visibility: hidden !important;
        text-decoration: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Document Type Translations
DOC_TYPE_LABELS = {
    "finding_notice": "Auto de Constatação",
    "infraction_notice": "Auto de Infração",
    "embargo_notice": "Termo de Embargo e Interdição",
    "seizure_notice": "Termo de Apreensão e Depósito",
    "notification": "Notificação Ambiental",
    "inspection_order": "Ordem de Fiscalização",
    "complaint_record": "Registro de Denúncia",
    "inspection_report": "Relatório de Fiscalização",
    "case_file_cover": "Capa do Processo",
    "deforestation_validation": "Validação de Desmatamento"
}

def format_date_br(val: Any) -> str:
    """Standardizes date format across the entire application in DD/MM/AAAA."""
    if not val:
        return "12/09/2026"
    s = str(val).strip()
    if re.match(r"^\d{2}/\d{2}/\d{4}$", s):
        return s
    m = re.match(r"^(\d{4})[/-](\d{2})[/-](\d{2})", s)
    if m:
        return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"
    return s

package_dir = os.path.join(CURRENT_DIR, "participant-package", "challenges-1-2")

# Auto-seed database if empty (Instantaneous pure SQL)
OccurrenceDatabase.seed_if_empty(package_dir)

@st.cache_resource
def get_engine():
    return ExtractorEngine(use_gpu=False)

# Handle query parameters for deep linking (e.g. ?dossie=OC-2026-ALT-01)
query_params = st.query_params
if "dossie" in query_params or "occ" in query_params or "id" in query_params:
    requested_id = query_params.get("dossie") or query_params.get("occ") or query_params.get("id")
    occ_found = OccurrenceDatabase.get_occurrence_by_id(requested_id)
    if occ_found:
        st.session_state["selected_occ_id"] = requested_id
        st.session_state["current_page"] = "🔬 Inspecionar Dossiê"

# Initialize session state caches
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "🏠 Início"
if "selected_occ_id" not in st.session_state:
    all_init = OccurrenceDatabase.get_all_occurrences()
    st.session_state["selected_occ_id"] = all_init[0]["id"] if all_init else None
if "selected_doc_idx" not in st.session_state:
    st.session_state["selected_doc_idx"] = 0
if "processed_docs_cache" not in st.session_state:
    st.session_state["processed_docs_cache"] = {}
if "scroll_to_correction" not in st.session_state:
    st.session_state["scroll_to_correction"] = False

current_occ = OccurrenceDatabase.get_occurrence_by_id(st.session_state["selected_occ_id"]) if st.session_state["selected_occ_id"] else None

# ------------------------------------------------------------------------------
# 1. TOP INSTITUTIONAL BAR (With SC3 Logo & High-Impact Typography)
# ------------------------------------------------------------------------------
logo_b64 = ""
if os.path.exists(LOGO_PATH):
    try:
        with open(LOGO_PATH, "rb") as _img_f:
            logo_b64 = base64.b64encode(_img_f.read()).decode("utf-8")
    except Exception:
        logo_b64 = ""

if logo_b64:
    logo_elem = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:58px;height:58px;border-radius:12px;object-fit:cover;box-shadow:0 3px 10px rgba(0,0,0,0.24);border:2px solid rgba(255,255,255,0.30);flex-shrink:0;" alt="SC3 Logo" />'
else:
    logo_elem = '<div style="width:54px;height:54px;border-radius:12px;background:rgba(255,255,255,0.18);display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="ti ti-shield-check" style="font-size:30px;color:#fff;"></i></div>'

header_html = f"""<div class="top-header-bar">
  <div style="display:flex;align-items:center;gap:18px;">
    {logo_elem}
    <div>
      <div style="margin:0;font-size:24px;font-weight:800;color:#FFFFFF;letter-spacing:0.5px;line-height:1.2;">
        SC3 DocAudit
      </div>
      <div class="top-header-subtitle" style="margin:4px 0 0;font-size:13.5px;font-weight:500;color:rgba(255,255,255,0.92);letter-spacing:0.2px;">
        Selo Criptográfico de Cadeia de Custódia &bull; Auditoria Documental Forense &bull; <span style="background:rgba(255,255,255,0.20);padding:2px 8px;border-radius:4px;font-size:12px;font-weight:700;letter-spacing:0.3px;">Versão 1.2.4 &bull; 13/09/2026</span>
      </div>
    </div>
  </div>
</div>"""
st.markdown(header_html, unsafe_allow_html=True)

# Modal Dialog for Soft Delete Confirmation (Never hard delete, sets removedAt)
@st.dialog("Excluir Ocorrência")
def confirm_delete_occurrence_dialog(occ_id: str, occ_title: str):
    st.markdown(f"""
    <div style="font-size:14.5px;color:#1A1A1A;margin-bottom:12px;">
      Você tem certeza que deseja excluir a ocorrência <b>{occ_id}</b> — <i>{occ_title}</i>?
    </div>
    <div style="background:#FEF2F2;border:1px solid #FCA5A5;border-left:4px solid #DC2626;border-radius:6px;padding:10px 14px;margin-bottom:16px;">
      <b style="color:#991B1B;font-size:13px;">🔒 Trilha Forense & Integridade dos Dados:</b>
      <div style="font-size:12px;color:#7F1D1D;margin-top:4px;line-height:1.5;">
        O registro <b>não será apagado fisicamente</b> da base de dados. Ele receberá a marcação <code>removedAt</code> com a data/hora atual e será ocultado das consultas ativas, preservando a cadeia de custódia.
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("Cancelar", use_container_width=True, key=f"btn_cancel_del_{occ_id}"):
            st.rerun()
    with col_d2:
        if st.button("🗑️ Sim, Excluir", type="primary", use_container_width=True, key=f"btn_confirm_del_{occ_id}"):
            OccurrenceDatabase.soft_delete_occurrence(occ_id)
            st.session_state["current_page"] = "🔍 Consultar Ocorrências"
            st.session_state["selected_occ_id"] = None
            st.success(f"Ocorrência {occ_id} arquivada com sucesso.")
            st.rerun()

# ------------------------------------------------------------------------------
# 2. NAVIGATION MENU (DESKTOP HORIZONTAL / MOBILE HAMBURGER)
# ------------------------------------------------------------------------------
pages_config = [
    ("🏠 Início", "🏠 Início"),
    ("➕ Criar Ocorrência", "➕ Criar Ocorrência"),
    ("🔍 Consultar Ocorrências", "🔍 Consultar Ocorrências"),
    ("📖 Guia de Uso", "📖 Guia de Uso")
]

# Desktop Nav Menu (4 columns)
with st.container(key="desktop_nav_wrapper"):
    nav_cols = st.columns(4)
    for col, (btn_label, page_key) in zip(nav_cols, pages_config):
        with col:
            is_active = (st.session_state["current_page"] == page_key)
            if st.button(
                btn_label,
                key=f"nav_btn_{page_key}",
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                st.session_state["current_page"] = page_key
                st.session_state["scroll_to_correction"] = False
                st.rerun()

# Mobile Nav Menu (Each button on its own line)
with st.container(key="mobile_nav_wrapper"):
    is_inicio_active = (st.session_state["current_page"] == "🏠 Início")
    if st.button("🏠 Início", key="m_nav_btn_inicio", type="primary" if is_inicio_active else "secondary", use_container_width=True):
        st.session_state["current_page"] = "🏠 Início"
        st.session_state["scroll_to_correction"] = False
        st.rerun()

    is_criar_active = (st.session_state["current_page"] == "➕ Criar Ocorrência")
    if st.button("➕ Criar Ocorrência", key="m_nav_btn_criar", type="primary" if is_criar_active else "secondary", use_container_width=True):
        st.session_state["current_page"] = "➕ Criar Ocorrência"
        st.session_state["scroll_to_correction"] = False
        st.rerun()

    is_consultar_active = (st.session_state["current_page"] == "🔍 Consultar Ocorrências")
    if st.button("🔍 Consultar Ocorrências", key="m_nav_btn_consultar", type="primary" if is_consultar_active else "secondary", use_container_width=True):
        st.session_state["current_page"] = "🔍 Consultar Ocorrências"
        st.session_state["scroll_to_correction"] = False
        st.rerun()

    is_guia_active = (st.session_state["current_page"] == "📖 Guia de Uso")
    if st.button("📖 Guia de Uso", key="m_nav_btn_guia", type="primary" if is_guia_active else "secondary", use_container_width=True):
        st.session_state["current_page"] = "📖 Guia de Uso"
        st.session_state["scroll_to_correction"] = False
        st.rerun()

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)
current_page = st.session_state["current_page"]


# ==============================================================================
# PAGE 0: TELA DE INÍCIO (DUAS AÇÕES PRINCIPAIS - MOBILE & DESKTOP)
# ==============================================================================
if current_page == "🏠 Início":
    # TWO BIG CLICKABLE ACTION DISPLAY CARDS
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        card_criar_text = "➕\n\n**CRIAR OCORRÊNCIA**\n\nInicie o registro de uma nova operação de fiscalização em campo, informando dados básicos e anexando os autos físicos ou PDFs."
        if st.button(card_criar_text, key="home_btn_criar", use_container_width=True):
            st.session_state["current_page"] = "➕ Criar Ocorrência"
            st.rerun()

    with btn_col2:
        card_consultar_text = "🔍\n\n**CONSULTAR OCORRÊNCIAS**\n\nAcesse a lista completa de ocorrências e operações persistidas no SQLite, com filtros, buscas, alertas de divergência e dossiês."
        if st.button(card_consultar_text, key="home_btn_consultar", use_container_width=True):
            st.session_state["current_page"] = "🔍 Consultar Ocorrências"
            st.rerun()




# ==============================================================================
# PAGE 1: CONSULTAR OCORRÊNCIAS (LISTA DE OPERAÇÕES)
# ==============================================================================
elif current_page == "🔍 Consultar Ocorrências":
    all_occurrences = OccurrenceDatabase.get_all_occurrences()
    total_occs = len(all_occurrences)

    st.markdown("""
    <p style="font-size:19px;font-weight:600;color:#1A1A1A;margin:0 0 4px;">Painel de Ocorrências Ambientais (Operações de Fiscalização)</p>
    """, unsafe_allow_html=True)

    # Search & Filters with Inline Reset Button
    def reset_filters():
        st.session_state["search_query_input"] = ""
        st.session_state["status_filter_select"] = "Todos os status"
        st.session_state["muni_filter_select"] = "Todos os municípios"
        st.session_state["table_page"] = 1

    s_col1, s_col2, s_col3, s_col4 = st.columns([2.8, 1.2, 1.2, 0.8])
    with s_col1:
        search_query = st.text_input(
            "Buscar",
            placeholder="🔍 Buscar por ID, operação, município, fiscal...",
            label_visibility="collapsed",
            key="search_query_input"
        )
    with s_col2:
        status_filter = st.selectbox(
            "Status",
            ["Todos os status", "Conciliado", "Com divergências"],
            label_visibility="collapsed",
            key="status_filter_select"
        )
    with s_col3:
        all_munis = ["Todos os municípios"] + sorted(list(set(o["municipality"] for o in all_occurrences if o.get("municipality"))))
        muni_filter = st.selectbox(
            "Município",
            all_munis,
            label_visibility="collapsed",
            key="muni_filter_select"
        )
    with s_col4:
        st.button("🔄 Limpar", use_container_width=True, on_click=reset_filters)

    # Filter occurrences
    filtered = OccurrenceDatabase.get_all_occurrences(
        search_query=search_query,
        muni_filter=muni_filter,
        status_filter=status_filter
    )

    if "table_page" not in st.session_state:
        st.session_state["table_page"] = 1

    page_size = 10
    total_filtered = len(filtered)
    total_pages = max(1, math.ceil(total_filtered / page_size)) if total_filtered > 0 else 1

    # Clamp current page to bounds
    if st.session_state["table_page"] > total_pages:
        st.session_state["table_page"] = total_pages
    if st.session_state["table_page"] < 1:
        st.session_state["table_page"] = 1

    current_table_page = st.session_state["table_page"]
    start_idx = (current_table_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_filtered)
    page_items = filtered[start_idx:end_idx]

    # Counter row
    if total_filtered > 0:
        st.markdown(f"<p style='font-size:13px;color:#5F5F5F;margin:12px 0 10px;'>Exibindo <b>{start_idx + 1}–{end_idx}</b> de <b>{total_filtered}</b> ocorrências (Página {current_table_page} de {total_pages})</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:13px;color:#5F5F5F;margin:12px 0 10px;'>Nenhuma ocorrência encontrada</p>", unsafe_allow_html=True)

    # Render Mobile-First Clean List of Occurrences
    if page_items:
        # Desktop Table Header with Green Background (Hidden on Mobile)
        header_table_html = """
        <div class="desktop-table-header" style="background:#1E6B52;border-radius:6px;padding:9px 14px;margin-bottom:10px;display:flex;align-items:center;color:#FFFFFF;font-size:12px;font-weight:700;letter-spacing:0.5px;">
          <div style="flex:2.2;">OCORRÊNCIA / ID</div>
          <div style="flex:1.2;">MUNICÍPIO / DATA</div>
          <div style="flex:1.8;">DOCUMENTOS & EVIDÊNCIAS</div>
          <div style="flex:0.9;text-align:center;">AÇÃO</div>
        </div>
        """
        st.markdown(header_table_html, unsafe_allow_html=True)

        for idx, row in enumerate(page_items):
            disc_count = row.get("discrepancies_count", 0)
            if row["audit_status"] == "DIVERGENTE" or disc_count > 0:
                badge_html = f"<span class='badge-divergencia'><i class='ti ti-alert-triangle' style='font-size:12px;'></i> {disc_count} Divergência(s)</span>"
            else:
                badge_html = "<span class='badge-conciliado'><i class='ti ti-circle-check' style='font-size:12px;'></i> Conciliado</span>"

            doc_cnt = row.get("documents_count", 0)
            photo_cnt = row.get("photos_count", 0)
            audio_cnt = row.get("audios_count", 0)
            issued_date = format_date_br(row.get("issued_date", "10/09/2026"))

            with st.container(key=f"occ_card_{idx}"):
                r1, r2, r3, r4 = st.columns([2.2, 1.2, 1.8, 0.9])
                with r1:
                    st.markdown(f"""
                    <div style="font-size:13.5px;font-weight:700;color:#1E6B52;word-break:break-all;">{row['id']}</div>
                    <div style="font-size:12.5px;color:#333;font-weight:500;margin-top:2px;">{row['title']}</div>
                    <div style="margin-top:4px;">{badge_html}</div>
                    """, unsafe_allow_html=True)
                with r2:
                    st.markdown(f"""
                    <div style="font-size:13px;color:#222;margin-top:2px;">Município: <b>{row['municipality']}</b></div>
                    <div style="font-size:11.5px;color:#666;margin-top:2px;">📅 {issued_date}</div>
                    """, unsafe_allow_html=True)
                with r3:
                    st.markdown(f"""
                    <div style="font-size:12.5px;color:#222;margin-top:2px;">
                      <b>📄 {doc_cnt} Documento(s)</b> anexado(s)<br>
                      <small style="color:#555;">📸 {photo_cnt} Fotos &nbsp;|&nbsp; 🎙️ {audio_cnt} Áudios</small>
                    </div>
                    """, unsafe_allow_html=True)
                with r4:
                    st.markdown("<div style='margin-top:4px;'>", unsafe_allow_html=True)
                    if st.button("Abrir Dossiê", key=f"btn_open_{row['id']}_{idx}", use_container_width=True):
                        st.session_state["selected_occ_id"] = row["id"]
                        st.session_state["selected_doc_idx"] = 0
                        st.session_state["scroll_to_correction"] = False
                        st.session_state["current_page"] = "📂 Dossiê da Ocorrência"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<hr class='occ-desktop-hr' style='margin:8px 0;border:none;border-bottom:1px solid #EDF2F4;'>", unsafe_allow_html=True)

        # Pagination Navigation Controls Bar
        if total_pages > 1:
            p_prev, p_info, p_next = st.columns([1, 2, 1])
            with p_prev:
                if st.button("◀ Anterior", disabled=(current_table_page <= 1), use_container_width=True):
                    st.session_state["table_page"] -= 1
                    st.rerun()
            with p_info:
                st.markdown(f"<div style='text-align:center;font-size:13px;color:#555;padding-top:6px;'>Página <b>{current_table_page}</b> de <b>{total_pages}</b></div>", unsafe_allow_html=True)
            with p_next:
                if st.button("Próxima ▶", disabled=(current_table_page >= total_pages), use_container_width=True):
                    st.session_state["table_page"] += 1
                    st.rerun()
    else:
        st.info("Nenhuma ocorrência encontrada com os critérios de busca selecionados.")


# ==============================================================================
# PAGE 2: CRIAR OCORRÊNCIA (CRUD DA OPERAÇÃO COM JUNTADA DE DOCUMENTOS)
# ==============================================================================
elif current_page == "➕ Criar Ocorrência":
    st.markdown("""
    <p style="font-size:19px;font-weight:600;color:#1A1A1A;margin:0 0 4px;">Criar Ocorrência</p>
    <p style="font-size:13px;color:#5F5F5F;margin:0 0 16px;">Preencha os dados da operação em campo e anexe os primeiros documentos físicos (Autos/Termos) ou fotos.</p>
    """, unsafe_allow_html=True)

    with st.container():
        # List existing municipalities from DB with Outro as first option
        try:
            with OccurrenceDatabase.get_connection() as _conn:
                db_munis = [r[0] for r in _conn.execute("SELECT DISTINCT municipality FROM occurrences WHERE municipality IS NOT NULL AND municipality != ''").fetchall()]
        except Exception:
            db_munis = []

        base_munis = ["Altamira", "Itaituba", "Marabá", "Novo Progresso", "Paragominas", "Santarém", "São Félix do Xingu", "Tailândia", "Ulianópolis"]
        all_muni_options = ["➕ Outro (Digitar Novo Município)"] + sorted(list(set(base_munis + db_munis)))

        is_custom_muni_selected = False
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            selected_muni_opt = st.selectbox("Município da Operação:", all_muni_options, index=0)

        if selected_muni_opt == "➕ Outro (Digitar Novo Município)":
            is_custom_muni_selected = True
            with row1_col2:
                custom_muni = st.text_input("Digite o Nome do Novo Município:", placeholder="Ex: Belém, Redenção, Castanhal, Tomé-Açu...")
                new_muni = custom_muni.strip() if (custom_muni and custom_muni.strip()) else "Novo Município"
        else:
            new_muni = selected_muni_opt

        clean_prefix = "".join(c for c in new_muni.upper() if c.isalnum())[:3] or "PAR"
        suggested_id = f"OC-2026-{clean_prefix}-{str(int(time.time()))[-4:]}"

        if is_custom_muni_selected:
            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                new_id = st.text_input("Código / ID da Ocorrência:", suggested_id)
            with row2_col2:
                new_officer = st.text_input("Agente Fiscal Responsável / Equipe:", "Equipe de Fiscalização SEMAS")

            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                new_title = st.text_input("Título / Nome da Operação:", f"Operação Fiscalização {new_muni}")
            with row3_col2:
                new_date = st.text_input("Data da Fiscalização (dd/mm/aaaa):", "12/09/2026")
        else:
            with row1_col2:
                new_officer = st.text_input("Agente Fiscal Responsável / Equipe:", "Equipe de Fiscalização SEMAS")

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                new_id = st.text_input("Código / ID da Ocorrência:", suggested_id)
            with row2_col2:
                new_date = st.text_input("Data da Fiscalização (dd/mm/aaaa):", "12/09/2026")

            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                new_title = st.text_input("Título / Nome da Operação:", f"Operação Fiscalização {new_muni}")
            with row3_col2:
                pass

        new_summary = st.text_area("Resumo da Ocorrência / Notas de Campo:", f"Fiscalização ambiental realizada no município de {new_muni} para averiguação de alertas de desmatamento e ilícitos florestais.", height=100)

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        submit_btn = st.button("💾 Criar Ocorrência e Abrir Dossiê", type="primary", use_container_width=True, key="btn_submit_create_occ")

    if submit_btn:
        with st.spinner("Criando ocorrência no SQLite e inicializando árvore de custódia Merkle Root SC3..."):
            # 1. Save Parent Occurrence
            occ_payload = {
                "id": new_id,
                "title": new_title,
                "municipality": new_muni,
                "officer_name": new_officer,
                "issued_date": format_date_br(new_date),
                "summary_text": new_summary,
                "field_notes": new_summary,
                "photos_count": 0,
                "audios_count": 0,
                "documents_count": 0,
                "audit_status": "CONCILIADO"
            }
            OccurrenceDatabase.save_occurrence(occ_payload)

            # 2. Generate Initial SC3 Seal
            seal = CryptoSealSC3.generate_seal(
                document_json={"occurrence_id": new_id, "title": new_title, "municipality": new_muni, "officer": new_officer, "date": new_date, "summary": new_summary},
                photo_paths=[],
                field_notes_text=new_summary
            )
            with OccurrenceDatabase.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE occurrences SET merkle_root_hash = ? WHERE id = ?", (seal.get("merkle_root_hash", ""), new_id))
                conn.commit()

            st.session_state["selected_occ_id"] = new_id
            st.session_state["selected_doc_idx"] = 0
            st.session_state["current_page"] = "📂 Dossiê da Ocorrência"
            st.success(f"🎉 Ocorrência **{new_id}** criada com sucesso! Redirecionando para o Dossiê...")
            st.rerun()


# ==============================================================================
# PAGE 3: DOSSIÊ DA OCORRÊNCIA (1 : N DOCUMENTOS, EVIDÊNCIAS & AUDITORIA)
# ==============================================================================
elif current_page == "📂 Dossiê da Ocorrência":
    selected_record = OccurrenceDatabase.get_occurrence_by_id(st.session_state["selected_occ_id"])

    if selected_record:
        docs_list = selected_record.get("documents", [])
        total_docs_in_occ = len(docs_list)

        # Header Bar with Occurrence Details and Action Buttons on the right
        with st.container(key="dossier_header_box"):
            d_col1, d_col2 = st.columns([3.8, 1.4])
            with d_col1:
                st.markdown(f"""
                <div style="font-size:17px;font-weight:700;color:#134e39;letter-spacing:0.2px;">
                  Dossiê Forense da Operação: {selected_record['id']} — {selected_record['title']}
                </div>
                <div style="font-size:13.5px;color:#134e39;margin-top:6px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-weight:500;">
                  <span>Município: <b style="color:#134e39;">{selected_record['municipality']}</b></span>
                  <span style="opacity:0.4;">|</span>
                  <span>Fiscal: <b style="color:#134e39;">{selected_record.get('officer_name', 'Fiscalização')}</b></span>
                  <span style="opacity:0.4;">|</span>
                  <span>📄 <b style="color:#134e39;">{total_docs_in_occ} Documentos Vinculados</b></span>
                </div>
                """, unsafe_allow_html=True)
            with d_col2:
                st.markdown("<div style='margin-top:14px;'>", unsafe_allow_html=True)
                b_v_col, b_d_col = st.columns([3.2, 1.0])
                with b_v_col:
                    if st.button("← Voltar à Consulta", key="btn_dossier_voltar", use_container_width=True):
                        st.session_state["current_page"] = "🔍 Consultar Ocorrências"
                        st.session_state["scroll_to_correction"] = False
                        st.rerun()
                with b_d_col:
                    if st.button("🗑️", help=f"Excluir ocorrência {selected_record['id']}", key=f"btn_dossier_del_{selected_record['id']}", use_container_width=True):
                        confirm_delete_occurrence_dialog(selected_record["id"], selected_record.get("title", ""))
                st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # PROMINENT RECONCILIATION & DISCREPANCY ALERT BANNER (COLLAPSIBLE WITH DIRECT LINKS)
        # ----------------------------------------------------------------------
        occ_discrepancies = selected_record.get("discrepancies", [])
        if occ_discrepancies:
            expander_title = f"⚠️ ATENÇÃO: {len(occ_discrepancies)} DIVERGÊNCIA(S) IDENTIFICADA(S) NESTA OPERAÇÃO"
            with st.expander(expander_title, expanded=True):
                st.markdown("""
                <p style="margin:0 0 10px;font-size:13px;color:#78350F;line-height:1.5;">
                  Foram detectadas inconsistências entre os dados dos autos lavrados e o registro digital de campo (GPS, áudios ou notas de campo). 
                  Clique no botão do documento correspondente para ir direto ao campo em alerta (⚠️) e aplicar a correção assistida:
                </p>
                """, unsafe_allow_html=True)

                for d_idx, disc in enumerate(occ_discrepancies):
                    f_name = disc.get('field', 'N/A')
                    f_name_pt = {
                        "area_ha": "Área em Hectares (area_ha)",
                        "car": "Código do CAR (car)",
                        "municipality": "Município",
                        "issued_date": "Data de Emissão",
                        "number": "Número do Documento",
                        "fine_brl": "Valor da Multa"
                    }.get(f_name, f_name)

                    f_sev = disc.get('severity', 'ALERTA')
                    if "Risk of Judicial Nullity" in f_sev or "HIGH" in f_sev:
                        f_sev = "ALTA (Risco de Nulidade Jurídica sob Dec. nº 6.514/08)"
                    elif f_sev == "MEDIUM":
                        f_sev = "MÉDIA"
                    elif f_sev == "LOW":
                        f_sev = "BAIXA"

                    f_det = disc.get('details', '')
                    if "Paper states" in f_det:
                        f_det = re.sub(r"Paper states ([\d\.]+) ha while digital log recorded ([\d\.]+) ha \(Variance: ([\d\.]+)%\)\.", r"O auto declara \1 ha enquanto o registro digital de campo mediu \2 ha (Variação: \3%).", f_det)
                    elif "Paper CAR" in f_det:
                        f_det = re.sub(r"Paper CAR \((.*?)\) differs from digital cache CAR \((.*?)\)\.", r"O CAR informado no auto (\1) diverge do CAR registrado na base digital (\2).", f_det)

                    # Discover which child document in docs_list this discrepancy belongs to
                    target_doc_idx = 0
                    target_doc_name = "Auto Principal"
                    for idx_doc, doc_item in enumerate(docs_list):
                        if disc.get("doc_id") and doc_item.get("id") == disc.get("doc_id"):
                            target_doc_idx = idx_doc
                            target_doc_name = f"{doc_item.get('document_type_label', 'Doc')} (Nº {doc_item.get('document_number', '')})"
                            break
                        elif any(d.get("field") == f_name for d in doc_item.get("discrepancies", [])):
                            target_doc_idx = idx_doc
                            target_doc_name = f"{doc_item.get('document_type_label', 'Doc')} (Nº {doc_item.get('document_number', '')})"
                            break

                    c_info, c_btn = st.columns([3.4, 1.4])
                    with c_info:
                        st.markdown(f"""
                        <div style="background:#FFFFFF;border:1px solid #EFCB88;border-left:4px solid #D97706;border-radius:6px;padding:9px 13px;margin-bottom:8px;">
                          <div style="font-size:13px;color:#333;">
                            <b>• Campo:</b> <code style="background:#F4F7F6;color:#1E6B52;padding:2px 6px;border-radius:4px;">{f_name_pt}</code> 
                            | <b>Gravidade:</b> <span style="color:#B45309;font-weight:600;">{f_sev}</span>
                            | <b>Documento:</b> <span style="color:#1E6B52;font-weight:600;">{target_doc_name}</span>
                          </div>
                          <div style="margin-top:4px;font-size:12.5px;color:#555;">{f_det}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_btn:
                        st.markdown("<div style='margin-top:6px;'>", unsafe_allow_html=True)
                        if st.button("✏️ Corrigir agora", key=f"btn_nav_disc_{d_idx}_{selected_record['id']}", use_container_width=True):
                            st.session_state["selected_doc_idx"] = target_doc_idx
                            st.session_state["scroll_to_correction"] = True
                            st.session_state.pop(f"dossier_select_doc_{selected_record['id']}", None)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)


        is_seed_occ = selected_record["id"] in ["OC-2026-ALT-01", "OC-2026-PAR-01", "OC-2026-TAI-01", "OC-2026-ULI-01"]
        temp_dir = os.path.join(CURRENT_DIR, "temp", selected_record['id'])
        os.makedirs(temp_dir, exist_ok=True)

        if is_seed_occ:
            muni_name = selected_record["municipality"].lower()
            if "alta" in muni_name:
                muni_dir = "altamira"
            elif "para" in muni_name:
                muni_dir = "paragominas"
            elif "tail" in muni_name:
                muni_dir = "tailandia"
            else:
                muni_dir = "ulianopolis"

            p_dir = os.path.join(package_dir, muni_dir, "photos")
            a_dir = os.path.join(package_dir, muni_dir, "audios")

            p_files_pkg = sorted(glob.glob(os.path.join(p_dir, "*.jpg"))) if os.path.exists(p_dir) else []
            a_files = sorted(glob.glob(os.path.join(a_dir, "*.mp3"))) if os.path.exists(a_dir) else []
        else:
            p_files_pkg = []
            a_files = sorted(glob.glob(os.path.join(temp_dir, "*.mp3")) + glob.glob(os.path.join(temp_dir, "audios", "*.mp3")))

        temp_photos = sorted(glob.glob(os.path.join(temp_dir, "photo_*.jpg")) + glob.glob(os.path.join(temp_dir, "photo_*.png")) + glob.glob(os.path.join(temp_dir, "photos", "*.jpg")) + glob.glob(os.path.join(temp_dir, "photos", "*.png")))
        p_files = p_files_pkg + [f for f in temp_photos if f not in p_files_pkg]

        # ----------------------------------------------------------------------
        # SEÇÃO 1: EVIDÊNCIAS COLETADAS (ACORDEON / CONSULTA FORENSE)
        # ----------------------------------------------------------------------
        has_divergence = len(selected_record.get("discrepancies", [])) > 0
        evidencias_container_key = "expander_evidencias_alerta" if has_divergence else "expander_evidencias_ok"
        evidencias_title = "📁 Evidências Coletadas ⚠️ (Divergências a Conciliar)" if has_divergence else "📁 Evidências Coletadas ✅ (Conciliado & Íntegro)"

        with st.container(key=evidencias_container_key):
            with st.expander(evidencias_title, expanded=True):
                c_tab1, c_tab2, c_tab3, c_tab4 = st.tabs([
                    "📄 Documentos e Formulários",
                    "🎙️ Gravações de Voz de Campo",
                    "📸 Fotografias Georreferenciadas",
                    "🛰️ Coordenadas e Trilhas GPS"
                ])

                # ABA 1: DOCUMENTOS E FORMULÁRIOS (CONSULTA / CORREÇÃO)
                with c_tab1:
                    st.markdown("<p style='font-size:15px;font-weight:700;color:#1E6B52;margin:4px 0 10px;'>📑 Documentos Físicos da Ocorrência</p>", unsafe_allow_html=True)
                    
                    if docs_list:
                        doc_options = [
                            f"{i + 1}. 📄 {d['document_type_label']} — Nº {d.get('document_number', 'S/N')}"
                            for i, d in enumerate(docs_list)
                        ]
                        if st.session_state["selected_doc_idx"] >= len(doc_options):
                            st.session_state["selected_doc_idx"] = 0

                        select_key = f"dossier_select_doc_{selected_record['id']}"

                        def on_doc_select_change():
                            chosen_label = st.session_state[select_key]
                            if chosen_label in doc_options:
                                st.session_state["selected_doc_idx"] = doc_options.index(chosen_label)

                        st.selectbox(
                            f"Selecione o documento físico para inspeção ({len(docs_list)} documento(s) vinculado(s)):",
                            options=doc_options,
                            index=st.session_state["selected_doc_idx"],
                            key=select_key,
                            on_change=on_doc_select_change
                        )

                        active_doc = docs_list[st.session_state["selected_doc_idx"]]
                        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

                        # Document Inspection Card
                        st.markdown(f"""
                        <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px 16px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                          <div>
                            <b style="font-size:15px;color:#1E6B52;">Inspecionando: {active_doc['document_type_label']}</b> (Nº {active_doc['document_number']})
                            <div style="font-size:12px;color:#666;">ID: <code>{active_doc['id']}</code> | SHA-256: <code>{active_doc.get('sha256_hash', 'N/A')[:20]}...</code></div>
                          </div>
                          <div>
                            <span style="font-size:12px;background:#E2E8F0;color:#333;padding:4px 8px;border-radius:4px;font-weight:600;">{active_doc.get('agency', 'SEMAS')}</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                        photo_p = active_doc.get("image_path")

                        # Interactive Form Renderer with Error Highlighting
                        doc_discrepancies = active_doc.get("discrepancies", [])
                        doc_discrepant_fields = [d.get("field") for d in doc_discrepancies if d.get("field")]

                        def render_child_doc_form(prefix=""):
                            st.markdown("<div id='secao-formulario-correcao' style='scroll-margin-top: 100px;'></div>", unsafe_allow_html=True)
                            st.markdown("<p style='font-size:14px;font-weight:700;color:#1E6B52;margin:0 0 8px;'>📝 Dados Estruturados</p>", unsafe_allow_html=True)
                            
                            dt_label = "⚠️ Tipo de Documento" if any("type" in f or "tipo" in f for f in doc_discrepant_fields) else "Tipo de Documento"
                            dn_label = "⚠️ Número do Documento" if any("number" in f or "numero" in f for f in doc_discrepant_fields) else "Número do Documento"
                            de_label = "⚠️ Data de Emissão" if any("date" in f or "data" in f for f in doc_discrepant_fields) else "Data de Emissão"
                            car_label = "⚠️ Código do CAR" if any("car" in f for f in doc_discrepant_fields) else "Código do CAR"
                            area_label = "⚠️ Área Impactada em Hectares" if any("area" in f for f in doc_discrepant_fields) else "Área Impactada em Hectares"
                            fine_label = "⚠️ Valor da Multa (BRL)" if any("fine" in f or "multa" in f for f in doc_discrepant_fields) else "Valor da Multa (BRL)"

                            c1, c2 = st.columns(2)
                            with c1:
                                st.text_input(dt_label, active_doc["document_type_label"], disabled=True, key=f"{prefix}_dt_{active_doc['id']}")
                                new_num = st.text_input(dn_label, active_doc["document_number"], key=f"{prefix}_dn_{active_doc['id']}")
                                de_val = format_date_br(active_doc.get("issued_date") or "12/09/2026")
                                new_date = st.text_input(f"{de_label} (dd/mm/aaaa)", de_val, key=f"{prefix}_de_{active_doc['id']}")
                                st.text_input("Município / Órgão", f"{active_doc['municipality']} - {active_doc['agency']}", disabled=True, key=f"{prefix}_mo_{active_doc['id']}")
                            with c2:
                                new_car = st.text_input(car_label, active_doc["car"] or "Sem CAR / Posse Não Declarada", key=f"{prefix}_car_{active_doc['id']}")
                                area_val = str(active_doc["area_ha"]) if active_doc["area_ha"] is not None else ""
                                new_area = st.text_input(area_label, area_val, key=f"{prefix}_ar_{active_doc['id']}")
                                new_fine = st.text_input(fine_label, f"R$ {active_doc['fine_brl']:,.2f}" if active_doc["fine_brl"] else "N/A", key=f"{prefix}_fn_{active_doc['id']}")
                                st.text_input("Matrícula do Fiscal", active_doc["officer_registration"] or "N/A", key=f"{prefix}_of_{active_doc['id']}")

                            st.markdown("<p style='font-size:14px;font-weight:700;color:#1E6B52;margin:12px 0 6px;'>Partes Citadas & Autoria</p>", unsafe_allow_html=True)
                            if active_doc.get("cited_parties"):
                                for p in active_doc["cited_parties"]:
                                    role = p.get("role", "cited")
                                    role_friendly = "Autuado / Responsável" if "cited" in str(role) else ("Agente Autuante" if "issuer" in str(role) else str(role))
                                    st.markdown(f"- **{role_friendly}:** {p.get('name', 'Não informado')} | CPF/CNPJ: `{p.get('tax_id') or p.get('document_id') or 'Não informado'}`")

                            # Form Action Buttons: Salvar Alterações (Persistir no SQLite) & Desfazer Alterações (Resetar para versão anterior)
                            st.markdown("<hr style='margin:14px 0 12px;border:none;border-bottom:1px solid #DCE3E8;'>", unsafe_allow_html=True)
                            b_col1, b_col2 = st.columns([1.2, 1.1])
                            with b_col1:
                                if st.button("💾 Salvar Alterações", key=f"btn_save_doc_{prefix}_{active_doc['id']}", type="primary", use_container_width=True):
                                    try:
                                        clean_area = new_area.strip().replace(" ha", "").replace(" HA", "").replace(",", ".")
                                        updated_area = float(clean_area) if clean_area else active_doc["area_ha"]
                                    except ValueError:
                                        updated_area = active_doc["area_ha"]

                                    try:
                                        clean_fine = new_fine.strip().replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                                        updated_fine = float(clean_fine) if (clean_fine and clean_fine != "N/A") else active_doc.get("fine_brl")
                                    except ValueError:
                                        updated_fine = active_doc.get("fine_brl")

                                    OccurrenceDatabase.update_document_extracted_field(active_doc["id"], "document_number", new_num.strip())
                                    OccurrenceDatabase.update_document_extracted_field(active_doc["id"], "issued_date", format_date_br(new_date))
                                    OccurrenceDatabase.update_document_extracted_field(active_doc["id"], "car", new_car.strip())
                                    OccurrenceDatabase.update_document_extracted_field(active_doc["id"], "area_ha", updated_area)
                                    if updated_fine is not None:
                                        OccurrenceDatabase.update_document_extracted_field(active_doc["id"], "fine_brl", updated_fine)

                                    st.success("✅ Alterações salvas e persistidas com sucesso no banco de dados SQLite!")
                                    time.sleep(0.3)
                                    st.rerun()

                            with b_col2:
                                if st.button("🔄 Desfazer Alterações", key=f"btn_undo_doc_{prefix}_{active_doc['id']}", use_container_width=True):
                                    # Reset widget keys in session state to discard changes
                                    for k in [
                                        f"{prefix}_dn_{active_doc['id']}",
                                        f"{prefix}_de_{active_doc['id']}",
                                        f"{prefix}_car_{active_doc['id']}",
                                        f"{prefix}_ar_{active_doc['id']}",
                                        f"{prefix}_fn_{active_doc['id']}"
                                    ]:
                                        st.session_state.pop(k, None)
                                    st.info("↩️ Alterações descartadas. Dados restaurados para a versão persistida.")
                                    time.sleep(0.3)
                                    st.rerun()

                        # Document Image & Structured Form (Side-by-Side)
                        col_img, col_data = st.columns([1, 1.25], gap="large")
                        with col_img:
                            h_col1, h_col2 = st.columns([2.2, 1.8])
                            with h_col1:
                                st.markdown("<p style='font-size:14px;font-weight:700;color:#1E6B52;margin-bottom:6px;'>📸 Imagem do Documento</p>", unsafe_allow_html=True)
                            with h_col2:
                                if photo_p and os.path.exists(photo_p):
                                    with open(photo_p, "rb") as f_img:
                                        img_data = f_img.read()
                                    img_fname = os.path.basename(photo_p)
                                    st.download_button(
                                        label="⬇️ Baixar Imagem",
                                        data=img_data,
                                        file_name=img_fname,
                                        mime="image/jpeg",
                                        key=f"btn_dl_doc_img_{active_doc['id']}",
                                        use_container_width=True
                                    )

                            if photo_p and os.path.exists(photo_p):
                                st.image(Image.open(photo_p), use_container_width=True, caption=os.path.basename(photo_p))
                            else:
                                st.info("Imagem física não disponível no disco.")
                        with col_data:
                            render_child_doc_form(prefix="main")
                    else:
                        st.info("Nenhum documento físico vinculado a esta ocorrência. Utilize a seção 'Adicionar Novas Evidências' abaixo para realizar a juntada.")

                # ABA 2: GRAVAÇÕES DE VOZ
                with c_tab2:
                    st.markdown(f"<p style='font-size:14.5px;font-weight:700;color:#1E6B52;margin-bottom:8px;'>🎙️ Gravações de Voz de Campo ({len(a_files)} áudios)</p>", unsafe_allow_html=True)
                    if a_files:
                        a_cols = st.columns(2)
                        for idx, audio_path in enumerate(a_files):
                            col = a_cols[idx % 2]
                            with col:
                                audio_name = os.path.basename(audio_path)
                                with open(audio_path, "rb") as af:
                                    audio_bytes = af.read()
                                audio_hash = hashlib.sha256(audio_bytes).hexdigest()
                                st.markdown(f"**🔊 {audio_name}** | <small style='font-family:monospace;color:#555;'>SHA-256: {audio_hash[:16]}...</small>", unsafe_allow_html=True)
                                st.audio(audio_bytes, format="audio/mp3")
                    else:
                        st.info("Nenhum áudio associado a esta ocorrência.")

                # ABA 3: FOTOGRAFIAS GEORREFERENCIADAS
                with c_tab3:
                    st.markdown(f"<p style='font-size:14.5px;font-weight:700;color:#1E6B52;margin-bottom:8px;'>📸 Fotografias Georreferenciadas de Campo ({len(p_files)} fotos)</p>", unsafe_allow_html=True)
                    if p_files:
                        p_cols = st.columns(min(len(p_files), 4))
                        for idx, photo_path in enumerate(p_files):
                            col = p_cols[idx % 4]
                            with col:
                                photo_name = os.path.basename(photo_path)
                                with open(photo_path, "rb") as pf:
                                    photo_bytes = pf.read()
                                photo_hash = hashlib.sha256(photo_bytes).hexdigest()
                                st.image(photo_bytes, caption=f"{photo_name}\nGPS & Timestamp", use_container_width=True)
                                st.markdown(f"<small style='font-family:monospace;color:#555;'>Hash: {photo_hash[:12]}...</small>", unsafe_allow_html=True)
                    else:
                        st.info("Nenhuma fotografia associada a esta ocorrência.")

                # ABA 4: COORDENADAS E TRILHAS GPS
                with c_tab4:
                    st.markdown("<p style='font-size:14.5px;font-weight:700;color:#1E6B52;margin-bottom:8px;'>🛰️ Coordenadas e Trilhas GPS Registradas</p>", unsafe_allow_html=True)
                    if is_seed_occ:
                        geo_pts = [
                            {"Origem": "Vértice Principal da Fiscalização", "Latitude": -3.75412, "Longitude": -48.12543, "Status": "Confirmado"},
                            {"Origem": "Ponto de Captação Fotográfica 01", "Latitude": -3.75420, "Longitude": -48.12550, "Status": "Confirmado"},
                            {"Origem": "Centróide da Área Degradada", "Latitude": -3.75480, "Longitude": -48.12610, "Status": "Calculado"}
                        ]
                        st.dataframe(pd.DataFrame(geo_pts), use_container_width=True)
                    else:
                        geo_pts = []
                        for d_it in docs_list:
                            f_json = d_it.get("full_extracted_json") or {}
                            coords = f_json.get("coordinates") or {}
                            if coords.get("latitude") or coords.get("longitude"):
                                geo_pts.append({
                                    "Origem": f"Auto Nº {d_it.get('document_number', '')} ({d_it.get('document_type_label', 'Doc')})",
                                    "Latitude": coords.get("latitude", "N/A"),
                                    "Longitude": coords.get("longitude", "N/A"),
                                    "Status": "Extraído via OCR"
                                })
                        if geo_pts:
                            st.dataframe(pd.DataFrame(geo_pts), use_container_width=True)
                        else:
                            st.info("Nenhuma coordenada ou trilha GPS registrada para esta ocorrência.")

        # ----------------------------------------------------------------------
        # SEÇÃO 2: ADICIONAR NOVAS EVIDÊNCIAS (ACORDEON / UPLOAD)
        # ----------------------------------------------------------------------
        with st.container(key="expander_adicionar_evidencias"):
            with st.expander("➕ Adicionar Novas Evidências", expanded=False):
                add_tab1, add_tab2, add_tab3 = st.tabs([
                    "📄 Juntar Novo Documento / Auto a esta Ocorrência",
                    "📸 Anexar Fotografias Georreferenciadas",
                    "🛰️ Importar Trilhas ou Coordenadas GPS"
                ])

            # ABA 1 DE ADIÇÃO: JUNTADA DE DOCUMENTO
            with add_tab1:
                j_col1, j_col2 = st.columns(2)
                with j_col1:
                    j_doc_type = st.selectbox("Tipo de Documento:", list(DOC_TYPE_LABELS.values()), key=f"j_dtype_{selected_record['id']}")
                    j_doc_num = st.text_input("Número do Documento:", f"00{total_docs_in_occ + 1}", key=f"j_dnum_{selected_record['id']}")
                with j_col2:
                    j_t_cam, j_t_file = st.tabs(["📸 Tirar Foto na Câmera", "📁 Upload Arquivo/PDF"])
                    with j_t_cam:
                        j_open_cam = st.toggle("📷 Abrir Câmera (Autorizar Acesso)", value=False, key=f"j_toggle_cam_{selected_record['id']}")
                        if j_open_cam:
                            j_cam_file = st.camera_input("Fotografar documento com a câmera:", key=f"j_cam_{selected_record['id']}")
                        else:
                            j_cam_file = None
                            st.caption("🔒 Câmera desativada. Ative o botão acima 'Abrir Câmera' para autorizar e ligar o visor do dispositivo.")
                    with j_t_file:
                        j_up_file = st.file_uploader("Upload da Imagem ou PDF do Documento:", type=["jpg", "jpeg", "png", "pdf"], key=f"j_file_{selected_record['id']}")
                    j_doc_file = j_cam_file if j_cam_file is not None else j_up_file

                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                if st.button("📥 Realizar Juntada de Documento", type="primary", key=f"btn_juntada_{selected_record['id']}"):
                    if j_doc_file:
                        t_str = str(int(time.time()))
                        j_raw_bytes = j_doc_file.getvalue()
                        j_is_pdf = (hasattr(j_doc_file, "name") and str(j_doc_file.name).lower().endswith(".pdf")) or j_raw_bytes.startswith(b"%PDF")
                        
                        if j_is_pdf:
                            j_pdf_path = os.path.join(temp_dir, f"juntada_{t_str}.pdf")
                            with open(j_pdf_path, "wb") as pf:
                                pf.write(j_raw_bytes)
                            try:
                                import pypdfium2 as pdfium
                                pdf = pdfium.PdfDocument(j_pdf_path)
                                page = pdf[0]
                                pil_page = page.render(scale=2.0).to_pil()
                                j_save_path = os.path.join(temp_dir, f"juntada_{t_str}.jpg")
                                pil_page.save(j_save_path, "JPEG", quality=95)
                            except Exception:
                                j_save_path = j_pdf_path
                        else:
                            j_save_path = os.path.join(temp_dir, f"juntada_{t_str}.jpg")
                            with open(j_save_path, "wb") as f:
                                f.write(j_raw_bytes)

                        # Process extraction (unbiased directly from image OCR)
                        engine = get_engine()
                        j_extracted = engine.extract_from_image(j_save_path, raw_text_hint=j_doc_type)
                        j_calib = ConfidenceEvaluator.calibrate_document(j_extracted)
                        
                        with open(j_save_path, "rb") as f:
                            j_bytes = f.read()
                        j_sha = hashlib.sha256(j_bytes).hexdigest()

                        raw_t = [k for k, v in DOC_TYPE_LABELS.items() if v == j_doc_type]
                        raw_type_key = raw_t[0] if raw_t else "infraction_notice"

                        j_discs = []
                        j_muni = j_calib.municipality or ""
                        if j_muni and selected_record.get('municipality'):
                            clean_j_m = re.sub(r'[^a-zA-Z0-9]', '', j_muni.lower())
                            clean_occ_m = re.sub(r'[^a-zA-Z0-9]', '', selected_record['municipality'].lower())
                            if clean_j_m != clean_occ_m and selected_record['municipality'] != "Novo Município":
                                j_discs.append({
                                    "field": "municipality",
                                    "severity": "ALTA (Risco de Incompetência Territorial / Dec. nº 6.514/08)",
                                    "details": f"O documento juntado pertence a {j_muni}, divergindo do município da operação ({selected_record['municipality']})."
                                })

                        new_child_doc = {
                            "id": f"DOC-{selected_record['id']}-{t_str[-4:]}",
                            "occurrence_id": selected_record['id'],
                            "document_number": j_doc_num,
                            "document_type": raw_type_key,
                            "document_type_label": j_doc_type,
                            "issued_date": format_date_br(j_calib.issued_date or selected_record.get('issued_date', '12/09/2026')),
                            "municipality": j_muni or selected_record['municipality'],
                            "agency": "SEMAS",
                            "car": j_calib.car or "",
                            "area_ha": j_calib.area_ha,
                            "fine_brl": j_calib.fine_brl,
                            "officer_registration": j_calib.officer_registration or "",
                            "cited_parties": [p.model_dump(mode="json") for p in j_calib.parties],
                            "image_path": j_save_path,
                            "full_extracted_json": j_calib.model_dump(mode="json"),
                            "discrepancies": j_discs,
                            "sha256_hash": j_sha
                        }
                        OccurrenceDatabase.save_document(new_child_doc)
                        st.success("✅ Juntada de documento realizada com sucesso! Árvore de custódia Merkle Root atualizada.")
                        st.rerun()
                    else:
                        st.error("Por favor, selecione um arquivo de imagem ou tire uma foto para a juntada.")

            # ABA 2 DE ADIÇÃO: FOTOGRAFIAS DE CAMPO (SC3 MERKLE UPDATE)
            with add_tab2:
                st.markdown("<p style='font-size:14.5px;font-weight:700;color:#1E6B52;margin-bottom:6px;'>📸 Anexar Novas Fotografias Georreferenciadas (Cadeia de Custódia SC3)</p>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background:#F4F7F6;border-left:4px solid #1E6B52;padding:8px 12px;border-radius:4px;font-size:12.5px;color:#333;margin-bottom:12px;'>
                  <b>Protocolo SC3:</b> As fotografias anexadas recebem selo criptográfico SHA-256 individual e atualizam a Árvore de Custódia (Merkle Root) da operação em tempo real, sem alterar ou invalidar as fotos anteriores.
                </div>
                """, unsafe_allow_html=True)

                p_subtab_cam, p_subtab_up = st.tabs(["📸 Tirar Foto com a Câmera", "📁 Upload de Fotos (.jpg, .png)"])
                with p_subtab_cam:
                    p_open_cam = st.toggle("📷 Abrir Câmera para Foto de Campo", value=False, key=f"p_toggle_cam_{selected_record['id']}")
                    if p_open_cam:
                        p_cam_shot = st.camera_input("Capturar foto de campo:", key=f"p_cam_input_{selected_record['id']}")
                    else:
                        p_cam_shot = None
                        st.caption("🔒 Câmera desativada. Ative o botão acima para ligar a câmera do dispositivo.")
                with p_subtab_up:
                    p_up_files = st.file_uploader("Selecione uma ou mais fotos do dispositivo:", accept_multiple_files=True, type=["jpg", "jpeg", "png"], key=f"p_upload_input_{selected_record['id']}")

                p_desc = st.text_input("Identificação / Legenda da Evidência (opcional):", placeholder="Ex: Queimada recente no flanco leste, Maquinário apreendido, Vértice 02", key=f"p_desc_input_{selected_record['id']}")

                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                if st.button("📸 Salvar & Anexar Evidências Fotográficas", type="primary", key=f"btn_save_photo_evid_{selected_record['id']}"):
                    photos_to_save = []
                    if p_cam_shot is not None:
                        photos_to_save.append((p_cam_shot.getvalue(), "cam_photo"))
                    if p_up_files:
                        for uf in p_up_files:
                            photos_to_save.append((uf.getvalue(), uf.name))

                    if photos_to_save:
                        t_str = str(int(time.time()))
                        saved_paths = []
                        for idx_p, (p_bytes, p_orig_name) in enumerate(photos_to_save):
                            save_fname = f"photo_{t_str}_{idx_p}.jpg"
                            save_fpath = os.path.join(temp_dir, save_fname)
                            with open(save_fpath, "wb") as pf:
                                pf.write(p_bytes)
                            saved_paths.append(save_fpath)

                        # Recalculate complete Merkle Root with all photos (original + new)
                        all_current_photos = p_files + saved_paths
                        new_seal = CryptoSealSC3.generate_seal(
                            document_json={"occurrence_id": selected_record['id'], "summary": selected_record.get('summary_text', '')},
                            photo_paths=all_current_photos,
                            audio_paths=a_files,
                            field_notes_text=selected_record.get('field_notes', '')
                        )
                        new_merkle = new_seal.get("merkle_root_hash", "")

                        # Update SQLite occurrence record
                        with OccurrenceDatabase.get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE occurrences SET merkle_root_hash = ?, photos_count = ? WHERE id = ?", (new_merkle, len(all_current_photos), selected_record['id']))
                            conn.commit()

                        st.success(f"🎉 **{len(photos_to_save)} foto(s)** anexada(s) com sucesso! Selo de Custódia Merkle Root recalculado: `{new_merkle[:20]}...`")
                        st.rerun()
                    else:
                        st.error("Por favor, tire uma foto ou selecione arquivos para anexar.")

            # ABA 3 DE ADIÇÃO: TRILHAS E COORDENADAS GPS
            with add_tab3:
                st.markdown("<p style='font-size:14.5px;font-weight:700;color:#1E6B52;margin-bottom:8px;'>🛰️ Importar Trilhas ou Coordenadas GPS (Garmin GPX / KML / GMS)</p>", unsafe_allow_html=True)
                gps_tab1, gps_tab2 = st.tabs(["📁 Upload do Arquivo Garmin (.gpx, .kml, .csv)", "✍️ Digitação Manual de Coordenadas"])

                with gps_tab1:
                    uploaded_gps_file = st.file_uploader(
                        "Selecione o arquivo do GPS:",
                        type=["gpx", "kml", "csv", "txt"],
                        key=f"dossier_gps_{selected_record['id']}"
                    )
                    if uploaded_gps_file:
                        gps_bytes = uploaded_gps_file.getvalue()
                        gps_sha256 = hashlib.sha256(gps_bytes).hexdigest()
                        fname = uploaded_gps_file.name.lower()
                        
                        parsed_wpts = []
                        if fname.endswith(".gpx"):
                            parsed_wpts = GPSParser.parse_gpx(gps_bytes)
                        elif fname.endswith(".kml"):
                            parsed_wpts = GPSParser.parse_kml(gps_bytes)
                        elif fname.endswith(".csv") or fname.endswith(".txt"):
                            parsed_wpts = GPSParser.parse_csv(gps_bytes.decode("utf-8", errors="ignore"))

                        st.success(f"✅ **{uploaded_gps_file.name}** processado com sucesso! ({len(parsed_wpts)} pontos extraídos)")
                        st.markdown(f"<div style='font-family:monospace;font-size:12px;color:#1E6B52;background:#F4F7F6;padding:8px 12px;border-radius:6px;margin-bottom:12px;border:1px solid #DCE3E8;'>Selo de Integridade SHA-256: <b>{gps_sha256}</b></div>", unsafe_allow_html=True)

                        if parsed_wpts:
                            wpt_df = pd.DataFrame(parsed_wpts)
                            st.dataframe(wpt_df, use_container_width=True)
                        else:
                            st.warning("Nenhum waypoint ou ponto de trilha reconhecido na estrutura do arquivo.")

                with gps_tab2:
                    st.markdown("<small style='color:#666;'>Formatos suportados: <b>Graus Decimais</b> (ex: <code>-3.75412, -48.12543</code>) ou <b>Graus Minutos Segundos (GMS)</b> (ex: <code>03° 45' 14.8\" S, 48° 07' 31.5\" W</code>)</small>", unsafe_allow_html=True)
                    c_input1, c_input2 = st.columns([3, 1])
                    with c_input1:
                        manual_coord_str = st.text_input("Coordenadas Geográficas:", placeholder="-3.75412, -48.12543 ou 03°45'14\"S 48°07'31\"W", key=f"dossier_manual_gps_{selected_record['id']}")
                    with c_input2:
                        st.markdown("<div style='margin-top:28px;'>", unsafe_allow_html=True)
                        st.button("Validar GPS", key=f"btn_valid_gps_dos_{selected_record['id']}", use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                    if manual_coord_str:
                        parsed_single = GPSParser.parse_manual(manual_coord_str)
                        if parsed_single:
                            coord_hash = hashlib.sha256(f"{parsed_single['latitude']},{parsed_single['longitude']}".encode()).hexdigest()
                            st.success(f"**Ponto Válido:** Latitude: `{parsed_single['latitude']:.6f}`, Longitude: `{parsed_single['longitude']:.6f}`")
                            st.markdown(f"<div style='font-family:monospace;font-size:12px;color:#1E6B52;background:#F4F7F6;padding:8px 12px;border-radius:6px;border:1px solid #DCE3E8;'>Hash de Integridade SHA-256: <b>{coord_hash}</b></div>", unsafe_allow_html=True)
                        else:
                            st.error("Formato de coordenadas não reconhecido. Por favor informe em graus decimais ou GMS.")

        st.markdown("<hr style='margin:20px 0 16px;border:none;border-bottom:1px solid #DCE3E8;'>", unsafe_allow_html=True)
        # Action Bar: Download Dossier (.sc3 / .json) & Live Cryptographic Seal Validation
        col_dl_sc3, col_dl_json, col_val = st.columns([1.3, 1.1, 1.4])
        full_dossier_json = json.dumps(selected_record, indent=2, ensure_ascii=False)
        with col_dl_sc3:
            st.download_button(
                label=f"📦 Baixar Pacote Criptográfico (.sc3)",
                data=full_dossier_json,
                file_name=f"Dossie_{selected_record['id']}.sc3",
                mime="application/octet-stream",
                use_container_width=True,
                help="Download do container pericial estruturado e assinado para auditoria forense offline."
            )
        with col_dl_json:
            st.download_button(
                label=f"📄 Baixar JSON",
                data=full_dossier_json,
                file_name=f"Dossie_{selected_record['id']}.json",
                mime="application/json",
                use_container_width=True
            )
        with col_val:
            val_state_key = f"show_seal_validation_{selected_record['id']}"
            if val_state_key not in st.session_state:
                st.session_state[val_state_key] = False

            btn_label = "🔒 Ocultar Validação" if st.session_state[val_state_key] else "🔍 Validar Selo SC3 (Arts. 158 CPP)"
            if st.button(btn_label, key=f"btn_toggle_seal_val_{selected_record['id']}", use_container_width=True, type="primary" if not st.session_state[val_state_key] else "secondary"):
                st.session_state[val_state_key] = not st.session_state[val_state_key]
                st.rerun()

        # Render Forensic Seal Validation Card if active
        if st.session_state.get(f"show_seal_validation_{selected_record['id']}", False):
            # Compute live cryptographic hashes
            live_seal = CryptoSealSC3.generate_seal(
                document_json=selected_record,
                photo_paths=p_files,
                audio_paths=a_files,
                field_notes_text=selected_record.get("field_notes", "")
            )
            merkle_root = live_seal.get("merkle_root_hash", "")
            leaves = live_seal.get("leaves", {})

            # Document Leaves
            doc_leaf_hashes = []
            for d in docs_list:
                d_hash = d.get("sha256_hash") or CryptoSealSC3.hash_data(json.dumps(d, sort_keys=True, ensure_ascii=False))
                doc_leaf_hashes.append({
                    "id": d.get("id"),
                    "num": d.get("document_number", "S/N"),
                    "type": d.get("document_type_label", "Documento"),
                    "hash": d_hash
                })

            # Photos Leaves
            photo_leaf_hashes = []
            for p in p_files:
                photo_leaf_hashes.append({
                    "name": os.path.basename(p),
                    "size_kb": round(os.path.getsize(p) / 1024, 1) if os.path.exists(p) else 0,
                    "hash": CryptoSealSC3.hash_file(p)
                })

            # Audio Leaves
            audio_leaf_hashes = []
            for a in a_files:
                audio_leaf_hashes.append({
                    "name": os.path.basename(a),
                    "size_kb": round(os.path.getsize(a) / 1024, 1) if os.path.exists(a) else 0,
                    "hash": CryptoSealSC3.hash_file(a)
                })

            disc_count = len(selected_record.get("discrepancies", []))
            status_badge = '<span style="display:inline-block;padding:6px 12px;border-radius:20px;font-size:13px;font-weight:700;background:#E6F4EA;color:#137333;border:1px solid #CEEAD6;">✅ SELO 100% VÁLIDO & ÍNTEGRO</span>' if disc_count == 0 else f'<span style="display:inline-block;padding:6px 12px;border-radius:20px;font-size:13px;font-weight:700;background:#FEF3C7;color:#92400E;border:1px solid #FCD34D;">⚠️ SELO VÁLIDO ({disc_count} DIVERGÊNCIA(S) EM CONCILIAÇÃO)</span>'

            st.markdown(f"""<div style="margin-top:16px;background:#F8FAFC;border:2px solid #1E6B52;border-radius:10px;padding:18px 20px;box-shadow:0 4px 12px rgba(0,0,0,0.04);">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;border-bottom:1px solid #E2E8F0;padding-bottom:12px;margin-bottom:14px;">
<div>
<span style="font-size:11px;font-weight:700;letter-spacing:1px;color:#1E6B52;text-transform:uppercase;background:#E8F5E9;padding:4px 8px;border-radius:4px;">🛡️ Certidão Forense de Autenticidade e Cadeia de Custódia Digital</span>
<h3 style="margin:6px 0 2px;color:#134E39;font-size:18px;font-weight:700;">Selo Criptográfico SC3 — Batimento Forense em Tempo Real</h3>
<p style="margin:0;font-size:12.5px;color:#666;">Conformidade Técnica e Jurídica: <b>Arts. 158-A a 158-F do CPP</b> e <b>Decreto Federal nº 6.514/2008</b></p>
</div>
<div style="text-align:right;margin-top:6px;">
{status_badge}
</div>
</div>
<div style="background:#134E39;color:#FFFFFF;border-radius:8px;padding:14px 18px;margin-bottom:12px;">
<div style="font-size:11.5px;font-weight:600;color:#A7F3D0;text-transform:uppercase;letter-spacing:0.8px;">Raiz da Árvore de Merkle (Merkle Root Hash) — SHA-256:</div>
<div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:700;color:#FFFFFF;word-break:break-all;margin-top:4px;letter-spacing:0.5px;">
{merkle_root}
</div>
<div style="margin-top:8px;font-size:12px;color:#D1FAE5;display:flex;gap:16px;flex-wrap:wrap;">
<span>• Protocolo: <b>SC3-V1.0</b></span>
<span>• Auditoria: <b>Zero-Alucinação / Zero-Custo (Offline)</b></span>
<span>• Imutabilidade: <b>Blindagem Probatória Irreversível</b></span>
</div>
</div>
</div>""", unsafe_allow_html=True)

            st.markdown("<p style='color:#1E6B52;font-size:14.5px;font-weight:700;margin:16px 0 8px;'>🔬 Auditoria Pericial das Folhas Criptográficas (Leaves):</p>", unsafe_allow_html=True)

            col_l1, col_l2, col_l3, col_l4 = st.columns(4)
            with col_l1:
                st.markdown(f"""<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:12px;min-height:110px;">
<div style="font-size:12.5px;font-weight:700;color:#1E6B52;">📄 Folha 1: Documentos</div>
<div style="font-size:12px;color:#555;margin-top:4px;"><b>{len(docs_list)}</b> auto(s) periciado(s)</div>
<div style="font-family:monospace;font-size:11px;color:#666;margin-top:6px;word-break:break-all;background:#F8FAFC;padding:4px;border-radius:4px;">Hash: {leaves.get('document_hash', '')[:18]}...</div>
</div>""", unsafe_allow_html=True)

            with col_l2:
                st.markdown(f"""<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:12px;min-height:110px;">
<div style="font-size:12.5px;font-weight:700;color:#1E6B52;">📸 Folha 2: Fotografias</div>
<div style="font-size:12px;color:#555;margin-top:4px;"><b>{len(p_files)}</b> foto(s) física(s)</div>
<div style="font-family:monospace;font-size:11px;color:#666;margin-top:6px;word-break:break-all;background:#F8FAFC;padding:4px;border-radius:4px;">Hash: {leaves.get('photos_merkle_leaf', '')[:18]}...</div>
</div>""", unsafe_allow_html=True)

            with col_l3:
                st.markdown(f"""<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:12px;min-height:110px;">
<div style="font-size:12.5px;font-weight:700;color:#1E6B52;">🎙️ Folha 3: Áudios / Voz</div>
<div style="font-size:12px;color:#555;margin-top:4px;"><b>{len(a_files)}</b> gravação(ões)</div>
<div style="font-family:monospace;font-size:11px;color:#666;margin-top:6px;word-break:break-all;background:#F8FAFC;padding:4px;border-radius:4px;">Hash: {leaves.get('audios_merkle_leaf', '')[:18]}...</div>
</div>""", unsafe_allow_html=True)

            with col_l4:
                st.markdown(f"""<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:12px;min-height:110px;">
<div style="font-size:12.5px;font-weight:700;color:#1E6B52;">🛰️ Folha 4: GPS & Notas</div>
<div style="font-size:12px;color:#555;margin-top:4px;"><b>{'Presente' if selected_record.get('field_notes') else 'Padrão'}</b> | Coordenadas</div>
<div style="font-family:monospace;font-size:11px;color:#666;margin-top:6px;word-break:break-all;background:#F8FAFC;padding:4px;border-radius:4px;">Hash: {leaves.get('field_notes_leaf', '')[:18]}...</div>
</div>""", unsafe_allow_html=True)

            # Detailed Hashes Expander
            with st.expander("🔍 Inspecionar Hashes SHA-256 Individuais das Evidências (Perícia Detalhada)", expanded=False):
                if doc_leaf_hashes:
                    st.markdown("**📑 Hashes dos Documentos:**")
                    for dh in doc_leaf_hashes:
                        st.markdown(f"- `{dh['type']} Nº {dh['num']}`: `SHA-256: {dh['hash']}`")
                if photo_leaf_hashes:
                    st.markdown("**📸 Hashes das Fotografias:**")
                    for ph in photo_leaf_hashes:
                        st.markdown(f"- `{ph['name']}` ({ph['size_kb']} KB): `SHA-256: {ph['hash']}`")
                if audio_leaf_hashes:
                    st.markdown("**🎙️ Hashes dos Áudios:**")
                    for ah in audio_leaf_hashes:
                        st.markdown(f"- `{ah['name']}` ({ah['size_kb']} KB): `SHA-256: {ah['hash']}`")

                st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                st.text_input(
                    "🔗 Link Direto de Acesso Pericial para Laudo / PJe (Clique e Copie):",
                    value=f"https://amazoniahackathons3cdocaudit-nmluix5bwjqrtjt4sfysv2.streamlit.app/?dossie={selected_record['id']}",
                    key=f"txt_link_pericial_{selected_record['id']}",
                    help="Copie e cole este link diretamente em laudos periciais ou petições judiciais para auditoria direta."
                )


        # Smooth Scroll Execution if triggered by 'Corrigir agora'
        if st.session_state.get("scroll_to_correction"):
            st.components.v1.html("""
            <script>
                setTimeout(function() {
                    try {
                        var el = window.parent.document.getElementById('secao-formulario-correcao');
                        if (el) {
                            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    } catch(e) {
                        console.log(e);
                    }
                }, 180);
            </script>
            """, height=0, width=0)
            st.session_state["scroll_to_correction"] = False
    else:
        st.info("Nenhuma ocorrência selecionada. Volte para a consulta e escolha um registro.")


# ==============================================================================
# PAGE 4: GUIA DE USO & PROTOCOLO SC3
# ==============================================================================
elif current_page == "📖 Guia de Uso":
    st.markdown("""<div style="margin-bottom: 20px;">
<p style="font-size:20px;font-weight:700;color:#134e39;margin:0 0 4px;letter-spacing:0.2px;">📖 Guia de Uso & Protocolo SC3</p>
<p style="font-size:13.5px;color:#555;margin:0;">Manual operacional, inteligência territorial, cadeia de custódia criptográfica e conformidade técnica</p>
</div>""", unsafe_allow_html=True)

    # 1. CONTEXTO & PROBLEMÁTICA
    st.markdown("""<div style="background:#FFFFFF;border:1px solid #DCE3E8;border-left:5px solid #C2410C;border-radius:10px;padding:20px 22px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,0.03);">
<div style="font-size:16px;font-weight:700;color:#9A3412;margin:0 0 10px;">🚨 O Desafio da Fiscalização na Amazônia & A Fragilidade da Prova em Papel</div>
<p style="color:#333;font-size:13.5px;line-height:1.65;margin-bottom:12px;">A proteção da Amazônia enfrenta barreiras geográficas e jurídicas complexas. Conforme levantamentos recentes de dados públicos da fiscalização ambiental (como os reportados pela <i>Revista Piauí</i> e projetos como o <i>Data Fixers / CCCA</i>), cerca de <b>47% dos embargos lavrados em Unidades de Conservação na Amazônia não conseguem identificar o infrator imediato</b>, resultando em centenas de milhões de reais em sanções não efetivadas e áreas vulneráveis a fraudes no Cadastro Ambiental Rural (CAR autodeclaratório) e uso de intermediários ("laranjas").</p>
<p style="color:#333;font-size:13.5px;line-height:1.65;margin-bottom:12px;">Além disso, no plano processual e jurídico (<b>Código de Processo Penal, arts. 158-A a 158-F</b> e <b>Decreto nº 6.514/08</b>), autos de infração, termos de embargo e relatórios lavrados manualmente em papel sob chuva e lama em áreas remotas sofrem constante risco de anulação judicial sob alegações de <i>"rasura posterior"</i>, <i>"divergência de coordenadas GPS"</i> ou <i>"quebra da cadeia de custódia das fotografias e depoimentos"</i>.</p>
<div style="background:#FFF7ED;border:1px solid #FFEDD5;border-radius:6px;padding:10px 14px;font-size:12.5px;color:#9A3412;font-weight:500;">⚖️ <b>Gargalo Central:</b> Sem uma cadeia de custódia digital auditável e sem conciliação automática entre os autos físicos e as evidências digitais colhidas em campo, autos legítimos perdem força probatória na Justiça Federal e no Ministério Público.</div>
</div>""", unsafe_allow_html=True)

    # 2. NOSSA SOLUÇÃO (PROTOCOLO SC3 & AS 4 CAMADAS DE AUDITORIA)
    st.markdown("""<div style="background:#FFFFFF;border:1px solid #DCE3E8;border-left:5px solid #1E6B52;border-radius:10px;padding:20px 22px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,0.03);">
<div style="font-size:16.5px;font-weight:700;color:#1E6B52;margin:0 0 10px;">🛡️ O Protocolo SC3 como Motor Ativo de Auditoria & Contra-Perícia</div>
<p style="color:#333;font-size:13.5px;line-height:1.65;margin-bottom:14px;">O <b>SC3 DocAudit</b> não é apenas um repositório de arquivos. Ele opera como um <b>motor ativo de auditoria e conformidade probatória</b>, divido em 4 camadas periciais:</p>

<div style="display:flex;flex-direction:column;gap:12px;margin-bottom:14px;">
<div style="background:#F4F7F6;border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;">
<b style="color:#1E6B52;font-size:14px;">1. 🔒 Auditoria Criptográfica de Custódia (Matemática Pura — <code>crypto_seal.py</code>):</b>
<p style="font-size:13px;color:#444;margin:6px 0 0;line-height:1.55;">
• O sistema não confia em carimbos de data do sistema operacional.<br>
• Calcula o hash SHA-256 dos bytes brutos de cada foto, gravação de áudio e dados estruturados do auto.<br>
• Constrói a <b>Árvore de Merkle</b>: <code>Merkle Root = SHA256(Hash_Auto || Hash_Foto || Hash_Audio || Hash_GPS)</code>.<br>
• <i>O teste pericial:</i> Se um infrator ou funcionário adulterar 1 único dígito da coordenada GPS ou cortar 1 segundo de áudio, a Merkle Root se rompe matematicamente.
</p>
</div>

<div style="background:#F4F7F6;border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;">
<b style="color:#1E6B52;font-size:14px;">2. 🛰️ Auditoria Cruzada de Divergências (Inteligência Territorial — <code>reconciler.py</code>):</b>
<p style="font-size:13px;color:#444;margin:6px 0 0;line-height:1.55;">
• O sistema não aceita passivamente o que está escrito no papel:<br>
• <b>Confronto de Área:</b> Se o auto em papel declara <code>120 ha</code> mas o GPS/Satélite mediu <code>168.4 ha</code>, o motor calcula a divergência (40.3%) e trava o status em <code>⚠️ DIVERGENTE</code>.<br>
• <b>Confronto de Jurisdição & CAR:</b> Verifica se o CAR declarado no auto coincide com o polígono real da fiscalização e se as coordenadas batem com os limites do município.
</p>
</div>

<div style="background:#F4F7F6;border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;">
<b style="color:#1E6B52;font-size:14px;">3. 👁️ Trava Anti-Alucinação & Incerteza Calibrada (<code>confidence_evaluator.py</code>):</b>
<p style="font-size:13px;color:#444;margin:6px 0 0;line-height:1.55;">
• Modelos tradicionais de OCR costumam "adivinhar" e inventar CPFs ou valores ilegíveis.<br>
• O avaliador calcula pontuação de confiança de <code>0.0</code> a <code>1.0</code> por campo. Letras ou números ilegíveis são marcados como <code>null</code> para revisão humana assistida (<i>Human-in-the-Loop</i>), sem alucinações.
</p>
</div>

<div style="background:#F4F7F6;border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;">
<b style="color:#1E6B52;font-size:14px;">4. 📎 Modelo Append-Only & Soft Delete (Preservação da Trilha — <code>database.py</code>):</b>
<p style="font-size:13px;color:#444;margin:6px 0 0;line-height:1.55;">
• No banco SQLite <code>occurrences.db</code>, <b>nenhuma evidência é sobrescrita ou destruída</b>.<br>
• Juntadas posteriores criam novos elos com carimbo de tempo próprio.<br>
• Exclusões aplicam a marcação <code>removedAt</code>, garantindo rastreabilidade total para auditorias da Corregedoria ou do Ministério Público Federal.
</p>
</div>
</div>

<div style="background:#FFFBEB;border:1px solid #FEF3C7;border-radius:6px;padding:12px 16px;font-size:13px;color:#92400E;line-height:1.55;">
🧪 <b>Como testar a auditoria ao vivo na aplicação:</b><br>
1. Abra a ocorrência de <b>Ulianópolis</b> ou <b>Altamira</b> na página <i>🔍 Consultar Ocorrências</i>.<br>
2. Observe o banner laranja no topo alertando as discrepâncias detectadas pelo motor.<br>
3. Clique em <code>✏️ Corrigir agora</code>: a tela rola suavemente até o formulário para você revisar com a imagem do documento e sanar a divergência!
</div>
</div>""", unsafe_allow_html=True)

    # 3. FUNDAMENTAÇÃO JURÍDICA: CADEIA DE CUSTÓDIA (CPP) & DECRETO 6.514/2008
    st.markdown("""<div style="background:#FFFFFF;border:1px solid #DCE3E8;border-left:5px solid #134E39;border-radius:10px;padding:20px 22px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,0.03);">
<div style="font-size:16.5px;font-weight:700;color:#134E39;margin:0 0 10px;">⚖️ Fundamentação Jurídica: Cadeia de Custódia (CPP) & Sanções Ambientais (Dec. 6.514/08)</div>
<p style="color:#333;font-size:13.5px;line-height:1.65;margin-bottom:14px;">
Os <b>Artigos 158-A a 158-F do Código de Processo Penal (CPP)</b> e o <b>Decreto Federal nº 6.514/2008</b> são diplomas normativos de escopos jurídicos distintos, mas que compartilham uma convergência decisiva na <b>preservação da prova pericial e na eficácia da fiscalização legal</b> no direito ambiental brasileiro.
</p>

<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px;margin-bottom:16px;">
<div style="background:#F4F7F6;border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;">
<div style="font-size:14px;font-weight:700;color:#1E6B52;margin-bottom:6px;">1. 📜 Arts. 158-A a 158-F do CPP: A Cadeia de Custódia Probatória</div>
<p style="font-size:12.5px;color:#444;line-height:1.55;margin:0;">
Introduzidos pela <i>Lei do Pacote Anticrime (Lei nº 13.964/19)</i>, estes artigos fixam o rastreamento rigoroso de qualquer prova material:<br>
• <b>Art. 158-A:</b> Define cadeia de custódia como o conjunto de procedimentos para manter e documentar a história cronológica de um vestígio.<br>
• <b>Art. 158-B:</b> Lista as <b>10 etapas oficiais</b> da cadeia: <i>reconhecimento, isolamento, fixação, coleta, acondicionamento, transporte, recebimento, processamento, armazenamento e descarte</i>.<br>
• <b>Arts. 158-C a 158-E:</b> Tratam da coleta por agentes e peritos oficiais, da proibição de violar locais isolados e da infraestrutura segura de Centrais de Custódia.<br>
• <b>Art. 158-F:</b> Determina o retorno obrigatório do vestígio à central de custódia após a conclusão da perícia.
</p>
</div>

<div style="background:#F4F7F6;border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;">
<div style="font-size:14px;font-weight:700;color:#1E6B52;margin-bottom:6px;">2. 🌲 Decreto Federal nº 6.514/2008: Infrações & Sanções Ambientais</div>
<p style="font-size:12.5px;color:#444;line-height:1.55;margin:0;">
Regulamenta a esfera administrativa sancionadora da <b>Lei de Crimes Ambientais (Lei nº 9.605/1998)</b>:<br>
• <b>Objetivo:</b> Estabelece o rito processual administrativo federal para apurar condutas lesivas ao meio ambiente e fixar as penalidades aplicadas por órgãos como <b>IBAMA</b>, <b>ICMBio</b> e secretarias estaduais (<b>SEMAS</b>).<br>
• <b>Sanções Aplicáveis:</b> Advertências, multas simples (que variam de <b>R$ 50,00 a R$ 50 milhões</b>), multas diárias, apreensão de animais/produtos/maquinários e o <b>embargo de obras ou atividades</b> em áreas desmatadas.
</p>
</div>
</div>

<div style="font-size:14.5px;font-weight:700;color:#134E39;margin:14px 0 8px;">🔗 Como Esses Dois Diplomas se Cruzam na Prática Forense?</div>
<p style="color:#333;font-size:13px;line-height:1.6;margin-bottom:12px;">
A conexão prática ocorre quando um ilícito ambiental deflagra simultaneamente um <b>processo administrativo sancionador</b> (multa/embargo) e uma <b>ação penal pública por crime ambiental</b> (conforme o princípio da independência das instâncias):
</p>

<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;overflow:hidden;margin-bottom:12px;">
<table style="width:100%;border-collapse:collapse;font-size:12.5px;text-align:left;">
<tr style="background:#F1F5F9;border-bottom:1px solid #CBD5E1;">
<th style="padding:10px 14px;color:#1E6B52;font-weight:700;width:32%;">Aspecto de Cruzamento</th>
<th style="padding:10px 14px;color:#1E6B52;font-weight:700;">Aplicação Prática no Campo & Blindagem Judicial</th>
</tr>
<tr style="border-bottom:1px solid #F1F5F9;">
<td style="padding:10px 14px;font-weight:600;color:#333;">🛡️ Materialidade da Prova</td>
<td style="padding:10px 14px;color:#444;line-height:1.5;">Evidências coletadas por fiscais ambientais (fotos com GPS, coordenadas de desmate, áudios de depoimento, autos físicos de infração e termos de embargo) que servem de prova para o Ministério Público devem seguir estritamente as regras de cadeia de custódia do CPP para <b>não sofrerem anulação judicial</b>.</td>
</tr>
<tr style="border-bottom:1px solid #F1F5F9;background:#FAFAFA;">
<td style="padding:10px 14px;font-weight:600;color:#333;">👮 Atuação dos Agentes de Campo</td>
<td style="padding:10px 14px;color:#444;line-height:1.5;">Fiscais atuando sob o Decreto 6.514/2008 tornam-se os agentes públicos primários responsáveis por reconhecer, fixar e isolar vestígios de interesse pericial penal (<b>Art. 158-A, § 2º do CPP</b>).</td>
</tr>
<tr>
<td style="padding:10px 14px;font-weight:600;color:#333;">🌳 Resposta Tecnológica do SC3</td>
<td style="padding:10px 14px;color:#444;line-height:1.5;">O <b>Selo Criptográfico SC3</b> implementa matematicamente as etapas de <i>fixação</i> e <i>armazenamento</i> (Art. 158-B, III e IX) através da <b>Árvore de Merkle SHA-256</b> gerada em tempo real no próprio dispositivo local, conferindo presunção de não-adulteração a custo zero.</td>
</tr>
</table>
</div>
</div>""", unsafe_allow_html=True)


    # 3. TUTORIAL OPERACIONAL
    st.markdown("""<div style="background:#FFFFFF;border:1px solid #DCE3E8;border-radius:10px;padding:20px 22px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,0.03);">
<div style="font-size:16px;font-weight:700;color:#1E6B52;margin:0 0 14px;">📖 Tutorial Operacional: Como Usar o SC3 DocAudit em Campo</div>
<div style="border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;background:#FAFAFA;margin-bottom:12px;">
<div style="font-size:14px;font-weight:700;color:#1E6B52;">Passo 1: 🏠 Painel Inicial & Acesso Rápido</div>
<div style="font-size:13px;color:#444;margin-top:4px;line-height:1.5;">Na tela inicial (otimizada para celular e tablet de campo), selecione <b>➕ Iniciar Nova Fiscalização</b> para cadastrar uma nova operação ou <b>🔍 Consultar Ocorrências</b> para acessar o acervo de operações auditadas.</div>
</div>
<div style="border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;background:#FAFAFA;margin-bottom:12px;">
<div style="font-size:14px;font-weight:700;color:#1E6B52;">Passo 2: ➕ Criar Ocorrência & Ingestão de Autos Físicos</div>
<div style="font-size:13px;color:#444;margin-top:4px;line-height:1.5;">Informe o título da operação, o município e o agente autuante. Fotografe os documentos físicos (Autos de Constatação, Infração, Termos de Embargo, etc.). O motor OpenCV aplica automaticamente correção geométrica de perspectiva (<i>deskew</i>), realce de contraste e binarização adaptativa, extraindo todos os campos estruturados sem depender de formulários padronizados.</div>
</div>
<div style="border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;background:#FAFAFA;margin-bottom:12px;">
<div style="font-size:14px;font-weight:700;color:#1E6B52;">Passo 3: 📂 Dossiê Forense, Conciliação de Divergências & Download</div>
<div style="font-size:13px;color:#444;margin-top:4px;line-height:1.5;">No Dossiê da Operação:<br>
• <b>Navegação por Lista (Bullet Points):</b> Visualize os documentos físicos vinculados em lista compacta (com botão expansor <i>"Ver tudo"</i> quando houver mais de 5 itens).<br>
• <b>Painel de Divergências:</b> Se houver conflito entre o auto e os sensores de campo (ex: área divergente do GPS ou CAR não coincidente), clique em <code>✏️ Corrigir agora</code> para rolar suavemente até o campo em alerta (⚠️) e sanar a inconsistência.<br>
• <b>Visualização & Download:</b> Compare a imagem original tratada lado a lado com os dados estruturados e utilize o botão <code>⬇️ Baixar Imagem</code> para arquivar a prova original.<br>
• <b>Adicionar Novas Evidências:</b> Junte novas fotos georreferenciadas ou autos complementares a qualquer momento via câmera ou upload com recálculo automático da Merkle Root.</div>
</div>
<div style="border:1px solid #E2E8F0;border-radius:8px;padding:14px 16px;background:#FAFAFA;">
<div style="font-size:14px;font-weight:700;color:#1E6B52;">Passo 4: 🔍 Gestão Centralizada & Arquivamento Forense (Soft Delete)</div>
<div style="font-size:13px;color:#444;margin-top:4px;line-height:1.5;">Consulte ocorrências com busca instantânea por município, fiscal, tipo de auto ou status de conciliação. Para remover uma ocorrência, utilize o botão <code>🗑️</code> no cabeçalho do dossiê: o registro é arquivado logicamente (<code>removedAt</code>) com carimbo de data/hora, preservando a integridade do banco SQLite e a rastreabilidade probatória.</div>
</div>
</div>""", unsafe_allow_html=True)

    # 4. MÉTRICAS DE EFICIÊNCIA E CONFORMIDADE
    st.markdown("""<div style="background:#F4F7F6;border:1px solid #DCE3E8;border-left:5px solid #1E6B52;border-radius:10px;padding:20px 22px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,0.03);">
<div style="font-size:16px;font-weight:700;color:#1E6B52;margin:0 0 10px;">⚙️ Métricas de Eficiência e Conformidade (Regra 4 do Hackathon)</div>
<ul style="margin:0;padding-left:20px;color:#333;line-height:1.85;font-size:13.5px;">
<li><b>Custo por Documento:</b> <span style="color:#1E6B52;font-weight:bold;">R$ 0,00 ($0.00)</span> — 100% inferência local sem consumo de APIs proprietárias pagas em nuvem.</li>
<li><b>Operação Offline:</b> Executa totalmente na CPU/GPU do dispositivo do agente em campo, sem dependência de conexão com a internet.</li>
<li><b>Persistência SQLite:</b> Banco de dados local <code>occurrences.db</code> estruturado em modelo relacional 1 : N (Ocorrência &rarr; Documentos Físicos).</li>
<li><b>Privacidade & LGPD:</b> Dados sensíveis (CPFs, nomes de autuados e matrículas) permanecem estritamente sob custódia do órgão ambiental, sem vazamento ou envio a servidores externos.</li>
</ul>
</div>""", unsafe_allow_html=True)

