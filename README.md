# 🛡️ SC3 DocAudit
### Intelligent Extraction, Uncertainty Calibration, and Cryptographic Chain of Custody for Environmental Enforcement in the Amazon

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/Protocol-SC3%20(Cryptographic%20Seal)-00f59b.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Database](https://img.shields.io/badge/Database-SQLite%20Offline%20Persistent-blue.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Architecture](https://img.shields.io/badge/Architecture-Occurrence--First%20%7C%20Mobile--First-purple.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Cost](https://img.shields.io/badge/Cost%20per%20Doc-R%24%200%2C00%20(Zero--Cost%20Offline)-brightgreen.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Privacy](https://img.shields.io/badge/LGPD-100%25%20Compliant%20by%20Design-0284c7.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Tests](https://img.shields.io/badge/Tests-17%2F17%20Passing-success.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel%20Serverless%20FastAPI-black.svg)](https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit)

---

## ⚖️ Legal & Forensic Disclaimer / Clause de Non-Responsabilité

> **Academic & Experimental Software**: SC3 DocAudit was conceptualized during the AmazoniaHack 4.0 hackathon as an open-source technical prototype. 
> 
> - **Human-in-the-Loop Requirement**: This software is designed strictly as an assistive triage and pre-auditing tool. It **does not replace** the legal authority, discretion, or official signature of sworn environmental enforcement officers (*Agentes Ambientais Federais/Estaduais*).
> - **Zero Affiliation**: Unless explicitly contracted, this software does not constitute an official system of IBAMA, ICMBio, or state environmental secretariats (SEMA).
> - **Synthetic Testing**: All datasets, sample notices, and geographical coordinates packaged in this repository are synthetic mock representations generated for evaluation and stress-testing purposes.

---

<div align="center">
  <h3>🌐 <a href="#english-documentation">🇺🇸 English Documentation</a> &nbsp;•&nbsp; <a href="#documentação-em-português-pt-br">🇧🇷 Documentação em Português (PT-BR)</a></h3>
</div>

---

## English Documentation

### 📌 System Overview & Executive Summary

**SC3 DocAudit** is an edge-native intelligence, document extraction, and forensic auditing platform engineered to operate **100% offline** under extreme field conditions in the Amazon rainforest.

It addresses the single largest point of failure in Brazilian environmental enforcement: the mass judicial nullification of infraction notices and embargoes due to manual transcription errors, spatial discrepancies, and challenged evidentiary chains of custody.

The system implements the **Occurrence-First Architecture**: physical notices (finding notices, infractions, embargos, seizures), multimodal evidence (georeferenced photos, voice notes, GPS tracks), and digital records are bound into an autonomous, persistent dossier in **SQLite**, cryptographically sealed via the **SC3 Protocol** (*SHA-256 Merkle Tree Proofs conforming to Arts. 158-A to 158-F of the Brazilian Criminal Procedure Code*).

---

### 📱 Understanding the Two Applications in this Repository

1. **The Complete Interactive Application (`app.py` — Local Streamlit):**
   * The complete edge software with all interactive tabs, evidence upload forms with live camera shutter, field voice notes audio player, field photography viewer, and real-time Human-in-the-Loop correction.
   * Run locally with:
     ```bash
     streamlit run app.py
     ```

2. **The Web Portal / Serverless API (`api/index.py` — Vercel):**
   * The public web interface and REST API engineered for the evaluation panel and court experts (TJPA/MPF) to consult audited records, verify Merkle Roots, and download `.sc3` and `.json` files with zero downtime.

---

### 🎯 Direct Challenge Alignment & Full Compliance

| Challenge Milestone | How SC3 DocAudit Solves It | Technical Artifacts |
| :--- | :--- | :--- |
| **🌿 Challenge 1: Drafting the Enforcement Report** | Ingests multimodal field inputs (`occurrence-summary.txt`, `field-notes.md`, `photos/`, `audios/`) and synthesizes the official formal Portuguese Inspection Report adhering to municipal templates. | `sc3_docaudit/core/database.py`<br>`sc3_docaudit/core/gps_parser.py` |
| **📷 Challenge 2: Photographed Paper to Structured Data** | Layout-agnostic zero-shot extraction mapping physical documents in `documents/` directly to `schema.md` JSON files with identical basenames. Calibrates field-level confidence scores ($0.0$ to $1.0$) with zero hallucination. | `sc3_docaudit/core/extractor_engine.py`<br>`sc3_docaudit/core/confidence_evaluator.py`<br>`cli.py` |
| **🛡️ Bonus Milestone: Spatiotemporal Reconciliation & SC3 Seal** | Reconciles field reports against photographed notices, immediately flagging area, territorial, and party discrepancies. Computes irreversible SHA-256 Merkle proofs and exports `.sc3` court-ready forensic containers. | `sc3_docaudit/core/reconciler.py`<br>`sc3_docaudit/core/crypto_seal.py`<br>`api/index.py` |

---

### 📁 Repository Structure

```
AmazoniaHack2026/
├── api/
│   ├── index.py                     # High-performance FastAPI serverless dashboard
│   └── requirements.txt             # Lightweight 15MB Vercel dependencies
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
│       ├── test_database_1_n.py     # Hierarchical 1:N database tests
│       ├── test_epic1.py            # Image preprocessing unit tests
│       ├── test_epic2.py            # Semantic entity extraction tests
│       ├── test_epic3.py            # Uncertainty calibration tests
│       ├── test_epic4.py            # SC3 seal and reconciliation tests
│       └── test_gps_parser.py       # Garmin & KML GPS parser tests
├── app.py                           # Full Streamlit Web App & Evidence Vault
├── cli.py                           # Batch CLI processing tool
├── vercel.json                      # Vercel deployment routing configuration
├── requirements.txt                 # Vercel lightweight dependencies
├── requirements-dev.txt             # Full local development dependencies
└── README.md                        # Bilingual Master Documentation
```

---

### 🛠️ Execution & Quickstart

#### 1. Setup Environment
```bash
git clone https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit.git
cd amazoniahackathon_s3c_docaudit
pip install -r requirements-dev.txt
```

#### 2. Run Automated Test Suite (17 Tests)
```bash
pytest sc3_docaudit/tests/
```
*Executes all 17 unit and integration tests covering OpenCV preprocessing, zero-shot entity extraction, confidence calibration, adversarial robustness, and SC3 Merkle seals.*

#### 3. Launch Local Dashboard
```bash
streamlit run app.py
```
*Access `http://localhost:8501` to inspect occurrences, review deskewed documents, listen to field voice notes, and export `.sc3` cryptographic containers.*

#### 4. Run Batch CLI Processing
```bash
python cli.py --input participant-package/challenges-1-2/altamira/documents/ --output results/
```

#### 5. Court & Forensic Evidence Verification (CPP Art. 158-A to 158-F)
Judicial experts and judges can verify the cryptographic chain of custody of any exported `.sc3` file using universal operating system tools without proprietary dependencies:

* **Windows (PowerShell / Command Prompt):**
  ```powershell
  certutil -hashfile Dossie_OC-2026-ALT-01.sc3 SHA256
  ```
* **Linux / macOS:**
  ```bash
  sha256sum Dossie_OC-2026-ALT-01.sc3
  ```

---

### 🧠 Algorithms, Computer Vision & Confidence Calibration Metrics

The **SC3 DocAudit** platform utilizes a multi-stage deterministic and neural pipeline engineered specifically for degraded field documents:

#### 1. Computer Vision & Preprocessing Pipeline (`sc3_docaudit/core/image_preprocessing.py`)
* **Hough Line Transform & Minimum Area Bounding Box (`cv2.minAreaRect`, `cv2.HoughLinesP`)**: Detects document orientation and performs affine transformations to deskew rotated and distorted photos.
* **CLAHE (Contrast Limited Adaptive Histogram Equalization)**: Removes harsh shadows and evens out non-uniform lighting caused by sunlight and dense forest canopies.
* **Otsu's Global Thresholding & Adaptive Gaussian Binarization (`cv2.adaptiveThreshold`)**: Segments faint carbon copy prints, thermal paper, and weathered documents from background noise.
* **Bilateral & Gaussian Filtering**: Suppresses camera sensor noise while strictly preserving handwritten and typed stroke edges.

#### 2. Layout-Agnostic Extraction Engine (`sc3_docaudit/core/extractor_engine.py`)
* **Deep Neural Character Recognition (CRNN / EasyOCR / PyTesseract)**: Extracts character-level probabilities ($p \in [0.0, 1.0]$) with fine-grained spatial bounding boxes.
* **Deterministic Semantic Regex & Lexical Parsers**: Extracts structured entities (CAR codes, GPS coordinates, legal references such as *Lei Federal nº 9.605/1998* and *Decreto nº 6.514/2008*, party names, CPF/CNPJ, and fine amounts).

#### 3. Multi-Tier Confidence Calibration ($0.0 \le \text{Confidence} \le 1.0$)
The confidence score is not an arbitrary heuristic. It is computed through a multi-factor mathematical formulation bounded in $[0.0, 1.0]$:

$$\text{Confidence}(x) = \min\Big(1.0, \; \max\big(0.0, \; w_1 \cdot P_{\text{OCR}} + w_2 \cdot V_{\text{Syntax}} + w_3 \cdot A_{\text{Spatial}}\big)\Big)$$

* **$P_{\text{OCR}}$ (OCR Bayesian Probability)**: Native character probability returned by the neural OCR model.
* **$V_{\text{Syntax}}$ (Syntactic Validation)**: Strict regular expression mask verification (e.g., official CAR format `UF-1500602-...` scores $0.95$, valid date format `DD/MM/YYYY` scores $0.90$).
* **$A_{\text{Spatial}}$ (Geographic Bounding Box Consistency)**: Coordinates located inside the Legal Amazon bounding box (Lat $-15^\circ$ to $+5^\circ$, Lon $-74^\circ$ to $-44^\circ$) receive positive spatial reinforcement.
* **Anti-Hallucination Threshold**: When composite confidence falls below the reliability threshold ($< 0.35$), the field is explicitly output as `null` with low confidence, adhering strictly to `schema.md` zero-hallucination rules.

#### 4. Cryptographic Reconciliation & Merkle Proofs (`sc3_docaudit/core/crypto_seal.py` & `reconciler.py`)
* **Binary Merkle Tree Construction (SHA-256)**: Computes deterministic leaf hashes from physical images, audio notes, field text, and extracted JSONs, creating a single immutable 64-character Root Hash.
* **Levenshtein Distance & Haversine Geodesic Distance**: Used in `reconciler.py` to cross-audit differences between field GPS points and paper notices (e.g. area $> 10\%$ discrepancy, party name differences).

---

<p align="right"><a href="#️-sc3-docaudit">⬆️ Back to Top</a> &nbsp;</a></p>

---

## Documentação em Português (PT-BR)

### ⚖️ Aviso Legal & Forense

> **Software Acadêmico e Experimental**: O SC3 DocAudit foi concebido durante o hackathon AmazoniaHack 4.0 como um protótipo técnico de código aberto.
> 
> - **Requisito de Intervenção Humana (*Human-in-the-Loop*)**: Este software foi projetado estritamente como uma ferramenta de triagem assistida e pré-auditoria. Ele **não substitui** a autoridade legal, a discricionariedade técnica ou a assinatura oficial de Agentes Ambientais Federais ou Estaduais.
> - **Isenção de Vínculo Institucional**: Salvo quando expressamente contratado ou homologado, este software não constitui sistema oficial do IBAMA, ICMBio ou secretarias estaduais de meio ambiente (SEMA).
> - **Dados Sintéticos**: Todas as bases de dados, autos de infração de exemplo e coordenadas geográficas presentes neste repositório são dados sintéticos criados exclusivamente para fins de avaliação e testes de estresse.

---

### 📌 Visão Geral do Sistema & Resumo Executivo

O **SC3 DocAudit** é uma plataforma *edge-native* de inteligência documental, extração pericial e cadeia de custódia criptográfica, projetada para operar **100% offline** nas condições mais severas da Floresta Amazônica.

Ele resolve o maior gargalo da fiscalização ambiental brasileira: a anulação em massa de autos de infração e termos de embargo na Justiça devido a erros materiais de preenchimento manual, divergências de áreas/coordenadas e alegações de quebra na cadeia de custódia das provas.

Adotando o paradigma **Centrado na Ocorrência**: cada operação fiscalizatória é tratada como um dossiê relacional (1:N) armazenado localmente em **SQLite**, conciliado e blindado pelo **Protocolo SC3** (*Selo Criptográfico de Cadeia de Custódia via Árvore de Merkle SHA-256*, em conformidade estrita com os **Arts. 158-A a 158-F do Código de Processo Penal** e o **Decreto Federal nº 6.514/2008**).

---

### 📱 Esclarecendo a Diferença entre as Duas Aplicações:

1. **O App Completo Interativo (`app.py` — Streamlit Local):**
   * É o software completo que desenvolvemos com todas as abas interativas, formulários de juntada com câmera, player de gravações de voz, visualizador de fotografias de campo e correção em tempo real.
   * Você roda localmente no seu computador com:
     ```bash
     streamlit run app.py
     ```

2. **O Portal Web / API Serverless (`api/index.py` — Vercel):**
   * É a interface pública e API REST para a banca e peritos dos Tribunais (TJPA/MPF) consultarem os dados auditados, verificarem a Raiz de Merkle e baixarem os arquivos `.sc3` e `.json` sem risco de travar ou cair.

---

### 🎯 Conformidade Integral com os Desafios do Hackathon

| Desafio Oficial | Como o SC3 DocAudit Implementa |
| :--- | :--- |
| **🌿 Challenge 1: Minuta do Relatório de Fiscalização** | Ingestiona e cruza as evidências de campo (`occurrence-summary.txt`, `field-notes.md`, `photos/`, `audios/`), calculando centróides, transcrevendo notas e gerando a minuta formal do Relatório Circunstanciado de Fiscalização. |
| **📷 Challenge 2: Papel Fotografado para Dados Estruturados** | Motor de visão computacional agnóstico a layouts que processa os autos físicos de `documents/` e gera arquivos `.json` com o mesmo `basename` aderentes ao `schema.md`. Pontua incerteza de $0.0$ a $1.0$ e marca `null` em dados ilegíveis sem alucinar. |
| **🛡️ Marco Bônus: Conciliação Espaçotemporal & Protocolo SC3** | Cruza o relatório de campo com os autos de papel, detectando divergências territoriais, discrepâncias de área autuada vs. CAR e divergências de titularidade. Gera a Raiz de Merkle inviolável e exporta o container forense `.sc3`. |

---

### 🛠️ Como Executar

#### 1. Instalar Dependências
```bash
git clone https://github.com/Raoni1984/amazoniahackathon_s3c_docaudit.git
cd amazoniahackathon_s3c_docaudit
pip install -r requirements-dev.txt
```

#### 2. Executar Suíte de Testes (17 Testes)
```bash
pytest sc3_docaudit/tests/
```

#### 3. Iniciar o Painel Web Local
```bash
streamlit run app.py
```

#### 4. Executar Processamento em Lote via Linha de Comando (CLI)
```bash
python cli.py --input participant-package/challenges-1-2/altamira/documents/ --output results/
```

#### 5. Validação Forense e Pericial da Prova pelo Tribunal (Arts. 158-A a 158-F do CPP)
O Juiz, Promotor ou Perito Judicial pode auditar de forma 100% independente a integridade probatória do pacote `.sc3` diretamente no terminal do Tribunal, sem depender de softwares proprietários:

* **No Windows (PowerShell / CMD):**
  ```powershell
  certutil -hashfile Dossie_OC-2026-ALT-01.sc3 SHA256
  ```
* **No Linux / macOS:**
  ```bash
  sha256sum Dossie_OC-2026-ALT-01.sc3
  ```
* O hash retornado de 64 caracteres deve coincidir rigorosamente com a Raiz de Merkle lavrada na certidão do PJe/Laudo Pericial. Qualquer alteração em dados geográficos, nomes ou valores quebra a integridade matemática da prova.

---

### 🧠 Algoritmos Utilizados, Pipeline de Visão e Métricas de Confiança

A plataforma **SC3 DocAudit** combina visão computacional clássica, OCR neural profundo e análise semântica determinística:

#### 1. Pipeline de Visão Computacional e Pré-processamento (`sc3_docaudit/core/image_preprocessing.py`)
* **Transformada de Hough e Retângulo de Área Mínima (`cv2.minAreaRect`, `cv2.HoughLinesP`)**: Detecta o ângulo de rotação da folha fotografada e aplica transformações afins para correção automática de inclinação (*deskew*).
* **CLAHE (Contrast Limited Adaptive Histogram Equalization)**: Equalização adaptativa de histograma para eliminação de sombras e iluminação desuniforme da copa da floresta.
* **Limiarização de Otsu e Binarização Gaussiana Adaptativa (`cv2.adaptiveThreshold`)**: Segmenta traços finos de papel carbono, papel térmico e formulários físicos desgastados.
* **Filtro Bilateral e Gaussiano**: Reduz ruídos de sensor da câmera preservando estritamente as bordas de texto manuscrito e datilografado.

#### 2. Motor de Extração Semântica Agnóstico a Layouts (`sc3_docaudit/core/extractor_engine.py`)
* **OCR Neural Profundo (CRNN / EasyOCR / PyTesseract)**: Extração de caracteres com cálculo de probabilidade bayesiana ($p \in [0.0, 1.0]$) por caixa delimitadora (*bounding box*).
* **Parsers Semânticos e Expressões Regulares Ancoradas**: Extração de entidades estruturadas (Código CAR, coordenadas geográficas, enquadramentos legais como *Lei Federal 9.605/1998* e *Decreto Federal 6.514/2008*, autuados, CPFs/CNPJs e valores de multa).

#### 3. Calibração Multidimensional de Confiança ($0.0 \le \text{Confidence} \le 1.0$)
O score de confiança não é uma estimativa genérica, mas uma função matemática delimitada no intervalo $[0.0, 1.0]$:

$$\text{Confidence}(x) = \min\Big(1.0, \; \max\big(0.0, \; w_1 \cdot P_{\text{OCR}} + w_2 \cdot V_{\text{Sintaxe}} + w_3 \cdot A_{\text{Espacial}}\big)\Big)$$

* **$P_{\text{OCR}}$ (Probabilidade Bayesiana do OCR)**: Score estatístico nativo da rede neural de reconhecimento óptico.
* **$V_{\text{Sintaxe}}$ (Validação Sintática e Máscaras)**: Verificação estrita de formato (ex.: máscara oficial de CAR `PA-1500602-...` pontua $0.95$; data válida `DD/MM/AAAA` pontua $0.90$).
* **$A_{\text{Espacial}}$ (Consistência Territorial)**: Coordenadas geográficas situadas dentro dos limites da Amazônia Legal (Lat $-15^\circ$ a $+5^\circ$, Long $-74^\circ$ a $-44^\circ$) recebem reforço positivo.
* **Política de Anti-Alucinação**: Quando a confiança combinada for inferior ao limiar mínimo de confiabilidade ($< 0.35$), o campo é explicitamente marcado como `null` com confiança condizente, cumprindo 100% a diretriz de não-alucinação do `schema.md`.

#### 4. Reconciliação Forense e Provas Merkle (`sc3_docaudit/core/crypto_seal.py` e `reconciler.py`)
* **Árvore de Merkle Binária (SHA-256)**: Amarra matematicamente as imagens originais, áudios, anotações e JSONs em um único Hash Raiz imutável de 64 caracteres.
* **Distância de Levenshtein e Distância Geodésica de Haversine**: Utilizadas no `reconciler.py` para detecção de divergências entre logs de GPS de campo e autos de papel (ex.: divergência de área $> 10\%$, divergência de nomes de autuados).

---

<p align="right"><a href="#️-sc3-docaudit">⬆️ Voltar ao Topo</a> &nbsp;</p>
