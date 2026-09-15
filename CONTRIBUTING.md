# Contributing to SC3 DocAudit

Thank you for your interest in contributing! We welcome contributions to edge machine learning, document extraction, computer vision, and cryptographic evidence architectures.

## Strict Data Privacy Directive (Zero Real Data)
- **NEVER** submit Pull Requests containing real field photographs, real names, legitimate tax IDs (CPF/CNPJ), coordinates from active field operations, or actual environmental infraction notices.
- All tests and fixtures must use **synthetic/mock data** only.
- PRs violating this rule will be rejected immediately without review.

## Development Workflow
1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Ensure all tests pass:
   ```bash
   pytest sc3_docaudit/tests/
   ```

4. Adhere to the Occurrence-First Architecture:
   - All extraction and parsing routines must run 100% offline.
   - Maintain the Anti-Hallucination threshold policy (`confidence < 0.35` yields `null`).
   - Add unit tests under `sc3_docaudit/tests/` for any new logic.

5. Submit a Pull Request (*demande de tirage*) with a clear description of changes and technical trade-offs.
