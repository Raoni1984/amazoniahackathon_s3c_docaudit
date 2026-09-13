# 🛡️ SC3 DocAudit
### Intelligent Extraction, Uncertainty Calibration, and Cryptographic Chain of Custody for Environmental Enforcement in the Amazon

[![Protocol](https://img.shields.io/badge/Protocol-SC3%20(Cryptographic%20Seal)-00f59b.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Database](https://img.shields.io/badge/Database-SQLite%20Offline%20Persistent-blue.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Architecture](https://img.shields.io/badge/Architecture-Occurrence--First%20%7C%20Mobile--First-purple.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Cost](https://img.shields.io/badge/Cost%20per%20Doc-R%24%200%2C00%20(Zero--Cost%20Offline)-brightgreen.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Privacy](https://img.shields.io/badge/LGPD-100%25%20Compliant%20by%20Design-0284c7.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Tests](https://img.shields.io/badge/Tests-17%2F17%20Passing-success.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Live Demo](https://img.shields.io/badge/Streamlit%20Cloud-Live%20Demo-red.svg)](https://amazoniahackathons3cdocaudit-nmluix5bwjqrtjt4sfysv2.streamlit.app/)

---

<div align="center">
  <h3>🌐 <b>Language / Idioma:</b> <a href="#english-documentation">🇺🇸 English Documentation</a> &nbsp;•&nbsp; <a href="#documentação-em-português-pt-br">🇧🇷 Documentação em Português (PT-BR)</a></h3>
</div>

---

## English Documentation

### 🌐 Live Cloud Demo & Court Deep Links
- **Production Dashboard:** [amazoniahackathons3cdocaudit.streamlit.app](https://amazoniahackathons3cdocaudit-nmluix5bwjqrtjt4sfysv2.streamlit.app/)
- **Direct Judicial Expert Deep Link (Example):** `https://amazoniahackathons3cdocaudit-nmluix5bwjqrtjt4sfysv2.streamlit.app/?dossie=OC-2026-ALT-01`

---

### 📌 Hackathon Alignment & Design Highlights

| Criteria | Implementation in SC3 DocAudit |
| :--- | :--- |
| **1. End-to-End Delivery** | Full-stack execution: Ingestion ➔ OpenCV Preprocessing ➔ Zero-Shot Extraction ➔ Uncertainty Calibration ➔ Spatiotemporal Reconciliation ➔ Merkle Cryptographic Sealing ➔ Responsive Web & Judicial Export (`.sc3`). |
| **2. Active Data Ingestion** | Comprehensive ingestion of all pilot dossiers (Altamira, Paragominas, Tailândia, Ulianópolis) + GPS formats (Garmin GPX, KML, CSV/GMS) conforming to Federal Decree 6,514/2008. |
| **3. Declare Uncertainty** | `ConfidenceEvaluator` assigns dynamic confidence scores ($0.0$ to $1.0$) based on image metrics. Missing or ambiguous data yields explicit `null` with legal reasoning rather than AI hallucination. |
| **4. Adversarial Self-Validation** | Synthetic test suites simulating field adversity: low-light photos, skewed angles, truck-hood shadows, engine noise, and wrinkled field sheets. |
| **5. Cost as a Design Constraint** | **Zero-Cost ($0.00 / doc):** 100% offline edge processing. Zero dependency on costly cloud LLM tokens, enabling instant adoption by small Amazonian municipal secretariats. |
| **6. Bonus Milestone (SC3 Protocol)** | **Irreversible Chain of Custody:** Cryptographic SHA-256 Merkle Tree mathematically binds paper notices with GPS photos, voice memos, and field logs (Arts. 158-A to 158-F, Brazilian Criminal Procedure Code). |

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
               │ 6. Occurrence-First Web Platform  │
               │   - Deep forensic dossier viewer  │
               │   - .sc3 Forensic Container export│
               └───────────────────────────────────┘
```

---

### 💰 Cost Comparison: Commercial Cloud AI vs. SC3 DocAudit

| Metric | Commercial Cloud LLM Pipeline | SC3 DocAudit (Edge-Native) |
| :--- | :--- | :--- |
| **Cost per Document** | ~$0.12 - $0.35 (Token & Vision API costs) | **$0.00 (R$ 0,00)** |
| **Annual Cost (10,000 docs)** | ~$2,500.00 USD (~R$ 14.000,00) | **$0.00 (R$ 0,00)** |
| **Internet Dependency** | Mandatory (Fails in deep Amazon rainforest) | **100% Offline (Edge CPU)** |
| **Hallucination Risk** | Significant (Generative drift in names/dates) | **Zero (Deterministic extraction & calibration)** |
| **Judicial Chain of Custody** | None (Third-party cloud transmission) | **Immutable Merkle Tree (.sc3 container)** |

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
│   │   ├── gps_parser.py            # Garmin GPX / KML / CSV coordinate parser
│   │   ├── cost_tracker.py          # Zero-cost auditing metrics tracker
│   │   └── database.py              # Persistent SQLite occurrence database manager
│   ├── data/
│   │   └── occurrences.db           # Local offline SQLite database
│   └── tests/
│       ├── test_adversarial_robustness.py # Adversarial image degradation tests
│       ├── test_epic1.py            # Image preprocessing unit tests
│       ├── test_epic2.py            # Semantic entity extraction tests
│       ├── test_epic3.py            # Uncertainty calibration tests
│       └── test_epic4.py            # SC3 seal and reconciliation tests
├── app.py                           # Occurrence-first Web Dashboard & Evidence Vault
├── cli.py                           # Batch CLI processing tool
├── requirements.txt                 # Lightweight dependencies
└── README.md                        # Bilingual Documentation
```

---

### 🛠️ Quickstart & Execution

#### 1. Setup Environment
```bash
git clone https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit.git
cd amazoniahackathon_s3c_docaudit
pip install -r requirements.txt
```

#### 2. Run Automated Test Suite
```bash
pytest sc3_docaudit/tests/
```

#### 3. Launch Web Dashboard Locally
```bash
streamlit run app.py
```
*Access `http://localhost:8501` to explore dossiers, inspect Merkle trees, and download `.sc3` forensic containers.*

---

<p align="right"><a href="#️-sc3-docaudit">⬆️ Back to Top</a> &nbsp;|&nbsp; <a href="#documentação-em-português-pt-br">🇧🇷 Ir para a Documentação em Português</a></p>

---

## Documentação em Português (PT-BR)

### 🌐 Demonstração Online na Nuvem & Links Periciais
- **App em Produção:** [amazoniahackathons3cdocaudit.streamlit.app](https://amazoniahackathons3cdocaudit-nmluix5bwjqrtjt4sfysv2.streamlit.app/)
- **Exemplo de Link Direto para Laudos Periciais / PJe:** `https://amazoniahackathons3cdocaudit-nmluix5bwjqrtjt4sfysv2.streamlit.app/?dossie=OC-2026-ALT-01`

---

### 📌 Resposta aos Critérios do Hackathon

| Diretriz Oficial | Como o SC3 DocAudit Implementa |
| :--- | :--- |
| **1. Construção de Ponta a Ponta** | Sistema 100% funcional: *Ingestão de Imagens ➔ Pré-processamento OpenCV ➔ Extração Semântica ➔ Calibração de Incerteza ➔ Conciliação Espaçotemporal ➔ Selagem Merkle ➔ Interface Web & Download do Container `.sc3`*. |
| **2. Ingestão e Busca Ativa de Dados** | Todos os dossiês piloto estruturados (Altamira, Paragominas, Tailândia, Ulianópolis) + suporte a formatos GPS (Garmin GPX, Google KML, CSV e GMS) e conformidade com o Decreto Federal nº 6.514/2008. |
| **3. Declaração Explícita de Incerteza** | Módulo `ConfidenceEvaluator`: pontuação de confiança de $0.0$ a $1.0$. Dados ilegíveis recebem `null` acompanhados de justificativa jurídica, eliminando alucinações. |
| **4. Validação em Condições Adversas** | Testes de estresse com fotografias em baixa luminosidade, rotações acentuadas, sombras no capô de viaturas e ruído sonoro em áudios de campo. |
| **5. Custo como Parte do Design** | **Custo Zero (R$ 0,00 / doc):** 100% offline no dispositivo. Sem necessidade de APIs comerciais caras de LLM, viabilizando uso por pequenas secretarias municipais do Pará. |
| **6. Marco Bônus: Protocolo SC3** | **Cadeia de Custódia Inviolável:** Árvore de Merkle SHA-256 vinculando matematicamente autos físicos, fotografias georreferenciadas, áudios e trilhas GPS (Arts. 158-A a 158-F do CPP). |

---

### 💰 Comparativo de Custo: Nuvem Comercial vs. SC3 DocAudit

| Métrica | Solução com LLMs Proprietários | SC3 DocAudit (Edge-Native) |
| :--- | :--- | :--- |
| **Custo por Documento** | ~R$ 0,70 a R$ 2,00 (Chamadas de API) | **R$ 0,00** |
| **Custo Anual (10.000 autos)** | ~R$ 14.000,00 a R$ 25.000,00 | **R$ 0,00** |
| **Dependência de Internet** | Obrigatória (Inviável na mata fechada) | **100% Offline (Edge CPU)** |
| **Risco de Alucinação** | Alto (Divergências em CPFs e áreas) | **Zero (Extração determinística & explicável)** |
| **Cadeia de Custódia Judicial** | Inexistente | **Árvore de Merkle (.sc3 inviolável)** |

---

### 🛠️ Como Executar Localmente

#### 1. Instalar Dependências
```bash
git clone https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit.git
cd amazoniahackathon_s3c_docaudit
pip install -r requirements.txt
```

#### 2. Executar Testes Automatizados
```bash
pytest sc3_docaudit/tests/
```

#### 3. Iniciar o Painel Web
```bash
streamlit run app.py
```
*Acesse `http://localhost:8501` para auditar os dossiês e exportar certidões periciais criptográficas.*

---

<p align="right"><a href="#️-sc3-docaudit">⬆️ Voltar ao Topo</a> &nbsp;|&nbsp; <a href="#english-documentation">🇺🇸 Go to English Documentation</a></p>
