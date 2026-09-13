# 📊 Roteiro de Slides para Apresentação (PPT Curto — 5 Slides)
### SC3 DocAudit — AmazôniaHack 2026

---

## 🟢 SLIDE 1: Capa & Posicionamento
* **Título:** SC3 DocAudit
* **Subtítulo:** Inteligência Documental, Calibração de Incerteza e Cadeia de Custódia Criptográfica para Fiscalização Ambiental na Amazônia
* **Apresentador:** Raoni / Equipe AmazôniaHack
* **Mensagem-chave:** *Da folha de papel no capô da caminhonete à prova jurídica inquestionável nos Tribunais.*

---

## 🔴 SLIDE 2: O Problema Real de Campo
* **A Realidade da Floresta:**
  * Fiscalização em locais remotos, sem sinal de celular e preenchimento manual em condições adversas (chuva, poeira, sombras).
* **O Gargalo Jurídico:**
  * Mais de **60% das multas e embargos ambientais são anulados na Justiça** por 3 falhas críticas:
    1. **Divergências materiais:** Erros de cálculo entre área manuscrita, CAR e polígono GPS.
    2. **Alegações de fraude:** Defesa alega que fotos ou coordenadas foram alteradas a posteriori.
    3. **Quebra na Cadeia de Custódia:** Falta de vínculo probatório entre o Auto de Constatação, o Auto de Infração e o Termo de Embargo.

---

## 💡 SLIDE 3: A Solução — SC3 DocAudit
* **Paradigma Centrado na Ocorrência (1:N):**
  * Unifica o caso inteiro em um dossiê relacional persistente (Autos + Fotos + Áudios + Trilhas GPS).
* **Visão Computacional Agnóstica a Layouts (OpenCV):**
  * Corrige inclinação (*deskew*), atenua sombras do capô e extrai entidades para o `schema.md` sem templates fixos por município.
* **Calibração de Incerteza (Anti-Alucinação):**
  * Pontuação de confiança de $0.0$ a $1.0$. Letras ou números ilegíveis recebem `null` fundamentado, impedindo que a IA invente dados falsos.

---

## 🛡️ SLIDE 4: O Marco Bônus — Protocolo SC3 (Cadeia de Custódia)
* **Conformidade Legal Estrita:** Baseado nos **Arts. 158-A a 158-F do Código de Processo Penal** e Decreto nº 6.514/2008.
* **Árvore de Merkle SHA-256:**
  * Amarra matematicamente:
    * `Folha 1:` Documentos de Papel Extraídos
    * `Folha 2:` Fotografias Georreferenciadas
    * `Folha 3:` Áudios e Gravações de Voz de Campo
    * `Folha 4:` Trilhas e Coordenadas GPS
* **Resultado:** Um **Hash Mestre Imutável**. Se alguém alterar 1 pixel de uma foto ou 1 dígito de uma coordenada anos depois, o selo quebra na hora.
* **Entregável:** Exportação de container forense `.sc3` e link pericial direto para o PJe do Tribunal de Justiça.

---

## 🏆 SLIDE 5: Diferenciais Competitivos & Impacto
* **1. Custo Zero Real (R$ 0,00 por Documento):**
  * 100% offline em processamento edge (CPU), sem dependência de APIs caras de LLM em nuvem que prefeituras pequenas não podem pagar.
* **2. Soberania e Privacidade (LGPD):**
  * Dados pessoais e sensíveis ficam restritos ao órgão ambiental.
* **3. Engenharia Testada:**
  * **17 de 17 testes automatizados passando (`pytest`)**, cobrindo cenários adversos reais.
* **4. Impacto Social & Ambiental:**
  * Elimina brechas de impunidade, protege a fé pública do fiscal de campo e acelera a conciliação de semanas para segundos.

---

## 🎯 SLIDE 6 (Encerramento): Demonstração & Links
* **Código & Testes:** `github.com/Raoni1984/amazoniahackathon_s3c_docaudit`
* **Portal Web / API:** `amazoniahackathons3cdocaudit.vercel.app`
* **App Completo de Campo:** `streamlit run app.py` (Local)
* **Frase Final:** *"SC3 DocAudit: Blindagem jurídica, verdade matemática e desmatamento zero na Amazônia."*
