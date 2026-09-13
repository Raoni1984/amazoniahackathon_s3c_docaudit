# 📋 Rastreamento de Épicos: Projeto SC3 DocAudit
**AmazôniaHack 2026 — Desafio 2 & Marco Bônus**
*Protocolo SC3 (Selo Criptográfico de Cadeia de Custódia)*

---

## 🧭 Visão Geral do Cronograma

| Épico | Nome | Estimativa | Status |
| :---: | :--- | :---: | :---: |
| **Épico 1** | Fundação, Schema Pydantic e Pré-processamento de Imagens | 1h30 | 🟢 **Concluído** |
| **Épico 2** | Motor de Extração Zero-Shot Layout-Agnostic (Core VLM/OCR) | 3h00 | 🟢 **Concluído** |
| **Épico 3** | Calibração de Incerteza e Otimização de Custos (Regra 4) | 2h30 | 🟢 **Concluído** |
| **Épico 4** | ⭐ Marco Bônus: Conciliação Espaço-Temporal & Protocolo SC3 | 2h30 | 🟢 **Concluído** |
| **Épico 5** | Interface de Ponta a Ponta (CLI & Dashboard Human-in-the-Loop) | 2h30 | 🟢 **Concluído** |
| **Épico 6** | Testes Adversos, Validação dos 20 Casos e Pitch/Demo | 2h00 | 🟢 **Concluído** |

---

## 📌 Detalhamento das Tarefas por Épico

### 🔹 Épico 1: Fundação, Schema Pydantic e Pré-processamento de Imagens (1h30)
- [x] Estruturação do repositório limpo (`sc3_docaudit/`) e `README.md`.
- [x] Implementação de `core/schema.py` com tipagem Pydantic estrita conforme `schema.md`.
- [x] Criação de validadores e normalizadores para `document_type`, `parties`, `references` e `coordinates`.
- [x] Implementação de `core/image_preprocessing.py` (OpenCV: auto-deskew, redução de sombras, correção de contraste e iluminação de campo).
- [x] Testes unitários com as imagens de exemplo dos 4 municípios (100% aprovados).

### 🔹 Épico 2: Motor de Extração Zero-Shot Layout-Agnostic (3h00)
- [x] Implementação de `core/extractor_engine.py`.
- [x] Extração de manuscrito e texto impresso sem dependência de templates fixos por município.
- [x] Estratégia semântica de parsing de layouts complexos (partes, CPF/CNPJ, coordenadas literais, CAR, multas).
- [x] Extração e amarração da cadeia de documentos (`references`).
- [x] Testes de integração E2E com documento real de campo (100% aprovados).

### 🔹 Épico 3: Calibração de Incerteza e Otimização de Custos (2h30)
- [x] Implementação de `core/confidence_evaluator.py`.
- [x] Algoritmo de score de confiança (0.0 a 1.0) por campo.
- [x] Regra estrita anti-alucinação: setar `null` com justificativa para revisão humana.
- [x] Calculadora e relatório de custo/tempo por página processada ($0 local / CPU).

### 🔹 Épico 4: ⭐ Marco Bônus: Conciliação Espaço-Temporal & Protocolo SC3 (2h30)
- [x] Implementação de `core/crypto_seal.py` (Árvore de Merkle e Hashes SHA-256).
- [x] Implementação de `core/reconciler.py` (Motor de conciliação papel x digital).
- [x] Cálculo e auditoria de área geodésica em hectares para blindagem contra nulidade judicial.
- [x] Testes de conciliação e geração do Selo SC3 (100% aprovados).

### 🔹 Épico 5: Interface de Ponta a Ponta (CLI & Dashboard Web) (2h30)
- [x] Implementação de `cli.py` para processamento automatizado em lote.
- [x] Implementação de `app.py` (Dashboard Web Streamlit com visão lado a lado e alertas de incerteza).
- [x] Validação da exportação do JSON oficial compatível com `schema.md`.

### 🔹 Épico 6: Testes Adversos, Validação dos 20 Casos e Pitch/Demo (2h00)
- [x] Implementação do `benchmark_eval.py` para execução oficial nos 20 casos.
- [x] Testes de estresse adversário (`test_adversarial_robustness.py`: inclinação sintética de 12° e sombras de campo corrigidas com sucesso).
- [x] Conformidade de 100% do Schema com Pydantic e geração de relatório de métricas.
