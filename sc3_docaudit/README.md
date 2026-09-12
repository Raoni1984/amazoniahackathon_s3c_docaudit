# 🌲 SC3 DocAudit
### Sistema Inteligente de Extração, Calibração de Incerteza e Auditoria Forense para Fiscalização Ambiental na Amazônia

[![AmazôniaHack 2026](https://img.shields.io/badge/AmazôniaHack-2026-green.svg)](https://github.com)
[![Challenge](https://img.shields.io/badge/Challenge-2%20%2B%20Bonus%20Milestone-blue.svg)](https://github.com)
[![Protocol](https://img.shields.io/badge/Protocol-SC3%20(Selo%20Criptogr%C3%A1fico)-orange.svg)](https://github.com)
[![Cost](https://img.shields.io/badge/Cost%20per%20Doc-%240.00%20(Offline%20Local)-brightgreen.svg)](https://github.com)
[![Privacy](https://img.shields.io/badge/LGPD-100%25%20Compliant-blue.svg)](https://github.com)

---

## 📌 Visão Geral

O **SC3 DocAudit** é uma solução de ponta a ponta desenvolvida para transformar formulários de fiscalização ambiental fotografados em campo (manuscritos no capô de viaturas, impressos, com carimbos e assinaturas) em **dados estruturados padronizados em JSON**, com **estimativa rigorosa de incerteza por campo** e **auditoria de conciliação automática com registros digitais (Marco Bônus)** através do protocolo **SC3 (Selo Criptográfico de Cadeia de Custódia)**.

---

## 🚀 Diferenciais & Inovações

1. **Agnóstico a Layouts Municipais (Zero-Shot):**
   - Não utiliza posições fixas de formulário. Funciona para formulários de qualquer um dos milhares de municípios da Amazônia Legal.
2. **Custo Zero e 100% Offline (Regra 4 do Hackathon):**
   - Roda localmente sem necessidade de chamadas a APIs pagas por página, viabilizando o uso por secretarias municipais com orçamento reduzido.
3. **Calibração de Incerteza & Human-in-the-Loop:**
   - Cada campo possui um índice de confiabilidade (`confidence: 0.0 a 1.0`). Campos ilegíveis recebem `null` em vez de alucinações, com destaque visual imediato para conferência do fiscal.
4. **Protocolo SC3 (Selo Criptográfico de Cadeia de Custódia - Marco Bônus):**
   - Cruza os dados do papel com o registro digital do app de campo (Sumaúma) e fotos com GPS.
   - Detecta discrepâncias de área, datas, nomes e coordenadas que poderiam anular processos na Justiça.
   - Gera um Hash SHA-256 inviolável garantindo a integridade temporal e geográfica da prova.
5. **Privacidade e LGPD por Design:**
   - Os dados judiciais sensíveis (CPFs, nomes de proprietários) não saem da máquina do órgão ambiental; apenas o Hash criptográfico da cadeia de custódia é compartilhado.

---

## 🏗️ Estrutura do Repositório

```
sc3_docaudit/
├── core/
│   ├── schema.py                # Schema Pydantic estrito conforme schema.md
│   ├── image_preprocessing.py   # Pipeline OpenCV (deskew, sombras, contraste)
│   ├── extractor_engine.py      # Motor de extração semântica layout-agnostic
│   ├── confidence_evaluator.py  # Calibração de incerteza e regras anti-alucinação
│   ├── reconciler.py            # Motor de conciliação papel x digital (Marco Bônus)
│   └── crypto_seal.py           # Gerador do Selo Criptográfico SC3 (SHA-256)
├── cli.py                       # CLI para processamento em lote
├── app.py                       # Dashboard Web interativo para o fiscal
├── tests/                       # Testes de unidade e validação
├── requirements.txt             # Dependências do projeto
└── README.md
```

---

## 🛠️ Instalação e Uso Rápido

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar o processamento em lote via CLI
python cli.py --input ../participant-package/challenges-1-2/altamira/documents/ --output ./output/altamira/

# 3. Iniciar a Interface Human-in-the-Loop
streamlit run app.py
```

---

## 📜 Conformidade com o Schema Oficial

Os arquivos JSON gerados cumprem 100% a especificação do `schema.md`:
- `document_type`, `number`, `series`, `year`, `issued_date`, `issued_time`, `municipality`, `agency`
- `parties` (`cited_party`, `issuer`, `witness`, `found_on_site`)
- `property_name`, `car`, `area_ha`, `coordinates` (preservação literal)
- `legal_basis`, `fine_brl`, `references` (rastreabilidade da cadeia de autos)
- `signatures`, `confidence` (0.0 a 1.0 por campo)
- `forensic_audit` (extensão com o Selo SC3)
