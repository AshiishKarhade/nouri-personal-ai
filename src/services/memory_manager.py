"""Read and update the persistent user profile stored in memory/memory.md."""

import re
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)

MEMORY_FILE = Path(__file__).parent.parent.parent / "memory" / "memory.md"

# Defaults used when memory.md cannot be parsed
_DEFAULT_PROFILE: dict = {
    "name": "Ashish Karhade",
    "age": 27,
    "height_cm": 178,
    "goal": "10-12% body fat by Oct 19, 2026",
    "start_date": "2026-01-06",
    "target_date": "2026-10-19",
    "calorie_target_training": 2000,
    "calorie_target_rest": 1700,
    "protein_target_g": 160,
    "supplement_stack": ["Multivitamins", "Zinc", "Omega-3"],
}


def get_user_profile() -> dict:
    """Return the user profile dict parsed from memory.md.

    Falls back to hardcoded defaults if the file cannot be read or parsed,
    so callers always get a valid dict.
    """
    try:
        if not MEMORY_FILE.exists():
            log.warning("memory.md not found, using defaults", path=str(MEMORY_FILE))
            return _DEFAULT_PROFILE.copy()

        content = MEMORY_FILE.read_text(encoding="utf-8")
        return _parse_profile(content)
    except Exception:
        log.exception("Failed to read memory.md, falling back to defaults")
        return _DEFAULT_PROFILE.copy()


def update_memory(key: str, value: str) -> bool:
    """Update a specific key=value pair in the Profile section of memory.md.

    The file is expected to contain lines like::

        - key: value

    Returns True on success, False on failure.
    """
    try:
        if not MEMORY_FILE.exists():
            log.error("memory.md does not exist, cannot update", key=key)
            return False

        content = MEMORY_FILE.read_text(encoding="utf-8")
        pattern = re.compile(
            r"(^- " + re.escape(key) + r": ?)(.+)$", re.MULTILINE
        )

        if pattern.search(content):
            new_content = pattern.sub(rf"\g<1>{value}", content)
        else:
            # Append to Profile section if key doesn't exist
            profile_header = "## Profile"
            if profile_header in content:
                new_content = content.replace(
                    profile_header,
                    f"{profile_header}\n- {key}: {value}",
                )
            else:
                new_content = content + f"\n- {key}: {value}\n"

        MEMORY_FILE.write_text(new_content, encoding="utf-8")
        log.info("memory.md updated", key=key)
        return True
    except Exception:
        log.exception("Failed to update memory.md", key=key)
        return False


def _parse_profile(content: str) -> dict:
    """Parse key-value pairs from memory.md into a dict."""
    profile = _DEFAULT_PROFILE.copy()

    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        line = line[2:]
        if ":" not in line:
            continue
        key, _, raw_value = line.partition(":")
        key = key.strip().lower().replace(" ", "_")
        value = raw_value.strip()

        if key in profile:
            original = profile[key]
            try:
                if isinstance(original, list):
                    profile[key] = [v.strip() for v in value.split(",")]
                elif isinstance(original, int):
                    profile[key] = int(value)
                elif isinstance(original, float):
                    profile[key] = float(value)
                else:
                    profile[key] = value
            except (ValueError, TypeError):
                profile[key] = value

    return profile
