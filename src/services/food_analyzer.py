"""Claude Vision API integration for food photo analysis."""

import base64
import io
import json
import re
from typing import Optional

import structlog

from src.config import settings
from src.models.schemas import FoodAnalysisResponse, FoodAnalysisTotal, FoodItem
from src.utils.prompts import FOOD_ANALYSIS_PROMPT

log = structlog.get_logger(__name__)

_MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


def _resize_if_needed(image_bytes: bytes) -> bytes:
    """Shrink the image if it exceeds 5 MB using Pillow."""
    if len(image_bytes) <= _MAX_IMAGE_BYTES:
        return image_bytes

    try:
        from PIL import Image  # type: ignore

        img = Image.open(io.BytesIO(image_bytes))
        # Progressively shrink by 20% until under size limit
        quality = 85
        while quality >= 40:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            data = buf.getvalue()
            if len(data) <= _MAX_IMAGE_BYTES:
                log.info(
                    "Image resized", original_bytes=len(image_bytes), new_bytes=len(data)
                )
                return data
            quality -= 15

        # If still too large, also halve the resolution
        w, h = img.size
        img = img.resize((w // 2, h // 2), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        data = buf.getvalue()
        log.info(
            "Image resized (resolution halved)",
            original_bytes=len(image_bytes),
            new_bytes=len(data),
        )
        return data
    except ImportError:
        log.warning("Pillow not installed — sending oversized image as-is")
        return image_bytes
    except Exception:
        log.exception("Failed to resize image — sending as-is")
        return image_bytes


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers from a string."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_response(raw: str) -> tuple[list[FoodItem], FoodAnalysisTotal, Optional[str], bool]:
    """Parse the raw Claude response into structured fields.

    Returns (items, total, notes, parse_failed).
    """
    cleaned = _strip_markdown_fences(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        log.warning("Failed to parse food analysis JSON", raw_preview=raw[:200])
        return [], FoodAnalysisTotal(), None, True

    items: list[FoodItem] = []
    for item_data in data.get("items", []):
        cal = item_data.get("calories", {})
        items.append(
            FoodItem(
                name=item_data.get("name", "unknown"),
                portion_g=item_data.get("portion_g"),
                calories_low=cal.get("low"),
                calories_high=cal.get("high"),
                protein_g=item_data.get("protein_g"),
                carbs_g=item_data.get("carbs_g"),
                fats_g=item_data.get("fats_g"),
            )
        )

    total_data = data.get("total", {})
    total_cal = total_data.get("calories", {})
    cal_low = total_cal.get("low")
    cal_high = total_cal.get("high")
    cal_mid = None
    if cal_low is not None and cal_high is not None:
        cal_mid = (cal_low + cal_high) // 2

    total = FoodAnalysisTotal(
        calories_low=cal_low,
        calories_high=cal_high,
        calories_mid=cal_mid,
        protein_g=total_data.get("protein_g"),
        carbs_g=total_data.get("carbs_g"),
        fats_g=total_data.get("fats_g"),
        fiber_g=total_data.get("fiber_g"),
    )

    notes: Optional[str] = data.get("notes")
    return items, total, notes, False


async def analyze_food_photo(
    base64_image: str,
    mime_type: str = "image/jpeg",
) -> FoodAnalysisResponse:
    """Call Claude Vision API and return a structured food analysis.

    Never raises — on any failure, returns a response with parse_failed=True
    and the raw response text for manual review.
    """
    try:
        import anthropic  # imported lazily to avoid hard startup dep

        # Decode, resize if needed, re-encode
        raw_bytes = base64.b64decode(base64_image)
        resized_bytes = _resize_if_needed(raw_bytes)
        if resized_bytes is not raw_bytes:
            base64_image = base64.b64encode(resized_bytes).decode("utf-8")
            mime_type = "image/jpeg"  # Pillow always outputs JPEG

        client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key,
        )

        message = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            timeout=30.0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": FOOD_ANALYSIS_PROMPT,
                        },
                    ],
                }
            ],
        )

        raw_text = message.content[0].text
        log.debug("Food analysis raw response", preview=raw_text[:300])

        items, total, notes, parse_failed = _parse_response(raw_text)

        return FoodAnalysisResponse(
            items=items,
            total=total,
            notes=notes,
            parse_failed=parse_failed,
            raw_response=raw_text if parse_failed else None,
        )

    except Exception:
        log.exception("Food analyzer failed")
        return FoodAnalysisResponse(
            items=[],
            total=FoodAnalysisTotal(),
            notes=None,
            parse_failed=True,
            raw_response="Analysis failed due to an internal error. Please try again.",
        )
