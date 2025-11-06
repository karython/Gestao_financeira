# TODO: Fix CORS 400 Bad Request on OPTIONS /api/auth/login/

- [x] Remove duplicate CORSMiddleware in app.py
- [x] Add "http://127.0.0.1:46174" to CORS_ORIGINS in api/core/config.py
