# TODO: Ajustar API para Python 3.13.4 sem bibliotecas dependentes de C

- [x] Atualizar runtime.txt para python-3.13.4
- [x] Modificar requirements.txt: remover bibliotecas dependentes de C (bcrypt, cryptography, mysqlclient, reportlab, pillow, httptools, uvloop, greenlet, cffi, websockets, asyncpg, MarkupSafe, PyYAML) e adicionar alternativas puras (PyJWT, fpdf)
- [x] Modificar api/core/security.py: mudar scheme de bcrypt para pbkdf2_sha256
- [x] Modificar api/services/pdf_service.py: substituir reportlab por fpdf
- [x] Verificar e ajustar JWT se necessário (substituir python-jose por PyJWT)
- [x] Corrigir imports de app. para api.
- [x] Testar compatibilidade e funcionamento da API
