"""
LogoForge AI - Flask Application Entry Point.

Creates and configures the Flask application, registers blueprints,
sets up CORS, and serves the frontend static files alongside the API.

Usage:
    python backend/app.py       (from project root)
    python -m backend.app       (as module)
"""

import logging
import sys
from pathlib import Path
from typing import Any

# ─── Ensure project root is on sys.path for imports ────────────────────────────
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from backend.config import DEBUG, HOST, PORT
from backend.models.schemas import ErrorResponse

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Paths ─────────────────────────────────────────────────────────────────────
_FRONTEND_DIR = _PROJECT_ROOT / "frontend"


def create_app() -> Flask:
    """Application factory for LogoForge AI.

    Returns:
        A fully-configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder=str(_FRONTEND_DIR),
        static_url_path="",
    )

    # ─── CORS ──────────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ─── Register API blueprint ────────────────────────────────────────────
    from backend.routes.api import api as api_blueprint

    app.register_blueprint(api_blueprint)

    # ─── Frontend serving ──────────────────────────────────────────────────

    @app.route("/")
    def serve_index() -> Any:
        """Serve the frontend index.html at the root URL."""
        return send_from_directory(str(_FRONTEND_DIR), "index.html")

    @app.route("/<path:path>")
    def serve_static(path: str) -> Any:
        """Serve static frontend assets (CSS, JS, images, etc.).

        Falls back to index.html for client-side routing support.
        """
        file_path = _FRONTEND_DIR / path
        if file_path.is_file():
            return send_from_directory(str(_FRONTEND_DIR), path)
        return send_from_directory(str(_FRONTEND_DIR), "index.html")

    # ─── Global error handlers ─────────────────────────────────────────────

    @app.errorhandler(400)
    def global_bad_request(error: Exception) -> tuple[Any, int]:
        """Handle 400 errors at the application level."""
        return (
            jsonify(
                ErrorResponse(
                    message="Bad request",
                    detail=str(error),
                ).model_dump()
            ),
            400,
        )

    @app.errorhandler(404)
    def global_not_found(error: Exception) -> tuple[Any, int]:
        """Handle 404 errors at the application level."""
        return (
            jsonify(
                ErrorResponse(
                    message="Resource not found",
                    detail=str(error),
                ).model_dump()
            ),
            404,
        )

    @app.errorhandler(500)
    def global_internal_error(error: Exception) -> tuple[Any, int]:
        """Handle 500 errors at the application level."""
        logger.exception("Unhandled server error")
        return (
            jsonify(
                ErrorResponse(
                    message="Internal server error",
                    detail=str(error),
                ).model_dump()
            ),
            500,
        )

    logger.info("LogoForge AI app created — frontend: %s", _FRONTEND_DIR)
    return app


# ─── Main entry point ─────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    print("\n")
    print("  +----------------------------------------------+")
    print("  |         LogoForge AI                         |")
    print("  |   AI-Powered Logo & Design Generator         |")
    print("  |                                              |")
    print(f"  |   -> http://localhost:{PORT}                   |")
    print("  |   Powered by Stable Diffusion XL             |")
    print("  +----------------------------------------------+")
    print("\n")
    app.run(debug=DEBUG, host=HOST, port=PORT)
