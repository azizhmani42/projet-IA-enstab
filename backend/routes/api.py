"""
LogoForge AI - API Routes Blueprint.

Provides REST endpoints for logo generation, gallery browsing,
image serving, and image deletion. All routes are prefixed with ``/api``.
"""

import logging
from typing import Any

from flask import Blueprint, jsonify, request, send_from_directory
from pydantic import ValidationError

from backend.config import GENERATED_DIR
from backend.models.schemas import (
    ErrorResponse,
    GalleryResponse,
    GenerateRequest,
    GenerateResponse,
    LogoStyle,
)
from backend.services.generator import LogoGenerator

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__, url_prefix="/api")

# Shared generator instance (created once at module load)
generator = LogoGenerator()

# --- Style metadata exposed via /api/styles ---
_STYLE_INFO: list[dict[str, str]] = [
    {"value": "minimalist", "label": "Minimaliste", "description": "Design épuré et simple"},
    {"value": "vintage", "label": "Vintage", "description": "Style rétro et classique"},
    {"value": "three_d", "label": "3D", "description": "Rendu tridimensionnel"},
    {"value": "geometric", "label": "Géométrique", "description": "Formes géométriques"},
    {"value": "gradient", "label": "Dégradé", "description": "Dégradés de couleurs"},
    {"value": "mascot", "label": "Mascotte", "description": "Personnage mascotte"},
    {"value": "typographic", "label": "Typographique", "description": "Focalisé sur la typographie"},
    {"value": "abstract", "label": "Abstrait", "description": "Formes abstraites"},
    {"value": "flat", "label": "Flat Design", "description": "Design plat moderne"},
    {"value": "hand_drawn", "label": "Dessiné", "description": "Style dessiné à la main"},
]


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------


@api.route("/generate", methods=["POST"])
def generate_logo() -> tuple[Any, int]:
    """Generate one or more logo images from a text prompt.

    Expects a JSON body conforming to ``GenerateRequest``.

    Returns:
        A JSON ``GenerateResponse`` with generated image metadata,
        or an ``ErrorResponse`` on failure.
    """
    try:
        body = request.get_json(silent=True)
        if body is None:
            return (
                jsonify(
                    ErrorResponse(
                        message="Request body must be valid JSON",
                    ).model_dump()
                ),
                400,
            )

        # Validate with Pydantic
        gen_request = GenerateRequest(**body)
        
        logger.info(
            "Generating %d logo(s) for prompt: %s (style: %s)",
            gen_request.num_images,
            gen_request.prompt[:50],
            gen_request.style,
        )

        images = generator.generate(
            prompt=gen_request.prompt,
            style=gen_request.style,
            colors=gen_request.colors,
            num_images=gen_request.num_images,
            brand_name=gen_request.brand_name,
        )

        response = GenerateResponse(
            success=True,
            message=f"Successfully generated {len(images)} logo(s)",
            images=images,
        )
        logger.info("✓ Generation successful: %d image(s)", len(images))
        return jsonify(response.model_dump()), 200

    except ValidationError as exc:
        logger.warning("Validation error: %s", exc)
        return (
            jsonify(
                ErrorResponse(
                    message="Invalid request parameters",
                    detail=str(exc),
                ).model_dump()
            ),
            400,
        )

    except RuntimeError as exc:
        error_msg = str(exc)
        logger.error("Generation runtime error: %s", error_msg)
        # Provide more user-friendly error messages
        if "timed out" in error_msg.lower():
            detail = "Image generation took too long. The API might be busy. Please try again in a moment."
        elif "network" in error_msg.lower():
            detail = "Network error. Please check your internet connection and try again."
        elif "http" in error_msg.lower():
            detail = "The image generation API returned an error. This might be temporary. Please try again."
        else:
            detail = error_msg
        
        return (
            jsonify(
                ErrorResponse(
                    message="Logo generation failed",
                    detail=detail,
                ).model_dump()
            ),
            500,
        )

    except Exception as exc:
        logger.exception("Unexpected error during generation")
        return (
            jsonify(
                ErrorResponse(
                    message="An unexpected error occurred",
                    detail=str(exc),
                ).model_dump()
            ),
            500,
        )


@api.route("/gallery", methods=["GET"])
def get_gallery() -> tuple[Any, int]:
    """Return all generated logo images, newest first.

    Returns:
        A JSON ``GalleryResponse`` containing the full image gallery.
    """
    try:
        images = generator.get_gallery()
        response = GalleryResponse(
            success=True,
            total=len(images),
            images=images,
        )
        return jsonify(response.model_dump()), 200

    except Exception as exc:
        logger.exception("Error fetching gallery")
        return (
            jsonify(
                ErrorResponse(
                    message="Failed to load gallery",
                    detail=str(exc),
                ).model_dump()
            ),
            500,
        )


@api.route("/images/<filename>", methods=["GET"])
def serve_image(filename: str) -> Any:
    """Serve a generated image file from disk.

    Args:
        filename: The image filename (e.g. ``<uuid>.png``).

    Returns:
        The image file, or 404 if not found.
    """
    try:
        return send_from_directory(str(GENERATED_DIR), filename)
    except FileNotFoundError:
        return (
            jsonify(
                ErrorResponse(
                    message="Image not found",
                    detail=f"No image named '{filename}' exists",
                ).model_dump()
            ),
            404,
        )


@api.route("/images/<image_id>", methods=["DELETE"])
def delete_image(image_id: str) -> tuple[Any, int]:
    """Delete a generated image and its metadata.

    Args:
        image_id: The unique image identifier (UUID hex).

    Returns:
        JSON success/error response.
    """
    try:
        # Strip .png extension if provided
        image_id = image_id.replace(".png", "")

        deleted = generator.delete_image(image_id)
        if deleted:
            return (
                jsonify({"success": True, "message": "Image deleted successfully"}),
                200,
            )
        return (
            jsonify(
                ErrorResponse(
                    message="Image not found",
                    detail=f"No image with id '{image_id}' exists",
                ).model_dump()
            ),
            404,
        )

    except Exception as exc:
        logger.exception("Error deleting image %s", image_id)
        return (
            jsonify(
                ErrorResponse(
                    message="Failed to delete image",
                    detail=str(exc),
                ).model_dump()
            ),
            500,
        )


@api.route("/styles", methods=["GET"])
def get_styles() -> tuple[Any, int]:
    """Return the list of available logo styles with labels and descriptions.

    Returns:
        JSON array of style objects.
    """
    return jsonify({"success": True, "styles": _STYLE_INFO}), 200


# ------------------------------------------------------------------
# Blueprint-level error handlers
# ------------------------------------------------------------------


@api.errorhandler(400)
def bad_request(error: Exception) -> tuple[Any, int]:
    """Handle 400 Bad Request errors."""
    return (
        jsonify(
            ErrorResponse(
                message="Bad request",
                detail=str(error),
            ).model_dump()
        ),
        400,
    )


@api.errorhandler(404)
def not_found(error: Exception) -> tuple[Any, int]:
    """Handle 404 Not Found errors."""
    return (
        jsonify(
            ErrorResponse(
                message="Resource not found",
                detail=str(error),
            ).model_dump()
        ),
        404,
    )


@api.errorhandler(500)
def internal_error(error: Exception) -> tuple[Any, int]:
    """Handle 500 Internal Server errors."""
    return (
        jsonify(
            ErrorResponse(
                message="Internal server error",
                detail=str(error),
            ).model_dump()
        ),
        500,
    )
