# 🛡️ SC3 DocAudit
### Intelligent Extraction, Uncertainty Calibration, and Cryptographic Chain of Custody for Environmental Enforcement in the Amazon

[![Protocol](https://img.shields.io/badge/Protocol-SC3%20(Cryptographic%20Seal)-00f59b.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Database](https://img.shields.io/badge/Database-SQLite%20Offline%20Persistent-blue.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Architecture](https://img.shields.io/badge/Architecture-Occurrence--First%20%7C%20Mobile--First-purple.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Cost](https://img.shields.io/badge/Cost%20per%20Doc-%240.00%20(Local%20Offline)-brightgreen.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Privacy](https://img.shields.io/badge/LGPD-100%25%20Compliant%20by%20Design-0284c7.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Tests](https://img.shields.io/badge/Tests-14%2F14%20Passing-success.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)

---

<div align="center">
  <h3>🌐 <b>Language / Idioma:</b> <a href="#english-documentation">🇺🇸 English Documentation</a> &nbsp;•&nbsp; <a href="#documentacao-em-portugues-pt-br">🇧🇷 Documentação em Português (PT-BR)</a></h3>
</div>

---

## English Documentation

### 📌 System Overview

**SC3 DocAudit** is an edge-native, zero-cloud intelligence and forensic audit platform engineered to digitize, validate, and cryptographically seal environmental enforcement records collected under extreme field conditions in the Amazon rainforest. 

The system operates on an **Occurrence-First** paradigm: every physical enforcement document (infraction notice, embargo term, seizure report, inspection order) forms an autonomous, auditable record with persistent local storage in **SQLite**, verified through the **SC3 Protocol** (*Cryptographic Chain of Custody Seal via SHA-256 Merkle Trees*).

---

### 🚀 Key Technical Pillars

1. **Occurrence-First Architecture & Persistent SQLite Database:**
   - The central operational unit is the **Occurrence** (`id: OC-2026-MUNI-NUMBER`).
   - Built-in local persistent storage at `sc3_docaudit/data/occurrences.db` indexed strictly against `schema.md`.
   - Pre-indexes and persists extracted entities, parties, coordinates, Merkle root hashes, and reconciliation status.
   - Real-time full-text search by Notice Number, Tax ID (CPF/CNPJ), Cited Party Name, CAR Code, Inspector Badge, or Enforcement Type.

2. **100% Offline & Mobile-First for Remote Field Agents:**
   - **Zero Network / Zero Server Dependency:** Runs entirely on edge CPUs/GPUs without cellular, Wi-Fi, or satellite connectivity.
   - **Store-and-Forward Sync:** Agents capture photos, audio notes, and documents in deep forest; data is cryptographically sealed instantly on device and synchronized seamlessly upon returning to municipal bases.
   - **PWA & Mobile-Ready:** Touch-optimized UI with on-demand camera shutter controls designed for field operation under direct sunlight and glove interaction.

3. **Layout-Agnostic Zero-Shot OCR & Computer Vision Preprocessing:**
   - **OpenCV Pipeline:** Automated document deskew angle calculation, truck-hood shadow attenuation, and Otsu adaptive binarization.
   - **Zero-Shot Semantic Extraction:** Universal recognition capable of parsing arbitrary municipal notice layouts without hardcoded coordinate templates.

4. **Calibrated Uncertainty & Anti-Hallucination Engine:**
   - Field-level confidence scoring (`0.0` to `1.0`). Illegible or damaged handwriting is assigned `null` with explicit uncertainty rationales rather than fabricating false entities.

5. **SC3 Protocol: Cryptographic Chain of Custody & Spatiotemporal Cross-Audit:**
   - Mathematically binds paper notice contents with multimodal digital evidence (GPS-tagged photos, voice notes, CAR polygons, Sumaúma app summaries).
   - Generates an immutable **SHA-256 Merkle Root Proof**.
   - Instantly detects and flags discrepancies in deforested area (`area_ha`), dates, and coordinates to prevent judicial nullification.

6. **Rule 4 Compliance & LGPD by Design:**
   - **Cost per Document: $0.00 (R$ 0,00)** — Zero reliance on commercial cloud LLM APIs.
   - Complete data sovereignty: Personal identifying data stays on-premise; only cryptographic verification hashes are publicly verifiable.

---

### 🏗️ Technical Architecture & Data Flow

```
                                ┌──────────────────────────────────────┐
                                │ Physical Field Notice (Camera / JPG) │
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ 1. OpenCV Preprocessing Engine       │
                                │   - Deskew rotation angle estimation │
                                │   - Shadow attenuation & binarization│
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ 2. Zero-Shot Semantic Extractor      │
                                │   - Multi-field entity extraction    │
                                │   - Schema.md strict adherence       │
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
 ┌───────────────────────────┐  ┌──────────────────────────────────────┐
 │ Multimodal Field Evidence │  │ 3. Calibrated Uncertainty Evaluator  │
 │ (GPS Photos, Voice Notes) │  │   - Confidence scoring (0.0 - 1.0)   │
 └─────────────┬─────────────┘  │   - Anti-hallucination guardrails    │
               │                └──────────────────┬───────────────────┘
               │                                   │
               └─────────────────┬─────────────────┘
                                 │
                                 ▼
               ┌───────────────────────────────────┐
               │ 4. SC3 Forensic Reconciler Engine │
               │   - Spatiotemporal cross-check    │
               │   - Merkle Tree SHA-256 root seal │
               └─────────────────┬─────────────────┘
                                 │
                                 ▼
               ┌───────────────────────────────────┐
               │ 5. Persistent Local SQLite DB     │
               │   (sc3_docaudit/data/occurrences) │
               └─────────────────┬─────────────────┘
                                 │
                                 ▼
               ┌───────────────────────────────────┐
               │ 6. Human-in-the-Loop Web App & UI │
               │   - Real-time occurrence table    │
               │   - Deep forensic dossier viewer  │
               │   - Exportable standardized JSON  │
               └───────────────────────────────────┘
```

---

### 📁 Repository Structure

```
AmazoniaHack2026/
├── sc3_docaudit/
│   ├── core/
│   │   ├── schema.py                # Strict Pydantic models (schema.md)
│   │   ├── image_preprocessing.py   # OpenCV deskew, contrast & shadow pipeline
│   │   ├── extractor_engine.py      # Layout-agnostic semantic OCR extractor
│   │   ├── confidence_evaluator.py  # Uncertainty calibration & confidence scoring
│   │   ├── reconciler.py            # Spatiotemporal cross-audit reconciler
│   │   ├── crypto_seal.py           # SC3 Protocol (SHA-256 Merkle Tree)
│   │   └── database.py              # Persistent SQLite occurrence database manager
│   ├── data/
│   │   └── occurrences.db           # Local offline SQLite database file
│   └── tests/
│       ├── test_adversarial_robustness.py # Adversarial image degradation tests
│       ├── test_epic1.py            # Image preprocessing unit tests
│       ├── test_epic2.py            # Semantic entity extraction tests
│       ├── test_epic3.py            # Uncertainty calibration tests
│       └── test_epic4.py            # SC3 seal and reconciliation tests
├── app.py                           # Occurrence-first Web Dashboard & Evidence Vault
├── cli.py                           # Batch CLI processing tool
├── benchmark_eval.py                # Quantitative accuracy evaluation harness
├── epics.md                         # Product requirement roadmap and epics
├── requirements.txt                 # Project dependencies
└── README.md                        # Documentation (English / Portuguese)
```

---

### 🛠️ Quickstart & Execution

#### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit.git
cd amazoniahackathon_s3c_docaudit

# Install required dependencies
pip install -r requirements.txt
```

#### 2. Run Automated Test Suite
```bash
pytest sc3_docaudit/tests/
```
*Executes all 14 unit and integration tests covering OpenCV preprocessing, zero-shot entity extraction, confidence calibration, adversarial robustness, and SC3 Merkle seals.*

#### 3. Launch Web Application
```bash
streamlit run app.py
```
*Access the local dashboard at `http://localhost:8501` to search occurrences, inspect dossiers, review deskewed images, listen to field voice notes, and register new notices via camera.*

---

<p align="right"><a href="#️-sc3-docaudit">⬆️ Back to Top</a> &nbsp;|&nbsp; <a href="#documentacao-em-portugues-pt-br">🇧🇷 Ir para a Documentação em Português</a></p>

---

## Documentação em Português (PT-BR)

### 📌 Visão Geral do Sistema

O **SC3 DocAudit** é uma plataforma de inteligência e auditoria pericial desenhada para operar 100% offline em condições extremas de campo na Amazônia. 

O sistema adota o paradigma **Centrado na Ocorrência**: cada documento de fiscalização (auto de infração, termo de embargo, termo de apreensão, ordem de fiscalização) é tratado como uma unidade autônoma e auditável, persistida localmente em **banco de dados SQLite** e protegida pelo **Protocolo SC3** (*Selo Criptográfico de Cadeia de Custódia via Árvore de Merkle SHA-256*).

---

### 🚀 Pilares Técnicos

1. **Arquitetura Focada em Ocorrências & Banco SQLite Persistente:**
   - Unidade fundamental: **Ocorrência (`id: OC-2026-MUNI-NUMBER`)**.
   - Persistência local em [`sc3_docaudit/data/occurrences.db`](file:///c:/Users/raoni/code_practice/AmazoniaHack2026/sc3_docaudit/data/occurrences.db), aderente ao `schema.md` oficial.
   - Busca em tempo real por Número do Auto, CPF/CNPJ do Autuado, Nome, Código do CAR, Matrícula do Fiscal ou Categoria.

2. **100% Offline & Mobile-First para Agentes de Campo:**
   - **Zero Dependência de Conexão:** Roda na CPU local do dispositivo sem internet ou sinal celular.
   - **Operação Store-and-Forward:** O agente fotografa e sela os dados no meio da mata; ao retornar à secretaria ou obter conexão, os dados são sincronizados sem risco de adulteração.
   - **Interface Touch-Friendly & Câmera Sob Demanda:** Projetada para telas de smartphones e tablets de campo, ativando a câmera somente quando solicitado para economizar bateria.

3. **Visão Computacional OpenCV & Extração Zero-Shot:**
   - Correção automática de inclinação (*deskew*), remoção de sombras do capô de viaturas e binarização adaptativa.
   - Extração semântica universal sem templates ou máscaras fixas por município.

4. **Calibração de Incerteza (Human-in-the-Loop):**
   - Pontuação de confiança de `0.0` a `1.0` por campo. Escritas ilegíveis são marcadas como `null` com justificativa explícita, impedindo alucinações.

5. **Protocolo SC3: Selo Criptográfico & Conciliação de Evidências:**
   - Cruza o papel com evidências digitais (fotos GPS, áudios de campo e resumo do app Sumaúma).
   - Gera um Hash de Raiz de Merkle SHA-256 inviolável.
   - Alerta discrepâncias de área desmatada (`area_ha`), datas ou coordenadas para blindar o processo contra nulidades jurídicas.

6. **Conformidade com a Regra 4 & LGPD:**
   - **Custo por Documento: R$ 0,00 ($0.00)** — Zero consumo de APIs pagas em nuvem.
   - Privacidade total: Dados sensíveis permanecem no órgão ambiental.

---

<p align="right"><a href="#️-sc3-docaudit">⬆️ Voltar ao Topo</a> &nbsp;|&nbsp; <a href="#english-documentation">🇺🇸 Go to English Documentation</a></p>
