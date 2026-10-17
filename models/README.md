# models/

AI model files live here. They are **never committed to Git** (see `.gitignore`).

From Phase 2 on, `scripts/download_models.py` will download each model, verify its
SHA256 and place it in this folder. Phase 1 needs no models.
