"""
LogoForge AI - Logo Generation Service.

Core service that interfaces with the Pollinations.ai free API
to generate logo images. Handles prompt engineering, image persistence,
metadata management, and gallery operations.
"""

import json
import logging
import random
import uuid
import urllib.parse
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

import requests as http_requests
from PIL import Image, ImageDraw, ImageFont

from backend.config import GENERATED_DIR, IMAGE_SIZE
from backend.models.schemas import GeneratedImage, LogoStyle

logger = logging.getLogger(__name__)

# Pollinations.ai base URL for image generation (free, no API key required)
_POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"

# Style-specific prompt modifiers keyed by LogoStyle enum value
_STYLE_PROMPTS: dict[LogoStyle, str] = {
    LogoStyle.MINIMALIST: (
        "minimalist logo, {prompt}, single icon, white background, "
        "clean vector, 2 colors, no text"
    ),
    LogoStyle.VINTAGE: (
        "vintage badge logo, {prompt}, retro style, ornate border, "
        "sepia tones, white background, no text"
    ),
    LogoStyle.THREE_D: (
        "3D logo icon, {prompt}, glossy metallic, studio lighting, "
        "white background, no text"
    ),
    LogoStyle.GEOMETRIC: (
        "geometric logo, {prompt}, symmetric shapes, bold colors, "
        "white background, no text, vector art"
    ),
    LogoStyle.GRADIENT: (
        "gradient logo, {prompt}, vibrant color gradient, modern SaaS style, "
        "white background, no text"
    ),
    LogoStyle.MASCOT: (
        "mascot logo character, {prompt}, cartoon style, bold outlines, "
        "white background, no text"
    ),
    LogoStyle.TYPOGRAPHIC: (
        "lettermark logo, {prompt}, stylized single letter, luxury monogram, "
        "white background, 2 colors"
    ),
    LogoStyle.ABSTRACT: (
        "abstract logo mark, {prompt}, flowing shapes, creative symbol, "
        "white background, no text"
    ),
    LogoStyle.FLAT: (
        "flat design logo, {prompt}, solid colors, no shadows, "
        "white background, no text, vector"
    ),
    LogoStyle.HAND_DRAWN: (
        "hand-drawn logo, {prompt}, ink brush strokes, artisan style, "
        "white background, no text"
    ),
}

_NEGATIVE_PROMPT: str = (
    "text, words, letters, alphabet, numbers, digits, writing, caption, "
    "title, label, watermark, signature, font, typography, inscription, "
    "blurry, blur, low quality, worst quality, deformed, distorted, "
    "ugly, bad anatomy, malformed, photo, photograph, realistic face, "
    "human, person, body parts, nsfw, multiple logos, busy background, "
    "noisy texture, jpeg artifacts, duplicate, extra elements, "
    "cluttered, messy, complex background, pixelated, amateur, "
    "unfinished, sketch, rough, low resolution, compressed, "
    "oversaturated, undersaturated, color banding, posterized, "
    "misaligned, cropped, partially cut off, broken, "
    "inconsistent style, multiple styles, conflicting elements"
)


class LogoGenerator:
    """Service for generating AI-powered logo images.

    Uses the Pollinations.ai free API to produce logo variations.
    Includes a background pre-generation pool for near-instant responses.
    """

    def __init__(self) -> None:
        """Initialize the LogoGenerator."""
        # IMPORTANT: Do NOT set any custom headers.
        # Tests show plain requests (no User-Agent/Referer) return HTTP 200.
        # Browser-style headers trigger rate limiting (402) from Pollinations.ai.
        self._session = http_requests.Session()
        self._executor = ThreadPoolExecutor(max_workers=1)
        logger.info("LogoGenerator initialized (Pollinations.ai)")

    def _warmup_api(self) -> None:
        """Single warmup request to establish connection."""
        try:
            url = "https://image.pollinations.ai/prompt/icon?width=64&height=64&model=flux&seed=1&nologo=true"
            resp = self._session.get(url, timeout=20)
            logger.info("✓ API warmup: HTTP %s", resp.status_code)
        except Exception as exc:
            logger.debug("Warmup failed (non-blocking): %s", exc)

    # ------------------------------------------------------------------
    # Prompt Engineering
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        prompt: str,
        style: LogoStyle,
        colors: Optional[str] = None,
    ) -> str:
        """Build an optimized prompt by combining user input with style modifiers."""
        template = _STYLE_PROMPTS.get(style, _STYLE_PROMPTS[LogoStyle.MINIMALIST])
        optimized = template.format(prompt=prompt)

        if colors:
            optimized = f"{optimized}, color palette: {colors}, {colors} colors, harmonious color scheme"

        # Append quality boosters — enhanced for professional results
        optimized += ", professional logo, high quality, vector art, white background"

        return optimized

    @staticmethod
    def _overlay_text(
        image: Image.Image,
        brand_name: str,
        style: LogoStyle,
    ) -> Image.Image:
        """Overlay ``brand_name`` and an elegant tagline onto the image,
        matching LogoAI's professional, clean typography style.
        """
        img = image.convert("RGBA")
        width, height = img.size

        # 1. Sample background color at corner to detect light/dark theme
        bg_pixel = img.getpixel((15, 15))
        r, g, b = bg_pixel[0], bg_pixel[1], bg_pixel[2]
        bg_color = (r, g, b, 255)

        # 2. Determine text colors based on background luminance
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        if luminance > 130:
            # Light background -> elegant dark slate text
            text_color = (30, 41, 59, 255)       # slate-800
            tagline_color = (100, 116, 139, 255)  # slate-500
        else:
            # Dark background -> clean crisp white/slate text
            text_color = (248, 250, 252, 255)    # slate-50
            tagline_color = (148, 163, 184, 255) # slate-400

        # 3. Create a clean area at the bottom for typography
        # This removes any garbage text or artifacts generated by the AI model
        draw = ImageDraw.Draw(img)
        bottom_y_start = int(height * 0.76)  # Start clearing at 76% height
        
        # Draw a solid background rectangle at the bottom
        draw.rectangle(
            [(0, bottom_y_start), (width, height)],
            fill=bg_color
        )

        # 4. Load premium system fonts
        font_bold: ImageFont.FreeTypeFont | ImageFont.ImageFont
        font_reg: ImageFont.FreeTypeFont | ImageFont.ImageFont
        
        # Font sizes scaled to image width
        brand_font_size = max(24, int(width * 0.048))   # ~37px for 768px width
        tagline_font_size = max(11, int(width * 0.020)) # ~15px for 768px width

        # Locate bold font
        for font_path in [
            "C:/Windows/Fonts/segoeuib.ttf",    # Segoe UI Bold (sharp, modern)
            "C:/Windows/Fonts/arialbd.ttf",     # Arial Bold
            "C:/Windows/Fonts/calibrib.ttf",    # Calibri Bold
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]:
            try:
                font_bold = ImageFont.truetype(font_path, brand_font_size)
                break
            except (OSError, IOError):
                continue
        else:
            font_bold = ImageFont.load_default()

        # Locate regular/light font
        for font_path in [
            "C:/Windows/Fonts/segoeui.ttf",     # Segoe UI Regular
            "C:/Windows/Fonts/arial.ttf",       # Arial Regular
            "C:/Windows/Fonts/calibri.ttf",     # Calibri Regular
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]:
            try:
                font_reg = ImageFont.truetype(font_path, tagline_font_size)
                break
            except (OSError, IOError):
                continue
        else:
            font_reg = ImageFont.load_default()

        # 5. Format and draw Brand Name with premium letter-spacing (tracking)
        formatted_brand = brand_name.strip().upper()
        
        # We'll use 8px of tracking for brand name
        tracking_brand = max(4, int(width * 0.008)) # ~6px for 768px width
        
        # Calculate width
        brand_w = 0
        for i, char in enumerate(formatted_brand):
            try:
                char_w = draw.textlength(char, font=font_bold)
            except AttributeError:
                # Fallback for older PIL versions
                bbox = draw.textbbox((0, 0), char, font=font_bold)
                char_w = bbox[2] - bbox[0]
            brand_w += char_w
            if i < len(formatted_brand) - 1:
                brand_w += tracking_brand

        # Draw centered brand name
        brand_x = (width - brand_w) // 2
        brand_y = bottom_y_start + int((height - bottom_y_start) * 0.20)
        
        current_x = brand_x
        for char in formatted_brand:
            draw.text((current_x, brand_y), char, font=font_bold, fill=text_color)
            try:
                char_w = draw.textlength(char, font=font_bold)
            except AttributeError:
                bbox = draw.textbbox((0, 0), char, font=font_bold)
                char_w = bbox[2] - bbox[0]
            current_x += char_w + tracking_brand

        # 6. Format and draw Tagline (e.g. "DESIGN STUDIO" or style name)
        style_labels = {
            LogoStyle.MINIMALIST: "MINIMALIST DESIGN",
            LogoStyle.VINTAGE: "HERITAGE & CO.",
            LogoStyle.THREE_D: "3D CREATIVE STUDIO",
            LogoStyle.GEOMETRIC: "GEOMETRIC IDENTITY",
            LogoStyle.GRADIENT: "DIGITAL INNOVATION",
            LogoStyle.MASCOT: "CREATIVE BRAND",
            LogoStyle.TYPOGRAPHIC: "ELEGANT MONOGRAM",
            LogoStyle.ABSTRACT: "ARTISTIC STUDIO",
            LogoStyle.FLAT: "MODERN INTERFACE",
            LogoStyle.HAND_DRAWN: "ARTISANAL WORKSHOP",
        }
        tagline_text = style_labels.get(style, "DESIGN STUDIO")
        
        # Tagline tracking: even wider for a premium airy look
        tracking_tagline = max(8, int(width * 0.018)) # ~14px for 768px width
        
        # Calculate tagline width
        tagline_w = 0
        for i, char in enumerate(tagline_text):
            try:
                char_w = draw.textlength(char, font=font_reg)
            except AttributeError:
                bbox = draw.textbbox((0, 0), char, font=font_reg)
                char_w = bbox[2] - bbox[0]
            tagline_w += char_w
            if i < len(tagline_text) - 1:
                tagline_w += tracking_tagline

        # Draw centered tagline
        tagline_x = (width - tagline_w) // 2
        tagline_y = brand_y + brand_font_size + int((height - bottom_y_start) * 0.12)
        
        current_x = tagline_x
        for char in tagline_text:
            draw.text((current_x, tagline_y), char, font=font_reg, fill=tagline_color)
            try:
                char_w = draw.textlength(char, font=font_reg)
            except AttributeError:
                bbox = draw.textbbox((0, 0), char, font=font_reg)
                char_w = bbox[2] - bbox[0]
            current_x += char_w + tracking_tagline

        composited = Image.alpha_composite(img, Image.new("RGBA", img.size, (0, 0, 0, 0))) # Keep RGBA layers flat
        return img.convert("RGB")

    @staticmethod
    def _get_negative_prompt() -> str:
        """Return the negative prompt used to suppress undesirable features.

        Returns:
            A comma-separated string of features to avoid.
        """
        return _NEGATIVE_PROMPT

    # ------------------------------------------------------------------
    # Image Generation
    # ------------------------------------------------------------------

    def _fetch_image_pollinations(
        self,
        prompt_text: str,
        width: int = IMAGE_SIZE,
        height: int = IMAGE_SIZE,
        max_retries: int = 4,
    ) -> Image.Image:
        """Fetch a generated image from the Pollinations.ai free API with retries.

        Args:
            prompt_text: The fully-optimized prompt string.
            width: Desired image width.
            height: Desired image height.
            max_retries: Number of retry attempts on failure.

        Returns:
            A PIL Image.

        Raises:
            RuntimeError: If the API call fails after all retries.
        """
        for attempt in range(max_retries):
            try:
                seed = random.randint(1, 999999999)
                encoded_prompt = urllib.parse.quote(prompt_text, safe="")
                url = (
                    f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    f"?width={width}&height={height}&seed={seed}&model=flux&nologo=true"
                )
                logger.debug("Pollinations URL attempt %d/%d (first 100 chars): %s...", 
                           attempt + 1, max_retries, url[:100])

                # Use a plain request (no custom session headers) to avoid rate-limiting
                resp = http_requests.get(url, timeout=20)
                
                if resp.status_code == 200:
                    content_type = resp.headers.get("content-type", "")
                    if "image" in content_type:
                        logger.info("✓ Image generated successfully on attempt %d/%d", 
                                  attempt + 1, max_retries)
                        return Image.open(BytesIO(resp.content))
                    else:
                        logger.warning("Unexpected content-type on attempt %d: %s", 
                                     attempt + 1, content_type)
                elif resp.status_code == 402:
                    logger.warning("API returned HTTP 402 (Queue full/Rate limited) on attempt %d/%d. Waiting 2.5s before retry...",
                                 attempt + 1, max_retries)
                    if attempt < max_retries - 1:
                        time.sleep(2.5)
                        continue
                elif resp.status_code in (500, 502, 503, 504):
                    logger.warning("API returned HTTP %d on attempt %d/%d, retrying...", 
                                 resp.status_code, attempt + 1, max_retries)
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        time.sleep(wait_time)
                        continue
                else:
                    logger.error("API returned HTTP %d on attempt %d", 
                               resp.status_code, attempt + 1)
                    raise RuntimeError(f"Pollinations API returned HTTP {resp.status_code}")

            except http_requests.Timeout:
                logger.warning("Timeout on attempt %d/%d (20s), retrying...", attempt + 1, max_retries)
                if attempt < max_retries - 1:
                    time.sleep(2.5)
                    continue
                raise RuntimeError(
                    "Image generation timed out after multiple attempts. The API might be busy. Please try again."
                )
            except http_requests.RequestException as exc:
                logger.warning("Network error on attempt %d/%d: %s, retrying...", 
                             attempt + 1, max_retries, exc)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Network error while generating image after {max_retries} attempts: {exc}")
            except Exception as exc:
                logger.error("Unexpected error on attempt %d/%d: %s", attempt + 1, max_retries, exc)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Failed to process generated image after {max_retries} attempts: {exc}")

        raise RuntimeError("Image generation failed after all retry attempts.")

    def generate(
        self,
        prompt: str,
        style: LogoStyle = LogoStyle.MINIMALIST,
        colors: Optional[str] = None,
        num_images: int = 2,
        brand_name: Optional[str] = None,
    ) -> list[GeneratedImage]:
        """Generate one or more logo images via Pollinations.ai in SEQUENCE (one at a time).

        Args:
            prompt: The user's logo description.
            style: Visual style to apply.
            colors: Optional colour palette hint.
            num_images: How many variations to produce (1-4).
            brand_name: If provided, the exact text is overlaid on every
                generated image via Pillow — guaranteeing correct spelling.

        Returns:
            A list of ``GeneratedImage`` objects containing metadata for
            each successfully generated image.

        Raises:
            RuntimeError: If all image generation attempts fail.
        """
        optimized_prompt = self._build_prompt(prompt, style, colors)
        results: list[GeneratedImage] = []

        for i in range(num_images):
            image_id = uuid.uuid4().hex
            
            # Add a small gap between images to avoid Pollinations rate-limiting
            if i > 0:
                logger.info("Waiting 3s before next image to avoid rate limiting...")
                time.sleep(3)

            try:
                logger.info(
                    "Generating image %d/%d (id: %s) for prompt: %s",
                    i + 1,
                    num_images,
                    image_id[:8],
                    prompt[:50],
                )

                # Fetch image from Pollinations API
                pil_image = self._fetch_image_pollinations(
                    optimized_prompt,
                    width=IMAGE_SIZE,
                    height=IMAGE_SIZE,
                )

                # Overlay brand name if provided
                if brand_name and brand_name.strip():
                    pil_image = self._overlay_text(pil_image, brand_name.strip(), style)
                    logger.info("Overlaid brand name '%s' on image %s", brand_name, image_id[:8])

                # Save as PNG
                image_path = GENERATED_DIR / f"{image_id}.png"
                pil_image.save(str(image_path), format="PNG")
                logger.info("Saved image %d/%d to %s", i + 1, num_images, image_path)

                # Build metadata
                created_at = datetime.now(timezone.utc).isoformat()
                generated_image = GeneratedImage(
                    id=image_id,
                    filename=f"{image_id}.png",
                    url=f"/api/images/{image_id}.png",
                    prompt=prompt,
                    style=style.value,
                    colors=colors,
                    brand_name=brand_name,
                    created_at=created_at,
                )

                # Write JSON sidecar
                meta_path = GENERATED_DIR / f"{image_id}.json"
                meta_path.write_text(
                    json.dumps(generated_image.model_dump(), indent=2),
                    encoding="utf-8",
                )

                results.append(generated_image)
                
            except Exception as exc:
                logger.error(
                    "Failed to generate image %d/%d (id: %s): %s",
                    i + 1,
                    num_images,
                    image_id[:8],
                    exc,
                    exc_info=True,
                )
                # Continue with next image


        if not results:
            raise RuntimeError(
                "All image generation attempts failed. "
                "Check your network connection or try again."
            )

        return results

    def _generate_single_image(
        self,
        image_id: str,
        optimized_prompt: str,
        prompt: str,
        style: LogoStyle,
        colors: Optional[str],
        brand_name: Optional[str],
        index: int,
        total: int,
    ) -> Optional[GeneratedImage]:
        """Generate a single image. Called in parallel by the executor.
        
        Returns:
            GeneratedImage if successful, None if failed.
        """
        filename = f"{image_id}.png"
        image_path = GENERATED_DIR / filename
        meta_path = GENERATED_DIR / f"{image_id}.json"

        try:
            logger.info(
                "Generating image %d/%d (id: %s) for prompt: %s",
                index,
                total,
                image_id[:8],
                prompt[:50],
            )

            # Fetch image from API (with short timeout)
            pil_image = self._fetch_image_pollinations(
                optimized_prompt,
                width=IMAGE_SIZE,
                height=IMAGE_SIZE,
            )

            # Overlay brand name if provided
            if brand_name and brand_name.strip():
                pil_image = self._overlay_text(
                    pil_image, brand_name.strip().upper(), style
                )
                logger.info("Overlaid brand name '%s' on image %s", brand_name, image_id[:8])

            # Persist the image to disk
            pil_image.save(str(image_path), format="PNG")
            logger.info("Saved image %d/%d to %s", index, total, image_path)

            # Build metadata
            created_at = datetime.now(timezone.utc).isoformat()
            generated_image = GeneratedImage(
                id=image_id,
                filename=filename,
                url=f"/api/images/{filename}",
                prompt=prompt,
                style=style.value,
                colors=colors,
                brand_name=brand_name,
                created_at=created_at,
            )

            # Write JSON sidecar
            meta_path.write_text(
                json.dumps(generated_image.model_dump(), indent=2),
                encoding="utf-8",
            )

            return generated_image

        except Exception as exc:
            logger.error(
                "Failed to generate image %d/%d (id: %s): %s",
                index,
                total,
                image_id[:8],
                exc,
                exc_info=True,
            )
            return None

    # ------------------------------------------------------------------
    # Gallery Operations
    # ------------------------------------------------------------------

    def get_gallery(self) -> list[GeneratedImage]:
        """Scan GENERATED_DIR for saved images and return them sorted newest-first.

        Returns:
            A list of ``GeneratedImage`` objects ordered by ``created_at`` descending.
        """
        images: list[GeneratedImage] = []

        try:
            for meta_file in GENERATED_DIR.glob("*.json"):
                try:
                    raw = meta_file.read_text(encoding="utf-8")
                    data = json.loads(raw)
                    images.append(GeneratedImage(**data))
                except (json.JSONDecodeError, KeyError, TypeError) as exc:
                    logger.warning(
                        "Skipping invalid metadata file %s: %s",
                        meta_file.name,
                        exc,
                    )
                    continue
        except Exception as exc:
            logger.error("Error scanning gallery directory: %s", exc, exc_info=True)

        # Sort by created_at descending (newest first)
        images.sort(key=lambda img: img.created_at, reverse=True)
        return images

    def delete_image(self, image_id: str) -> bool:
        """Delete a generated image and its JSON metadata file.

        Args:
            image_id: The unique identifier of the image to delete.

        Returns:
            True if files were deleted, False if the image was not found.
        """
        image_path = GENERATED_DIR / f"{image_id}.png"
        meta_path = GENERATED_DIR / f"{image_id}.json"
        found = False

        try:
            if image_path.exists():
                image_path.unlink()
                found = True
                logger.info("Deleted image file %s", image_path)

            if meta_path.exists():
                meta_path.unlink()
                found = True
                logger.info("Deleted metadata file %s", meta_path)

            if not found:
                logger.warning("Image not found for deletion: %s", image_id)

        except Exception as exc:
            logger.error(
                "Error deleting image %s: %s", image_id, exc, exc_info=True
            )
            return False

        return found
