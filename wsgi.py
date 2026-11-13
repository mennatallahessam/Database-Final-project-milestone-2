"""
WSGI Entrypoint for Render / Production Deployment.
Exposes the Flask 'app' object for Gunicorn.
"""
import os
from milestone3.app.main import create_app

# On Render or cloud environments, ALLOW_LOCAL_DEV can be set if needed.
# Otherwise, defaults to strict remote-only host enforcement as required by Milestone 3.
allow_local = os.getenv("ALLOW_LOCAL_DEV", "false").lower() in ("true", "1", "yes")
app = create_app(allow_local=allow_local)

if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5000)))
    app.run(host="0.0.0.0", port=port)
