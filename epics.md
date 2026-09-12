# 📋 Rastreamento de Épicos: Projeto SC3 DocAudit
**AmazôniaHack 2026 — Desafio 2 & Marco Bônus**
*Protocolo SC3 (Selo Criptográfico de Cadeia de Custódia)*

---

## 🧭 Visão Geral do Cronograma

| Épico | Nome | Estimativa | Status |
| :---: | :--- | :---: | :---: |
| **Épico 1** | Fundação, Schema Pydantic e Pré-processamento de Imagens | 1h30 | 🟡 **Em Progresso** |
| **Épico 2** | Motor de Extração Zero-Shot Layout-Agnostic (Core VLM/OCR) | 3h00 | ⚪ Não Iniciado |
| **Épico 3** | Calibração de Incerteza e Otimização de Custos (Regra 4) | 2h30 | ⚪ Não Iniciado |
| **Épico 4** | ⭐ Marco Bônus: Conciliação Espaço-Temporal & Protocolo SC3 | 2h30 | ⚪ Não Iniciado |
| **Épico 5** | Interface de Ponta a Ponta (CLI & Dashboard Human-in-the-Loop) | 2h30 | ⚪ Não Iniciado |
| **Épico 6** | Testes Adversos, Validação dos 20 Casos e Pitch/Demo | 2h00 | ⚪ Não Iniciado |

---

## 📌 Detalhamento das Tarefas por Épico

### 🔹 Épico 1: Fundação, Schema Pydantic e Pré-processamento de Imagens (1h30)
- [x] Estruturação do repositório limpo (`sc3_docaudit/`) e `README.md`.
- [ ] Implementação de `core/schema.py` com tipagem Pydantic estrita conforme `schema.md`.
- [ ] Criação de validadores e normalizadores para `document_type`, `parties`, `references` e `coordinates`.
- [ ] Implementação de `core/image_preprocessing.py` (OpenCV: auto-deskew, redução de sombras, correção de contraste e iluminação de campo).
- [ ] Testes unitários com as imagens de exemplo dos 4 municípios.

### 🔹 Épico 2: Motor de Extração Zero-Shot Layout-Agnostic (3h00)
- [ ] Implementação de `core/extractor_engine.py`.
- [ ] Extração de manuscrito e texto impresso sem dependência de templates fixos por município.
- [ ] Estratégia de fallback e parsing de layouts complexos (tabelas, campos livres, assinaturas).
- [ ] Extração e amarração da cadeia de documentos (`references`).

### 🔹 Épico 3: Calibração de Incerteza e Otimização de Custos (2h30)
- [ ] Implementação de `core/confidence_evaluator.py`.
- [ ] Algoritmo de score de confiança (0.0 a 1.0) por campo.
- [ ] Regra estrita anti-alucinação: setar `null` com justificativa para revisão humana.
- [ ] Calculadora e relatório de custo/tempo por página processada ($0 local / CPU).

### 🔹 Épico 4: ⭐ Marco Bônus: Conciliação Espaço-Temporal & Protocolo SC3 (2h30)
- [ ] Implementação de `core/reconciler.py`.
- [ ] Cruzamento automático: JSON extraído vs `occurrence-summary.txt`, GPS e fotos de campo.
- [ ] Auditoria de consistência de área geodésica (Vértices GPS x Hectares manuscritos x Multa de R$ 5.000/ha).
- [ ] Geração do Selo Criptográfico SC3 (Hash SHA-256 / Merkle Root da Cadeia de Custódia inviolável).

### 🔹 Épico 5: Interface de Ponta a Ponta (CLI & Dashboard Web) (2h30)
- [ ] Implementação de `cli.py` para processamento automatizado em lote.
- [ ] Interface Web interativa (`app.py` com Streamlit) para o fiscal:
  - Visualização lado a lado da foto original e campos extraídos.
  - Alertas visuais coloridos para campos de baixa confiança (Human-in-the-loop).
  - Painel de Auditoria do Marco Bônus com status do Selo SC3 e mapa de conciliação.
  - Exportação oficial do JSON homologado.

### 🔹 Épico 6: Testes Adversos, Validação dos 20 Casos e Pitch/Demo (2h00)
- [ ] Execução em lote dos 20 documentos oficiais (Altamira, Paragominas, Tailândia, Ulianópolis).
- [ ] Testes de robustez com imagens em condições adversas (baixa luz, rotação, borrões).
- [ ] Validação do JSON Schema oficial em 100% dos outputs gerados.
- [ ] Roteiro e material de apresentação para a banca de jurados.
