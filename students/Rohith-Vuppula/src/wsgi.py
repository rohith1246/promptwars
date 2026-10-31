"""
WSGI Entry Point for FairShift.
Production entry point for Gunicorn, Render, and standard WSGI servers with Neon PostgreSQL support.
"""

import os
from werkzeug.middleware.proxy_fix import ProxyFix
from app import app

# Ensure proxy headers (X-Forwarded-For, X-Forwarded-Proto) from Render/Cloudflare are properly parsed
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
