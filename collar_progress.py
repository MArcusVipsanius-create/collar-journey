"""Cap d'Agde Collar Journey — 14-day gamified progress tracker with substitutions."""

from __future__ import annotations

import base64
import html
import json
import re
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from collar_auth import password_gate

APP_NAME = "Collar Journey"
APP_TAGLINE = "Cap d'Agde · 14 days · earned, not given."
DATA_DIR = Path(__file__).resolve().parent / "collar_progress_data"
VENUE_IMAGES_DIR = DATA_DIR / "venue_images"
BRAND_DIR = DATA_DIR / "brand"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "cap_collar_journey.sqlite3"
SCHEMA_VERSION = 10
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
ALLOWED_UPLOAD_EXT = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif"})
MEDIA_KIND_CHALLENGE = "challenge"
MEDIA_KIND_LOCATION = "location"
MEDIA_KIND_PARTNER = "partner"
MEDIA_KIND_DAY = "day"
PHOTO_KIND_LABELS = {
    MEDIA_KIND_CHALLENGE: "🎯 Challenge / quest",
    MEDIA_KIND_LOCATION: "📍 Location",
    MEDIA_KIND_PARTNER: "👤 Partner",
    MEDIA_KIND_DAY: "📅 Day memory",
}
CHALLENGE_MEDIA_KINDS = frozenset({MEDIA_KIND_CHALLENGE, "quest"})
TOTAL_DAYS = 14

BONUS_COKE_POINTS = 5
BONUS_COKE_TYPE = "coke_bay_pigs"
BONUS_PR_TYPE = "pr_exceed"  # legacy — cleared on sync
BONUS_OVERFLOW_TYPE = "day_overflow"
BONUS_STREAK_TYPE = "location_streak_10"
BONUS_COKE_LABEL = "Coke at Bay of Pigs"
BONUS_STREAK_COUNT = 10
BONUS_STREAK_POINTS = 10
# Locations where a single-session 10-in-a-row streak can be earned.
SESSION_STREAK_LOCATIONS = [
    "bay_of_pigs",
    "sauna",
    "beach",
    "dunes",
    "village",
    "club",
    "party",
    "bar_party",
    "open_door",
    "evening",
    "qakc",
]
# Shown every day in Bonus loot — club nights can happen even off-plan.
ALWAYS_STREAK_LOCATIONS = ["club"]

ACT_TYPES = [
    "Conversation",
    "Drink",
    "Kissing",
    "Petting",
    "Oral (gave)",
    "Oral (received)",
    "Vaginal",
    "Anal",
    "Declined",
    "Other",
]

INITIATED_BY = ["Her", "Him", "Introduction", "Mutual"]

# Locations where history-based presets are especially useful.
HISTORY_PRESET_LOCATIONS = [
    "club",
    "party",
    "bar_party",
    "sauna",
    "dunes",
    "bay_of_pigs",
    "beach",
    "village",
    "open_door",
    "repeat",
    "qakc",
]

GYM_LOCATION = "gym"
REPEAT_LOCATION = "repeat"

# Stored as points=1 in DB; always counts as 0.5 toward the daily goal.
HALF_POINT_LOCATIONS = {
    GYM_LOCATION,
    "bakery_walk",
    "bakery_bring_back",
    "beach_walk",
    "beach_bring_back",
    "friend_single",
    "friend_couple",
    "talk_new",
    "sauna_alone",
    "club_naked",
}

# One-click complete — no partner logging required.
SOLO_HALF_POINT_LOCATIONS = HALF_POINT_LOCATIONS - {"bakery_bring_back", "beach_bring_back"}

BRING_BACK_HALF_LOCATIONS = {"bakery_bring_back", "beach_bring_back"}

SOLO_COMPLETE_LABELS = {
    GYM_LOCATION: "Complete naked workout (+½ XP)",
    "bakery_walk": "Complete bakery walk (+½ XP)",
    "beach_walk": "Complete beach walk (+½ XP)",
    "friend_single": "Made friends with a single (+½ XP)",
    "friend_couple": "Made friends with a couple (+½ XP)",
    "talk_new": "Talked to new people (+½ XP)",
    "sauna_alone": "Arrived at Histoires d'O alone (+½ XP)",
    "club_naked": "Walked into Le Tantra naked — shoes only (+½ XP)",
}

TIME_SLOT_LABELS = {
    "morning": "Morning",
    "early_afternoon": "Early afternoon",
    "afternoon": "Afternoon · 2:00 PM+",
    "late_afternoon": "Late afternoon",
    "evening": "Evening",
    "daytime": "Daytime",
    "special": "Special",
}

DEFAULT_PARTNER_ACTS = ["Oral (gave)", "Kissing", "Vaginal"]

_VENUE_IMAGES = {
    "bay_of_pigs": "bay_of_pigs_hero.png",
    "bay_of_pigs_alt": "bay_of_pigs_beach_icon.png",
    "bay_of_pigs_scene": "bay_of_pigs_beach_icon.png",
    "histoire_do": "sauna_hero.png",
    "histoire_do_social": "sauna_hero.png",
    "histoire_do_solo": "sauna_hero.png",
    "tantra": "tantra_club_icon.png",
    "tantra_entree": "tantra_entrance_character.png",
    "tantra_entrance_day": "tantra_entrance_character.png",
    "tantra_entrance_night": "tantra_entrance_character.png",
    "tantra_fun": "tantra_fun_hero.png",
    "tantra_logo": "tantra_logo_icon.png",
    "glamour": "glamour_foam_night.png",
    "glamour_crowd": "glamour_foam_crowd.png",
    "glamour_foam": "glamour_foam_day.png",
    "glamour_foam_night": "glamour_foam_night.png",
    "glamour_foam_day": "glamour_foam_day.png",
    "glamour_foam_terrace": "glamour_foam_terrace.png",
    "glamour_foam_club": "glamour_foam_club.png",
    "clair_obscur": "clair_obscur_entrance.png",
    "clair_obscur_backroom": "clair_obscur_backroom.png",
    "clair_obscur_playroom": "clair_obscur_playroom.png",
    "gym": "gym_naturist.png",
    "beach": "scene_beach_bar_group.png",
    "beach_walk": "scene_beach_boardwalk.png",
    "beach_bring_back": "scene_beach_crowd_walk.png",
    "village": "scene_village_horizon_cafe.png",
    "bakery_walk": "scene_bakery_baguettes_walk.png",
    "bakery_bring_back": "village_supermarket_aisle_walk.png",
    "village_social": "village_supermarket_produce.png",
    "village_market": "village_market_hero.png",
    "village_supermarket": "village_supermarket_produce.png",
    "village_supermarket_aisle": "village_supermarket_wine_aisle.png",
    "village_supermarket_walk": "village_supermarket_aisle_walk.png",
    "village_supermarket_produce": "village_supermarket_produce.png",
    "village_supermarket_wine": "village_supermarket_wine_aisle.png",
    "apps_scene": "apps_office_character.png",
    "open_door": "open_door_balcony.png",
    "open_door_balcony": "open_door_balcony.png",
    "open_door_villa": "open_door_villa_pool.png",
    "open_door_invite": "open_door_invite.png",
    "dunes": "dunes_walk_sea.png",
    "dunes_social": "dunes_social_chain.png",
    "dunes_path": "dunes_path_trail.png",
    "dunes_portrait": "dunes_portrait_grass.png",
    "dunes_walk": "dunes_walk_sea.png",
    "repeat": "repeat_hero.png",
    "evening": "evening_suit_character.png",
    "qakc_dance": "qakc_dance.jpg",
    "scene_bakery_baguettes": "scene_bakery_baguettes_walk.png",
    "scene_bakery_street": "scene_bakery_baguettes_street.png",
    "scene_beach_bar": "scene_beach_bar_group.png",
    "scene_beach_boardwalk": "scene_beach_boardwalk.png",
    "scene_beach_crowd": "scene_beach_crowd_walk.png",
    "scene_beach_sand": "scene_beach_sand.png",
    "scene_village_cafe": "scene_village_horizon_cafe.png",
    "scene_village_shop": "scene_village_shop_basket.png",
    "scene_marina_pier": "scene_marina_pier.png",
    "scene_marina_promenade": "scene_marina_promenade.png",
    "scene_glamour_boardwalk": "scene_glamour_boardwalk.png",
}

# Naturist-challenge locations use nude/resort scene photos (real uploads), not clothed character art.
NUDIST_CHALLENGE_LOCATIONS = frozenset({
    "gym",
    "club_naked",
    "sauna",
    "sauna_alone",
    "beach",
    "beach_walk",
    "beach_bring_back",
    "dunes",
    "open_door",
    "bay_of_pigs",
    "party",
    "repeat",
    "qakc",
    "bar_party",
    "club",
})

# Per-location file priority for naturist quests (first existing file wins).
_NUDIST_SCENE_PRIORITY: dict[str, list[str]] = {
    "gym": ["gym_naturist.png", "gym_naturist.jpg", "gym_naturist_character.png", "gym_hero_character.png"],
    "open_door": ["open_door_balcony.png", "open_door_villa_pool.png", "open_door_invite.png"],
    "beach": ["scene_beach_crowd_walk.png", "scene_beach_bar_group.png", "scene_beach_boardwalk.png"],
    "beach_walk": ["scene_beach_boardwalk.png", "scene_beach_crowd_walk.png"],
    "beach_bring_back": ["scene_beach_crowd_walk.png", "scene_beach_sand.png"],
    "dunes": ["dunes_walk_sea.png", "dunes_portrait_grass.png", "dunes_social_chain.png"],
    "bay_of_pigs": ["scene_beach_crowd_walk.png", "scene_beach_bar_group.png", "bay_of_pigs_hero.png"],
    "sauna": ["sauna_hero.png", "histoire_do_social_icon.png"],
    "sauna_alone": ["histoire_do_solo_icon.png", "sauna_hero.png"],
    "party": ["glamour_foam_terrace.png", "glamour_foam_crowd.png", "glamour_foam_night.png"],
    "club": ["tantra_entrance_character.png", "tantra_entrance_couple.png", "tantra_entrance_night.png", "tantra_fun_hero.png"],
    "club_naked": ["tantra_entrance_character.png", "tantra_entrance_couple.png", "tantra_entrance_day.png", "tantra_entrance_night.png"],
    "bar_party": ["clair_obscur_playroom.png", "clair_obscur_backroom.png", "clair_obscur_entrance.png"],
    "qakc": ["qakc_dance.jpg"],
    "repeat": ["repeat_hero.png", "open_door_invite.png"],
}

# Clothed digital-character scenes (office, suit, café, etc.).
CHARACTER_CLOTHED_LOCATIONS = frozenset({"apps", "village", "evening", "bakery_walk"})

BRAND_PORTRAIT = "brand_portrait.jpg"
BRAND_HERO = "brand_hero.jpg"
BRAND_THUMB = "brand_thumb.jpg"
BRAND_ICON = "brand_icon.png"
BRAND_JOURNEY_START = "journey_start.jpg"
BRAND_JOURNEY_END = "journey_end.jpg"
APPLE_TOUCH_ICON = "apple-touch-icon.png"
STATIC_APPLE_TOUCH_ICON = "app/static/apple-touch-icon.png"
STATIC_WEB_MANIFEST = "app/static/manifest.webmanifest"

# Which venue image to feature on path/calendar when a day has several.
SIGNATURE_VENUE_PRIORITY = [
    "club",
    "party",
    "qakc",
    "bay_of_pigs",
    "bar_party",
    "sauna",
    "dunes",
    "gym",
    "open_door",
    "beach",
]

# One unique venue photo per journey day for calendar cells (no repeats across the grid).
_CALENDAR_HERO_BY_DAY: dict[int, str] = {
    1: "gym_naturist.png",
    2: "scene_marina_promenade.png",
    3: "scene_village_horizon_cafe.png",
    4: "dunes_walk_sea.png",
    5: "clair_obscur_entrance.png",
    6: "tantra_entrance_character.png",
    7: "open_door_balcony.png",
    8: "scene_beach_crowd_walk.png",
    9: "open_door_villa_pool.png",
    10: "dunes_social_chain.png",
    11: "qakc_dance.jpg",
    12: "tantra_fun_hero.png",
    13: "clair_obscur_playroom.png",
    14: "scene_beach_bar_group.png",
}


def _mime_for_ext(ext: str) -> str:
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext.lower(), "image/jpeg")


def _bytes_to_data_uri(raw: bytes, ext: str, *, max_bytes: int = 12 * 1024 * 1024) -> str | None:
    if not raw or len(raw) > max_bytes:
        return None
    mime = _mime_for_ext(ext)
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def _path_to_data_uri(path: Path, *, max_bytes: int = 12 * 1024 * 1024) -> str | None:
    if not path.is_file():
        return None
    try:
        size = path.stat().st_size
    except OSError:
        return None
    if size < 1 or size > max_bytes:
        return None
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    return _bytes_to_data_uri(raw, path.suffix, max_bytes=max_bytes)


@lru_cache(maxsize=256)
def venue_image_data_uri(filename: str, mtime_ns: int) -> str | None:
    return _path_to_data_uri(VENUE_IMAGES_DIR / filename)


def _venue_image_uri(filename: str) -> str | None:
    path = VENUE_IMAGES_DIR / filename
    if not path.is_file():
        return None
    return venue_image_data_uri(filename, path.stat().st_mtime_ns)


@lru_cache(maxsize=32)
def brand_image_data_uri(filename: str, mtime_ns: int) -> str | None:
    return _path_to_data_uri(BRAND_DIR / filename)


def _brand_image_uri(filename: str) -> str | None:
    path = BRAND_DIR / filename
    if not path.is_file():
        return None
    return brand_image_data_uri(filename, path.stat().st_mtime_ns)


def brand_ring_class(pct: float, collar_earned: bool) -> str:
    if collar_earned:
        return "earned"
    if pct >= 75:
        return "hot"
    if pct >= 40:
        return "warm"
    return "start"


def inject_ios_homescreen_meta() -> None:
    """Inject home-screen meta + icon into the main page (not the component iframe)."""
    title = json.dumps(APP_NAME)
    static_path = json.dumps(STATIC_APPLE_TOUCH_ICON)
    manifest_path = json.dumps(STATIC_WEB_MANIFEST)
    components.html(
        f"""
<div id="cj-offline-banner" class="cj-offline-banner">No connection — changes may not save</div>
<script>
(function() {{
  const doc = window.parent.document;
  const head = doc.head;
  const base = window.parent.location.origin;
  const icon = base + {static_path};
  const manifest = base + {manifest_path};
  [
    ["name", "apple-mobile-web-app-capable", "yes"],
    ["name", "apple-mobile-web-app-title", {title}],
    ["name", "apple-mobile-web-app-status-bar-style", "black-translucent"],
    ["name", "mobile-web-app-capable", "yes"],
    ["name", "theme-color", "#1a1020"],
  ].forEach(([attr, key, val]) => {{
    if (head.querySelector(`meta[${{attr}}="${{key}}"]`)) return;
    const m = doc.createElement("meta");
    m.setAttribute(attr, key);
    m.content = val;
    head.appendChild(m);
  }});
  if (!head.querySelector('link[rel="manifest"]')) {{
    const man = doc.createElement("link");
    man.rel = "manifest";
    man.href = manifest;
    head.appendChild(man);
  }}
  if (!head.querySelector('link[rel="apple-touch-icon"]')) {{
    const link = doc.createElement("link");
    link.rel = "apple-touch-icon";
    link.sizes = "180x180";
    link.href = icon;
    head.appendChild(link);
  }}
  if (!head.querySelector('link[rel="icon"]')) {{
    const fav = doc.createElement("link");
    fav.rel = "icon";
    fav.href = icon;
    head.appendChild(fav);
  }}
  let banner = doc.getElementById("cj-offline-banner");
  if (!banner) {{
    banner = document.getElementById("cj-offline-banner");
    if (banner) doc.body.prepend(banner);
  }}
  const syncOffline = () => {{
    if (!banner) return;
    banner.classList.toggle("show", !navigator.onLine);
  }};
  window.parent.addEventListener("online", syncOffline);
  window.parent.addEventListener("offline", syncOffline);
  syncOffline();
}})();
</script>
""",
        height=0,
        width=0,
    )


def brand_portrait_html(size: int = 112, ring_cls: str = "start") -> str:
    if size <= 120:
        fname = BRAND_THUMB
        tier = "sm"
    elif size <= 280:
        fname = BRAND_HERO
        tier = "md"
    else:
        fname = BRAND_PORTRAIT
        tier = "lg"
    uri = _brand_image_uri(fname)
    if not uri:
        return "🔗"
    return (
        f'<div class="cj-brand-frame {ring_cls} cj-brand-{tier}" '
        f'style="--cj-brand-size:{size}px;">'
        f'<div class="cj-brand-photo-wrap">'
        f'<img class="cj-brand-portrait" src="{uri}" alt="" '
        f'style="width:{size}px;height:{size}px;" title="The collar — earned, not given" />'
        f"</div></div>"
    )


def journey_milestone_html(filename: str, label: str, side_cls: str, size: int = 112) -> str:
    uri = _brand_image_uri(filename)
    if not uri:
        return ""
    return (
        f'<div class="cj-journey-milestone {side_cls}">'
        f'<div class="cj-journey-photo">'
        f'<img src="{uri}" alt="" style="width:{size}px;height:{int(size * 1.33)}px;" />'
        f"</div>"
        f'<div class="cj-journey-label">{label}</div></div>'
    )


def level_progress_html(
    stats: dict,
    level: str,
    level_desc: str,
    *,
    compact: bool = False,
) -> str:
    pct = min(float(stats.get("pct", 0)), 100)
    fill_cls = "gold" if stats.get("collar_earned") or pct >= 100 else ""
    photo_size = 62 if compact else 108
    if compact:
        start = journey_milestone_html(BRAND_JOURNEY_START, "Day 1", "start", photo_size)
        end = journey_milestone_html(BRAND_JOURNEY_END, "Day 14 🔗", "end", photo_size)
    else:
        start = journey_milestone_html(BRAND_JOURNEY_START, "Day 1 · Angel", "start", photo_size)
        end = journey_milestone_html(BRAND_JOURNEY_END, "Day 14 · The Collar 🔗", "end", photo_size)
    compact_cls = " compact" if compact else ""
    level_top = (
        f'<div class="dl-level-top">'
        f"<span>🏅 <strong>{level}</strong></span>"
        f"<span>{pct:.0f}% · {level_desc}</span>"
        f"</div>"
        if not compact
        else (
            f'<div class="dl-level-top compact">'
            f"<span>{pct:.0f}% journey</span>"
            f"<span>{level}</span>"
            f"</div>"
        )
    )
    return (
        f'<div class="cj-level-journey{compact_cls}">'
        f"{start}"
        f'<div class="cj-level-center">'
        f"{level_top}"
        f'<div class="dl-level-bar">'
        f'<div class="dl-level-fill {fill_cls}" style="width:{pct}%;"></div>'
        f"</div></div>"
        f"{end}"
        f"</div>"
    )


# Alternate scene photos per location — used so strip/banner/icon never repeat the same file.
_LOCATION_ALT_IMAGES: dict[str, list[str]] = {
    "bay_of_pigs": [
        "scene_beach_bar_group.png",
        "bay_of_pigs_hero.png",
        "bay_of_pigs_beach_icon.png",
        "bay_of_pigs_fun_icon.png",
        "bay_of_pigs_icon.png",
    ],
    "sauna": ["sauna_hero.png", "histoire_do_social_icon.png", "histoire_do_fun_icon.png"],
    "sauna_alone": ["histoire_do_solo_icon.png", "sauna_hero.png", "histoire_do_icon.png"],
    "village": [
        "scene_village_horizon_cafe.png",
        "scene_marina_promenade.png",
        "village_cafe_hero.png",
        "village_cafe_icon.png",
        "village_icon.png",
    ],
    "beach": [
        "scene_beach_bar_group.png",
        "scene_beach_crowd_walk.png",
        "scene_beach_boardwalk.png",
        "beach_bar_hero.png",
        "beach_icon.png",
        "beach_crowd_icon.png",
    ],
    "beach_walk": [
        "scene_beach_boardwalk.png",
        "scene_beach_crowd_walk.png",
        "beach_walk_icon.png",
        "beach_shower_icon.png",
        "scene_beach_bar_group.png",
    ],
    "beach_bring_back": [
        "scene_beach_crowd_walk.png",
        "scene_beach_sand.png",
        "bay_of_pigs_beach_icon.png",
        "scene_beach_boardwalk.png",
    ],
    "dunes": [
        "dunes_walk_sea.png",
        "dunes_path_trail.png",
        "dunes_portrait_grass.png",
        "dunes_social_chain.png",
        "dunes_hero.png",
    ],
    "evening": ["evening_suit_character.png", "evening_hero.png", "evening_fun_icon.png"],
    "bar_party": [
        "clair_obscur_entrance.png",
        "clair_obscur_backroom.png",
        "clair_obscur_playroom.png",
    ],
    "club": [
        "tantra_entrance_character.png",
        "tantra_entrance_couple.png",
        "tantra_entrance_night.png",
        "tantra_entrance_day.png",
        "tantra_fun_hero.png",
    ],
    "club_naked": [
        "tantra_entrance_character.png",
        "tantra_entrance_couple.png",
        "tantra_entrance_day.png",
        "tantra_entrance_night.png",
    ],
    "party": [
        "scene_glamour_boardwalk.png",
        "glamour_foam_night.png",
        "glamour_foam_day.png",
        "glamour_foam_crowd.png",
        "glamour_foam_terrace.png",
        "glamour_foam_club.png",
        "glamour_foam_action.png",
        "glamour_foam_dance.png",
    ],
    "open_door": [
        "open_door_balcony.png",
        "open_door_villa_pool.png",
        "open_door_invite.png",
        "open_door_hero.png",
    ],
    "gym": ["gym_naturist.png", "gym_naturist.jpg", "gym_naturist_character.png", "gym_hero_character.png"],
    "repeat": ["repeat_hero.png", "repeat_fun_icon.png"],
    "bakery_walk": [
        "scene_bakery_baguettes_walk.png",
        "scene_bakery_baguettes_street.png",
        "scene_marina_pier.png",
        "scene_marina_promenade.png",
        "bakery_croqmed_morning.png",
        "village_marina_hero.png",
        "bakery_walk_icon.png",
    ],
    "bakery_bring_back": [
        "village_supermarket_aisle_walk.png",
        "village_supermarket_produce.png",
        "village_supermarket_wine_aisle.png",
    ],
    "friend_single": [
        "scene_village_shop_basket.png",
        "village_supermarket_wine_aisle.png",
        "village_supermarket_produce.png",
        "scene_marina_promenade.png",
    ],
    "friend_couple": [
        "scene_marina_promenade.png",
        "village_supermarket_produce.png",
        "scene_village_horizon_cafe.png",
        "village_supermarket_wine_aisle.png",
    ],
    "talk_new": [
        "scene_marina_promenade.png",
        "scene_village_shop_basket.png",
        "scene_village_horizon_cafe.png",
        "village_supermarket_produce.png",
    ],
    "qakc": [
        "qakc_dance.jpg",
    ],
    "apps": ["apps_office_character.png", "village_path_icon.png", "village_icon.png"],
}


def _venue_image_exists(filename: str) -> bool:
    path = VENUE_IMAGES_DIR / filename
    return path.is_file() and path.stat().st_size >= 400


def naturist_scene_image(location: str) -> str | None:
    """Best nude/resort scene photo for a naturist-challenge location."""
    loc = str(location or "")
    if loc not in NUDIST_CHALLENGE_LOCATIONS:
        return None
    for fname in _NUDIST_SCENE_PRIORITY.get(loc, []):
        if _venue_image_exists(fname):
            return fname
    fallback = _VENUE_IMAGES.get(loc) or LOCATIONS.get(loc, {}).get("image")
    if fallback and _venue_image_exists(str(fallback)):
        return str(fallback)
    return None


def challenge_image_for_location(location: str) -> str | None:
    """Pick naturist scene vs clothed digital-character art by location."""
    loc = str(location or "")
    nat = naturist_scene_image(loc)
    if nat:
        return nat
    key = _VENUE_IMAGES.get(loc)
    if key and _venue_image_exists(str(key)):
        return str(key)
    meta = LOCATIONS.get(loc, {})
    img = meta.get("image")
    return str(img) if img and _venue_image_exists(str(img)) else None


def _location_image_candidates(location: str, preferred: str | None = None) -> list[str]:
    loc = str(location or "")
    candidates: list[str] = []
    if preferred:
        candidates.append(preferred)
    for img in _LOCATION_ALT_IMAGES.get(loc, []):
        if img not in candidates:
            candidates.append(img)
    meta = LOCATIONS.get(loc, {})
    default = meta.get("image")
    if default and default not in candidates:
        candidates.append(str(default))
    return [img for img in candidates if _venue_image_exists(img)]


def activity_row_visuals(row, used_images: set[str] | None = None) -> list[dict]:
    """One or more unique images for a quest row."""
    used = used_images or set()
    loc = str(row.get("location", ""))
    meta = activity_meta(row)
    base_label = str(meta.get("label") or row.get("title") or loc)
    results: list[dict] = []

    alt_img = str(meta.get("image_alt") or "").strip()
    main_img = str(meta.get("image") or "").strip()

    for img in (main_img, alt_img):
        if not img or img in used or not _venue_image_exists(img):
            continue
        results.append({"image": img, "label": base_label, "location": loc})
        used.add(img)
        break

    preferred = main_img or None
    for img in _location_image_candidates(loc, preferred):
        if img in used:
            continue
        results.append({"image": img, "label": base_label, "location": loc})
        used.add(img)
        break
    return results


def activity_row_visual(row, used_images: set[str] | None = None) -> dict | None:
    visuals = activity_row_visuals(row, used_images)
    return visuals[0] if visuals else None


def day_activity_visuals(df: pd.DataFrame, day_num: int) -> list[dict]:
    day_df = df[df["day_num"] == day_num].copy()
    if day_df.empty:
        return []
    if "time_slot" in day_df.columns:
        day_df = day_df.sort_values(["time_slot", "id"], kind="stable")
    used: set[str] = set()
    visuals: list[dict] = []
    for _, row in day_df.iterrows():
        for visual in activity_row_visuals(row, used):
            visuals.append(visual)
    return visuals


def _pick_path_banner(
    visuals: list[dict],
    day_num: int,
    prev_banner_image: str | None,
) -> dict | None:
    if not visuals:
        return None

    qakc = [v for v in visuals if v.get("location") == "qakc"]
    if day_num == 11 and qakc:
        hit = next((v for v in qakc if v["image"] == "qakc_dance.jpg"), None)
        if hit and hit["image"] != prev_banner_image:
            return hit
        if qakc[0]["image"] != prev_banner_image:
            return qakc[0]

    banner_idx = (day_num - 1) % len(visuals)
    if prev_banner_image and visuals[banner_idx]["image"] == prev_banner_image and len(visuals) > 1:
        banner_idx = (banner_idx + 1) % len(visuals)
    return visuals[banner_idx]


def day_path_visual_plan(
    df: pd.DataFrame,
    day_num: int,
    prev_banner_image: str | None = None,
) -> dict:
    visuals = day_activity_visuals(df, day_num)
    empty = {"banner": None, "icon": None, "strip": [], "all": visuals}
    if not visuals:
        return empty

    banner = _pick_path_banner(visuals, day_num, prev_banner_image)
    if not banner:
        return empty

    icon_candidates = [v for v in visuals if v["image"] != banner["image"]]
    icon = (
        icon_candidates[(day_num * 2 - 1) % len(icon_candidates)]
        if icon_candidates
        else None
    )

    used_on_card = {banner["image"]}
    if icon:
        used_on_card.add(icon["image"])
    strip = [v for v in visuals if v["image"] not in used_on_card][:4]
    return {"banner": banner, "icon": icon, "strip": strip, "all": visuals}


def day_venue_locations(df: pd.DataFrame, day_num: int) -> list[str]:
    return [v["location"] for v in day_activity_visuals(df, day_num)]


def day_signature_location(df: pd.DataFrame, day_num: int) -> str | None:
    plan = day_path_visual_plan(df, day_num)
    banner = plan.get("banner")
    return str(banner["location"]) if banner else None


def calendar_cell_image(
    df: pd.DataFrame,
    day_num: int,
    used_images: set[str],
) -> str | None:
    """Pick a unique venue photo for a calendar day — never reuse across the grid."""
    candidates: list[str] = []

    hero = _CALENDAR_HERO_BY_DAY.get(day_num)
    if hero:
        candidates.append(hero)

    for visual in day_activity_visuals(df, day_num):
        if visual["image"] not in candidates:
            candidates.append(visual["image"])

    day_df = df[df["day_num"] == day_num]
    for _, row in day_df.iterrows():
        meta = activity_meta(row)
        pref = str(meta.get("image") or "").strip() or None
        for img in _location_image_candidates(str(row["location"]), pref):
            if img not in candidates:
                candidates.append(img)

    for img in candidates:
        if img not in used_images and _venue_image_exists(img):
            used_images.add(img)
            return img

    for img in _CALENDAR_HERO_BY_DAY.values():
        if img not in used_images and _venue_image_exists(img):
            used_images.add(img)
            return img

    for img in candidates:
        if _venue_image_exists(img):
            return img
    return None


def day_venue_strip_html(
    df: pd.DataFrame,
    day_num: int,
    max_icons: int = 4,
    size: int = 30,
    mode: str = "all",
) -> str:
    plan = day_path_visual_plan(df, day_num)
    pool = plan["strip"] if mode == "path" else plan["all"]
    items = pool[:max_icons]
    if not items:
        return ""
    chips = "".join(
        location_meta_icon_html({"image": v["image"], "icon": "📍"}, size)
        for v in items
    )
    return f'<div class="cj-day-venue-strip">{chips}</div>'


def activity_meta(row) -> dict:
    """Display meta for a quest row — merges LOCATIONS with per-activity overrides."""
    loc = str(row.get("location", ""))
    base = LOCATIONS.get(
        loc,
        {"label": loc, "icon": "📍", "color": "#1CB0F6", "image": None},
    )
    meta = dict(base)
    venue = str(row.get("venue_name") or "").strip()
    if venue:
        meta["label"] = venue
    img = str(row.get("image_file") or "").strip()
    if img:
        meta["image"] = img
    else:
        challenge_img = challenge_image_for_location(loc)
        if challenge_img:
            meta["image"] = challenge_img
    return meta


def location_meta_icon_html(meta: dict, size: int = 26) -> str:
    image = meta.get("image")
    if image:
        uri = _venue_image_uri(str(image))
        if uri:
            img_name = str(image)
            if "qakc_dance" in img_name:
                pos = "center 38%"
            else:
                pos = "center top"
            return (
                f'<img class="cj-loc-icon-img cj-polaroid" src="{uri}" alt="" '
                f'style="width:{size}px;height:{size}px;object-fit:cover;object-position:{pos};'
                f'border-radius:8px;vertical-align:-0.35em;margin-right:0.2rem;" />'
            )
    return str(meta.get("icon", "📍"))


def qakc_face_hero_html(featured: bool = False) -> str:
    """Single prominent QAKC face photo."""
    uri = _venue_image_uri("qakc_dance.jpg")
    if not uri:
        return ""
    cls = "cj-qakc-solo featured" if featured else "cj-qakc-solo compact"
    color = LOCATIONS.get("qakc", {}).get("color", "#fd79a8")
    return (
        f'<div class="cj-quest-hero {cls}" style="border-color:{color}99;">'
        f'<img src="{uri}" alt="" title="QAKC · Gay Club" /></div>'
    )


def venue_hero_html(location: str, row=None, *, featured: bool = False) -> str:
    if row is not None:
        act_key = str(row.get("activity_key") or "")
        if act_key:
            user_uri = challenge_media_uri(act_key)
            if user_uri:
                meta = activity_meta(row)
                color = meta.get("color", "#1CB0F6")
                hero_cls = "cj-quest-hero featured" if featured else "cj-quest-hero"
                return (
                    f'<div class="{hero_cls}" style="border-color:{color}99;">'
                    f'<img src="{user_uri}" alt="" /></div>'
                )
    if str(location) == "qakc":
        return qakc_face_hero_html(featured=featured)
    loc_uri = location_media_uri(str(location))
    if loc_uri:
        meta = LOCATIONS.get(location, {})
        color = meta.get("color", "#1CB0F6")
        hero_cls = "cj-quest-hero featured" if featured else "cj-quest-hero"
        return (
            f'<div class="{hero_cls}" style="border-color:{color}99;">'
            f'<img src="{loc_uri}" alt="" /></div>'
        )
    meta = activity_meta(row) if row is not None else LOCATIONS.get(location, {})
    if row is None and location:
        meta = LOCATIONS.get(location, meta)
    image = meta.get("image")
    if not image:
        return ""
    uri = _venue_image_uri(str(image))
    if not uri:
        return ""
    color = meta.get("color", "#1CB0F6")
    alt = meta.get("image_alt")
    alt_uri = _venue_image_uri(str(alt)) if alt else None
    hero_cls = "cj-quest-hero featured" if featured else "cj-quest-hero"
    if alt_uri and not featured:
        return (
            f'<div class="cj-quest-hero dual" style="border-color:{color}99;">'
            f'<img src="{alt_uri}" alt="" title="Getting ready" />'
            f'<img src="{uri}" alt="" title="At QAKC" /></div>'
        )
    return (
        f'<div class="{hero_cls}" style="border-color:{color}99;">'
        f'<img src="{uri}" alt="" /></div>'
    )


def venue_scene_open_html(location: str, row=None) -> str:
    meta = activity_meta(row) if row is not None else LOCATIONS.get(location, {})
    if row is None and location:
        meta = LOCATIONS.get(location, meta)
    color = meta.get("color", "#1CB0F6")
    image = meta.get("image")
    bg = f'<div class="cj-quest-scene-bg solid" style="background:linear-gradient(135deg,{color}33,{color}08);"></div>'
    if image:
        uri = _venue_image_uri(str(image))
        if uri:
            bg = f'<div class="cj-quest-scene-bg"><img src="{uri}" alt="" /></div>'
    return f'<div class="cj-quest-scene">{bg}<div class="cj-quest-scene-overlay"></div><div class="cj-quest-scene-inner">'


def location_image_uri(location: str) -> str | None:
    meta = LOCATIONS.get(location, {})
    image = meta.get("image")
    if image:
        uri = _venue_image_uri(str(image))
        if uri:
            return uri
    challenge = challenge_image_for_location(location)
    if challenge:
        return _venue_image_uri(challenge)
    return None


def venue_photo_layer_html(uri: str, extra_cls: str = "") -> str:
    if not uri:
        return ""
    return f'<div class="cj-photo-layer {extra_cls}"><img src="{uri}" alt="" /></div>'


def day_venue_banner_html(df: pd.DataFrame, day_num: int, title: str = "") -> str:
    plan = day_path_visual_plan(df, day_num)
    layers_src = plan["all"][:3]
    if not layers_src:
        return ""
    layers = []
    for i, visual in enumerate(layers_src):
        uri = _venue_image_uri(visual["image"])
        if uri:
            layers.append(venue_photo_layer_html(uri, f"mosaic-{i}"))
    if not layers:
        return ""
    meta = day_plan_meta(day_num)
    label = title or f"Day {day_num} — {meta['title']}"
    lead = layers_src[0]
    venue_name = lead.get("label", lead.get("location", ""))
    extra = len(layers_src) - 1
    return f"""
<div class="cj-day-banner">
  <div class="cj-day-banner-photos">{''.join(layers)}</div>
  <div class="cj-day-banner-scrim"></div>
  <div class="cj-day-banner-text">
    <div class="cj-day-banner-kicker">📍 {venue_name}{' +' + str(extra) + ' more' if extra > 0 else ''}</div>
    <div class="cj-day-banner-title">{label}</div>
  </div>
</div>
"""


def quest_pick_image_uri(row) -> str | None:
    act_key = str(row.get("activity_key") or "").strip()
    if act_key:
        user_uri = challenge_media_uri(act_key)
        if user_uri:
            return user_uri
    img_file = str(row.get("image_file") or "").strip()
    if img_file:
        uri = _venue_image_uri(img_file)
        if uri:
            return uri
    meta = activity_meta(row)
    img = meta.get("image")
    if img:
        uri = _venue_image_uri(str(img))
        if uri:
            return uri
    return location_image_uri(str(row.get("location", "")))


def quest_pick_tile_html(row, selected: bool = False) -> str:
    """Large photo tile for quest selection grid."""
    loc = str(row["location"])
    meta = LOCATIONS.get(loc, {})
    uri = quest_pick_image_uri(row)
    cls = "cj-quest-pick-tile selected" if selected else "cj-quest-pick-tile"
    if uri:
        media = f'<img src="{uri}" class="cj-quest-pick-tile-img" alt="" />'
    else:
        media = f'<div class="cj-quest-pick-tile-emoji">{meta.get("icon", "📍")}</div>'
    slot = time_slot_label(str(row["time_slot"]))
    return (
        f'<div class="{cls}">'
        f'{media}<div class="cj-quest-pick-tile-meta">{slot} · {activity_xp_badge(row)}</div>'
        f"</div>"
    )


def quest_day_tile_html(row, selected: bool = False) -> str:
    """Photo tile for the day quest grid — pending and completed."""
    is_earned = row["status"] == "earned"
    loc = str(row["location"])
    meta = LOCATIONS.get(loc, {})
    uri = quest_pick_image_uri(row)
    css = ["cj-quest-day-tile"]
    if selected:
        css.append("selected")
    if is_earned:
        css.append("earned")
    if uri:
        media = f'<img src="{uri}" class="cj-quest-day-tile-img" alt="" />'
    else:
        media = f'<div class="cj-quest-day-tile-emoji">{meta.get("icon", "📍")}</div>'
    chip = "✅" if is_earned else activity_xp_badge(row)
    return (
        f'<div class="{" ".join(css)}">'
        f"{media}"
        f'<span class="cj-quest-day-tile-chip">{chip}</span>'
        f"</div>"
    )


def quest_day_tile_button_label(row, is_open: bool) -> str:
    short = str(row["title"])
    if len(short) > 32:
        short = short[:30] + "…"
    slot = time_slot_label(str(row["time_slot"]))
    xp = activity_xp_badge(row)
    if is_open:
        return f"▲ Close · {short}"
    if row["status"] == "earned":
        return f"✅ {short} · {slot}"
    return f"🎯 {short} · {slot} · {xp}"


def quest_pick_card_html(row, selected: bool = False) -> str:
    loc = str(row["location"])
    meta = LOCATIONS.get(loc, {})
    uri = location_image_uri(loc)
    cls = "cj-quest-pick-card selected" if selected else "cj-quest-pick-card"
    thumb = (
        f'<img src="{uri}" alt="" />'
        if uri
        else f'<span class="cj-quest-pick-emoji">{meta.get("icon", "📍")}</span>'
    )
    short = str(row["title"])
    if len(short) > 28:
        short = short[:26] + "…"
    return f"""
<div class="{cls}">
  <div class="cj-quest-pick-thumb">{thumb}</div>
  <div class="cj-quest-pick-body">
    <div class="cj-quest-pick-xp">{activity_xp_badge(row)}</div>
    <div class="cj-quest-pick-title">{short}</div>
    <div class="cj-quest-pick-slot">{time_slot_label(str(row['time_slot']))}</div>
  </div>
</div>
"""


def path_node_photo_banner_html(
    df: pd.DataFrame,
    day_num: int,
    prev_banner_image: str | None = None,
) -> str:
    plan = day_path_visual_plan(df, day_num, prev_banner_image)
    banner = plan.get("banner")
    if not banner:
        return ""
    label = banner.get("label", banner.get("location", ""))
    qakc_cls = " qakc" if banner.get("location") == "qakc" else ""
    uri = _venue_image_uri(banner["image"])
    if not uri:
        return ""
    return f"""
<div class="cj-path-photo-banner{qakc_cls}">
  {venue_photo_layer_html(uri, "ken-burns")}
  <div class="cj-path-photo-scrim{' light' if qakc_cls else ''}"></div>
  <span class="cj-path-photo-label">{label}</span>
</div>
"""


VENUE_SCENE_CLOSE_HTML = "</div></div>"


def complete_quest_button_label(row, points: int | None = None) -> str:
    if str(row["location"]) in HALF_POINT_LOCATIONS:
        return "✅ Complete quest · +½ XP"
    pts = int(points) if points is not None else int(row["points"])
    return f"✅ Complete quest · +{pts} XP"


def celebrations_enabled(settings: dict | None = None) -> bool:
    if settings is None:
        settings = load_settings()
    return settings.get("celebrations_enabled", "1") != "0"


def location_icon_html(location: str, size: int = 22) -> str:
    uri = location_media_uri(location)
    if uri:
        return (
            f'<img class="cj-loc-icon-img cj-polaroid" src="{uri}" alt="" '
            f'style="width:{size}px;height:{size}px;object-fit:cover;object-position:center top;'
            f'border-radius:8px;vertical-align:-0.35em;margin-right:0.2rem;" />'
        )
    meta = LOCATIONS.get(location, {"icon": "📍"})
    return location_meta_icon_html(meta, size)


LOCATIONS = {
    "bay_of_pigs": {
        "label": "Bay of Pigs",
        "icon": "🌊",
        "color": "#4a90d9",
        "image": _VENUE_IMAGES["bay_of_pigs"],
    },
    "sauna": {
        "label": "Histoires d'O",
        "icon": "♨️",
        "color": "#e07a5f",
        "image": _VENUE_IMAGES["histoire_do"],
    },
    "village": {
        "label": "Village",
        "icon": "🏘️",
        "color": "#d4af7a",
        "image": _VENUE_IMAGES["village"],
    },
    "beach": {
        "label": "Beach",
        "icon": "🏖️",
        "color": "#f2cc8f",
        "image": _VENUE_IMAGES["beach"],
    },
    "dunes": {
        "label": "Dunes",
        "icon": "🏜️",
        "color": "#c9a227",
        "image": _VENUE_IMAGES["dunes"],
    },
    "apps": {
        "label": "Apps",
        "icon": "📱",
        "color": "#9b8ec4",
        "image": _VENUE_IMAGES["apps_scene"],
    },
    "evening": {
        "label": "Evening",
        "icon": "🌙",
        "color": "#6c5ce7",
        "image": _VENUE_IMAGES["evening"],
    },
    "bar_party": {
        "label": "Clair Obscur · BDSM",
        "icon": "🖤",
        "color": "#1a1a2e",
        "image": _VENUE_IMAGES["clair_obscur"],
    },
    "club": {
        "label": "Le Tantra",
        "icon": "⛓️",
        "color": "#8b1a1a",
        "image": _VENUE_IMAGES["tantra_entree"],
    },
    "party": {
        "label": "Le Glamour",
        "icon": "🎉",
        "color": "#e84393",
        "image": _VENUE_IMAGES["glamour"],
    },
    "open_door": {
        "label": "Open Door",
        "icon": "🚪",
        "color": "#00b894",
        "image": _VENUE_IMAGES["open_door"],
    },
    "gym": {
        "label": "Gym",
        "icon": "🏋️",
        "color": "#636e72",
        "image": _VENUE_IMAGES["gym"],
    },
    "repeat": {
        "label": "Previous Connection",
        "icon": "🔁",
        "color": "#a29bfe",
        "image": _VENUE_IMAGES["repeat"],
    },
    "bakery_walk": {
        "label": "Bakery Walk",
        "icon": "🥐",
        "color": "#e17055",
        "image": _VENUE_IMAGES["bakery_walk"],
    },
    "bakery_bring_back": {
        "label": "Bakery Bring-Back",
        "icon": "🏠",
        "color": "#d63031",
        "image": _VENUE_IMAGES["village_supermarket_walk"],
    },
    "beach_walk": {
        "label": "Beach Walk",
        "icon": "🚶",
        "color": "#00cec9",
        "image": _VENUE_IMAGES["beach_walk"],
    },
    "beach_bring_back": {
        "label": "Beach Bring-Back",
        "icon": "🏠",
        "color": "#0984e3",
        "image": _VENUE_IMAGES["beach_bring_back"],
    },
    "friend_single": {
        "label": "Friend a Single",
        "icon": "🤝",
        "color": "#fdcb6e",
        "image": _VENUE_IMAGES["scene_village_shop"],
    },
    "friend_couple": {
        "label": "Friend a Couple",
        "icon": "👫",
        "color": "#e84393",
        "image": _VENUE_IMAGES["scene_marina_promenade"],
    },
    "talk_new": {
        "label": "Talk to New People",
        "icon": "💬",
        "color": "#74b9ff",
        "image": _VENUE_IMAGES["scene_marina_promenade"],
    },
    "sauna_alone": {
        "label": "Histoires d'O",
        "icon": "🧖",
        "color": "#fab1a0",
        "image": _VENUE_IMAGES["histoire_do_solo"],
    },
    "club_naked": {
        "label": "Le Tantra",
        "icon": "👠",
        "color": "#6c5ce7",
        "image": _VENUE_IMAGES["tantra_entree"],
    },
    "qakc": {
        "label": "QAKC · Gay Club",
        "icon": "💃",
        "color": "#fd79a8",
        "image": _VENUE_IMAGES["qakc_dance"],
    },
}

LEVELS = [
    (0, "Arrivée", "Just landed in the village."),
    (8, "Curious", "Testing the waters."),
    (18, "Initiative", "Starting to approach."),
    (30, "Chosen", "Letting others lead sometimes."),
    (45, "Social Flow", "Moving through spaces with ease."),
    (60, "Devoted", "Halfway to the collar."),
    (75, "Collar Candidate", "The finish line is in sight."),
    (90, "Almost Hers", "One final push."),
    (100, "Collar Earned", "Every activity complete."),
]

BADGES = [
    ("day_1", "First Light", "Complete Day 1 — Orientation.", lambda s: s["days_complete"] >= 1),
    ("week_1", "Week One", "Complete Days 1–7.", lambda s: s["days_complete"] >= 7),
    ("club_1", "Club Night I", "Complete Day 6 club bonus.", lambda s: s.get("d6_club", False)),
    ("club_2", "Club Night II", "Complete Day 12 club bonus.", lambda s: s.get("d12_club", False)),
    ("dunes", "Dunes Walker", "Complete 3 dunes challenges.", lambda s: s.get("dunes_done", 0) >= 3),
    ("open_door", "Open Door", "Complete Day 9 open-door challenge.", lambda s: s.get("d9_open", False)),
    ("social_chain", "Social Chain", "Complete Day 13 evening chain.", lambda s: s.get("d13_chain", False)),
    ("final_test", "Final Test", "Complete Day 14.", lambda s: s.get("d14_done", False)),
    ("perfect_day", "Perfect Day", "Earn every point on a single day.", lambda s: s.get("perfect_days", 0) >= 1),
    ("streak_3", "Hot Streak", "3 consecutive days complete.", lambda s: s.get("max_streak", 0) >= 3),
    ("coke", "Coke Earned", "Earned a Coke at the Bay of Pigs.", lambda s: s.get("coke_count", 0) >= 1),
    ("pr_break", "PR Breaker", "Exceeded a personal best day.", lambda s: s.get("pr_breaks", 0) >= 1),
    ("streak_10", "Ten in a Row", "10 consecutive interactions in one session at a location.", lambda s: s.get("streak_count", 0) >= 1),
]

DAY_PATH_META: dict[int, dict] = {
    1: {"icon": "🧭", "accent": "#58CC02", "kind": "start", "reward": "First steps"},
    2: {"icon": "💪", "accent": "#1CB0F6", "kind": "normal", "reward": "Initiative XP"},
    3: {"icon": "🎲", "accent": "#CE82FF", "kind": "normal", "reward": "Chosen badge"},
    4: {"icon": "🏜️", "accent": "#c9a227", "kind": "challenge", "reward": "Dunes Walker"},
    5: {"icon": "🍸", "accent": "#fd79a8", "kind": "normal", "reward": "Social flow"},
    6: {"icon": "⛓️", "accent": "#8b1a1a", "kind": "chest", "reward": "Club Bonus I 🎁"},
    7: {"icon": "🦋", "accent": "#00b894", "kind": "checkpoint", "reward": "Week 1 crown"},
    8: {"icon": "🏘️", "accent": "#d4af7a", "kind": "normal", "reward": "Pickup pro"},
    9: {"icon": "🚪", "accent": "#00b894", "kind": "challenge", "reward": "Open Door"},
    10: {"icon": "🏜️", "accent": "#c9a227", "kind": "chest", "reward": "Dunes Double 🎁"},
    11: {"icon": "🎉", "accent": "#e84393", "kind": "party", "reward": "Party legend"},
    12: {"icon": "⛓️", "accent": "#8b1a1a", "kind": "chest", "reward": "Club Bonus II 🎁"},
    13: {"icon": "🔗", "accent": "#6c5ce7", "kind": "challenge", "reward": "Social Chain"},
    14: {"icon": "👑", "accent": "#FFC800", "kind": "finale", "reward": "THE COLLAR"},
}

BADGE_ICONS = {
    "day_1": "🌅",
    "week_1": "🗓️",
    "club_1": "⛓️",
    "club_2": "💎",
    "dunes": "🏜️",
    "open_door": "🚪",
    "social_chain": "🔗",
    "final_test": "👑",
    "perfect_day": "⭐",
    "streak_3": "🔥",
    "coke": "🥤",
    "pr_break": "📈",
    "streak_10": "🔟",
}

_CORE_DAY_PLANS = [
    {
        "day": 1,
        "title": "Orientation",
        "target": 10,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Morning naked workout at the resort gym — half point for showing up in the buff and putting in the reps. "
                "Flirt optional; sweat mandatory.",
                1,
            ),
            (
                "early_afternoon",
                "village",
                "Village — Early Afternoon",
                "Walk the promenade — one single she picks; real talk, maybe plan a drink later.",
                1,
            ),
            (
                "early_afternoon",
                "apps",
                "Apps — Early Afternoon",
                "Two chats that move fast toward a meet — tonight or tomorrow. "
                "Direct: she's here for more than messaging.",
                1,
            ),
            (
                "early_afternoon",
                "repeat",
                "Previous Connections — Early Afternoon",
                "Reconnect with two men from earlier contacts — apps, village, wherever the spark started. "
                "Pick up where you left off.",
                2,
            ),
            (
                "afternoon",
                "sauna",
                "Histoires d'O — Afternoon",
                "Steam and bare skin after 2:00 PM. When two men approach, she makes room for both — "
                "hands wander, no pretending she's shy.",
                2,
            ),
            (
                "late_afternoon",
                "bay_of_pigs",
                "Bay of Pigs — Late Afternoon",
                "Open beach sex — crowds drift over to watch. Approach one; let two others come to her. "
                "Dunes nearby for privacy, or stay put and let the circle grow.",
                3,
            ),
        ],
    },
    {
        "day": 2,
        "title": "Initiative",
        "target": 10,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Naked workout at the gym — half point. Start the day hot, loose, and visibly available.",
                1,
            ),
            (
                "morning",
                "repeat",
                "Previous Connections — Morning",
                "Two morning reconnects — coffee, a walk, or invite someone back while the day is still open.",
                2,
            ),
            (
                "early_afternoon",
                "village",
                "Village — Early Afternoon",
                "She picks one man and makes the first move. Drink if mutual; "
                "if the vibe holds, the rental door is on the table.",
                1,
            ),
            (
                "early_afternoon",
                "apps",
                "Apps — Early Afternoon",
                "Two new matches; she names the place and the hour.",
                1,
            ),
            (
                "late_afternoon",
                "bay_of_pigs",
                "Bay of Pigs — Late Afternoon",
                "She initiates all three — wave someone over, join a towel, "
                "or ask a group if she can sit. Audacious beats polite.",
                3,
            ),
            (
                "afternoon",
                "sauna",
                "Histoires d'O — Afternoon",
                "Two who approach her in the heat after 2:00 PM — both welcomed, no playing hard to get.",
                2,
            ),
        ],
    },
    {
        "day": 3,
        "title": "Being Chosen",
        "target": 10,
        "activities": [
            (
                "morning",
                "repeat",
                "Previous Connections — Morning",
                "Two men she's already met — easy morning follow-up before they disappear into someone else's week.",
                2,
            ),
            (
                "early_afternoon",
                "village",
                "Village — Early Afternoon",
                "Wait to be chosen once on the strip — then lean into whoever picks her.",
                1,
            ),
            (
                "early_afternoon",
                "apps",
                "Apps — Early Afternoon",
                "Two fresh contacts; push toward flesh, not endless flirting.",
                1,
            ),
            (
                "afternoon",
                "sauna",
                "Histoires d'O — Afternoon",
                "First three adults who approach appropriately after 2:00 PM — accept the queue, "
                "rotate attention, see where each leads.",
                3,
            ),
            (
                "late_afternoon",
                "beach",
                "Beach — Late Afternoon",
                "Lie out where people pass. Two who approach first — she says yes before overthinking.",
                2,
            ),
            (
                "evening",
                "evening",
                "Evening",
                "One unplanned encounter — bar, beach path, elevator; wherever the night finds her.",
                1,
            ),
        ],
    },
    {
        "day": 4,
        "title": "Dunes Challenge",
        "target": 13,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Naked workout — half point. Legs burning before the dunes do.",
                1,
            ),
            (
                "early_afternoon",
                "village",
                "Village — Early Afternoon",
                "One single on the strip — bold eye contact, direct opener.",
                1,
            ),
            (
                "early_afternoon",
                "apps",
                "Apps — Early Afternoon",
                "Two contacts lined up for a meet.",
                2,
            ),
            (
                "early_afternoon",
                "repeat",
                "Previous Connections",
                "One repeat from earlier in the trip — keep the roster warm.",
                1,
            ),
            (
                "late_afternoon",
                "beach",
                "Beach — Late Afternoon",
                "Two one-on-one moments on the sand — different men, same confidence.",
                2,
            ),
            (
                "late_afternoon",
                "dunes",
                "Dunes / Social Beach",
                "Find a group of 3–4 already playing. Each person counts — "
                "she can be the center while they share her attention.",
                4,
            ),
            (
                "afternoon",
                "sauna",
                "Histoires d'O — Afternoon",
                "Two new faces in the steam after 2:00 PM — welcome both.",
                2,
            ),
        ],
    },
    {
        "day": 5,
        "title": "Invitation Day",
        "target": 12,
        "activities": [
            (
                "morning",
                "repeat",
                "Previous Connections — Morning",
                "Two morning reconnects — someone from apps, someone from the village strip; easy invites back.",
                2,
            ),
            (
                "early_afternoon",
                "village",
                "Village — Early Afternoon",
                "One man on the strip; drink if mutual. "
                "The bar should know she's not going home alone yet.",
                1,
            ),
            (
                "early_afternoon",
                "apps",
                "Apps — Early Afternoon",
                "Two new hooks — meet while the energy is high.",
                1,
            ),
            (
                "afternoon",
                "sauna",
                "Histoires d'O — Afternoon",
                "First three who approach after 2:00 PM — rotate; don't lock onto one body.",
                3,
            ),
            (
                "late_afternoon",
                "beach",
                "Beach — Late Afternoon",
                "Two new connections — she can make it physical fast if they hesitate.",
                2,
            ),
            (
                "evening",
                "bar_party",
                "Clair Obscur — BDSM Night",
                "Clair Obscur dungeon: collect three invitations (scene, drink, more). Accept what she wants; "
                "declined still counts as working the room.",
                3,
            ),
        ],
    },
    {
        "day": 6,
        "title": "CLUB BONUS I",
        "target": 17,
        "bonus_target": 19,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Naked workout before club night — half point. Warm up the body before the playroom.",
                1,
            ),
            ("early_afternoon", "village", "Village — Early Afternoon", "One quick hit on the strip.", 1),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "Two contacts for tonight or tomorrow.", 2),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Steam session at Histoires d'O after 2:00 PM — two interactions.", 2),
            ("late_afternoon", "beach", "Beach — Late Afternoon", "Warm-up on the sand — two connections before the club.", 2),
            (
                "evening",
                "club",
                "Le Tantra — Bonus",
                "Le Tantra playroom night: ten different adults minimum. Never camp with one — "
                "circulate, let strangers choose her, choose strangers back. Declined still counts.",
                10,
                True,
            ),
        ],
    },
    {
        "day": 7,
        "title": "Independent Day",
        "target": 11,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Naked workout — half point. Her rhythm, her body, no audience required.",
                1,
            ),
            ("early_afternoon", "village", "Village — Early Afternoon", "One spontaneous street or café moment.", 1),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "She arranges one meeting herself — time, place, her call.", 1),
            (
                "morning",
                "repeat",
                "Previous Connections — Morning",
                "Two people via whatever worked best in week one — morning coffee or a walk before the day fills up.",
                2,
            ),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Two in the sauna after 2:00 PM.", 2),
            ("late_afternoon", "beach", "Beach — Late Afternoon", "Two on the beach — her rhythm, her picks.", 2),
            (
                "evening",
                "evening",
                "Evening",
                "Two unplanned — bar, path, elevator; wherever independence leads.",
                2,
            ),
        ],
    },
    {
        "day": 8,
        "title": "Village Pickup Challenge",
        "target": 13,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Naked workout — half point.",
                1,
            ),
            (
                "early_afternoon",
                "village",
                "Village — Early Afternoon",
                "One bold approach on the strip — eye contact, direct opener.",
                1,
            ),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "Two new contacts.", 2),
            (
                "late_afternoon",
                "village",
                "Village — Pickup Challenge",
                "Afternoon on the strip: approach two more singles; drinks if mutual. "
                "Rental invite for whoever earns it.",
                2,
            ),
            ("late_afternoon", "beach", "Beach — Late Afternoon", "Two new bodies on the beach.", 2),
            (
                "late_afternoon",
                "dunes",
                "Dunes",
                "One group of three in the sand — passed around or holding court; each person counts.",
                3,
            ),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Two who approach her after 2:00 PM — both get attention.", 2),
        ],
    },
    {
        "day": 9,
        "title": "Open-Door Challenge",
        "target": 14,
        "activities": [
            ("early_afternoon", "village", "Village — Early Afternoon", "One on the strip.", 1),
            (
                "morning",
                "repeat",
                "Previous Connections — Morning",
                "Two morning reconnects before the open-door period — warm the network while there's still time.",
                2,
            ),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "One contact lined up for later.", 1),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Two in the steam after 2:00 PM.", 2),
            ("late_afternoon", "beach", "Beach — Late Afternoon", "Two interactions on the sand.", 2),
            (
                "special",
                "open_door",
                "Open-Door Period",
                "Rental door open, adults only. First four visitors — individual attention each; "
                "overlap if she dares. She closes when she's had enough.",
                4,
            ),
            ("evening", "apps", "Apps — Evening", "Two contacts.", 2),
        ],
    },
    {
        "day": 10,
        "title": "Dunes Double",
        "target": 14,
        "bonus_target": 15,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Naked workout — half point before the group scenes.",
                1,
            ),
            ("early_afternoon", "village", "Village — Early Afternoon", "One on the strip.", 1),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "Two contacts.", 2),
            (
                "late_afternoon",
                "dunes",
                "Dunes — First Group",
                "First group of 3–4 in the dunes — new faces, shared scene; she doesn't pick just one.",
                4,
            ),
            (
                "late_afternoon",
                "dunes",
                "Dunes — Second Group",
                "Later, a completely different cluster — fresh group, same boldness; prove it wasn't luck.",
                4,
            ),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Cool down with two in the steam after 2:00 PM.", 2),
        ],
    },
    {
        "day": 11,
        "title": "Mousse / Party Day",
        "target": 16,
        "activities": [
            (
                "morning",
                "repeat",
                "Previous Connections — Morning",
                "Two morning reconnects — stack the network before mousse night.",
                2,
            ),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "One new contact before the party.", 1),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Two in the sauna after 2:00 PM.", 2),
            ("late_afternoon", "beach", "Beach — Late Afternoon", "Two on the beach.", 2),
            (
                "evening",
                "qakc",
                "QAKC Gay Club — Dance",
                "Head to QAKC (the gay club) and dance — own the floor, get noticed, "
                "warm up before mousse night.",
                2,
            ),
            (
                "evening",
                "party",
                "Le Glamour — Mousse",
                "Le Glamour mousse night: six distinct — two she hunts, two hunt her, "
                "two with couples or groups. Work the room like she owns it.",
                6,
            ),
            ("evening", "apps", "Apps — Evening", "Two new contacts — stack tonight or tomorrow.", 2),
        ],
    },
    {
        "day": 12,
        "title": "CLUB BONUS II",
        "target": 21,
        "bonus_target": 23,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Naked workout — half point. Pre-game before the second club push.",
                1,
            ),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "Two contacts.", 2),
            (
                "late_afternoon",
                "bay_of_pigs",
                "Bay of Pigs — Late Afternoon",
                "Back on the open beach — two interactions; the crowd may gather again.",
                2,
            ),
            (
                "late_afternoon",
                "dunes",
                "Dunes",
                "Group of 3–4 — full sand session; multiple partners, one audacious scene.",
                4,
            ),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Two in the steam after 2:00 PM.", 2),
            (
                "evening",
                "club",
                "Le Tantra — Playroom",
                "Ten distinct at Le Tantra — 3 she initiates, 3 choose her, 1 via introduction. "
                "Keep moving; the playroom isn't for staying with one.",
                10,
                True,
            ),
        ],
    },
    {
        "day": 13,
        "title": "Social Chain",
        "target": 16,
        "activities": [
            (
                "morning",
                "repeat",
                "Previous Connections — Morning",
                "Two morning reconnects — fuel for tonight's introduction chain.",
                2,
            ),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "Two people from apps.", 2),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Two people in the steam after 2:00 PM.", 2),
            ("late_afternoon", "beach", "Beach — Late Afternoon", "Two on the beach.", 2),
            (
                "late_afternoon",
                "dunes",
                "Dunes",
                "Group of 3–4 — minimum three interactions; shared attention in the sand.",
                3,
            ),
            (
                "evening",
                "evening",
                "Evening — Social Chain",
                "Four people only through introductions from earlier contacts — "
                "her network feeds her audacity.",
                4,
            ),
        ],
    },
    {
        "day": 14,
        "title": "Final Collar Test",
        "target": 17,
        "activities": [
            (
                "morning",
                "gym",
                "Gym — Naked Workout",
                "Final naked workout — half point. Last morning ritual before the collar test.",
                1,
            ),
            (
                "morning",
                "repeat",
                "Previous Connections — Morning",
                "Two favorites from the trip — morning coffee or a walk with people who already want her.",
                2,
            ),
            ("early_afternoon", "apps", "Apps — Early Afternoon", "Two contacts.", 2),
            (
                "late_afternoon",
                "bay_of_pigs",
                "Bay of Pigs — Late Afternoon",
                "Two on the open beach — Dom doesn't pick who. She chooses where anyone can watch.",
                2,
            ),
            (
                "late_afternoon",
                "dunes",
                "Dunes / Group",
                "Three in a dunes group — multiple hands, sand, sun; she takes what she wants.",
                3,
            ),
            ("afternoon", "sauna", "Histoires d'O — Afternoon", "Two in the steam after 2:00 PM.", 2),
            (
                "evening",
                "evening",
                "Evening — Final Test",
                "Four self-selected anywhere in the resort — her call entirely. "
                "Cap the journey the way she wants to be remembered.",
                4,
            ),
        ],
    },
]

# Light morning social quests — rotated per day (not the full catalog every day).
_ACT_BAKERY_WALK = (
    "morning",
    "bakery_walk",
    "Bakery Walk — Chat a Single",
    "Morning stroll to Croq'Med — chat up one new single on the way. Half point.",
    1,
)
_ACT_BAKERY_BRING_BACK = (
    "morning",
    "bakery_bring_back",
    "Bakery — Bring Him Back",
    "Bonus half point if you bring him back to the rental before noon ends.",
    1,
)
_ACT_BEACH_WALK = (
    "morning",
    "beach_walk",
    "Beach Walk — New Face",
    "Short walk toward the beach — talk to someone new on the path. Half point.",
    1,
)
_ACT_BEACH_BRING_BACK = (
    "morning",
    "beach_bring_back",
    "Beach Walk — Bring Back",
    "Bonus half point if you bring someone from the walk back for sex — while the morning's still loose.",
    1,
)
_ACT_FRIEND_SINGLE = (
    "morning",
    "friend_single",
    "Friend a Single",
    "Make friends with a single — conversation past small talk. Half point.",
    1,
)
_ACT_FRIEND_COUPLE = (
    "morning",
    "friend_couple",
    "Friend a Couple",
    "Warm up a couple over coffee — chat, flirt, get them to like her. Half point.",
    1,
)
_ACT_TALK_NEW = (
    "morning",
    "talk_new",
    "Talk to New People",
    "Talk to strangers — shop, path, pool, café. Easy morning half point.",
    1,
)

# 1–2 morning social quests per day; pairs with at most one core morning item (gym or repeat).
_MORNING_SOCIAL_BY_DAY: dict[int, list[tuple]] = {
    1: [_ACT_BAKERY_WALK, _ACT_TALK_NEW],
    2: [_ACT_BEACH_WALK],
    3: [_ACT_BAKERY_WALK, _ACT_FRIEND_SINGLE],
    4: [_ACT_BAKERY_WALK],
    5: [_ACT_BEACH_WALK, _ACT_TALK_NEW],
    6: [_ACT_TALK_NEW],
    7: [_ACT_BAKERY_WALK],
    8: [_ACT_BEACH_WALK],
    9: [_ACT_BAKERY_WALK, _ACT_BAKERY_BRING_BACK],
    10: [_ACT_TALK_NEW],
    11: [_ACT_BEACH_WALK, _ACT_TALK_NEW],
    12: [_ACT_TALK_NEW],
    13: [_ACT_BAKERY_WALK, _ACT_FRIEND_SINGLE],
    14: [_ACT_BEACH_WALK],
}

_SAUNA_ALONE_ACTIVITY = (
    "early_afternoon",
    "sauna_alone",
    "Sauna — Arrive Alone",
    "Show up at the sauna alone — no escort, no buffer. Half point for going solo.",
    1,
)

_CLUB_NAKED_ACTIVITY = (
    "evening",
    "club_naked",
    "Club — Naked, Shoes Only",
    "Walk into the club wearing nothing but shoes. Half point for pure audacity.",
    1,
)

_CLUB_BONUS_DAYS = {6, 12}


def planned_activity_effective_points(act: tuple) -> float:
    location = act[1]
    if location in HALF_POINT_LOCATIONS:
        return 0.5
    return float(act[4])


def _inject_daily_social(day_cfg: dict) -> dict:
    """Add 1–2 light morning social quests; insert sauna-alone and club-naked where relevant."""
    day = day_cfg["day"]
    core = list(day_cfg["activities"])
    activities: list = list(_MORNING_SOCIAL_BY_DAY.get(day, [_ACT_TALK_NEW]))
    sauna_alone_added = False
    club_naked_added = False

    for act in core:
        if act[1] == "sauna" and not sauna_alone_added:
            activities.append(_SAUNA_ALONE_ACTIVITY)
            sauna_alone_added = True
        if act[1] == "club" and day in _CLUB_BONUS_DAYS and not club_naked_added:
            activities.append(_CLUB_NAKED_ACTIVITY)
            club_naked_added = True
        activities.append(act)

    if not sauna_alone_added:
        activities.append(_SAUNA_ALONE_ACTIVITY)

    planned_target = sum(planned_activity_effective_points(a) for a in activities)
    result = {**day_cfg, "activities": activities, "target": planned_target}
    bonus = day_cfg.get("bonus_target")
    if bonus is not None:
        stretch = float(bonus) - float(day_cfg["target"])
        result["bonus_target"] = planned_target + stretch
    return result


# Fantasy quests — concrete who / do / where; appended to days 8–14.
# Each entry: {"days": [int, ...], "row": (time_slot, location, title, description, points)}
_FANTASY_ACTIVITIES: list[dict] = [
    {
        "days": [8],
        "row": (
            "late_afternoon",
            "bay_of_pigs",
            "Tease Without Giving In",
            "Who: her (you watch). Do: flirt & touch men; stop before sex — she stays in control. "
            "Where: Bay of Pigs beach.",
            3,
        ),
    },
    {
        "days": [8],
        "row": (
            "evening",
            "bay_of_pigs",
            "Attention From Other Men",
            "Who: her + men you approve. Do: draw a crowd; group scene — you set pace & picks. "
            "Where: Bay of Pigs.",
            5,
        ),
    },
    {
        "days": [9],
        "row": (
            "evening",
            "open_door",
            "Blindfold — You Decide",
            "Who: you + her. Do: blindfold her; you choose each next act. Where: rental villa.",
            3,
        ),
    },
    {
        "days": [9],
        "row": (
            "evening",
            "open_door",
            "Blindfold & Sensory Play",
            "Who: you + her. Do: blindfold; ice, feather, touch — no penetration until she asks. "
            "Where: villa.",
            3,
        ),
    },
    {
        "days": [9],
        "row": (
            "special",
            "open_door",
            "Threesome — Another Man",
            "Who: you + her + 1 man (both approve). Do: MFM threesome; acts agreed pre-scene. "
            "Where: villa.",
            5,
        ),
    },
    {
        "days": [9],
        "row": (
            "special",
            "open_door",
            "Threesome — Another Woman",
            "Who: you + her + 1 woman (both approve). Do: FMF threesome; acts agreed pre-scene. "
            "Where: villa.",
            5,
        ),
    },
    {
        "days": [9],
        "row": (
            "evening",
            "open_door",
            "Switch Roles — She Decides",
            "Who: she leads 30+ min. Do: she sets rules & acts; you follow. Where: villa.",
            3,
        ),
    },
    {
        "days": [10],
        "row": (
            "late_afternoon",
            "dunes",
            "Forbidden Fantasy",
            "Who: you + her (+ optional approved third). Do: semi-public scene; risk of being seen is "
            "part of it. Where: dunes path.",
            4,
        ),
    },
    {
        "days": [10],
        "row": (
            "evening",
            "evening",
            "Something Completely New",
            "Who: you + her. Do: one act or venue neither has tried — pick & do same day. "
            "Where: on-site.",
            3,
        ),
    },
    {
        "days": [10],
        "row": (
            "late_afternoon",
            "dunes",
            "Surrender Control",
            "Who: you + her. Do: tie her; she safewords only — full surrender. "
            "Where: dunes or villa.",
            4,
        ),
    },
    {
        "days": [11],
        "row": (
            "evening",
            "party",
            "Another Couple",
            "Who: you + her + 1 couple (both approve). Do: flirt → swap or four-way if chemistry. "
            "Where: Le Glamour or villa.",
            5,
        ),
    },
    {
        "days": [11],
        "row": (
            "late_afternoon",
            "beach",
            "Shower Area Show",
            "Who: her, then you join. Do: playful naked show at beach showers; pull you in. "
            "Where: beach shower area.",
            3,
        ),
    },
    {
        "days": [11],
        "row": (
            "evening",
            "evening",
            "Surprise Evening",
            "Who: you plan, she follows. Do: full evening (venues + people + scene) — no spoilers. "
            "Where: village / clubs.",
            4,
        ),
    },
    {
        "days": [12],
        "row": (
            "evening",
            "club",
            "Sex Swing",
            "Who: you + her. Do: use the club sex swing together. Where: Le Tantra playroom.",
            4,
        ),
    },
    {
        "days": [12],
        "row": (
            "evening",
            "club",
            "Choose a Woman & Watch",
            "Who: she picks, you perform. Do: she chooses a woman on the floor; you have sex while "
            "she watches. Where: Le Tantra.",
            4,
        ),
    },
    {
        "days": [12],
        "row": (
            "evening",
            "club",
            "Be Dominated",
            "Who: you dominate her. Do: commands, restraint, service — limits agreed first. "
            "Where: Tantra or villa.",
            4,
        ),
    },
    {
        "days": [12],
        "row": (
            "evening",
            "club",
            "Be the Dominatrix",
            "Who: she dominates you. Do: she sets rules; you obey (+ guest if she wants). "
            "Where: Tantra or villa.",
            4,
        ),
    },
    {
        "days": [13],
        "row": (
            "evening",
            "bar_party",
            "The Dungeon",
            "Who: you + her. Do: tour cross, sling & gear; one equipment scene if mutual. "
            "Where: Clair Obscur dungeon.",
            3,
        ),
    },
    {
        "days": [13],
        "row": (
            "evening",
            "bar_party",
            "Bondage — Different Ties",
            "Who: you + her. Do: try 2+ tie setups (standing, spread, etc.). "
            "Where: Clair Obscur or villa.",
            3,
        ),
    },
    {
        "days": [13],
        "row": (
            "evening",
            "bar_party",
            "Forced Role-Play",
            "Who: you + her + 1 man (both approve). Do: consensual 'forced' scene with hard limits set. "
            "Where: Clair Obscur backroom.",
            5,
        ),
    },
    {
        "days": [13],
        "row": (
            "evening",
            "bar_party",
            "Consensual Rough Fantasy",
            "Who: you + her + 1 man (both approve). Do: rough scene — pin, intensity per limits. "
            "Where: Clair Obscur or villa.",
            5,
        ),
    },
    {
        "days": [14],
        "row": (
            "early_afternoon",
            "gym",
            "Public Gym Show",
            "Who: you + her. Do: naked workout becomes tease/show in the gym area. Where: village gym.",
            1,
        ),
    },
    {
        "days": [14],
        "row": (
            "afternoon",
            "sauna",
            "Sauna Fantasy — Open Door",
            "Who: you + her + men you approve. Do: fuck her with sauna cabin door open; invite "
            "approved men in. Where: Histoires d'O.",
            5,
        ),
    },
]


def _inject_fantasy_activities(day_cfg: dict) -> dict:
    day = day_cfg["day"]
    extras = [f["row"] for f in _FANTASY_ACTIVITIES if day in f["days"]]
    if not extras:
        return day_cfg
    activities = list(day_cfg["activities"]) + extras
    planned_target = sum(planned_activity_effective_points(a) for a in activities)
    result = {**day_cfg, "activities": activities, "target": planned_target}
    bonus = day_cfg.get("bonus_target")
    if bonus is not None:
        stretch = float(bonus) - float(day_cfg["target"])
        result["bonus_target"] = planned_target + stretch
    return result


FOURTEEN_DAY_PLAN = [
    _inject_fantasy_activities(_inject_daily_social(d)) for d in _CORE_DAY_PLANS
]

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap');

:root {
    --dl-green: #58CC02;
    --dl-green-dark: #46A302;
    --dl-yellow: #FFC800;
    --dl-yellow-dark: #E5B400;
    --dl-blue: #1CB0F6;
    --dl-blue-dark: #1899D6;
    --dl-orange: #FF9600;
    --dl-red: #FF4B4B;
    --dl-purple: #CE82FF;
    --dl-bg: #FFFFFF;
    --dl-bg-soft: #F7F9FC;
    --dl-text: #3C3C3C;
    --dl-muted: #777777;
    --dl-border: #E5E5E5;
    --dl-shadow: 0 4px 0 rgba(0,0,0,0.12);
    --dl-shadow-sm: 0 3px 0 rgba(0,0,0,0.10);
}

.stApp {
    background: linear-gradient(180deg, #EAF6FF 0%, #FFF9E6 45%, #FFFFFF 100%);
    color: var(--dl-text);
    font-family: Nunito, system-ui, sans-serif;
}
.block-container { padding-top: 0.75rem; max-width: 1200px; }
header[data-testid="stHeader"] { background: transparent; }
div[data-testid="stToolbar"] { display: none; }

/* ── HUD bar ── */
.dl-hud {
    display: flex; gap: 0.55rem; flex-wrap: wrap;
    margin: 0.5rem 0 1rem; align-items: stretch;
}
.dl-pill {
    flex: 1; min-width: 100px;
    background: white; border: 2px solid var(--dl-border);
    border-radius: 16px; padding: 0.55rem 0.75rem;
    box-shadow: var(--dl-shadow-sm);
    display: flex; align-items: center; gap: 0.45rem;
}
.dl-pill.xp { border-color: var(--dl-yellow-dark); background: #FFF8E1; }
.dl-pill.streak { border-color: var(--dl-orange); background: #FFF3E0; }
.dl-pill.gems { border-color: var(--dl-blue-dark); background: #E8F7FF; }
.dl-pill-icon { font-size: 1.45rem; line-height: 1; }
.cj-loc-icon-img {
    display: inline-block; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.28);
    border: 1.5px solid rgba(255,255,255,0.35);
}
.cj-loc-chip .cj-loc-icon-img { margin-right: 0.15rem; }
.cj-quest-row {
    display: flex; gap: 0.85rem; align-items: flex-start;
}
.cj-quest-hero {
    flex-shrink: 0; width: 96px; height: 96px;
    border-radius: 16px; overflow: hidden;
    border: 2.5px solid; box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}
.cj-quest-hero.featured {
    width: 100%; max-width: 100%; height: 200px;
    border-radius: 18px; border-width: 3px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.28);
    margin-bottom: 0.65rem;
}
.cj-quest-hero img {
    width: 100%; height: 100%; object-fit: cover; object-position: center top;
    display: block;
}
.cj-quest-hero.dual {
    display: flex; flex-direction: column; gap: 2px;
}
.cj-quest-hero.dual img {
    flex: 1; min-height: 0; width: 100%; height: auto;
    object-position: center center;
}
.cj-quest-body { flex: 1; min-width: 0; }
.dl-pill-label { font-size: 0.62rem; font-weight: 800; text-transform: uppercase; color: var(--dl-muted); letter-spacing: 0.04em; }
.dl-pill-value { font-family: Fredoka, sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--dl-text); line-height: 1.1; }

/* ── Mascot + bubble ── */
.dl-hero {
    display: flex; align-items: center; gap: 1.35rem;
    background: linear-gradient(135deg, #1a1020 0%, #2d1838 45%, #1f1528 100%);
    border: 2px solid #3d2548; border-radius: 24px; padding: 1.15rem 1.25rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.22); margin-bottom: 1rem;
    color: #f5eef8;
}
.cj-brand-hero .cj-brand-frame { flex-shrink: 0; }
.cj-brand-hero .dl-bubble {
    background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.14);
}
.cj-brand-hero .dl-bubble-title { color: #ffc800; }
.cj-brand-hero .dl-bubble-text { color: #ece4f0; }
.cj-brand-hero .dl-tagline { color: #b8a8c4; }
.cj-brand-frame {
    flex-shrink: 0; border-radius: 50%; padding: 5px;
    background: linear-gradient(145deg, #c8c8d0, #3a3a42 35%, #1a1a1e 70%, #888);
    box-shadow: 0 8px 28px rgba(0,0,0,0.45), 0 0 0 2px rgba(255,255,255,0.12);
    position: relative;
}
.cj-brand-photo-wrap {
    position: relative; border-radius: 50%; overflow: hidden;
    line-height: 0;
}
.cj-brand-frame.warm {
    background: linear-gradient(145deg, #ffc800, #e07a5f, #8b1a1a);
    box-shadow: 0 8px 28px rgba(224,122,95,0.45), 0 0 16px rgba(255,200,0,0.25);
}
.cj-brand-frame.hot {
    background: linear-gradient(145deg, #ffd700, #ffc800, #e84393);
    animation: dlPulse 2s ease-in-out infinite;
    box-shadow: 0 8px 32px rgba(255,200,0,0.5), 0 0 20px rgba(232,67,147,0.35);
}
.cj-brand-frame.earned {
    background: linear-gradient(145deg, #ffd700, #46a302, #ffc800);
    animation: dlCelebrate 1.4s ease-in-out infinite;
    box-shadow: 0 10px 36px rgba(255,215,0,0.55), 0 0 24px rgba(70,163,2,0.35);
}
.cj-brand-portrait {
    display: block; border-radius: 50%; object-fit: cover;
    object-position: center 40%; border: 2px solid rgba(0,0,0,0.4);
}
.cj-brand-frame.sm { padding: 4px; }
.cj-brand-md, .cj-brand-lg { padding: 6px; }
.cj-brand-path-hero .cj-brand-frame {
    box-shadow: 0 10px 32px rgba(70,163,2,0.35), 0 0 0 3px rgba(88,204,2,0.25);
}
.cj-day-venue-strip {
    display: flex; gap: 0.25rem; flex-wrap: wrap;
    margin: 0.35rem 0 0.15rem;
}
.cj-day-venue-strip .cj-loc-icon-img {
    border-radius: 7px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.dl-path-node-icon.img .cj-loc-icon-img {
    width: 52px !important; height: 52px !important;
    border-radius: 12px !important;
}
.dl-mascot {
    font-size: 3.2rem; line-height: 1;
    animation: dlBounce 2.2s ease-in-out infinite;
    filter: drop-shadow(0 4px 0 rgba(0,0,0,0.08));
}
.dl-bubble {
    flex: 1; background: var(--dl-bg-soft);
    border: 2px solid var(--dl-border); border-radius: 18px;
    padding: 0.75rem 0.95rem; position: relative;
}
.dl-bubble-title {
    font-family: Fredoka, sans-serif; font-size: 1.45rem; font-weight: 700;
    color: var(--dl-green-dark); margin-bottom: 0.15rem;
}
.dl-bubble-text { font-size: 0.92rem; color: var(--dl-text); line-height: 1.45; }
.dl-tagline { color: var(--dl-muted); font-size: 0.82rem; margin-top: 0.25rem; }

/* ── XP / level bar ── */
.dl-level-wrap { margin: 0.5rem 0 0.85rem; }
.cj-level-journey {
    display: flex; align-items: center; gap: 0.85rem;
    margin: 0.5rem 0 0.85rem;
}
.cj-level-center { flex: 1; min-width: 120px; }
.cj-journey-milestone {
    flex-shrink: 0; text-align: center; max-width: 118px;
}
.cj-journey-photo {
    border-radius: 14px; overflow: hidden;
    border: 3px solid var(--dl-border);
    box-shadow: 0 5px 16px rgba(0,0,0,0.18);
    line-height: 0;
}
.cj-journey-photo img {
    display: block; object-fit: cover; object-position: center 18%;
}
.cj-journey-milestone.start .cj-journey-photo img { object-position: center 22%; }
.cj-journey-milestone.end .cj-journey-photo img { object-position: center 12%; }
.cj-journey-milestone.start .cj-journey-photo {
    border-color: #c8c8d0;
    opacity: 0.92;
}
.cj-journey-milestone.end .cj-journey-photo {
    border-color: var(--dl-green-dark);
    box-shadow: 0 6px 20px rgba(70,163,2,0.28), 0 0 0 2px rgba(88,204,2,0.2);
}
.cj-journey-label {
    font-family: Fredoka, sans-serif; font-size: 0.62rem; font-weight: 700;
    color: var(--dl-muted); margin-top: 0.3rem; line-height: 1.2;
}
.cj-journey-milestone.end .cj-journey-label { color: var(--dl-green-dark); }
.dl-level-top {
    display: flex; justify-content: space-between; align-items: center;
    font-family: Fredoka, sans-serif; font-size: 0.95rem; font-weight: 600;
    margin-bottom: 0.35rem;
}
.dl-level-bar {
    height: 18px; border-radius: 999px; background: #E5E5E5;
    overflow: hidden; border: 2px solid #D0D0D0;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.08);
}
.dl-level-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, var(--dl-green) 0%, #7AE000 100%);
    transition: width 0.8s cubic-bezier(.34,1.56,.64,1);
    box-shadow: inset 0 -2px 0 rgba(0,0,0,0.12);
}
.dl-level-fill.gold {
    background: linear-gradient(90deg, var(--dl-yellow) 0%, #FFE566 100%);
}

/* ── Journey path (Duolingo nodes) ── */
.dl-path-section { margin: 1rem 0; }
.dl-path-title {
    font-family: Fredoka, sans-serif; font-size: 1.2rem; font-weight: 700;
    color: var(--dl-text); margin-bottom: 0.75rem;
}
.dl-path-row {
    display: flex; justify-content: center; align-items: center;
    gap: 0.35rem; flex-wrap: wrap; margin-bottom: 0.65rem;
}
.dl-node-wrap { display: flex; flex-direction: column; align-items: center; width: 72px; }
.dl-node {
    width: 58px; height: 58px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem; font-weight: 800; font-family: Fredoka, sans-serif;
    border: 3px solid #D0D0D0; background: #ECECEC; color: #AFAFAF;
    box-shadow: 0 4px 0 #C0C0C0; position: relative;
    transition: transform 0.15s ease;
}
.dl-node.met {
    background: var(--dl-green); border-color: var(--dl-green-dark);
    color: white; box-shadow: 0 4px 0 var(--dl-green-dark);
}
.dl-node.exceeded {
    background: linear-gradient(145deg, #FFD700 0%, #FFC800 100%);
    border-color: var(--dl-yellow-dark);
    color: #5C4A00; box-shadow: 0 4px 0 var(--dl-yellow-dark);
}
.dl-node.complete {
    background: var(--dl-green); border-color: var(--dl-green-dark);
    color: white; box-shadow: 0 4px 0 var(--dl-green-dark);
}
.dl-node.current {
    background: var(--dl-blue); border-color: var(--dl-blue-dark);
    color: white; box-shadow: 0 4px 0 var(--dl-blue-dark);
    animation: dlPulse 1.5s ease-in-out infinite;
}
.dl-node-label {
    font-size: 0.58rem; font-weight: 700; color: var(--dl-muted);
    margin-top: 0.3rem; text-align: center; line-height: 1.15;
    max-width: 68px;
}
.dl-connector {
    width: 18px; height: 4px; background: #D8D8D8; border-radius: 999px;
    margin-bottom: 1.1rem;
}
.dl-connector.done, .dl-connector.met { background: var(--dl-green); }
.dl-connector.exceeded { background: var(--dl-yellow); }

/* ── Adventure path (Duolingo-style map) ── */
.dl-adventure-map {
    background: linear-gradient(165deg, #B8E6FF 0%, #D4F5C8 35%, #FFF3B0 70%, #FFE8CC 100%);
    border: 3px solid var(--dl-green-dark);
    border-radius: 28px;
    padding: 1.25rem 0.75rem 1.5rem;
    box-shadow: 0 6px 0 var(--dl-green-dark);
    margin: 0.5rem 0 1.25rem;
    position: relative;
    overflow: hidden;
}
.dl-adventure-map::before {
    content: ""; position: absolute; inset: 0;
    background: radial-gradient(circle at 20% 30%, rgba(255,255,255,0.45) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(255,255,255,0.35) 0%, transparent 45%);
    pointer-events: none;
}
.dl-path-hero {
    background: linear-gradient(135deg, #FFFFFF 0%, #F0FFE4 100%);
    border: 3px solid var(--dl-green-dark);
    border-radius: 24px;
    padding: 1.15rem 1.25rem;
    box-shadow: 0 5px 0 var(--dl-green-dark);
    margin-bottom: 1rem;
    display: flex; align-items: center; gap: 1.25rem; flex-wrap: wrap;
}
.cj-journey-unified-hero {
    display: flex; align-items: stretch; gap: 0.65rem;
    background: linear-gradient(135deg, #FFFFFF 0%, #F0FFE4 100%);
    border: 3px solid var(--dl-green-dark);
    border-radius: 20px;
    padding: 0.7rem 0.8rem;
    box-shadow: 0 5px 0 var(--dl-green-dark);
    margin-bottom: 0.85rem;
}
.cj-journey-unified-body { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
.cj-journey-unified-photo {
    flex-shrink: 0; display: flex; align-items: center; justify-content: center;
}
.cj-journey-unified-stats {
    color: var(--dl-muted); font-size: 0.74rem; font-weight: 700;
    margin-top: 0.12rem; line-height: 1.35;
}
.cj-journey-unified-today {
    font-size: 0.72rem; font-weight: 600; color: #555;
    margin-top: 0.25rem; line-height: 1.3;
}
.cj-journey-unified-hero .dl-path-hero-title {
    font-size: 1.25rem; line-height: 1.12;
}
.cj-journey-unified-hero .dl-collar-trail {
    margin: 0.32rem 0 0.1rem; justify-content: flex-start; gap: 0.14rem;
}
.cj-journey-unified-hero .dl-collar-seg {
    width: 17px; height: 17px; font-size: 0.48rem;
}
.cj-journey-unified-hero .dl-collar-end { font-size: 1.15rem; margin-left: 0.15rem; }
.cj-journey-unified-hero .cj-brand-frame {
    box-shadow: 0 6px 18px rgba(70,163,2,0.28), 0 0 0 2px rgba(88,204,2,0.22);
}
.cj-journey-unified-level {
    margin: 0.28rem 0 0.12rem;
}
.cj-journey-unified-hero .cj-level-journey.compact {
    margin: 0; gap: 0.4rem;
}
.cj-journey-unified-hero .cj-level-journey.compact .cj-journey-milestone {
    max-width: 68px;
}
.cj-journey-unified-hero .cj-level-journey.compact .cj-journey-label {
    font-size: 0.5rem; margin-top: 0.18rem;
}
.cj-journey-unified-hero .cj-level-journey.compact .dl-level-top.compact {
    font-size: 0.64rem; margin-bottom: 0.15rem;
}
.cj-journey-unified-hero .cj-level-journey.compact .dl-level-bar {
    height: 11px; border-width: 1px;
}
.cj-journey-unified-photo.venue {
    width: 76px; flex-shrink: 0; align-self: center;
    border-radius: 12px; overflow: hidden;
    border: 2px solid rgba(88,204,2,0.45);
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
    line-height: 0;
}
.cj-journey-unified-photo.venue img {
    width: 76px; height: 88px; object-fit: cover; object-position: center top;
    display: block;
}
.cj-journey-venue-cap {
    font-size: 0.48rem; font-weight: 800; text-align: center;
    padding: 0.18rem 0.15rem; background: rgba(240,255,228,0.95);
    color: var(--dl-green-dark); line-height: 1.15;
}
.cj-rich-bar-level {
    margin-top: 0.45rem; padding-top: 0.45rem;
    border-top: 1px solid rgba(255,255,255,0.14);
}
.cj-rich-bar-level .cj-level-journey.compact { margin: 0; gap: 0.35rem; }
.cj-rich-bar-level .cj-level-journey.compact .cj-journey-milestone { max-width: 58px; }
.cj-rich-bar-level .cj-level-journey.compact .cj-journey-label {
    color: #b8a8c4; font-size: 0.48rem;
}
.cj-rich-bar-level .cj-level-journey.compact .dl-level-top.compact {
    color: #e8dce8; font-size: 0.62rem; margin-bottom: 0.12rem;
}
.cj-rich-bar-level .cj-level-journey.compact .dl-level-bar {
    height: 10px; border-color: rgba(255,255,255,0.22); background: rgba(0,0,0,0.25);
}
.dl-path-hero-title {
    font-family: Fredoka, sans-serif; font-size: 1.75rem; font-weight: 700;
    color: var(--dl-green-dark); line-height: 1.15;
}
.dl-path-hero-sub { color: var(--dl-muted); font-size: 0.88rem; font-weight: 600; margin-top: 0.2rem; }
.dl-collar-trail {
    display: flex; align-items: center; gap: 0.2rem; flex-wrap: wrap;
    margin: 0.75rem 0 1rem; justify-content: center;
}
.dl-collar-seg {
    width: 22px; height: 22px; border-radius: 50%;
    border: 2px solid #C0C0C0; background: #ECECEC;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.55rem; font-weight: 800; color: #999;
    box-shadow: 0 2px 0 #B0B0B0;
}
.dl-collar-seg.met { background: var(--dl-green); border-color: var(--dl-green-dark); color: white; box-shadow: 0 2px 0 var(--dl-green-dark); }
.dl-collar-seg.exceeded { background: var(--dl-yellow); border-color: var(--dl-yellow-dark); color: #5C4A00; box-shadow: 0 2px 0 var(--dl-yellow-dark); }
.dl-collar-seg.current { background: var(--dl-blue); border-color: var(--dl-blue-dark); color: white; animation: dlPulse 1.5s ease-in-out infinite; }
.dl-collar-end { font-size: 1.6rem; margin-left: 0.35rem; filter: drop-shadow(0 2px 0 rgba(0,0,0,0.15)); }
.dl-milestone-banner {
    text-align: center; margin: 0.65rem auto; max-width: 420px;
    background: white; border: 2px dashed var(--dl-purple);
    border-radius: 16px; padding: 0.45rem 0.85rem;
    font-family: Fredoka, sans-serif; font-weight: 700; font-size: 0.82rem;
    color: #7B5BA6; box-shadow: 0 3px 0 rgba(206,130,255,0.35);
}
.dl-milestone-banner.gold {
    border-color: var(--dl-yellow-dark); color: #8B6914;
    background: linear-gradient(90deg, #FFF8E1, #FFFFFF);
    box-shadow: 0 3px 0 var(--dl-yellow-dark);
}
.dl-path-lane { display: flex; justify-content: center; margin: 0.15rem 0; position: relative; z-index: 1; }
.dl-path-lane.left { justify-content: flex-start; padding-left: 4%; }
.dl-path-lane.right { justify-content: flex-end; padding-right: 4%; }
.dl-path-lane.center { justify-content: center; }
.dl-path-vline {
    width: 5px; height: 22px; border-radius: 999px; background: #C8C8C8;
    margin: 0 auto;
}
.dl-path-vline.met, .dl-path-vline.exceeded { background: var(--dl-green); }
.dl-path-node-card {
    width: 100%; max-width: 300px;
    background: white; border: 3px solid #D0D0D0;
    border-radius: 22px; padding: 0.75rem 0.9rem 0.65rem;
    box-shadow: 0 5px 0 #B8B8B8;
    position: relative; transition: transform 0.12s ease;
}
.dl-path-node-card:hover { transform: translateY(-2px); }
.dl-path-node-card.met {
    border-color: var(--dl-green-dark); box-shadow: 0 5px 0 var(--dl-green-dark);
    background: linear-gradient(160deg, #F0FFE4 0%, #FFFFFF 55%);
}
.dl-path-node-card.exceeded {
    border-color: var(--dl-yellow-dark); box-shadow: 0 5px 0 var(--dl-yellow-dark);
    background: linear-gradient(160deg, #FFF8E1 0%, #FFFFFF 60%);
}
.dl-path-node-card.current {
    border-color: var(--dl-blue-dark); box-shadow: 0 5px 0 var(--dl-blue-dark);
    animation: dlPulse 2s ease-in-out infinite;
}
.dl-path-node-card.current::after {
    content: "YOU ARE HERE";
    display: block; text-align: center;
    font-family: Fredoka, sans-serif; font-size: 0.62rem; font-weight: 800;
    letter-spacing: 0.06em; color: var(--dl-blue-dark);
    margin-top: 0.35rem;
}
.dl-path-node-card.chest { border-color: #B8860B; }
.dl-path-node-card.chest.met, .dl-path-node-card.chest.exceeded {
    border-color: #DAA520; box-shadow: 0 5px 0 #B8860B, 0 0 12px rgba(255,200,0,0.35);
}
.dl-path-node-card.finale {
    border-color: var(--dl-yellow-dark);
    background: linear-gradient(145deg, #FFF8E1, #FFFFFF);
    box-shadow: 0 6px 0 var(--dl-yellow-dark);
}
.dl-path-node-top { display: flex; align-items: flex-start; gap: 0.65rem; }
.dl-path-node-icon {
    font-size: 2.1rem; line-height: 1; flex-shrink: 0;
    filter: drop-shadow(0 2px 0 rgba(0,0,0,0.1));
}
.dl-path-node-head { flex: 1; min-width: 0; }
.dl-path-node-day {
    font-family: Fredoka, sans-serif; font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em; color: var(--dl-muted);
}
.dl-path-node-title {
    font-family: Fredoka, sans-serif; font-size: 1.05rem; font-weight: 700;
    color: var(--dl-text); line-height: 1.15; margin: 0.1rem 0;
}
.dl-path-node-reward {
    font-size: 0.72rem; font-weight: 700; color: var(--dl-orange);
}
.dl-path-node-badge {
    position: absolute; top: -0.45rem; right: 0.65rem;
    font-size: 0.62rem; font-weight: 800; padding: 0.12rem 0.45rem;
    border-radius: 999px; border: 2px solid; background: white;
}
.dl-path-node-badge.start { border-color: var(--dl-green-dark); color: var(--dl-green-dark); }
.dl-path-node-badge.chest { border-color: #DAA520; color: #8B6914; background: #FFF8E1; }
.dl-path-node-badge.checkpoint { border-color: var(--dl-blue-dark); color: var(--dl-blue-dark); }
.dl-path-node-badge.finale { border-color: var(--dl-yellow-dark); color: #8B6914; background: #FFFBEB; }
.dl-path-mini-bar {
    height: 10px; border-radius: 999px; background: #ECECEC;
    border: 1.5px solid #DDD; overflow: hidden; margin: 0.45rem 0 0.25rem;
}
.dl-path-mini-fill {
    height: 100%; border-radius: 999px; background: var(--dl-blue);
    transition: width 0.3s ease;
}
.dl-path-mini-fill.met { background: var(--dl-green); }
.dl-path-mini-fill.exceeded { background: linear-gradient(90deg, var(--dl-yellow), #FFE566); }
.dl-path-node-stats {
    display: flex; justify-content: space-between; font-size: 0.68rem;
    font-weight: 700; color: var(--dl-muted);
}
.dl-path-status-pill {
    display: inline-block; font-size: 0.65rem; font-weight: 800;
    padding: 0.15rem 0.5rem; border-radius: 999px; margin-top: 0.35rem;
}
.dl-path-status-pill.pending { background: #E8F7FF; color: var(--dl-blue-dark); border: 1.5px solid var(--dl-blue-dark); }
.dl-path-status-pill.met { background: #E8FFD6; color: var(--dl-green-dark); border: 1.5px solid var(--dl-green-dark); }
.dl-path-status-pill.exceeded { background: #FFF8E1; color: #8B6914; border: 1.5px solid var(--dl-yellow-dark); }
.dl-path-status-pill.current { background: var(--dl-blue); color: white; border: 1.5px solid var(--dl-blue-dark); }
.dl-rewards-row {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.55rem; margin: 0.75rem 0;
}
.dl-reward-card {
    background: white; border: 2px solid var(--dl-border);
    border-radius: 16px; padding: 0.65rem 0.55rem; text-align: center;
    box-shadow: var(--dl-shadow-sm);
}
.dl-reward-card.unlocked {
    border-color: var(--dl-yellow-dark); background: #FFFBEB;
    box-shadow: 0 4px 0 var(--dl-yellow-dark);
}
.dl-reward-card.locked { opacity: 0.5; filter: grayscale(0.85); }
.dl-reward-icon { font-size: 1.75rem; line-height: 1.1; }
.dl-reward-name { font-family: Fredoka, sans-serif; font-size: 0.78rem; font-weight: 700; margin-top: 0.2rem; }
.dl-reward-desc { font-size: 0.62rem; color: var(--dl-muted); font-weight: 600; line-height: 1.2; margin-top: 0.15rem; }
.dl-loot-bar {
    display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.5rem;
}
.dl-loot-item {
    display: inline-flex; align-items: center; gap: 0.3rem;
    background: white; border: 2px solid var(--dl-border);
    border-radius: 999px; padding: 0.3rem 0.65rem;
    font-size: 0.78rem; font-weight: 700; box-shadow: var(--dl-shadow-sm);
}
.dl-section-head {
    font-family: Fredoka, sans-serif; font-size: 1.25rem; font-weight: 700;
    color: var(--dl-text); margin: 1.1rem 0 0.55rem;
    display: flex; align-items: center; gap: 0.4rem;
}

/* ── Cards & quests ── */
.cj-card, .dl-quest {
    background: white; border: 2px solid var(--dl-border);
    border-radius: 18px; padding: 1rem 1.1rem; margin-bottom: 0.7rem;
    box-shadow: var(--dl-shadow-sm);
}
.cj-day-met, .dl-quest.day-met {
    border-color: var(--dl-green-dark) !important;
    background: linear-gradient(135deg, #F0FFE4 0%, #FFFFFF 100%) !important;
    box-shadow: 0 4px 0 var(--dl-green-dark) !important;
}
.cj-day-exceeded, .dl-quest.day-exceeded {
    border-color: var(--dl-yellow-dark) !important;
    background: linear-gradient(135deg, #FFF8E1 0%, #FFFBEB 50%, #FFFFFF 100%) !important;
    box-shadow: 0 4px 0 var(--dl-yellow-dark) !important;
}
.cj-day-complete, .dl-quest.done {
    border-color: var(--dl-green-dark) !important;
    background: linear-gradient(135deg, #F0FFE4 0%, #FFFFFF 100%) !important;
    box-shadow: 0 4px 0 var(--dl-green-dark) !important;
}
.dl-quest.pending { border-color: var(--dl-blue-dark); background: linear-gradient(135deg, #E8F7FF 0%, #FFFFFF 100%); }
.dl-quest.pending.focused {
    border-color: var(--dl-orange) !important;
    border-width: 3px !important;
    box-shadow: 0 5px 0 var(--dl-orange), 0 0 0 3px rgba(253,121,168,0.25) !important;
}
.cj-quest-nav {
    background: white; border: 2px solid var(--dl-blue-dark);
    border-radius: 18px; padding: 0.85rem 1rem; margin: 0.75rem 0 1rem;
    box-shadow: 0 4px 0 var(--dl-blue-dark);
}
.cj-quest-nav-title {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.35rem;
    font-family: Fredoka, sans-serif; font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;
}
.cj-quest-nav-left {
    background: var(--dl-orange); color: white; padding: 0.15rem 0.55rem;
    border-radius: 999px; font-size: 0.85rem;
}
.cj-quest-nav-done { color: var(--dl-green-dark); font-weight: 800; }
.cj-quest-section-label {
    font-family: Fredoka, sans-serif; font-size: 0.95rem; font-weight: 700;
    color: var(--dl-text); margin: 0.5rem 0 0.35rem;
}
.cj-done-compact {
    background: #F0FFE4; border: 2px solid var(--dl-green-dark); border-radius: 14px;
    padding: 0.55rem 0.75rem; margin-bottom: 0.45rem;
}
.cj-day-current {
    border-color: var(--dl-blue-dark) !important;
    box-shadow: 0 4px 0 var(--dl-blue-dark) !important;
    animation: dlPulse 2s ease-in-out infinite;
}
.dl-xp-badge {
    float: right; background: var(--dl-yellow); color: #5C4A00;
    font-family: Fredoka, sans-serif; font-weight: 700; font-size: 0.82rem;
    padding: 0.2rem 0.55rem; border-radius: 999px;
    border: 2px solid var(--dl-yellow-dark);
    box-shadow: 0 2px 0 var(--dl-yellow-dark);
}
.cj-loc-chip {
    display: inline-block; padding: 0.18rem 0.6rem; border-radius: 999px;
    font-size: 0.72rem; font-weight: 800; margin-right: 0.35rem;
    border: 2px solid transparent;
}
.cj-sub-pool { color: var(--dl-orange); font-size: 0.85rem; font-weight: 600; }

/* ── Badges (Duolingo chest style) ── */
.dl-badges { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.cj-badge, .dl-badge {
    display: inline-flex; flex-direction: column; align-items: center;
    background: white; border: 2px solid var(--dl-border);
    border-radius: 16px; padding: 0.55rem 0.5rem; min-width: 82px;
    box-shadow: var(--dl-shadow-sm); font-size: 0.72rem; font-weight: 700;
    text-align: center; line-height: 1.2;
}
.cj-badge.unlocked, .dl-badge.unlocked {
    border-color: var(--dl-yellow-dark); background: #FFFBEB;
    box-shadow: 0 4px 0 var(--dl-yellow-dark);
    animation: dlPop 0.4s ease-out;
}
.cj-badge.locked, .dl-badge.locked { opacity: 0.45; filter: grayscale(0.8); }
.dl-badge-emoji { font-size: 1.5rem; margin-bottom: 0.15rem; }

/* ── Collar win celebration ── */
.cj-collar-win {
    text-align: center; padding: 1.5rem 1rem 2rem;
    background: linear-gradient(135deg, #1a1020, #2d1838 50%, #1f1528);
    border: 3px solid var(--dl-yellow-dark); border-radius: 28px;
    margin: 1rem 0; box-shadow: 0 6px 0 var(--dl-yellow-dark);
    animation: dlCelebrate 1.2s ease-in-out infinite;
    color: #f5eef8;
}
.cj-collar-win .cj-brand-frame {
    margin: 0 auto 0.75rem; display: inline-block;
}
.cj-collar-icon { font-size: 4.5rem; line-height: 1; animation: dlBounce 1s ease-in-out infinite; }

/* ── Calendar cells ── */
.cj-cal-grid {
    display: grid; grid-template-columns: repeat(7, 1fr);
    gap: 0.5rem; margin: 0.75rem 0 1rem;
}
.cj-cal-week-label {
    grid-column: 1 / -1;
    font-family: Fredoka, sans-serif; font-size: 1.05rem; font-weight: 700;
    color: var(--dl-blue-dark); margin: 0.5rem 0 0.1rem;
}
.cj-cal-cell {
    background: white; border: 2px solid var(--dl-border);
    border-radius: 16px; padding: 0.5rem 0.45rem 0.6rem;
    min-height: 140px; position: relative;
    box-shadow: var(--dl-shadow-sm);
}
.cj-cal-cell.today {
    border-color: var(--dl-blue-dark);
    box-shadow: 0 4px 0 var(--dl-blue-dark);
}
.cj-cal-cell.met {
    border-color: var(--dl-green-dark);
    background: linear-gradient(160deg, #F0FFE4, #FFFFFF);
    box-shadow: 0 4px 0 var(--dl-green-dark);
}
.cj-cal-cell.exceeded {
    border-color: var(--dl-yellow-dark);
    background: linear-gradient(160deg, #FFF8E1, #FFFBEB, #FFFFFF);
    box-shadow: 0 4px 0 var(--dl-yellow-dark);
}
.cj-cal-cell.complete {
    border-color: var(--dl-green-dark);
    background: linear-gradient(160deg, #F0FFE4, #FFFFFF);
    box-shadow: 0 4px 0 var(--dl-green-dark);
}
.cj-cal-cell.upcoming, .cj-cal-cell.future {
    border-style: dashed;
    border-color: #B8C9E0;
}
.cj-cal-cell.selected {
    border-color: var(--dl-blue-dark) !important;
    border-style: solid !important;
    box-shadow: 0 4px 0 var(--dl-blue-dark), 0 0 0 2px rgba(28, 176, 246, 0.35) !important;
}
.cj-cal-date { font-size: 0.62rem; font-weight: 700; color: var(--dl-muted); text-transform: uppercase; }
.cj-cal-daynum { font-family: Fredoka, sans-serif; font-size: 1rem; font-weight: 700; color: var(--dl-green-dark); }
.cj-cal-title { font-size: 0.64rem; color: var(--dl-text); margin: 0.1rem 0 0.3rem; line-height: 1.2; min-height: 2.2em; font-weight: 600; }
.cj-cal-progress { height: 8px; border-radius: 999px; background: #ECECEC; overflow: hidden; margin: 0.3rem 0; border: 1px solid #DDD; }
.cj-cal-progress-fill { height: 100%; border-radius: 999px; background: var(--dl-blue); }
.cj-cal-progress-fill.done, .cj-cal-progress-fill.met { background: var(--dl-green); }
.cj-cal-progress-fill.exceeded {
    background: linear-gradient(90deg, var(--dl-yellow) 0%, #FFE566 100%);
}
.cj-cal-stat { font-size: 0.58rem; color: var(--dl-muted); font-weight: 600; }
.cj-cal-ach {
    display: inline-block; font-size: 0.55rem; font-weight: 700;
    padding: 0.08rem 0.32rem; border-radius: 999px; margin: 0.1rem 0.1rem 0 0;
    border: 1.5px solid var(--dl-border); background: var(--dl-bg-soft);
}
.cj-cal-ach.done { border-color: var(--dl-green-dark); background: #E8FFD6; color: var(--dl-green-dark); }
.cj-cal-ach.pending { opacity: 0.4; border-style: dashed; }
.cj-cal-ach.bonus { border-color: var(--dl-yellow-dark); background: #FFF8E1; color: #8B6914; }
.cj-cal-locs { display: flex; flex-wrap: wrap; gap: 0.12rem; margin-top: 0.2rem; }
.cj-cal-trophy { position: absolute; top: 0.3rem; right: 0.35rem; font-size: 1rem; }
.cj-extra-chip {
    display: inline-block; font-size: 0.78rem; font-weight: 700;
    padding: 0.22rem 0.6rem; border-radius: 999px; margin: 0.15rem 0.25rem 0.15rem 0;
    border: 2px solid var(--dl-yellow-dark); background: #FFF8E1; color: #7A5B00;
    box-shadow: 0 2px 0 var(--dl-yellow-dark);
}

/* ── Metrics override ── */
div[data-testid="stMetric"] {
    background: white !important; border: 2px solid var(--dl-border) !important;
    border-radius: 16px !important; padding: 0.5rem 0.75rem !important;
    box-shadow: var(--dl-shadow-sm) !important;
}
div[data-testid="stMetric"] label { color: var(--dl-muted) !important; font-weight: 800 !important; font-size: 0.65rem !important; text-transform: uppercase !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--dl-text) !important;
    font-family: Fredoka, sans-serif !important;
    font-size: 1.4rem !important;
}

/* ── Tabs & buttons feel ── */
.stTabs [data-baseweb="tab-list"] { gap: 0.35rem; }
.stTabs [data-baseweb="tab"] {
    border-radius: 12px 12px 0 0 !important;
    font-family: Fredoka, sans-serif !important; font-weight: 600 !important;
}
.stButton > button {
    border-radius: 14px !important;
    font-family: Fredoka, sans-serif !important;
    font-weight: 700 !important;
    border-bottom-width: 4px !important;
    transition: transform 0.1s ease !important;
}
.stButton > button:active { transform: translateY(2px) !important; border-bottom-width: 2px !important; }

@keyframes dlBounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
@keyframes dlPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.06); }
}
@keyframes dlPop {
    0% { transform: scale(0.8); opacity: 0; }
    70% { transform: scale(1.05); }
    100% { transform: scale(1); opacity: 1; }
}
@keyframes dlCelebrate {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.01); }
}
.cj-pop { animation: dlPop 0.5s ease-out; }

/* ── Celebration toasts & fireworks ── */
.cj-celebrate-toast {
    position: fixed; left: 50%; top: 18%;
    transform: translateX(-50%) translateY(20px) scale(0.92);
    opacity: 0;
    z-index: 1000001;
    pointer-events: none;
    min-width: 240px; max-width: 92vw;
    padding: 0.95rem 1.25rem 1rem;
    border-radius: 22px;
    border: 3px solid var(--dl-yellow-dark);
    background: linear-gradient(135deg, #FFFBEB, #FFFFFF 55%, #F0FFE4);
    box-shadow: 0 8px 0 rgba(0,0,0,0.14), 0 16px 40px rgba(0,0,0,0.18);
    font-family: Fredoka, Nunito, sans-serif;
    text-align: center;
    animation: cjToastIn 0.55s cubic-bezier(.2,1.1,.3,1) forwards;
}
.cj-celebrate-toast.quest { border-color: var(--dl-green-dark); background: linear-gradient(135deg, #F0FFE4, #FFFFFF); }
.cj-celebrate-toast.bonus { border-color: var(--dl-orange); background: linear-gradient(135deg, #FFF3E0, #FFFFFF); }
.cj-celebrate-toast.day_complete, .cj-celebrate-toast.stretch {
    border-color: var(--dl-blue-dark); background: linear-gradient(135deg, #EAF6FF, #FFFFFF);
}
.cj-celebrate-toast.achievement {
    border-color: #B8860B; background: linear-gradient(135deg, #FFF8E1, #FFFBEB, #FFFFFF);
    animation: cjToastIn 0.55s cubic-bezier(.2,1.1,.3,1) forwards, cjTrophyPulse 1.2s ease-in-out 0.55s 2;
}
.cj-celebrate-emoji { font-size: 2.4rem; line-height: 1; margin-bottom: 0.2rem; }
.cj-celebrate-title {
    font-size: 1.2rem; font-weight: 700; color: var(--dl-text);
    margin-bottom: 0.15rem;
}
.cj-celebrate-sub { font-size: 0.82rem; font-weight: 700; color: var(--dl-muted); }
@keyframes cjToastIn {
    0% { opacity: 0; transform: translateX(-50%) translateY(30px) scale(0.85); }
    100% { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}
@keyframes cjTrophyPulse {
    0%, 100% { transform: translateX(-50%) translateY(0) scale(1); }
    50% { transform: translateX(-50%) translateY(-4px) scale(1.03); }
}

/* ── Streamlit widget skin (game UI) ── */
.stButton > button {
    font-family: Fredoka, Nunito, sans-serif !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
    padding: 0.45rem 1rem !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(180deg, #65d102 0%, var(--dl-green) 100%) !important;
    color: white !important;
    border: 2px solid var(--dl-green-dark) !important;
    box-shadow: 0 4px 0 var(--dl-green-dark) !important;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 0 var(--dl-green-dark) !important;
}
.stButton > button[kind="primary"]:active, .stButton > button[data-testid="stBaseButton-primary"]:active {
    transform: translateY(3px) !important;
    box-shadow: 0 1px 0 var(--dl-green-dark) !important;
}
.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"] {
    background: white !important;
    color: var(--dl-text) !important;
    border: 2px solid var(--dl-border) !important;
    box-shadow: 0 3px 0 #ccc !important;
}
.stButton > button[kind="secondary"]:active, .stButton > button[data-testid="stBaseButton-secondary"]:active {
    transform: translateY(2px) !important;
    box-shadow: 0 1px 0 #ccc !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0.35rem !important;
    flex-wrap: wrap !important;
    background: white;
    border: 2px solid var(--dl-border);
    border-radius: 18px;
    padding: 0.4rem 0.5rem;
    box-shadow: var(--dl-shadow-sm);
}
div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: var(--dl-bg-soft) !important;
    border: 2px solid var(--dl-border) !important;
    border-radius: 12px !important;
    padding: 0.35rem 0.7rem !important;
    margin: 0 !important;
    font-family: Fredoka, sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: var(--dl-blue) !important;
    border-color: var(--dl-blue-dark) !important;
    color: white !important;
    box-shadow: 0 3px 0 var(--dl-blue-dark) !important;
}
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 2px solid var(--dl-border) !important;
    font-family: Nunito, sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: var(--dl-blue-dark) !important;
    box-shadow: 0 0 0 2px rgba(28, 176, 246, 0.25) !important;
}
.stMultiSelect div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 2px solid var(--dl-border) !important;
}
.stExpander {
    border: 2px solid var(--dl-green-dark) !important;
    border-radius: 16px !important;
    background: #F0FFE4 !important;
    box-shadow: 0 3px 0 var(--dl-green-dark) !important;
}
.stExpander summary {
    font-family: Fredoka, sans-serif !important;
    font-weight: 700 !important;
}

/* ── Focused quest venue scene ── */
.cj-quest-scene {
    position: relative; border-radius: 22px; overflow: hidden;
    margin-bottom: 0.85rem;
    border: 3px solid var(--dl-orange);
    box-shadow: 0 6px 0 var(--dl-orange), 0 12px 32px rgba(0,0,0,0.12);
}
.cj-quest-scene-bg {
    position: absolute; inset: 0;
    overflow: hidden;
    filter: blur(2px) saturate(1.15);
    transform: scale(1.06);
    animation: cjKenBurns 18s ease-in-out infinite alternate;
}
.cj-quest-scene-bg img {
    width: 100%; height: 100%; object-fit: cover; object-position: center;
    display: block;
}
.cj-quest-scene-bg.solid { filter: none; transform: none; animation: none; }
.cj-quest-scene-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(125deg,
        rgba(255,255,255,0.88) 0%,
        rgba(255,255,255,0.72) 42%,
        rgba(255,248,225,0.55) 100%);
}
@keyframes cjKenBurns {
    0% { transform: scale(1.06) translate(0, 0); }
    100% { transform: scale(1.14) translate(-1.5%, -1%); }
}

/* ── Photo banners & mosaic ── */
.cj-photo-layer {
    position: absolute; inset: 0;
    overflow: hidden;
    filter: saturate(1.08);
}
.cj-photo-layer img {
    width: 100%; height: 100%; object-fit: cover; object-position: center top;
    display: block;
}
.cj-photo-layer.ken-burns { animation: cjKenBurns 16s ease-in-out infinite alternate; }
.cj-day-banner {
    position: relative; overflow: hidden; border-radius: 22px;
    min-height: 128px; margin: 0.5rem 0 1rem;
    border: 3px solid var(--dl-blue-dark);
    box-shadow: 0 5px 0 var(--dl-blue-dark);
}
.cj-day-banner-photos { position: absolute; inset: 0; display: flex; }
.cj-day-banner-photos .cj-photo-layer { position: relative; flex: 1; inset: auto; min-height: 128px; }
.cj-day-banner-photos .mosaic-0 { flex: 1.35; }
.cj-day-banner-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(90deg, rgba(26,16,32,0.72) 0%, rgba(26,16,32,0.35) 55%, rgba(26,16,32,0.15) 100%);
}
.cj-day-banner-text {
    position: relative; z-index: 1; padding: 1rem 1.15rem; color: #fff;
}
.cj-day-banner-kicker {
    font-size: 0.72rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.06em; opacity: 0.9;
}
.cj-day-banner-title {
    font-family: Fredoka, sans-serif; font-size: 1.35rem; font-weight: 700;
    line-height: 1.15; margin-top: 0.15rem; text-shadow: 0 2px 8px rgba(0,0,0,0.35);
}

.cj-path-photo-banner {
    position: relative; height: 72px; border-radius: 14px 14px 0 0;
    overflow: hidden; margin: -0.75rem -0.9rem 0.55rem;
}
.cj-path-photo-banner.dual {
    display: flex; flex-direction: row;
}
.cj-path-photo-banner.qakc {
    height: 118px;
}
.cj-path-photo-banner.qakc .cj-photo-layer {
    background-position: center 38%;
}
.cj-path-dual-half {
    flex: 1; height: 72px; background-size: cover; background-position: center top;
}
.cj-path-photo-scrim.light {
    background: linear-gradient(180deg, transparent 35%, rgba(0,0,0,0.45) 100%);
}
.cj-path-photo-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(180deg, transparent 20%, rgba(0,0,0,0.55) 100%);
}
.cj-path-photo-label {
    position: absolute; left: 0.55rem; bottom: 0.35rem; z-index: 1;
    font-size: 0.62rem; font-weight: 800; color: white; text-transform: uppercase;
    letter-spacing: 0.05em; text-shadow: 0 1px 4px rgba(0,0,0,0.5);
}

.cj-cal-cell.has-photo { overflow: hidden; }
.cj-cal-photo-bg {
    position: absolute; inset: 0;
    overflow: hidden;
    opacity: 0.28; filter: saturate(1.1);
}
.cj-cal-photo-bg img {
    width: 100%; height: 100%; object-fit: cover; object-position: center top;
    display: block;
}
.cj-cal-cell.met .cj-cal-photo-bg, .cj-cal-cell.exceeded .cj-cal-photo-bg { opacity: 0.38; }
.cj-cal-photo-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0.92) 68%);
}
.cj-cal-cell.met .cj-cal-photo-scrim {
    background: linear-gradient(180deg, rgba(240,255,228,0.45) 0%, rgba(255,255,255,0.94) 68%);
}
.cj-cal-content { position: relative; z-index: 1; }

.cj-quest-pick-card {
    display: flex; gap: 0.55rem; align-items: center;
    background: white; border: 2px solid var(--dl-border);
    border-radius: 14px; padding: 0.45rem 0.55rem; margin-bottom: 0.35rem;
    box-shadow: var(--dl-shadow-sm);
}
.cj-quest-pick-tile {
    border: 2px solid var(--dl-border); border-radius: 16px;
    overflow: hidden; margin-bottom: 0.35rem;
    box-shadow: var(--dl-shadow-sm); background: white;
}
.cj-quest-pick-tile.selected {
    border-color: var(--dl-orange); box-shadow: 0 4px 0 var(--dl-orange);
}
.cj-quest-pick-tile-img {
    width: 100%; height: 180px; object-fit: cover; object-position: center top;
    display: block;
}
.cj-quest-pick-tile-emoji {
    height: 180px; display: flex; align-items: center; justify-content: center;
    font-size: 3rem; background: var(--dl-bg-soft);
}
.cj-quest-pick-tile-meta {
    padding: 0.4rem 0.55rem 0.45rem;
    font-family: Fredoka, sans-serif; font-size: 0.72rem; font-weight: 700;
    color: var(--dl-muted); text-align: center;
}
.cj-quest-pick-card.selected {
    border-color: var(--dl-orange); box-shadow: 0 3px 0 var(--dl-orange);
}
.cj-quest-pick-thumb {
    width: 52px; height: 52px; border-radius: 10px; overflow: hidden; flex-shrink: 0;
    border: 2px solid rgba(0,0,0,0.12); box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.cj-quest-pick-thumb img { width: 100%; height: 100%; object-fit: cover; object-position: center top; }
.cj-quest-pick-emoji { font-size: 1.6rem; line-height: 52px; text-align: center; display: block; }
.cj-quest-pick-body { min-width: 0; flex: 1; }
.cj-quest-pick-xp {
    font-family: Fredoka, sans-serif; font-size: 0.68rem; font-weight: 700;
    color: #8B6914; background: var(--dl-yellow); display: inline-block;
    padding: 0.05rem 0.35rem; border-radius: 999px; border: 1px solid var(--dl-yellow-dark);
}
.cj-quest-pick-title {
    font-family: Fredoka, sans-serif; font-size: 0.78rem; font-weight: 700;
    color: var(--dl-text); line-height: 1.15; margin-top: 0.12rem;
}
.cj-quest-pick-slot { font-size: 0.62rem; font-weight: 700; color: var(--dl-muted); }

.cj-quest-day-grid { margin: 0.15rem 0 0.65rem; }
.cj-quest-day-tile {
    position: relative;
    border: 2px solid var(--dl-border); border-radius: 16px 16px 0 0;
    overflow: hidden; background: white;
    box-shadow: var(--dl-shadow-sm);
}
.cj-quest-day-tile-chip {
    position: absolute; top: 0.4rem; right: 0.4rem;
    font-family: Fredoka, sans-serif; font-size: 0.65rem; font-weight: 700;
    color: #8B6914; background: rgba(255,255,255,0.92);
    padding: 0.12rem 0.38rem; border-radius: 999px;
    border: 1px solid rgba(0,0,0,0.08);
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}
.cj-quest-day-tile.earned .cj-quest-day-tile-chip {
    color: var(--dl-green-dark); background: rgba(240,255,228,0.95);
}
.cj-quest-day-tile.selected {
    border-color: var(--dl-orange);
    box-shadow: 0 0 0 2px rgba(255,159,67,0.25);
}
.cj-quest-day-tile.earned { border-color: rgba(88,204,2,0.45); }
.cj-quest-day-tile.earned.selected {
    border-color: var(--dl-green-dark);
    box-shadow: 0 0 0 2px rgba(88,204,2,0.2);
}
.cj-quest-day-tile-img {
    width: 100%; height: 112px; object-fit: cover; object-position: center top;
    display: block;
}
.cj-quest-day-tile-emoji {
    height: 112px; display: flex; align-items: center; justify-content: center;
    font-size: 2.4rem; background: var(--dl-bg-soft);
}
div[data-testid="stMarkdown"]:has(.cj-quest-day-tile) + div[data-testid="stButton"] {
    margin-top: -0.35rem;
    margin-bottom: 0.7rem;
}
div[data-testid="stMarkdown"]:has(.cj-quest-day-tile.selected) + div[data-testid="stButton"] {
    margin-bottom: 0;
}
div[data-testid="stMarkdown"]:has(.cj-quest-day-tile) + div[data-testid="stButton"] button {
    border-radius: 0 0 14px 14px;
    border-top: none;
    min-height: 44px;
    font-size: 0.78rem;
    font-weight: 700;
}
div[data-testid="stMarkdown"]:has(.cj-quest-day-tile.selected) + div[data-testid="stButton"] button {
    border-radius: 0;
    border-bottom: none;
    margin-bottom: 0;
}
.cj-quest-tile-expand-mark {
    margin: 0 0 -0.35rem;
    padding: 0.45rem 0.65rem 0.35rem;
    border: 2px solid var(--dl-orange);
    border-bottom: none;
    border-radius: 0;
    background: linear-gradient(180deg, rgba(255,248,225,0.95) 0%, #fff 100%);
    font-family: Fredoka, sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--dl-text);
}
.cj-quest-tile-expand-mark.done {
    border-color: rgba(88,204,2,0.65);
    background: linear-gradient(180deg, rgba(240,255,228,0.95) 0%, #fff 100%);
}
div[data-testid="stMarkdown"]:has(.cj-quest-tile-expand-mark) + div[data-testid="stVerticalBlockBorderWrapper"] {
    margin-top: 0 !important;
    margin-bottom: 0.85rem !important;
}
div[data-testid="stMarkdown"]:has(.cj-quest-tile-expand-mark) + div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: var(--dl-orange) !important;
    border-top: none !important;
    border-radius: 0 0 16px 16px !important;
}
div[data-testid="stMarkdown"]:has(.cj-quest-tile-expand-mark.done) + div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: rgba(88,204,2,0.65) !important;
}
.cj-quest-expand-panel {
    border: 2px solid var(--dl-orange); border-radius: 18px;
    padding: 0.85rem 0.9rem 0.5rem; margin: 0.35rem 0 0.85rem;
    background: linear-gradient(180deg, rgba(255,248,225,0.55) 0%, #fff 72%);
    box-shadow: var(--dl-shadow-sm);
}
.cj-quest-expand-panel.done {
    border-color: rgba(88,204,2,0.55);
    background: linear-gradient(180deg, rgba(240,255,228,0.65) 0%, #fff 72%);
}

.cj-polaroid {
    box-shadow: 0 3px 10px rgba(0,0,0,0.22), 0 0 0 2px white, 0 0 0 3px rgba(0,0,0,0.08) !important;
    transform: rotate(-2deg);
}
.cj-day-venue-strip .cj-polaroid:nth-child(even) { transform: rotate(2deg); }

.cj-photos-collage {
    position: relative; display: flex; gap: 0.3rem;
    height: 128px; margin-bottom: 0.75rem;
    border-radius: 18px; overflow: hidden;
    border: 2px solid #3d2548;
    box-shadow: 0 6px 20px rgba(0,0,0,0.18);
    background: linear-gradient(135deg, #1a1020 0%, #2d1838 55%, #1f1528 100%);
}
.cj-photos-collage.empty {
    height: 76px; align-items: center; justify-content: center;
    color: #c9b8d4; font-family: Fredoka, sans-serif;
    font-size: 0.82rem; font-weight: 700; text-align: center;
    padding: 0 1rem; line-height: 1.35;
}
.cj-photos-collage.single .cj-photos-collage-main.full { flex: 1; height: 100%; }
.cj-photos-collage.duo { gap: 0.25rem; }
.cj-photos-collage.duo .cj-photos-collage-main { flex: 1; height: 100%; }
.cj-photos-collage-main {
    flex: 1.2; min-width: 0; height: 100%; overflow: hidden;
}
.cj-photos-collage-main img {
    width: 100%; height: 100%; object-fit: cover; object-position: center;
    display: block;
}
.cj-photos-collage-side {
    flex: 1; min-width: 0; height: 100%;
    display: grid; grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr); gap: 0.22rem;
    padding: 0.22rem 0.22rem 0.22rem 0;
}
.cj-photos-collage-tile {
    overflow: hidden; border-radius: 7px;
    border: 2px solid rgba(255,255,255,0.82);
    box-shadow: 0 2px 8px rgba(0,0,0,0.28);
    transform: rotate(var(--rot, 0deg));
}
.cj-photos-collage-tile img {
    width: 100%; height: 100%; object-fit: cover; display: block;
}
.cj-photos-collage-count {
    position: absolute; bottom: 0.38rem; right: 0.45rem; z-index: 2;
    background: rgba(0,0,0,0.58); color: #fff;
    font-family: Fredoka, sans-serif;
    font-size: 0.66rem; font-weight: 800;
    padding: 0.14rem 0.42rem; border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.25);
}
.cj-photos-collage-more {
    position: absolute; top: 0.38rem; left: 0.45rem; z-index: 2;
    background: rgba(255,200,0,0.88); color: #5C4A00;
    font-family: Fredoka, sans-serif; font-size: 0.62rem; font-weight: 800;
    padding: 0.12rem 0.38rem; border-radius: 999px;
}

.cj-quest-scene-inner { position: relative; z-index: 1; padding: 0.15rem; }
.cj-quest-scene .dl-quest.focused {
    border: none !important; box-shadow: none !important; margin-bottom: 0 !important;
    background: transparent !important;
}
.cj-quest-scene .cj-quest-row { flex-direction: column; align-items: stretch; }
.cj-quest-scene .cj-quest-hero {
    width: 100%; max-width: 100%; height: 200px; border-width: 3px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.28); margin-bottom: 0.5rem;
}

/* ── QAKC gay club — single face photo ── */
.cj-qakc-solo {
    width: 100%; max-width: 200px; height: 200px;
    border-radius: 16px; overflow: hidden;
    border: 3px solid rgba(253, 121, 168, 0.75);
    box-shadow: 0 8px 28px rgba(253, 121, 168, 0.35), 0 4px 16px rgba(0,0,0,0.18);
    flex-shrink: 0;
}
.cj-qakc-solo.compact {
    max-width: 140px; height: 140px; margin-bottom: 0;
}
.cj-qakc-solo.featured {
    max-width: 100%; width: 100%; height: 260px;
    margin-bottom: 0.75rem;
}
.cj-qakc-solo img {
    width: 100%; height: 100%; object-fit: cover;
    object-position: center 38%; display: block;
}
.cj-qakc-quest .cj-quest-body { width: 100%; }
.cj-qakc-quest.cj-qakc-focused .cj-qakc-solo.featured {
    margin: -0.15rem -0.15rem 0.75rem;
}

/* ── Day victory banner ── */
.cj-day-victory-banner {
    text-align: center; padding: 0.85rem 1rem; margin: 0.65rem 0 1rem;
    border-radius: 20px; font-family: Fredoka, sans-serif; font-weight: 700;
    border: 3px solid var(--dl-green-dark);
    background: linear-gradient(135deg, #F0FFE4, #FFFFFF, #FFF8E1);
    box-shadow: 0 5px 0 var(--dl-green-dark);
    animation: dlPop 0.5s ease-out;
}
.cj-day-victory-banner.exceeded {
    border-color: var(--dl-yellow-dark);
    background: linear-gradient(135deg, #FFF8E1, #FFFBEB, #FFFFFF);
    box-shadow: 0 5px 0 var(--dl-yellow-dark);
}

/* ── Compact header (action tabs) ── */
.cj-compact-bar {
    display: flex; gap: 0.45rem; flex-wrap: wrap; align-items: center;
    margin: 0.2rem 0 0.65rem; padding: 0.45rem 0.65rem;
    background: white; border: 2px solid var(--dl-border);
    border-radius: 14px; box-shadow: var(--dl-shadow-sm);
}
.cj-compact-stat {
    flex: 1; min-width: 72px; text-align: center;
    font-family: Fredoka, sans-serif; font-weight: 700; font-size: 0.88rem;
    color: var(--dl-text); line-height: 1.2;
}
.cj-compact-stat small {
    display: block; font-family: Nunito, sans-serif;
    font-size: 0.58rem; font-weight: 800; text-transform: uppercase;
    color: var(--dl-muted); letter-spacing: 0.04em;
}
.cj-day-victory-emoji { font-size: 2rem; line-height: 1; margin-bottom: 0.2rem; }
.cj-day-victory-title { font-size: 1.15rem; color: var(--dl-green-dark); }
.cj-day-victory-banner.exceeded .cj-day-victory-title { color: #8B6914; }
.cj-day-victory-sub { font-size: 0.82rem; color: var(--dl-muted); font-weight: 700; margin-top: 0.15rem; }

/* hide streamlit default progress — we use custom bars */
.stProgress > div > div { background: var(--dl-green) !important; border-radius: 999px !important; }
.stProgress > div { background: #ECECEC !important; border-radius: 999px !important; height: 14px !important; }

/* ── Rich visual layer (Nice structure + Collar photo drama) ── */
.cj-rich-bar {
    display: flex; align-items: center; gap: 1rem;
    background: linear-gradient(135deg, #1a1020 0%, #2d1838 45%, #1f1528 100%);
    border: 2px solid #3d2548; border-radius: 20px;
    padding: 0.75rem 1rem; margin-bottom: 0.85rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    color: #f5eef8;
}
.cj-rich-bar-center { flex: 1; min-width: 0; }
.cj-rich-bar-title {
    font-family: Fredoka, sans-serif; font-size: 1.15rem; font-weight: 700;
    color: #ffc800; line-height: 1.15;
}
.cj-rich-bar-sub { font-size: 0.78rem; color: #b8a8c4; font-weight: 600; margin-top: 0.1rem; }
.cj-rich-bar-chips {
    display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.45rem;
}
.cj-rich-chip {
    font-family: Fredoka, sans-serif; font-size: 0.72rem; font-weight: 700;
    padding: 0.18rem 0.5rem; border-radius: 999px;
    background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.18);
}
.cj-rich-chip.xp { background: rgba(255,200,0,0.22); border-color: rgba(255,200,0,0.45); color: #ffe082; }
.cj-rich-chip.hot { background: rgba(255,150,0,0.2); border-color: rgba(255,150,0,0.4); color: #ffd699; }

.cj-rich-cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.45rem; margin-bottom: 0.35rem; }
.cj-rich-cal-day {
    position: relative; border-radius: 14px; overflow: hidden;
    min-height: 92px; border: 2px solid #e5e5ea;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}
.cj-rich-cal-day.selected { border-color: var(--dl-orange); box-shadow: 0 4px 0 var(--dl-orange); }
.cj-rich-cal-day.today { border-color: var(--dl-blue-dark); }
.cj-rich-cal-day.met { border-color: var(--dl-green-dark); }
.cj-rich-cal-day.exceeded { border-color: var(--dl-yellow-dark); }
.cj-rich-cal-bg {
    position: absolute; inset: 0;
    overflow: hidden;
    filter: saturate(1.15);
}
.cj-rich-cal-bg img {
    width: 100%; height: 100%; object-fit: cover; object-position: center top;
    display: block;
}
.cj-rich-cal-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.15) 0%, rgba(20,10,30,0.82) 100%);
}
.cj-rich-cal-day.met .cj-rich-cal-scrim {
    background: linear-gradient(180deg, rgba(180,255,120,0.2) 0%, rgba(20,40,10,0.78) 100%);
}
.cj-rich-cal-inner {
    position: relative; z-index: 1; padding: 0.45rem 0.4rem 0.4rem;
    color: white; text-shadow: 0 1px 4px rgba(0,0,0,0.5);
}
.cj-rich-cal-num {
    font-family: Fredoka, sans-serif; font-size: 1.35rem; font-weight: 700; line-height: 1;
}
.cj-rich-cal-daylabel { font-size: 0.58rem; font-weight: 800; opacity: 0.92; text-transform: uppercase; }
.cj-rich-cal-icons { font-size: 0.72rem; margin-top: 0.2rem; line-height: 1.3; min-height: 1rem; }
.cj-rich-cal-prog {
    height: 4px; border-radius: 999px; background: rgba(255,255,255,0.25); margin-top: 0.25rem;
}
.cj-rich-cal-prog > div {
    height: 100%; border-radius: 999px; background: var(--dl-yellow);
}
.cj-rich-cal-day.hero {
    min-height: 108px;
    margin: 0.35rem 0 0.5rem;
    border-radius: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}
.cj-rich-cal-day.hero .cj-rich-cal-num { font-size: 2.2rem; }
.cj-rich-cal-day.hero .cj-rich-cal-daylabel { font-size: 0.72rem; }
.cj-rich-cal-day.hero .cj-rich-cal-icons { font-size: 0.85rem; min-height: 1.1rem; margin-top: 0.35rem; }
.cj-rich-cal-day.hero .cj-rich-cal-prog { height: 6px; margin-top: 0.35rem; }
.cj-rich-cal-track {
    position: relative; margin-top: 0.3rem; height: 20px;
}
.cj-rich-cal-track-rail {
    position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%);
    height: 4px; border-radius: 999px; background: rgba(255,255,255,0.22); overflow: hidden;
}
.cj-rich-cal-track-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, var(--dl-green) 0%, var(--dl-yellow) 100%);
}
.cj-rich-cal-track-icons {
    position: relative; z-index: 1; display: flex; justify-content: space-between;
    align-items: center; height: 20px; gap: 4px;
}
.cj-rich-cal-track-icons.split { align-items: flex-start; height: 22px; }
.cj-rich-cal-track-pending {
    display: flex; flex-wrap: wrap; gap: 2px; flex: 1; min-width: 0; align-items: center;
}
.cj-rich-cal-track-done {
    display: flex; flex-wrap: wrap; gap: 2px; justify-content: flex-end;
    align-items: center; flex-shrink: 0; max-width: 58%;
}
.cj-rich-cal-qicon {
    font-size: 0.58rem; width: 16px; height: 16px; flex: 0 0 16px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(0,0,0,0.38); border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.35); line-height: 1;
}
.cj-rich-cal-qicon.done {
    background: #58cc02; border-color: rgba(255,255,255,0.92);
    box-shadow: 0 0 0 1px rgba(70,163,2,0.55), 0 2px 5px rgba(88,204,2,0.45);
}
.cj-rich-cal-track-done .cj-rich-cal-qicon.done {
    width: 18px; height: 18px; flex-basis: 18px; font-size: 0.62rem;
}
.cj-rich-cal-qicon.pending { opacity: 0.45; filter: grayscale(0.4); }
.cj-rich-cal-done-badge {
    position: absolute; top: 0.5rem; right: 0.55rem; z-index: 2;
    background: linear-gradient(145deg, #58cc02 0%, #46a302 100%);
    color: #fff; border-radius: 12px;
    padding: 0.22rem 0.5rem 0.26rem;
    font-family: Fredoka, sans-serif; font-weight: 800;
    box-shadow: 0 3px 12px rgba(88,204,2,0.5), 0 0 0 2px rgba(255,255,255,0.55);
    text-shadow: none; line-height: 1.05; text-align: center;
    min-width: 3.1rem;
}
.cj-rich-cal-done-main { font-size: 0.88rem; letter-spacing: 0.01em; }
.cj-rich-cal-done-sub {
    font-size: 0.52rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.06em; opacity: 0.92;
}
.cj-rich-cal-done-badge.zero {
    background: rgba(255,255,255,0.14);
    box-shadow: 0 0 0 1px rgba(255,255,255,0.28);
    color: rgba(255,255,255,0.82);
}
.cj-rich-cal-done-badge.complete {
    background: linear-gradient(145deg, #89e219 0%, #58cc02 100%);
    box-shadow: 0 3px 14px rgba(137,226,25,0.55), 0 0 0 2px rgba(255,255,255,0.65);
}
.cj-rich-cal-kicker {
    font-family: Fredoka, sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    line-height: 1.2;
}
.cj-rich-cal-meta {
    font-size: 0.78rem;
    font-weight: 700;
    opacity: 0.92;
    margin: 0.2rem 0 0.25rem;
    line-height: 1.35;
}
.cj-rich-cal-day.hero .cj-rich-cal-kicker { font-size: 1.15rem; }
.cj-rich-cal-day.hero .cj-rich-cal-meta { font-size: 0.78rem; margin-bottom: 0.2rem; }
.cj-rich-cal-day.hero .cj-rich-cal-inner { padding: 0.75rem 4.6rem 0.65rem 0.85rem; }
.cj-rich-cal-day.hero .cj-rich-cal-kicker { padding-right: 0.15rem; }

.nice-app-bar {
    display: flex; justify-content: space-between; align-items: baseline;
    margin: 0 0 0.85rem; padding: 0.35rem 0.15rem 0.55rem;
    border-bottom: 1px solid #e8e8ed;
}
.nice-app-title {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif;
    font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; color: #1c1c1e;
}
.nice-app-sub {
    font-size: 0.78rem; font-weight: 600; color: #8e8e93;
}
.nice-cal-week { margin-bottom: 0.65rem; }
.nice-cal-dow {
    text-align: center; font-size: 0.62rem; font-weight: 700;
    text-transform: uppercase; color: #8e8e93; letter-spacing: 0.04em;
    margin-bottom: 0.25rem;
}
.nice-entry-list {
    display: flex; flex-direction: column; gap: 0.45rem;
    margin: 0.65rem 0 1rem;
}
.nice-entry-row {
    display: flex; align-items: center; gap: 0.75rem;
    background: #ffffff; border: 2px solid var(--dl-border);
    border-radius: 14px; padding: 0.55rem 0.75rem;
    box-shadow: var(--dl-shadow-sm);
}
.nice-entry-row.done {
    background: linear-gradient(90deg, #f0ffe4 0%, #ffffff 55%);
    border-color: var(--dl-green-dark);
}
.nice-entry-row.pending { border-color: #e5e5ea; }
.nice-entry-photo {
    width: 56px; height: 56px; border-radius: 12px; object-fit: cover;
    object-position: center top; flex-shrink: 0;
    border: 2px solid rgba(0,0,0,0.12); box-shadow: 0 3px 10px rgba(0,0,0,0.18);
}
.nice-entry-icon {
    width: 42px; height: 42px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem; flex-shrink: 0;
    background: #f2f2f7;
}
.nice-entry-body { flex: 1; min-width: 0; }
.nice-entry-title {
    font-size: 0.92rem; font-weight: 650; color: #1c1c1e;
    line-height: 1.25; font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}
.nice-entry-meta { font-size: 0.72rem; color: #8e8e93; font-weight: 600; margin-top: 0.12rem; }
.nice-entry-xp {
    font-size: 0.75rem; font-weight: 700; color: #5856d6;
    background: #eef0ff; padding: 0.2rem 0.45rem; border-radius: 8px;
}
.nice-stat-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.55rem; margin: 0.5rem 0 1rem;
}
.nice-stat-card {
    background: linear-gradient(145deg, #ffffff 0%, #f7f9fc 100%);
    border: 2px solid var(--dl-border); border-radius: 16px;
    padding: 0.85rem 0.75rem; text-align: center;
    box-shadow: var(--dl-shadow-sm);
}
.nice-stat-card.accent-xp { border-color: var(--dl-yellow-dark); background: linear-gradient(145deg, #fff8e1, #ffffff); }
.nice-stat-card.accent-hot { border-color: var(--dl-orange); background: linear-gradient(145deg, #fff3e0, #ffffff); }
.nice-stat-card.accent-blue { border-color: var(--dl-blue-dark); background: linear-gradient(145deg, #e8f7ff, #ffffff); }
.nice-stat-value {
    font-family: Fredoka, sans-serif; font-size: 1.45rem; font-weight: 700; color: var(--dl-text);
}
.nice-stat-label {
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    color: #8e8e93; letter-spacing: 0.04em; margin-top: 0.15rem;
}
.nice-loc-bar {
    display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.5rem 0;
}
.nice-loc-chip {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: white; border: 2px solid var(--dl-border); border-radius: 999px;
    padding: 0.28rem 0.55rem 0.28rem 0.35rem;
    font-size: 0.72rem; font-weight: 700; color: var(--dl-text);
    box-shadow: var(--dl-shadow-sm);
}
.nice-loc-chip img {
    width: 26px; height: 26px; border-radius: 8px; object-fit: cover;
}
.cj-stats-hero {
    position: relative; border-radius: 18px; overflow: hidden;
    min-height: 120px; margin: 0.5rem 0 1rem;
    border: 2px solid #3d2548; box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}
.cj-stats-hero-layer {
    position: absolute; inset: 0;
    overflow: hidden;
    opacity: 0.55;
}
.cj-stats-hero-layer img {
    width: 100%; height: 100%; object-fit: cover; object-position: center;
    display: block;
}
.cj-stats-hero-scrim {
    position: absolute; inset: 0;
    background: linear-gradient(90deg, rgba(26,16,32,0.92) 0%, rgba(26,16,32,0.5) 100%);
}
.cj-stats-hero-text {
    position: relative; z-index: 1; padding: 1rem 1.15rem; color: #f5eef8;
}
.cj-stats-hero-text h4 {
    font-family: Fredoka, sans-serif; margin: 0; color: #ffc800; font-size: 1.05rem;
}

/* ── iPhone / mobile ── */
@supports (padding: env(safe-area-inset-bottom)) {
    .stApp {
        padding-left: env(safe-area-inset-left);
        padding-right: env(safe-area-inset-right);
        padding-bottom: env(safe-area-inset-bottom);
    }
}
@media (max-width: 768px) {
    .block-container {
        padding-top: 0.35rem;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
        max-width: 100%;
    }
    .stButton > button {
        min-height: 48px;
        font-size: 1rem;
        font-weight: 700;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        gap: 0.35rem;
        padding-bottom: 0.35rem;
        scrollbar-width: none;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar { display: none; }
    div[data-testid="stRadio"] label {
        min-height: 44px;
        min-width: 3.2rem;
        padding: 0.45rem 0.65rem !important;
        white-space: nowrap;
        flex-shrink: 0;
    }
    div[data-testid="stRadio"] label p {
        font-size: 0.82rem !important;
    }
    .cj-rich-bar {
        flex-wrap: wrap;
        gap: 0.65rem;
        padding: 0.65rem 0.75rem;
        border-radius: 16px;
    }
    .cj-rich-bar-title { font-size: 1rem; }
    .cj-rich-bar-sub { font-size: 0.72rem; }
    .cj-rich-chip { font-size: 0.68rem; padding: 0.22rem 0.45rem; }
    .cj-rich-cal-day { min-height: 108px; border-radius: 12px; }
    .cj-rich-cal-day.hero { min-height: 180px; }
    .cj-rich-cal-day.hero .cj-rich-cal-num { font-size: 2rem; }
    .cj-rich-cal-num { font-size: 1.2rem; }
    .cj-rich-cal-icons { font-size: 0.65rem; }
    .cj-cal-week-label { font-size: 0.88rem; margin: 0.75rem 0 0.35rem; }
    .nice-entry-row {
        padding: 0.65rem 0.7rem;
        gap: 0.65rem;
    }
    .nice-entry-photo {
        width: 64px;
        height: 64px;
        border-radius: 14px;
    }
    .nice-entry-title { font-size: 0.95rem; }
    .nice-entry-meta { font-size: 0.75rem; }
    .nice-stat-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.45rem;
    }
    .nice-stat-value { font-size: 1.25rem; }
    .cj-quest-pick-tile-img,
    .cj-quest-pick-tile-emoji { height: 150px; }
    .cj-quest-day-tile-img,
    .cj-quest-day-tile-emoji { height: 118px; }
    .cj-quest-hero.featured,
    .cj-quest-scene .cj-quest-hero { height: 180px; }
    .cj-qakc-solo.featured { max-width: 100%; height: 220px; }
    .dl-hud { gap: 0.4rem; }
    .dl-pill { min-width: calc(50% - 0.25rem); flex: 1 1 calc(50% - 0.25rem); }
    .dl-hero, .cj-brand-hero { flex-direction: column; text-align: center; padding: 0.85rem; }
    .cj-quest-nav-title {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
        font-size: 0.82rem;
    }
    div[data-testid="stExpander"] details summary {
        min-height: 44px;
        font-size: 0.95rem;
    }
    input, textarea, select {
        font-size: 16px !important;
    }
    /* Bottom nav */
    .block-container {
        padding-bottom: calc(5.75rem + env(safe-area-inset-bottom)) !important;
    }
    section.main div[data-testid="stRadio"]:has([aria-label="AppNavigate"]) {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background: rgba(255,255,255,0.97);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-top: 1px solid #e5e5ea;
        padding: 0.3rem 0.35rem calc(0.35rem + env(safe-area-inset-bottom));
        margin: 0 !important;
        box-shadow: 0 -4px 24px rgba(0,0,0,0.08);
    }
    section.main div[data-testid="stRadio"]:has([aria-label="AppNavigate"]) > div[role="radiogroup"] {
        justify-content: space-around;
        overflow-x: visible;
        gap: 0.15rem;
        padding-bottom: 0;
    }
    section.main div[data-testid="stRadio"]:has([aria-label="AppNavigate"]) label {
        flex: 1;
        min-width: 0;
        justify-content: center;
        padding: 0.35rem 0.2rem !important;
    }
    section.main div[data-testid="stRadio"]:has([aria-label="AppNavigate"]) label p {
        font-size: 0.72rem !important;
    }
    /* Sticky complete buttons above bottom nav */
    section.main div[data-testid="stButton"]:has(button[kind="primary"]) {
        position: sticky;
        bottom: calc(4.75rem + env(safe-area-inset-bottom));
        z-index: 900;
        padding-top: 0.35rem;
        background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.92) 35%);
    }
    section.main div[data-testid="stButton"]:has(button[kind="primary"]) button {
        box-shadow: 0 4px 18px rgba(88,204,2,0.35);
    }
    /* Journey path — compact on phone */
    .dl-adventure-map { display: none !important; }
    .dl-path-node-card { margin-bottom: 0.45rem; }
    .cj-journey-unified-hero { padding: 0.62rem 0.68rem; gap: 0.5rem; }
    .cj-journey-unified-hero .dl-path-hero-title { font-size: 1.08rem; }
    .cj-journey-unified-stats { font-size: 0.68rem; }
    .cj-journey-unified-hero .dl-collar-seg { width: 15px; height: 15px; font-size: 0.42rem; }
    .cj-journey-unified-hero .dl-collar-end { font-size: 1rem; }
    .cj-journey-unified-photo.venue { width: 64px; }
    .cj-journey-unified-photo.venue img { width: 64px; height: 74px; }
    .cj-rich-bar-level .cj-level-journey.compact .cj-journey-milestone { max-width: 50px; }
    /* Hide wide tables on phone — cards remain */
    div[data-testid="stDataFrame"],
    div[data-testid="stArrowDataFrame"] {
        display: none !important;
    }
    .cj-offline-banner {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: #ff4b4b;
        color: white;
        text-align: center;
        font-weight: 800;
        font-size: 0.82rem;
        padding: 0.45rem 0.75rem;
        padding-top: calc(0.45rem + env(safe-area-inset-top));
    }
    .cj-offline-banner.show { display: block; }
    .cj-quick-complete-bar {
        position: sticky;
        top: calc(0.35rem + env(safe-area-inset-top));
        z-index: 950;
        background: linear-gradient(135deg, #e8f8e8 0%, #d4f5d4 100%);
        border: 2px solid #58cc02;
        border-radius: 14px;
        padding: 0.65rem 0.85rem;
        margin: 0.5rem 0 0.65rem;
        box-shadow: 0 4px 18px rgba(88,204,2,0.22);
    }
    .cj-quick-complete-title {
        font-weight: 800;
        font-size: 0.95rem;
        color: #2d6a00;
    }
    .cj-quick-complete-sub {
        font-size: 0.78rem;
        color: #4a6741;
        margin-top: 0.15rem;
        line-height: 1.35;
    }
    div[data-testid="stMarkdown"]:has(.cj-quick-complete-bar) + div[data-testid="stButton"] {
        position: sticky;
        top: calc(4.5rem + env(safe-area-inset-top));
        z-index: 951;
        margin-bottom: 0.35rem;
    }
    .cj-photos-collage { height: 108px; }
    .cj-photos-collage.empty { height: 64px; font-size: 0.76rem; }
}
.cj-quick-complete-bar {
    background: linear-gradient(135deg, #e8f8e8 0%, #d4f5d4 100%);
    border: 2px solid #58cc02;
    border-radius: 14px;
    padding: 0.65rem 0.85rem;
    margin: 0.5rem 0 0.65rem;
}
.cj-quick-complete-title {
    font-weight: 800;
    font-size: 0.95rem;
    color: #2d6a00;
}
.cj-quick-complete-sub {
    font-size: 0.78rem;
    color: #4a6741;
    margin-top: 0.15rem;
}
@media (max-width: 768px) and (prefers-color-scheme: dark) {
    .stApp {
        background: linear-gradient(180deg, #0f1520 0%, #1a1020 45%, #121018 100%);
        color: #ece4f0;
    }
    section.main div[data-testid="stRadio"]:has([aria-label="AppNavigate"]) {
        background: rgba(26,16,32,0.97);
        border-top-color: #3d2548;
    }
    .nice-entry-row, .nice-stat-card, .dl-pill {
        background: #1f1528;
        border-color: #3d2548;
        color: #ece4f0;
    }
    .nice-entry-title { color: #f5eef8; }
}
@media (max-width: 390px) {
    .cj-rich-cal-day { min-height: 96px; }
    .nice-stat-grid { grid-template-columns: 1fr 1fr; }
}
.cj-media-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(88px, 1fr));
    gap: 0.45rem;
    margin: 0.5rem 0;
}
.cj-media-thumb {
    position: relative;
    border-radius: 12px;
    overflow: hidden;
    aspect-ratio: 1;
    border: 2px solid var(--dl-border);
    box-shadow: var(--dl-shadow-sm);
    background: #f0f0f0;
}
.cj-media-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.cj-slideshow-wrap {
    background: #1a1020;
    border-radius: 18px;
    overflow: hidden;
    border: 2px solid #3d2548;
    box-shadow: 0 8px 28px rgba(0,0,0,0.25);
    margin: 0.75rem 0 1rem;
}
.cj-slideshow-stage {
    position: relative;
    width: 100%;
    aspect-ratio: 4/3;
    background: #0f0a14;
}
.cj-slideshow-stage img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
}
.cj-slideshow-caption {
    padding: 0.65rem 0.85rem;
    color: #ece4f0;
    font-weight: 700;
    font-size: 0.88rem;
    min-height: 2.4rem;
}
.cj-slideshow-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.45rem 0.65rem 0.75rem;
    gap: 0.5rem;
}
.cj-slideshow-btn {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.18);
    color: white;
    border-radius: 999px;
    padding: 0.45rem 0.85rem;
    font-weight: 800;
    cursor: pointer;
    touch-action: manipulation;
}
.cj-slideshow-counter {
    color: #b8a8c4;
    font-size: 0.78rem;
    font-weight: 700;
}
.cj-partner-avatar {
    display: inline-block;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid var(--dl-border);
    vertical-align: middle;
    margin-right: 0.35rem;
    box-shadow: var(--dl-shadow-sm);
}
.cj-partner-avatar-fallback {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #ece4f0;
    color: #5a3d68;
    font-weight: 800;
    vertical-align: middle;
    margin-right: 0.35rem;
    border: 2px solid var(--dl-border);
}
</style>
"""


def get_conn():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _seed_activities(cur):
    for day_plan in FOURTEEN_DAY_PLAN:
        for idx, row in enumerate(day_plan["activities"]):
            time_slot, location, title, desc, points = row[:5]
            is_club = 1 if len(row) > 5 and row[5] else 0
            key = f"d{day_plan['day']:02d}_{idx:02d}_{location}"
            cur.execute(
                """
                INSERT INTO activities(
                    activity_key, day_num, slot_order, time_slot, location,
                    title, description, points, is_club_bonus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (key, day_plan["day"], idx, time_slot, location, title, desc, points, is_club),
            )


_SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_key TEXT NOT NULL UNIQUE,
    day_num INTEGER NOT NULL,
    slot_order INTEGER NOT NULL,
    time_slot TEXT NOT NULL,
    location TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    points INTEGER NOT NULL,
    is_club_bonus INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    fulfilled_by_key TEXT,
    earned_points INTEGER,
    notes TEXT DEFAULT '',
    earned_at TEXT
);
CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL UNIQUE,
    auto_label TEXT NOT NULL,
    custom_name TEXT,
    first_location TEXT NOT NULL,
    first_seen_day INTEGER,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS encounters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_key TEXT NOT NULL,
    partner_id INTEGER NOT NULL,
    slot_index INTEGER NOT NULL,
    act_types TEXT NOT NULL DEFAULT '[]',
    initiated_by TEXT DEFAULT 'Mutual',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY (partner_id) REFERENCES partners(id),
    FOREIGN KEY (activity_key) REFERENCES activities(activity_key)
);
CREATE TABLE IF NOT EXISTS bonus_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_num INTEGER NOT NULL,
    bonus_type TEXT NOT NULL,
    label TEXT NOT NULL,
    points INTEGER NOT NULL,
    location TEXT,
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS preset_dismissals (
    activity_key TEXT NOT NULL,
    preset_id TEXT NOT NULL,
    dismissed_at TEXT NOT NULL,
    PRIMARY KEY (activity_key, preset_id)
);
"""


def _read_schema_version(cur) -> int:
    try:
        row = cur.execute("SELECT value FROM settings WHERE key='schema_version'").fetchone()
        return int(row["value"]) if row else 0
    except sqlite3.OperationalError:
        return 0


def _ensure_default_settings(cur):
    today = date.today().isoformat()
    if not cur.execute("SELECT 1 FROM settings WHERE key='journey_start'").fetchone():
        cur.execute("INSERT INTO settings(key,value) VALUES('journey_start', ?)", (today,))
    if not cur.execute("SELECT 1 FROM settings WHERE key='display_name'").fetchone():
        cur.execute("INSERT INTO settings(key,value) VALUES('display_name', 'Her journey')", ())
    if not cur.execute("SELECT 1 FROM settings WHERE key='dom_name'").fetchone():
        cur.execute("INSERT INTO settings(key,value) VALUES('dom_name', '')", ())


def _ensure_schema_migrations(cur):
    """Idempotent upgrades — run every startup so partial DBs self-heal."""
    try:
        cur.execute("ALTER TABLE bonus_events ADD COLUMN location TEXT")
    except sqlite3.OperationalError:
        pass
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS preset_dismissals (
            activity_key TEXT NOT NULL,
            preset_id TEXT NOT NULL,
            dismissed_at TEXT NOT NULL,
            PRIMARY KEY (activity_key, preset_id)
        );
        CREATE TABLE IF NOT EXISTS journey_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_id TEXT NOT NULL UNIQUE,
            kind TEXT NOT NULL,
            activity_key TEXT NOT NULL DEFAULT '',
            partner_id INTEGER,
            location TEXT NOT NULL DEFAULT '',
            day_num INTEGER,
            caption TEXT NOT NULL DEFAULT '',
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        """
    )
    for col_ddl in (
        "venue_name TEXT NOT NULL DEFAULT ''",
        "image_file TEXT NOT NULL DEFAULT ''",
        "user_locked INTEGER NOT NULL DEFAULT 0",
        "group_key TEXT NOT NULL DEFAULT ''",
    ):
        try:
            cur.execute(f"ALTER TABLE activities ADD COLUMN {col_ddl}")
        except sqlite3.OperationalError:
            pass


def sync_coke_bonus_points():
    conn = get_conn()
    conn.execute(
        "UPDATE bonus_events SET points = ? WHERE bonus_type = ?",
        (BONUS_COKE_POINTS, BONUS_COKE_TYPE),
    )
    conn.commit()
    conn.close()


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(_SCHEMA_DDL)
    conn.commit()

    _ensure_schema_migrations(cur)

    version = _read_schema_version(cur)
    if version == 0:
        activity_count = cur.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
        if activity_count == 0:
            _seed_activities(cur)

    _ensure_default_settings(cur)
    cur.execute(
        "INSERT OR REPLACE INTO settings(key,value) VALUES('schema_version', ?)",
        (str(SCHEMA_VERSION),),
    )

    conn.commit()
    conn.close()
    sync_plan_activities()


def load_settings() -> dict[str, str]:
    conn = get_conn()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


def save_setting(key: str, value: str):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
    conn.commit()
    conn.close()


def load_activities_df() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM activities ORDER BY day_num, slot_order",
        conn,
    )
    conn.close()
    for col, default in (
        ("venue_name", ""),
        ("image_file", ""),
        ("user_locked", 0),
        ("group_key", ""),
    ):
        if col not in df.columns:
            df[col] = default
    return df


def _next_slot_order(cur, day_num: int) -> int:
    row = cur.execute(
        "SELECT COALESCE(MAX(slot_order), -1) + 1 FROM activities WHERE day_num=?",
        (day_num,),
    ).fetchone()
    return int(row[0])


def save_activity_image(upload, activity_key: str) -> str | None:
    if upload is None:
        return None
    ext = Path(upload.name).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"
    stem = re.sub(r"[^\w.-]+", "_", Path(upload.name).stem)[:36]
    fname = f"act_{activity_key}_{stem}{ext}"
    VENUE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    (VENUE_IMAGES_DIR / fname).write_bytes(upload.getbuffer())
    clear_image_caches()
    return fname


def update_activity_record(
    activity_key: str,
    *,
    title: str,
    description: str,
    points: int,
    time_slot: str,
    day_num: int,
    location: str,
    venue_name: str,
    image_file: str | None = None,
    schedule_days: list[int] | None = None,
) -> None:
    """Save activity fields; optionally mirror to additional journey days (frequency)."""
    conn = get_conn()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT group_key, image_file, status FROM activities WHERE activity_key=?",
        (activity_key,),
    ).fetchone()
    if row is None:
        conn.close()
        return

    group_key = str(row["group_key"] or "").strip() or f"grp_{uuid.uuid4().hex[:10]}"
    img = image_file if image_file is not None else str(row["image_file"] or "")
    days = sorted({max(1, min(TOTAL_DAYS, int(d))) for d in (schedule_days or [day_num])})
    if day_num not in days:
        days.append(day_num)
        days.sort()

    template = {
        "title": title.strip(),
        "description": description.strip(),
        "points": max(1, int(points)),
        "time_slot": time_slot,
        "location": location.strip(),
        "venue_name": venue_name.strip(),
        "image_file": img,
        "group_key": group_key,
    }

    cur.execute(
        """
        UPDATE activities
        SET title=?, description=?, points=?, time_slot=?, day_num=?, location=?,
            venue_name=?, image_file=?, user_locked=1, group_key=?
        WHERE activity_key=?
        """,
        (
            template["title"],
            template["description"],
            template["points"],
            template["time_slot"],
            day_num,
            template["location"],
            template["venue_name"],
            template["image_file"],
            group_key,
            activity_key,
        ),
    )

    peer_keys = [
        r["activity_key"]
        for r in cur.execute(
            "SELECT activity_key FROM activities WHERE group_key=? AND activity_key!=?",
            (group_key, activity_key),
        ).fetchall()
    ]
    for pk in peer_keys:
        peer = cur.execute(
            "SELECT day_num, status FROM activities WHERE activity_key=?", (pk,)
        ).fetchone()
        if peer and peer["status"] == "earned":
            continue
        if peer and int(peer["day_num"]) not in days:
            cur.execute("DELETE FROM encounters WHERE activity_key=?", (pk,))
            cur.execute("DELETE FROM preset_dismissals WHERE activity_key=?", (pk,))
            cur.execute("DELETE FROM activities WHERE activity_key=?", (pk,))

    existing_days = {
        int(r["day_num"])
        for r in cur.execute(
            "SELECT day_num FROM activities WHERE group_key=?", (group_key,)
        ).fetchall()
    }
    for d in days:
        if d in existing_days:
            cur.execute(
                """
                UPDATE activities
                SET title=?, description=?, points=?, time_slot=?, location=?,
                    venue_name=?, image_file=?, user_locked=1
                WHERE group_key=? AND day_num=?
                """,
                (
                    template["title"],
                    template["description"],
                    template["points"],
                    template["time_slot"],
                    template["location"],
                    template["venue_name"],
                    template["image_file"],
                    group_key,
                    d,
                ),
            )
            continue
        slot = _next_slot_order(cur, d)
        loc_slug = re.sub(r"[^\w]+", "_", template["location"])[:24]
        new_key = f"custom_{group_key}_{d:02d}_{loc_slug}"
        cur.execute(
            """
            INSERT INTO activities(
                activity_key, day_num, slot_order, time_slot, location,
                title, description, points, is_club_bonus,
                venue_name, image_file, user_locked, group_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 1, ?)
            """,
            (
                new_key,
                d,
                slot,
                template["time_slot"],
                template["location"],
                template["title"],
                template["description"],
                template["points"],
                template["venue_name"],
                template["image_file"],
                group_key,
            ),
        )

    conn.commit()
    conn.close()


def create_activity_record(
    *,
    title: str,
    description: str,
    points: int,
    time_slot: str,
    location: str,
    venue_name: str,
    schedule_days: list[int],
    image_file: str = "",
) -> str:
    group_key = f"grp_{uuid.uuid4().hex[:10]}"
    days = sorted({max(1, min(TOTAL_DAYS, int(d))) for d in schedule_days}) or [1]
    loc_slug = re.sub(r"[^\w]+", "_", location.strip())[:24]
    first_key = ""
    conn = get_conn()
    cur = conn.cursor()
    for d in days:
        slot = _next_slot_order(cur, d)
        key = f"custom_{group_key}_{d:02d}_{loc_slug}"
        if not first_key:
            first_key = key
        cur.execute(
            """
            INSERT INTO activities(
                activity_key, day_num, slot_order, time_slot, location,
                title, description, points, is_club_bonus,
                venue_name, image_file, user_locked, group_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 1, ?)
            """,
            (
                key,
                d,
                slot,
                time_slot,
                location.strip(),
                title.strip(),
                description.strip(),
                max(1, int(points)),
                venue_name.strip(),
                image_file,
                group_key,
            ),
        )
    conn.commit()
    conn.close()
    return first_key


def delete_activity_record(activity_key: str, delete_group: bool = False) -> None:
    conn = get_conn()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT group_key, status FROM activities WHERE activity_key=?", (activity_key,)
    ).fetchone()
    if row is None:
        conn.close()
        return
    keys = [activity_key]
    if delete_group and str(row["group_key"] or "").strip():
        keys = [
            r["activity_key"]
            for r in cur.execute(
                "SELECT activity_key FROM activities WHERE group_key=?",
                (row["group_key"],),
            ).fetchall()
        ]
    for key in keys:
        st_row = cur.execute(
            "SELECT status FROM activities WHERE activity_key=?", (key,)
        ).fetchone()
        if st_row and st_row["status"] == "earned":
            continue
        cur.execute("DELETE FROM encounters WHERE activity_key=?", (key,))
        cur.execute("DELETE FROM preset_dismissals WHERE activity_key=?", (key,))
        cur.execute("DELETE FROM activities WHERE activity_key=?", (key,))
    conn.commit()
    conn.close()


def activity_manager_label(row) -> str:
    meta = activity_meta(row)
    pts = "½ pt" if str(row["location"]) in HALF_POINT_LOCATIONS else f"{int(row['points'])} pt"
    return f"{row['title']} · {meta['label']} · Day {int(row['day_num'])} · {pts}"


def frequency_days_for_row(df: pd.DataFrame, row) -> list[int]:
    gk = str(row.get("group_key") or "").strip()
    if gk:
        peers = df[df["group_key"] == gk]
        return sorted(int(d) for d in peers["day_num"].unique())
    matches = df[
        (df["title"] == row["title"])
        & (df["venue_name"].fillna("") == str(row.get("venue_name") or ""))
        & (df["location"] == row["location"])
    ]
    return sorted(int(d) for d in matches["day_num"].unique())


def location_picker_options() -> list[str]:
    return sorted(LOCATIONS.keys())


def render_activity_manager(df: pd.DataFrame):
    st.markdown("#### Activity manager")
    st.caption(
        "All quests in one place — edit title, points, schedule, venue name, and photo. "
        "Locked activities are kept when the default plan syncs."
    )

    sort_mode = st.selectbox(
        "Sort by",
        ["Title", "Venue", "Day", "Points"],
        key="act_mgr_sort",
    )
    search = st.text_input("Search activities", key="act_mgr_search").strip().lower()

    view = df.copy()
    if search:
        mask = view.apply(
            lambda r: search in activity_manager_label(r).lower()
            or search in str(r["description"]).lower(),
            axis=1,
        )
        view = view[mask]

    if sort_mode == "Title":
        view = view.sort_values(["title", "day_num"])
    elif sort_mode == "Venue":
        view = view.sort_values(["venue_name", "title", "day_num"])
    elif sort_mode == "Day":
        view = view.sort_values(["day_num", "slot_order"])
    else:
        view = view.sort_values(["points", "title"], ascending=[False, True])

    if view.empty:
        st.info("No activities match your search.")
    else:
        labels = [activity_manager_label(row) for _, row in view.iterrows()]
        pick_idx = st.selectbox(
            "Select activity to edit",
            range(len(view)),
            format_func=lambda i: labels[i],
            key="act_mgr_pick",
        )
        row = view.iloc[pick_idx]
        key = str(row["activity_key"])
        meta = activity_meta(row)
        freq_days = frequency_days_for_row(df, row)

        prev_cols = st.columns([1, 2])
        with prev_cols[0]:
            img = str(row.get("image_file") or meta.get("image") or "")
            img_path = VENUE_IMAGES_DIR / img if img else None
            if img_path and img_path.is_file():
                st.image(str(img_path), use_container_width=True)
            elif img:
                uri = _venue_image_uri(img)
                if uri:
                    st.markdown(
                        f'<img src="{uri}" style="width:100%;border-radius:12px;border:2px solid #ddd;" />',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div style='font-size:3rem;text-align:center'>{meta.get('icon', '📍')}</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    f"<div style='font-size:3rem;text-align:center'>{meta.get('icon', '📍')}</div>",
                    unsafe_allow_html=True,
                )
        with prev_cols[1]:
            st.markdown(f"**{row['title']}**")
            st.caption(
                f"Key `{key}` · Group `{row.get('group_key') or '—'}` · "
                f"{'🔒 locked' if int(row.get('user_locked') or 0) else 'plan default'}"
            )
            if len(freq_days) > 1:
                st.caption(f"Frequency — also on days: {', '.join(str(d) for d in freq_days)}")

        with st.form(f"edit_act_{key}"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Activity title", value=str(row["title"]))
                venue_name = st.text_input(
                    "Venue / business / event name",
                    value=str(row.get("venue_name") or meta.get("label", "")),
                    placeholder="e.g. Le Tantra, Baskin Robbins Ice Cream Cafe",
                )
                loc_opts = location_picker_options()
                loc_idx = loc_opts.index(str(row["location"])) if str(row["location"]) in loc_opts else 0
                location = st.selectbox("Location type (for presets & streaks)", loc_opts, index=loc_idx)
                points = st.number_input("Points (XP)", min_value=1, max_value=20, value=int(row["points"]))
            with c2:
                slot_keys = list(TIME_SLOT_LABELS.keys())
                ts_idx = slot_keys.index(str(row["time_slot"])) if str(row["time_slot"]) in slot_keys else 0
                time_slot = st.selectbox(
                    "Time slot",
                    slot_keys,
                    index=ts_idx,
                    format_func=lambda s: TIME_SLOT_LABELS.get(s, s),
                )
                day_num = st.number_input("Primary day", min_value=1, max_value=TOTAL_DAYS, value=int(row["day_num"]))
                schedule_days = st.multiselect(
                    "Frequency — schedule on days",
                    list(range(1, TOTAL_DAYS + 1)),
                    default=freq_days,
                    help="Same activity repeated on multiple days of the journey.",
                )
                description = st.text_area("Description", value=str(row["description"]), height=100)
            image_up = st.file_uploader(
                "Activity photo",
                type=["jpg", "jpeg", "png", "webp"],
                key=f"act_img_{key}",
            )
            save_btn = st.form_submit_button("Save activity", type="primary")

        del_col1, del_col2 = st.columns(2)
        with del_col1:
            delete_one = st.button("Delete this slot", key=f"del_one_{key}")
        with del_col2:
            delete_group = st.button("Delete all days in group", key=f"del_grp_{key}")

        if save_btn:
            img_file = save_activity_image(image_up, key) if image_up else None
            update_activity_record(
                key,
                title=title,
                description=description,
                points=int(points),
                time_slot=time_slot,
                day_num=int(day_num),
                location=location,
                venue_name=venue_name,
                image_file=img_file,
                schedule_days=schedule_days or [int(day_num)],
            )
            sync_scores(load_activities_df())
            st.success("Activity saved.")
            st.rerun()

        if delete_one:
            delete_activity_record(key, delete_group=False)
            sync_scores(load_activities_df())
            st.warning("Activity deleted.")
            st.rerun()

        if delete_group:
            delete_activity_record(key, delete_group=True)
            sync_scores(load_activities_df())
            st.warning("Group deleted (earned slots kept).")
            st.rerun()

    st.divider()
    st.markdown("##### Add new activity")
    with st.form("add_activity"):
        c1, c2 = st.columns(2)
        with c1:
            new_title = st.text_input("Title", key="new_act_title")
            new_venue = st.text_input("Venue / business / event name", key="new_act_venue")
            new_loc = st.selectbox("Location type", location_picker_options(), key="new_act_loc")
            new_points = st.number_input("Points", min_value=1, max_value=20, value=2, key="new_act_pts")
        with c2:
            new_slot = st.selectbox(
                "Time slot",
                list(TIME_SLOT_LABELS.keys()),
                format_func=lambda s: TIME_SLOT_LABELS.get(s, s),
                key="new_act_slot",
            )
            new_days = st.multiselect(
                "Schedule on days",
                list(range(1, TOTAL_DAYS + 1)),
                default=[1],
                key="new_act_days",
            )
            new_desc = st.text_area("Description", key="new_act_desc", height=90)
        new_img = st.file_uploader("Photo", type=["jpg", "jpeg", "png", "webp"], key="new_act_img")
        if st.form_submit_button("Add activity", type="primary"):
            if not new_title.strip():
                st.error("Title is required.")
            elif not new_days:
                st.error("Pick at least one day.")
            else:
                img_name = ""
                if new_img:
                    tmp_key = f"new_{uuid.uuid4().hex[:8]}"
                    img_name = save_activity_image(new_img, tmp_key) or ""
                create_activity_record(
                    title=new_title,
                    description=new_desc,
                    points=int(new_points),
                    time_slot=new_slot,
                    location=new_loc,
                    venue_name=new_venue or LOCATIONS.get(new_loc, {}).get("label", new_loc),
                    schedule_days=new_days,
                    image_file=img_name,
                )
                sync_scores(load_activities_df())
                st.success("Activity added.")
                st.rerun()

    with st.expander(f"All activities ({len(df)})"):
        summary = []
        for _, r in df.iterrows():
            m = activity_meta(r)
            summary.append(
                {
                    "Title": r["title"],
                    "Venue": m["label"],
                    "Day": int(r["day_num"]),
                    "Slot": time_slot_label(str(r["time_slot"])),
                    "Pts": int(r["points"]),
                    "Status": r["status"],
                }
            )
        st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)


def load_bonus_df() -> pd.DataFrame:
    conn = get_conn()
    try:
        df = pd.read_sql_query(
            "SELECT * FROM bonus_events ORDER BY day_num, id",
            conn,
        )
    except sqlite3.OperationalError:
        df = pd.DataFrame()
    conn.close()
    return df


def format_points(pts: float) -> str:
    if abs(pts - round(pts)) < 0.001:
        return str(int(round(pts)))
    return f"{pts:.1f}"


_BADGE_NAMES = {badge_id: name for badge_id, name, _, _ in BADGES}
_BONUS_CELEBRATION_LABELS = {
    BONUS_COKE_TYPE: ("🥤 Bonus loot!", "Coke at Bay of Pigs"),
    BONUS_STREAK_TYPE: ("👏 Hot streak!", "10 in a row — legendary"),
    BONUS_OVERFLOW_TYPE: ("💫 Bonus XP!", "Scored above the daily goal"),
}


def queue_celebration(event_type: str, title: str = "", subtitle: str = ""):
    st.session_state.setdefault("_cj_celebrations", []).append(
        {"type": event_type, "title": title, "subtitle": subtitle}
    )


def snapshot_celebration_state() -> dict:
    df = load_activities_df()
    bonus_df = load_bonus_df()
    stats = compute_stats(df, bonus_df)
    badges = {badge_id for badge_id, _, _, check in BADGES if check(stats["badge_state"])}
    bonus_keys: set[tuple] = set()
    if not bonus_df.empty:
        for _, row in bonus_df.iterrows():
            bonus_keys.add(
                (int(row["day_num"]), str(row["bonus_type"]), str(row.get("location") or ""))
            )
    day_status = {day_num: day_goal_status(df, day_num) for day_num in range(1, TOTAL_DAYS + 1)}
    day_scores = {day_num: day_activity_score(df, day_num) for day_num in range(1, TOTAL_DAYS + 1)}
    return {
        "badges": badges,
        "bonus_keys": bonus_keys,
        "day_status": day_status,
        "day_scores": day_scores,
        "collar_earned": bool(stats["collar_earned"]),
    }


def emit_celebration_diff(
    before: dict,
    after: dict,
    activity_key: str | None = None,
):
    if activity_key:
        df = load_activities_df()
        row = df[df["activity_key"] == activity_key]
        if not row.empty:
            act = row.iloc[0]
            queue_celebration("quest", str(act["title"]), activity_xp_badge(act))

    for day_num in range(1, TOTAL_DAYS + 1):
        prev = before["day_status"].get(day_num, "pending")
        curr = after["day_status"].get(day_num, "pending")
        if prev == "pending" and curr in ("met", "exceeded"):
            meta = day_plan_meta(day_num)
            queue_celebration(
                "day_complete",
                f"Day {day_num} complete!",
                str(meta.get("title", "")),
            )
        bonus_target = day_plan_meta(day_num).get("bonus_target")
        if bonus_target:
            prev_score = before["day_scores"].get(day_num, 0.0)
            curr_score = after["day_scores"].get(day_num, 0.0)
            if prev_score + 0.001 < float(bonus_target) <= curr_score + 0.001:
                queue_celebration(
                    "stretch",
                    f"Stretch goal crushed!",
                    f"Day {day_num} · {format_points(float(bonus_target))}+ XP",
                )

    for bonus_key in after["bonus_keys"] - before["bonus_keys"]:
        bonus_type = bonus_key[1]
        title, subtitle = _BONUS_CELEBRATION_LABELS.get(
            bonus_type,
            ("👏 Bonus earned!", "Extra loot unlocked"),
        )
        queue_celebration("bonus", title, subtitle)

    for badge_id in after["badges"] - before["badges"]:
        queue_celebration(
            "achievement",
            _BADGE_NAMES.get(badge_id, "Achievement unlocked!"),
            "Trophy added to your case",
        )

    if after["collar_earned"] and not before.get("collar_earned"):
        queue_celebration(
            "achievement",
            "THE COLLAR IS HERS!",
            "Every quest complete — incroyable!",
        )

    if activity_key:
        try:
            st.toast("Quest saved — updated ✓", icon="✅")
        except Exception:
            pass


def complete_quest(activity_key: str, notes: str = "", earned_points: int | None = None):
    before = snapshot_celebration_state()
    earn_activity(activity_key, notes, earned_points)
    reset_quest_picker_after_complete(activity_key)
    emit_celebration_diff(before, snapshot_celebration_state(), activity_key=activity_key)


def complete_substitute(slot_key: str, substitute_key: str, notes: str = ""):
    before = snapshot_celebration_state()
    substitute_activity(slot_key, substitute_key, notes)
    reset_quest_picker_after_complete(slot_key)
    emit_celebration_diff(before, snapshot_celebration_state(), activity_key=slot_key)


def celebrate_bonus_action(action) -> bool:
    before = snapshot_celebration_state()
    ok = action()
    if ok:
        emit_celebration_diff(before, snapshot_celebration_state())
    return ok


def render_pending_celebrations(settings: dict | None = None):
    if not celebrations_enabled(settings):
        st.session_state.pop("_cj_celebrations", None)
        return
    events = st.session_state.pop("_cj_celebrations", [])
    if not events:
        return
    payload = json.dumps(events).replace("<", "\\u003c")
    components.html(
        f"""
<div id="cj-celebrate-boot" data-events='{payload}'></div>
<script>
(function() {{
  const boot = document.getElementById("cj-celebrate-boot");
  const events = JSON.parse(boot.getAttribute("data-events") || "[]");
  if (!events.length) return;

  const doc = window.parent.document;
  const win = window.parent;
  const body = doc.body;
  if (!body) return;

  doc.querySelectorAll(".cj-celebrate-layer, .cj-celebrate-toast").forEach(el => el.remove());

  const layer = doc.createElement("div");
  layer.className = "cj-celebrate-layer";
  layer.style.cssText = "position:fixed;inset:0;pointer-events:none;z-index:1000000;overflow:hidden;";
  body.appendChild(layer);

  const canvas = doc.createElement("canvas");
  canvas.width = win.innerWidth;
  canvas.height = win.innerHeight;
  canvas.style.cssText = "position:fixed;inset:0;pointer-events:none;z-index:1000000;";
  layer.appendChild(canvas);
  const ctx = canvas.getContext("2d");

  let audioCtx = null;
  function ac() {{
    if (!audioCtx) audioCtx = new (win.AudioContext || win.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();
    return audioCtx;
  }}

  function tone(freq, start, dur, type, gain, slideTo) {{
    try {{
      const c = ac();
      const o = c.createOscillator();
      const g = c.createGain();
      o.type = type || "sine";
      o.frequency.setValueAtTime(freq, c.currentTime + start);
      if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, c.currentTime + start + dur);
      g.gain.setValueAtTime(0.0001, c.currentTime + start);
      g.gain.exponentialRampToValueAtTime(gain, c.currentTime + start + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + start + dur);
      o.connect(g); g.connect(c.destination);
      o.start(c.currentTime + start);
      o.stop(c.currentTime + start + dur + 0.05);
    }} catch (e) {{}}
  }}

  function noiseBurst(start, dur, gain) {{
    try {{
      const c = ac();
      const bufferSize = c.sampleRate * dur;
      const buffer = c.createBuffer(1, bufferSize, c.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
      const src = c.createBufferSource();
      src.buffer = buffer;
      const filt = c.createBiquadFilter();
      filt.type = "bandpass";
      filt.frequency.value = 900;
      const g = c.createGain();
      g.gain.setValueAtTime(gain, c.currentTime + start);
      g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + start + dur);
      src.connect(filt); filt.connect(g); g.connect(c.destination);
      src.start(c.currentTime + start);
    }} catch (e) {{}}
  }}

  function playQuest() {{
    tone(523, 0, 0.12, "sine", 0.14);
    tone(659, 0.08, 0.12, "sine", 0.12);
    tone(784, 0.16, 0.22, "triangle", 0.16);
  }}

  function playClap() {{
    [0, 0.11, 0.22, 0.34, 0.46, 0.58].forEach((t, i) => {{
      noiseBurst(t, 0.07, 0.18 - i * 0.015);
      tone(180 + i * 20, t, 0.05, "square", 0.04);
    }});
  }}

  function playCheer() {{
    [392, 494, 587, 659, 784].forEach((f, i) => tone(f, i * 0.07, 0.18, "triangle", 0.11));
    [0, 0.12, 0.24, 0.36].forEach(t => noiseBurst(t, 0.08, 0.08));
    tone(988, 0.35, 0.45, "sine", 0.13, 1175);
  }}

  function playFireworks() {{
    [0, 0.15, 0.28, 0.42, 0.55].forEach((t, i) => {{
      tone(900 - i * 60, t, 0.35, "sawtooth", 0.05, 120);
      noiseBurst(t + 0.18, 0.25, 0.22);
    }});
  }}

  const particles = [];
  function spawnConfetti(n, colors, power) {{
    for (let i = 0; i < n; i++) {{
      particles.push({{
        x: win.innerWidth * (0.35 + Math.random() * 0.3),
        y: win.innerHeight * 0.72,
        vx: (Math.random() - 0.5) * power,
        vy: -Math.random() * power - 4,
        size: 4 + Math.random() * 7,
        rot: Math.random() * 6.28,
        vr: (Math.random() - 0.5) * 0.35,
        color: colors[i % colors.length],
        life: 90 + Math.random() * 40,
        kind: "confetti",
      }});
    }}
  }}

  function spawnFirework() {{
    const x = win.innerWidth * (0.15 + Math.random() * 0.7);
    const y = win.innerHeight * (0.15 + Math.random() * 0.45);
    const colors = ["#FFC800", "#FF4B4B", "#58CC02", "#1CB0F6", "#CE82FF", "#FF9600"];
    for (let i = 0; i < 55; i++) {{
      const a = (Math.PI * 2 * i) / 55;
      const speed = 2 + Math.random() * 5;
      particles.push({{
        x, y, vx: Math.cos(a) * speed, vy: Math.sin(a) * speed,
        size: 3 + Math.random() * 4, rot: 0, vr: 0,
        color: colors[i % colors.length], life: 55 + Math.random() * 25,
        kind: "spark", gravity: 0.06,
      }});
    }}
  }}

  let animating = false;
  function tick() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = particles.length - 1; i >= 0; i--) {{
      const p = particles[i];
      p.x += p.vx; p.y += p.vy;
      if (p.kind === "confetti") {{ p.vy += 0.18; p.vx *= 0.99; }}
      else {{ p.vy += p.gravity || 0.04; p.vx *= 0.98; }}
      p.rot += p.vr; p.life -= 1;
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rot);
      ctx.fillStyle = p.color;
      if (p.kind === "confetti") ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      else {{ ctx.beginPath(); ctx.arc(0, 0, p.size / 2, 0, 6.28); ctx.fill(); }}
      ctx.restore();
      if (p.life <= 0) particles.splice(i, 1);
    }}
    if (particles.length) {{
      animating = true;
      win.requestAnimationFrame(tick);
    }} else {{
      animating = false;
    }}
  }}
  function kickAnim() {{ if (!animating) win.requestAnimationFrame(tick); }}

  const emojiMap = {{
    quest: "✅", bonus: "👏", day_complete: "🎉", stretch: "⭐", achievement: "🏆",
  }};

  function toast(ev, delay) {{
    win.setTimeout(() => {{
      const el = doc.createElement("div");
      el.className = "cj-celebrate-toast " + ev.type;
      el.innerHTML =
        '<div class="cj-celebrate-emoji">' + (emojiMap[ev.type] || "🎊") + '</div>' +
        '<div class="cj-celebrate-title">' + (ev.title || "Nice!") + '</div>' +
        (ev.subtitle ? '<div class="cj-celebrate-sub">' + ev.subtitle + '</div>' : "");
      body.appendChild(el);
      win.setTimeout(() => el.remove(), 2800);
    }}, delay);
  }}

  events.forEach((ev, idx) => {{
    const delay = idx * 900;
    win.setTimeout(() => {{
      if (ev.type === "quest") {{
        playQuest();
        spawnConfetti(36, ["#58CC02", "#1CB0F6", "#FFC800", "#CE82FF"], 9);
        kickAnim();
      }} else if (ev.type === "bonus") {{
        playClap();
        spawnConfetti(48, ["#FF9600", "#FFC800", "#FF4B4B"], 11);
        kickAnim();
      }} else if (ev.type === "day_complete" || ev.type === "stretch") {{
        playCheer();
        spawnConfetti(64, ["#1CB0F6", "#58CC02", "#FFC800", "#FF4B4B"], 13);
        kickAnim();
      }} else if (ev.type === "achievement") {{
        playFireworks();
        for (let i = 0; i < 4; i++) win.setTimeout(spawnFirework, i * 220);
        kickAnim();
      }}
      toast(ev, 80);
    }}, delay);
  }});

  win.setTimeout(() => {{
    layer.remove();
  }}, events.length * 900 + 3200);
}})();
</script>
""",
        height=0,
        scrolling=False,
    )


def activity_effective_points(row) -> float:
    loc = str(row["location"])
    if loc in HALF_POINT_LOCATIONS:
        return 0.5
    if row.get("status") == "earned" and pd.notna(row.get("earned_points")):
        return float(row["earned_points"])
    return float(row["points"])


def activity_xp_badge(row) -> str:
    if str(row["location"]) in HALF_POINT_LOCATIONS:
        return "+½ XP"
    return f"+{int(row['points'])} XP"


def time_slot_label(slot: str) -> str:
    return TIME_SLOT_LABELS.get(slot, slot.replace("_", " ").title())


BEFORE_NOON_SLOTS = {"morning"}


def is_before_noon_village(row) -> bool:
    return str(row["location"]) == "village" and str(row["time_slot"]) in BEFORE_NOON_SLOTS


def is_solo_half_point(row) -> bool:
    return str(row["location"]) in SOLO_HALF_POINT_LOCATIONS


def is_bring_back_half(row) -> bool:
    return str(row["location"]) in BRING_BACK_HALF_LOCATIONS


def day_activity_score(df: pd.DataFrame, day_num: int) -> float:
    day_df = df[(df["day_num"] == day_num) & (df["status"] == "earned")]
    if day_df.empty:
        return 0.0
    return sum(activity_effective_points(row) for _, row in day_df.iterrows())


def day_target_points(day_num: int) -> float:
    return float(day_plan_meta(day_num).get("target", 0))


def day_goal_points(df: pd.DataFrame, day_num: int) -> float:
    return min(day_activity_score(df, day_num), day_target_points(day_num))


def day_target_met(df: pd.DataFrame, day_num: int) -> bool:
    return day_activity_score(df, day_num) >= day_target_points(day_num)


def day_overflow_points(df: pd.DataFrame, day_num: int) -> int:
    target = day_target_points(day_num)
    score = day_activity_score(df, day_num)
    overflow = score - target
    return int(overflow) if overflow > 0 else 0


def journey_grand_total(df: pd.DataFrame, bonus_df: pd.DataFrame) -> float:
    goal = sum(day_goal_points(df, d) for d in range(1, TOTAL_DAYS + 1))
    extra = int(bonus_df["points"].sum()) if not bonus_df.empty else 0
    return goal + extra


def day_goal_status(df: pd.DataFrame, day_num: int) -> str:
    """Return pending, met (goal hit), or exceeded (goal beaten)."""
    meta = day_plan_meta(day_num)
    day_df = df[df["day_num"] == day_num]
    if day_df.empty:
        return "pending"
    earned = day_df[day_df["status"] == "earned"]
    earned_pts = day_activity_score(df, day_num)
    target = day_target_points(day_num)
    if len(earned) != len(day_df) or earned_pts + 0.001 < target:
        return "pending"
    if earned_pts > target + 0.001:
        return "exceeded"
    return "met"


def day_bonus_points(bonus_df: pd.DataFrame, day_num: int) -> int:
    if bonus_df.empty:
        return 0
    day_bonus = bonus_df[bonus_df["day_num"] == day_num]
    return int(day_bonus["points"].sum()) if not day_bonus.empty else 0


def day_total_score(df: pd.DataFrame, bonus_df: pd.DataFrame, day_num: int) -> int:
    return day_goal_points(df, day_num) + day_bonus_points(bonus_df, day_num)


def recompute_day_bonuses(df: pd.DataFrame):
    """Overflow above the daily target converts to bonus once the target is hit."""
    conn = get_conn()
    try:
        conn.execute(
            "DELETE FROM bonus_events WHERE bonus_type IN (?, ?)",
            (BONUS_PR_TYPE, BONUS_OVERFLOW_TYPE),
        )
        now = datetime.now().isoformat(timespec="seconds")
        for day_num in range(1, TOTAL_DAYS + 1):
            overflow = day_overflow_points(df, day_num)
            if overflow <= 0:
                continue
            target = day_target_points(day_num)
            score = day_activity_score(df, day_num)
            label = f"Over daily goal: {format_points(score)} pts ({target} goal + {overflow} bonus)"
            conn.execute(
                """
                INSERT INTO bonus_events(day_num, bonus_type, label, points, location, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (day_num, BONUS_OVERFLOW_TYPE, label, overflow, None, "", now),
            )
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()


def add_coke_bonus(day_num: int, notes: str = "") -> bool:
    df = load_activities_df()
    if not day_target_met(df, day_num):
        return False
    conn = get_conn()
    existing = conn.execute(
        """
        SELECT id FROM bonus_events
        WHERE day_num = ? AND bonus_type = ?
        """,
        (day_num, BONUS_COKE_TYPE),
    ).fetchone()
    if existing:
        conn.close()
        return False
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """
        INSERT INTO bonus_events(day_num, bonus_type, label, points, location, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (day_num, BONUS_COKE_TYPE, BONUS_COKE_LABEL, BONUS_COKE_POINTS, "bay_of_pigs", notes, now),
    )
    conn.commit()
    conn.close()
    return True


def remove_coke_bonus(day_num: int):
    conn = get_conn()
    conn.execute(
        "DELETE FROM bonus_events WHERE day_num = ? AND bonus_type = ?",
        (day_num, BONUS_COKE_TYPE),
    )
    conn.commit()
    conn.close()


def streak_bonus_label(location: str) -> str:
    return f"10 in a row — {location_person_label(location)}"


def bonus_icon(bonus_type: str) -> str:
    return {
        BONUS_COKE_TYPE: "🥤",
        BONUS_PR_TYPE: "🔥",
        BONUS_OVERFLOW_TYPE: "💫",
        BONUS_STREAK_TYPE: "🔟",
    }.get(bonus_type, "⭐")


def has_streak_bonus(bonus_df: pd.DataFrame, day_num: int, location: str) -> bool:
    if bonus_df.empty or "location" not in bonus_df.columns:
        return False
    hits = bonus_df[
        (bonus_df["day_num"] == day_num)
        & (bonus_df["bonus_type"] == BONUS_STREAK_TYPE)
        & (bonus_df["location"] == location)
    ]
    return not hits.empty


def day_streak_locations(df: pd.DataFrame, day_num: int) -> list[str]:
    locs = df[df["day_num"] == day_num]["location"].unique().tolist()
    ordered = [loc for loc in SESSION_STREAK_LOCATIONS if loc in locs]
    for loc in locs:
        if loc in SESSION_STREAK_LOCATIONS and loc not in ordered:
            ordered.append(loc)
    for loc in ALWAYS_STREAK_LOCATIONS:
        if loc not in ordered:
            ordered.append(loc)
    return ordered


def add_streak_bonus(day_num: int, location: str, notes: str = "") -> bool:
    if location not in SESSION_STREAK_LOCATIONS:
        return False
    df = load_activities_df()
    if not day_target_met(df, day_num):
        return False
    conn = get_conn()
    existing = conn.execute(
        """
        SELECT id FROM bonus_events
        WHERE day_num = ? AND bonus_type = ? AND location = ?
        """,
        (day_num, BONUS_STREAK_TYPE, location),
    ).fetchone()
    if existing:
        conn.close()
        return False
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """
        INSERT INTO bonus_events(day_num, bonus_type, label, points, location, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            day_num,
            BONUS_STREAK_TYPE,
            streak_bonus_label(location),
            BONUS_STREAK_POINTS,
            location,
            notes or f"{BONUS_STREAK_COUNT} interactions in one session",
            now,
        ),
    )
    conn.commit()
    conn.close()
    return True


def remove_streak_bonus(day_num: int, location: str):
    conn = get_conn()
    conn.execute(
        """
        DELETE FROM bonus_events
        WHERE day_num = ? AND bonus_type = ? AND location = ?
        """,
        (day_num, BONUS_STREAK_TYPE, location),
    )
    conn.commit()
    conn.close()


def maybe_auto_streak_bonus(day_num: int, location: str, partner_count: int) -> bool:
    if partner_count < BONUS_STREAK_COUNT:
        return False
    df = load_activities_df()
    if not day_target_met(df, day_num):
        return False
    return add_streak_bonus(
        day_num,
        location,
        f"Auto: {partner_count} partners logged in one session",
    )


def journey_pr_stats(df: pd.DataFrame) -> dict:
    best_day = 0
    best_score = 0
    for day_num in range(1, TOTAL_DAYS + 1):
        score = day_activity_score(df, day_num)
        if score > best_score:
            best_score = score
            best_day = day_num
    return {"best_day": best_day, "best_score": best_score}


def bonus_summary(bonus_df: pd.DataFrame) -> dict:
    empty = {
        "total_extra": 0,
        "coke_count": 0,
        "overflow_count": 0,
        "overflow_extra": 0,
        "pr_breaks": 0,
        "pr_extra": 0,
        "coke_extra": 0,
        "streak_count": 0,
        "streak_extra": 0,
    }
    if bonus_df.empty:
        return empty
    coke = bonus_df[bonus_df["bonus_type"] == BONUS_COKE_TYPE]
    overflow = bonus_df[bonus_df["bonus_type"] == BONUS_OVERFLOW_TYPE]
    streak = bonus_df[bonus_df["bonus_type"] == BONUS_STREAK_TYPE]
    return {
        "total_extra": int(bonus_df["points"].sum()),
        "coke_count": len(coke),
        "overflow_count": len(overflow),
        "overflow_extra": int(overflow["points"].sum()) if not overflow.empty else 0,
        "pr_breaks": 0,
        "pr_extra": 0,
        "coke_extra": int(coke["points"].sum()) if not coke.empty else 0,
        "streak_count": len(streak),
        "streak_extra": int(streak["points"].sum()) if not streak.empty else 0,
    }


def restore_default_plan():
    """Unlock plan rows and remove pending custom activities, then re-sync defaults."""
    conn = get_conn()
    cur = conn.cursor()
    pending_custom = [
        r["activity_key"]
        for r in cur.execute(
            "SELECT activity_key FROM activities WHERE activity_key LIKE 'custom_%' AND status='pending'"
        ).fetchall()
    ]
    for key in pending_custom:
        cur.execute("DELETE FROM encounters WHERE activity_key=?", (key,))
        cur.execute("DELETE FROM preset_dismissals WHERE activity_key=?", (key,))
        cur.execute("DELETE FROM activities WHERE activity_key=?", (key,))
    cur.execute("UPDATE activities SET user_locked=0")
    conn.commit()
    conn.close()
    sync_plan_activities()


def sync_plan_activities():
    """Push schedule updates from FOURTEEN_DAY_PLAN into the DB, preserving earned progress."""
    conn = get_conn()
    cur = conn.cursor()
    for day_plan in FOURTEEN_DAY_PLAN:
        day = day_plan["day"]
        for idx, row in enumerate(day_plan["activities"]):
            time_slot, location, title, desc, points = row[:5]
            is_club = 1 if len(row) > 5 and row[5] else 0
            new_key = f"d{day:02d}_{idx:02d}_{location}"

            existing = cur.execute(
                "SELECT activity_key, user_locked FROM activities WHERE day_num=? AND slot_order=?",
                (day, idx),
            ).fetchone()

            if existing is not None and int(existing["user_locked"] or 0):
                continue

            if existing is None:
                cur.execute(
                    """
                    INSERT INTO activities(
                        activity_key, day_num, slot_order, time_slot, location,
                        title, description, points, is_club_bonus
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (new_key, day, idx, time_slot, location, title, desc, points, is_club),
                )
                continue

            old_key = existing["activity_key"]
            if old_key != new_key:
                cur.execute(
                    "UPDATE encounters SET activity_key=? WHERE activity_key=?",
                    (new_key, old_key),
                )
                cur.execute(
                    "UPDATE activities SET fulfilled_by_key=? WHERE fulfilled_by_key=?",
                    (new_key, old_key),
                )
            cur.execute(
                """
                UPDATE activities
                SET activity_key=?, time_slot=?, location=?, title=?, description=?,
                    points=?, is_club_bonus=?
                WHERE day_num=? AND slot_order=?
                """,
                (new_key, time_slot, location, title, desc, points, is_club, day, idx),
            )

        max_idx = len(day_plan["activities"]) - 1
        extras = cur.execute(
            "SELECT activity_key FROM activities WHERE day_num=? AND slot_order>?",
            (day, max_idx),
        ).fetchall()
        for ex in extras:
            key = ex["activity_key"]
            if str(key).startswith("custom_"):
                continue
            locked = cur.execute(
                "SELECT user_locked FROM activities WHERE activity_key=?", (key,)
            ).fetchone()
            if locked and int(locked["user_locked"] or 0):
                continue
            cur.execute(
                """
                UPDATE activities
                SET fulfilled_by_key=activity_key
                WHERE fulfilled_by_key=?
                """,
                (key,),
            )
            cur.execute("DELETE FROM encounters WHERE activity_key=?", (key,))
            cur.execute("DELETE FROM preset_dismissals WHERE activity_key=?", (key,))
            cur.execute("DELETE FROM activities WHERE activity_key=?", (key,))

    valid_keys = {
        r["activity_key"] for r in cur.execute("SELECT activity_key FROM activities").fetchall()
    }
    broken = cur.execute(
        """
        SELECT activity_key, fulfilled_by_key FROM activities
        WHERE fulfilled_by_key IS NOT NULL
          AND fulfilled_by_key != activity_key
        """
    ).fetchall()
    for row in broken:
        if row["fulfilled_by_key"] not in valid_keys:
            cur.execute(
                """
                UPDATE activities
                SET fulfilled_by_key=activity_key
                WHERE activity_key=?
                """,
                (row["activity_key"],),
            )

    conn.commit()
    conn.close()
    repair_orphaned_activity_refs()


def substitution_source_row(df: pd.DataFrame, fulfilled_by_key: str) -> pd.Series | None:
    return activity_row(df, fulfilled_by_key)


def activity_row(df: pd.DataFrame, activity_key: str | None) -> pd.Series | None:
    if not activity_key or (isinstance(activity_key, float) and pd.isna(activity_key)):
        return None
    matches = df[df["activity_key"] == activity_key]
    if matches.empty:
        return None
    return matches.iloc[0]


def is_substitution_fill(row) -> bool:
    fb = row.get("fulfilled_by_key")
    if fb is None or (isinstance(fb, float) and pd.isna(fb)):
        return False
    return str(fb) != str(row["activity_key"])


def repair_orphaned_activity_refs():
    """Fix stale substitution links and earned rows after plan reshuffles."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE activities
        SET fulfilled_by_key=activity_key
        WHERE status='earned'
          AND (fulfilled_by_key IS NULL OR fulfilled_by_key='')
        """
    )
    valid_keys = {
        r["activity_key"] for r in cur.execute("SELECT activity_key FROM activities").fetchall()
    }
    broken = cur.execute(
        """
        SELECT activity_key, fulfilled_by_key FROM activities
        WHERE fulfilled_by_key IS NOT NULL
          AND fulfilled_by_key != activity_key
        """
    ).fetchall()
    for row in broken:
        if row["fulfilled_by_key"] not in valid_keys:
            cur.execute(
                """
                UPDATE activities
                SET fulfilled_by_key=activity_key
                WHERE activity_key=?
                """,
                (row["activity_key"],),
            )
    conn.commit()
    conn.close()


def valid_substitution_keys(df: pd.DataFrame) -> set[str]:
    """Substitution targets that still exist in the current plan."""
    valid = set(df["activity_key"].tolist())
    refs = df.loc[
        (df["status"] == "earned")
        & (df["fulfilled_by_key"].notna())
        & (df["fulfilled_by_key"] != df["activity_key"]),
        "fulfilled_by_key",
    ].tolist()
    return {str(k) for k in refs if k in valid}


def partner_row(partners: pd.DataFrame, partner_id: int) -> pd.Series | None:
    matches = partners[partners["id"] == partner_id]
    if matches.empty:
        return None
    return matches.iloc[0]


def sync_plan_descriptions():
    sync_plan_activities()


def sync_scores(df: pd.DataFrame):
    sync_plan_descriptions()
    recompute_day_bonuses(df)


def load_partners_df() -> pd.DataFrame:
    conn = get_conn()
    try:
        df = pd.read_sql_query("SELECT * FROM partners ORDER BY id", conn)
    except sqlite3.OperationalError:
        df = pd.DataFrame()
    conn.close()
    return df


def media_file_path(stored_filename: str) -> Path | None:
    path = UPLOADS_DIR / stored_filename
    return path if path.is_file() else None


def media_data_uri(stored_filename: str) -> str | None:
    path = media_file_path(stored_filename)
    if not path:
        return None
    return _path_to_data_uri(path, max_bytes=MAX_UPLOAD_BYTES)


def clear_image_caches() -> None:
    venue_image_data_uri.cache_clear()
    brand_image_data_uri.cache_clear()


def load_journey_media_df() -> pd.DataFrame:
    conn = get_conn()
    try:
        df = pd.read_sql_query(
            "SELECT * FROM journey_media ORDER BY created_at, id",
            conn,
        )
    except sqlite3.OperationalError:
        df = pd.DataFrame()
    conn.close()
    return df


def filter_journey_media(
    *,
    kind: str | None = None,
    activity_key: str | None = None,
    partner_id: int | None = None,
    location: str | None = None,
    day_num: int | None = None,
) -> pd.DataFrame:
    df = load_journey_media_df()
    if df.empty:
        return df
    if kind:
        if kind == MEDIA_KIND_CHALLENGE:
            df = df[df["kind"].isin(CHALLENGE_MEDIA_KINDS)]
        else:
            df = df[df["kind"] == kind]
    if activity_key:
        df = df[df["activity_key"] == activity_key]
    if partner_id is not None:
        df = df[df["partner_id"] == partner_id]
    if location:
        df = df[df["location"] == location]
    if day_num is not None:
        df = df[df["day_num"] == day_num]
    return df


def save_journey_media(
    file_bytes: bytes,
    original_name: str,
    *,
    kind: str,
    activity_key: str = "",
    partner_id: int | None = None,
    location: str = "",
    day_num: int | None = None,
    caption: str = "",
) -> tuple[bool, str]:
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_UPLOAD_EXT:
        return False, "Use JPG, PNG, WEBP, or GIF."
    if not file_bytes:
        return False, "Empty file."
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        return False, f"Max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB per photo."
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    media_id = uuid.uuid4().hex
    filename = f"{media_id}{ext}"
    try:
        (UPLOADS_DIR / filename).write_bytes(file_bytes)
    except OSError:
        return False, "Could not save photo."
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO journey_media(
            media_id, kind, activity_key, partner_id, location, day_num,
            caption, filename, original_name, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            media_id,
            kind,
            activity_key or "",
            partner_id,
            location or "",
            day_num,
            caption.strip(),
            filename,
            original_name,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()
    clear_image_caches()
    return True, media_id


def delete_journey_media(media_id: str) -> None:
    conn = get_conn()
    row = conn.execute(
        "SELECT filename FROM journey_media WHERE media_id = ?",
        (media_id,),
    ).fetchone()
    if row:
        path = UPLOADS_DIR / row["filename"]
        if path.is_file():
            try:
                path.unlink()
            except OSError:
                pass
        conn.execute("DELETE FROM journey_media WHERE media_id = ?", (media_id,))
        conn.commit()
    conn.close()


def latest_media_data_uri(media_df: pd.DataFrame) -> str | None:
    if media_df.empty:
        return None
    for _, row in media_df.iloc[::-1].iterrows():
        uri = media_data_uri(str(row["filename"]))
        if uri:
            return uri
    return None


def location_media_uri(location: str) -> str | None:
    return latest_media_data_uri(filter_journey_media(kind=MEDIA_KIND_LOCATION, location=location))


def partner_media_uri(partner_id: int) -> str | None:
    return latest_media_data_uri(filter_journey_media(kind=MEDIA_KIND_PARTNER, partner_id=partner_id))


def challenge_media_uri(activity_key: str) -> str | None:
    return latest_media_data_uri(filter_journey_media(kind=MEDIA_KIND_CHALLENGE, activity_key=activity_key))


def partner_avatar_html(partner_id: int, display_name: str, size: int = 36) -> str:
    uri = partner_media_uri(partner_id)
    if uri:
        return (
            f'<img class="cj-partner-avatar" src="{uri}" alt="" '
            f'style="width:{size}px;height:{size}px;" />'
        )
    initial = html.escape((display_name or "?")[:1].upper())
    return (
        f'<span class="cj-partner-avatar-fallback" '
        f'style="width:{size}px;height:{size}px;font-size:{max(12, size // 2)}px;">'
        f"{initial}</span>"
    )


def media_slide_label(
    row: pd.Series,
    df: pd.DataFrame,
    partners_df: pd.DataFrame,
    settings: dict,
) -> str:
    caption = str(row.get("caption") or "").strip()
    kind = str(row.get("kind") or "")
    if kind in CHALLENGE_MEDIA_KINDS and row.get("activity_key"):
        act = activity_row(df, str(row["activity_key"]))
        if act is not None:
            base = f"Day {int(act['day_num'])} · {act['title']}"
            return f"{base} — {caption}" if caption else base
    if kind == "partner" and pd.notna(row.get("partner_id")):
        prow = partner_row(partners_df, int(row["partner_id"]))
        if prow is not None:
            base = f"👤 {prow['display_name']}"
            return f"{base} — {caption}" if caption else base
    if kind == "day" and pd.notna(row.get("day_num")):
        d = int(row["day_num"])
        meta = day_plan_meta(d)
        when = journey_date(settings, d).strftime("%b %d")
        base = f"Day {d} · {meta['title']} · {when}"
        return f"{base} — {caption}" if caption else base
    if kind == "location" and row.get("location"):
        base = f"📍 {location_person_label(str(row['location']))}"
        if pd.notna(row.get("day_num")):
            base = f"Day {int(row['day_num'])} · {base}"
        return f"{base} — {caption}" if caption else base
    return caption or "Journey memory"


def render_media_thumbnail_grid(
    media_df: pd.DataFrame,
    key_prefix: str,
    *,
    deletable: bool = True,
) -> None:
    if media_df.empty:
        return
    valid_rows = [
        row
        for _, row in media_df.iterrows()
        if media_file_path(str(row["filename"])) is not None
    ]
    if not valid_rows:
        st.caption("Photos listed but image files are missing on this device.")
        return
    cols = st.columns(min(4, len(valid_rows)))
    for i, row in enumerate(valid_rows):
        path = media_file_path(str(row["filename"]))
        if not path:
            continue
        with cols[i % len(cols)]:
            st.image(str(path), use_container_width=True)
            cap = str(row.get("caption") or row.get("original_name") or "")
            if cap:
                st.caption(cap if len(cap) <= 40 else cap[:38] + "…")
            if deletable and st.button(
                "🗑 Remove",
                key=f"{key_prefix}_del_media_{row['media_id']}",
                use_container_width=True,
            ):
                delete_journey_media(str(row["media_id"]))
                st.toast("Photo removed")
                st.rerun()


def _photo_kind_index(default_kind: str) -> int:
    kinds = list(PHOTO_KIND_LABELS.keys())
    return kinds.index(default_kind) if default_kind in kinds else 0


def render_photo_upload_panel(
    key_prefix: str,
    *,
    df: pd.DataFrame,
    partners_df: pd.DataFrame,
    default_kind: str = MEDIA_KIND_CHALLENGE,
    default_activity_key: str = "",
    default_partner_id: int | None = None,
    default_location: str = "",
    default_day_num: int | None = None,
    label: str = "📸 Add a photo",
    compact: bool = False,
    standalone: bool = False,
) -> None:
    """Upload with photo type — location, challenge, partner, or day — for app thumbnails."""
    panel_key = f"{key_prefix}_photo_{default_day_num}_{default_activity_key}_{default_partner_id}"
    kind_list = list(PHOTO_KIND_LABELS.keys())

    def _upload_body() -> None:
        photo_kind = st.selectbox(
            "Photo type",
            kind_list,
            index=_photo_kind_index(default_kind),
            format_func=lambda k: PHOTO_KIND_LABELS[k],
            key=f"{panel_key}_kind",
        )
        activity_key = ""
        partner_id: int | None = None
        location = ""
        day_num = default_day_num

        if photo_kind == MEDIA_KIND_CHALLENGE:
            day_num = st.selectbox(
                "Day",
                list(range(1, TOTAL_DAYS + 1)),
                index=int(default_day_num or 1) - 1,
                format_func=lambda d: f"Day {d} — {day_plan_meta(d)['title']}",
                key=f"{panel_key}_challenge_day",
            )
            day_acts = df[df["day_num"] == day_num].sort_values(["time_slot", "slot_order"])
            if day_acts.empty:
                st.caption("No quests on this day.")
                return
            act_keys = day_acts["activity_key"].astype(str).tolist()
            default_act = default_activity_key if default_activity_key in act_keys else act_keys[0]
            activity_key = st.selectbox(
                "Challenge / quest",
                act_keys,
                index=act_keys.index(default_act),
                format_func=lambda k, _df=day_acts: quest_pick_label(_df, k),
                key=f"{panel_key}_challenge",
            )
            loc_row = day_acts[day_acts["activity_key"] == activity_key].iloc[0]
            location = str(loc_row["location"])
            st.caption("Used as the thumbnail when you pick this challenge.")
        elif photo_kind == MEDIA_KIND_LOCATION:
            loc_opts = location_picker_options()
            default_loc = default_location if default_location in loc_opts else loc_opts[0]
            location = st.selectbox(
                "Location",
                loc_opts,
                index=loc_opts.index(default_loc),
                format_func=location_person_label,
                key=f"{panel_key}_location",
            )
            st.caption("Used as the location icon across the app (banners, chips, strips).")
        elif photo_kind == MEDIA_KIND_PARTNER:
            if partners_df.empty:
                st.caption("Log a partner on a quest first, then add their photo here.")
                return
            partner_rows = partners_df.sort_values("display_name")
            partner_ids = [int(x) for x in partner_rows["id"].tolist()]
            default_pid = default_partner_id if default_partner_id in partner_ids else partner_ids[0]
            partner_id = st.selectbox(
                "Partner",
                partner_ids,
                index=partner_ids.index(default_pid),
                format_func=lambda pid, _p=partner_rows: str(
                    _p[_p["id"] == pid].iloc[0]["display_name"]
                ),
                key=f"{panel_key}_partner",
            )
            st.caption("Used as their avatar in partner logs and the Partners tab.")
        else:
            day_num = st.number_input(
                "Day",
                min_value=1,
                max_value=TOTAL_DAYS,
                value=int(default_day_num or 1),
                key=f"{panel_key}_day",
            )
            st.caption("General day memory — appears in the slideshow.")

        existing = filter_journey_media(
            kind=photo_kind,
            activity_key=activity_key or None,
            partner_id=partner_id,
            location=location or None,
            day_num=day_num if photo_kind == MEDIA_KIND_DAY else day_num,
        )
        if not existing.empty:
            render_media_thumbnail_grid(existing, f"{panel_key}_{photo_kind}_grid")

        caption = st.text_input("Caption (optional)", key=f"{panel_key}_cap")
        uploaded = st.file_uploader(
            "Choose photo(s)",
            type=["jpg", "jpeg", "png", "webp", "gif"],
            accept_multiple_files=True,
            key=f"{panel_key}_up",
            label_visibility="collapsed",
        )
        st.caption(
            "JPG/PNG/WEBP/GIF · up to 8 MB · saved on this device. "
            "Location & partner photos become app thumbnails automatically."
        )
        if uploaded and st.button(
            "Save photos",
            key=f"{panel_key}_save",
            type="primary",
            use_container_width=True,
        ):
            save_kind = MEDIA_KIND_CHALLENGE if photo_kind == MEDIA_KIND_CHALLENGE else photo_kind
            saved = 0
            errors: list[str] = []
            for file in uploaded:
                ok, msg = save_journey_media(
                    file.getvalue(),
                    file.name,
                    kind=save_kind,
                    activity_key=activity_key,
                    partner_id=partner_id,
                    location=location,
                    day_num=day_num,
                    caption=caption,
                )
                if ok:
                    saved += 1
                else:
                    errors.append(f"{file.name}: {msg}")
            if saved:
                st.toast(f"Saved {saved} photo{'s' if saved != 1 else ''} 📸")
            if errors:
                st.warning("Some photos were skipped: " + "; ".join(errors[:3]))
            if saved:
                st.rerun()

    if standalone:
        st.markdown(f"#### {label}")
        _upload_body()
    else:
        with st.expander(label, expanded=not compact):
            _upload_body()


def render_tagged_media_library(
    df: pd.DataFrame,
    partners_df: pd.DataFrame,
    settings: dict,
) -> None:
    media = load_journey_media_df()
    st.markdown("#### Tagged library")
    if media.empty:
        st.info("No photos yet — upload and tag above.")
        return
    filter_opts = ["All"] + list(PHOTO_KIND_LABELS.values())
    kind_by_label = {v: k for k, v in PHOTO_KIND_LABELS.items()}
    filter_pick = st.selectbox(
        "Show",
        filter_opts,
        key="photos_library_filter",
        label_visibility="collapsed",
    )
    if filter_pick != "All":
        kind_filter = kind_by_label.get(filter_pick)
        if kind_filter == MEDIA_KIND_CHALLENGE:
            media = media[media["kind"].isin(CHALLENGE_MEDIA_KINDS)]
        else:
            media = media[media["kind"] == kind_filter]
    if media.empty:
        st.caption("No photos for this filter.")
        return
    cols = st.columns(2)
    for i, (_, row) in enumerate(media.iterrows()):
        path = media_file_path(str(row["filename"]))
        if not path:
            continue
        kind = str(row.get("kind") or "")
        kind_label = PHOTO_KIND_LABELS.get(
            MEDIA_KIND_CHALLENGE if kind in CHALLENGE_MEDIA_KINDS else kind,
            kind,
        )
        tag = media_slide_label(row, df, partners_df, settings)
        with cols[i % 2]:
            st.image(str(path), use_container_width=True)
            st.markdown(f"**{kind_label}**")
            st.caption(tag if len(tag) <= 72 else tag[:70] + "…")
            if st.button(
                "🗑 Remove",
                key=f"photos_lib_del_{row['media_id']}",
                use_container_width=True,
            ):
                delete_journey_media(str(row["media_id"]))
                st.toast("Photo removed")
                st.rerun()


def _collage_items_from_media(media: pd.DataFrame, limit: int = 8) -> list[dict]:
    items: list[dict] = []
    if media.empty:
        return items
    for _, row in media.iloc[::-1].iterrows():
        uri = media_data_uri(str(row["filename"]))
        if uri:
            items.append({"uri": uri})
        if len(items) >= limit:
            break
    return items


def photos_collage_html(items: list[dict], total_count: int) -> str:
    if not items:
        return (
            '<div class="cj-photos-collage empty">'
            "📸 Your collage grows here as you add photos below"
            "</div>"
        )
    count_lbl = f"{total_count} photo{'s' if total_count != 1 else ''}"
    extra = total_count - len(items)
    extra_badge = (
        f'<div class="cj-photos-collage-more">+{extra} more</div>' if extra > 0 else ""
    )
    if len(items) == 1:
        return (
            f'<div class="cj-photos-collage single">'
            f'{extra_badge}'
            f'<div class="cj-photos-collage-main full">'
            f'<img src="{items[0]["uri"]}" alt="" /></div>'
            f'<div class="cj-photos-collage-count">{count_lbl}</div></div>'
        )
    if len(items) == 2:
        return (
            f'<div class="cj-photos-collage duo">'
            f'{extra_badge}'
            f'<div class="cj-photos-collage-main">'
            f'<img src="{items[0]["uri"]}" alt="" /></div>'
            f'<div class="cj-photos-collage-main">'
            f'<img src="{items[1]["uri"]}" alt="" /></div>'
            f'<div class="cj-photos-collage-count">{count_lbl}</div></div>'
        )
    hero = items[0]
    tiles = []
    rots = [-2.5, 1.5, -1, 2, -1.5, 1, 0.5]
    for i, item in enumerate(items[1:7]):
        rot = rots[i % len(rots)]
        tiles.append(
            f'<div class="cj-photos-collage-tile" style="--rot:{rot}deg">'
            f'<img src="{item["uri"]}" alt="" /></div>'
        )
    return (
        f'<div class="cj-photos-collage">'
        f"{extra_badge}"
        f'<div class="cj-photos-collage-main">'
        f'<img src="{hero["uri"]}" alt="" /></div>'
        f'<div class="cj-photos-collage-side">{"".join(tiles)}</div>'
        f'<div class="cj-photos-collage-count">{count_lbl}</div>'
        f"</div>"
    )


def render_photos_collage() -> None:
    media = load_journey_media_df()
    valid = media[
        media["filename"].astype(str).apply(lambda f: media_file_path(f) is not None)
    ]
    items = _collage_items_from_media(valid)
    st.markdown(photos_collage_html(items, len(valid)), unsafe_allow_html=True)


def render_photos_view(
    df: pd.DataFrame,
    partners_df: pd.DataFrame,
    settings: dict,
    journey_day: int,
) -> None:
    render_photos_collage()
    st.caption(
        "Upload & tag — challenge, location, partner, or day. "
        "Photos appear in the collage above and across the app."
    )
    render_photo_upload_panel(
        "photos",
        df=df,
        partners_df=partners_df,
        default_day_num=journey_day,
        label="Upload & tag",
        standalone=True,
    )
    st.divider()
    render_tagged_media_library(df, partners_df, settings)
    st.divider()
    render_journey_slideshow(df, partners_df, settings)


def render_media_upload_section(
    key_prefix: str,
    *,
    kind: str,
    activity_key: str = "",
    partner_id: int | None = None,
    location: str = "",
    day_num: int | None = None,
    label: str = "📸 Add photos",
    compact: bool = False,
    df: pd.DataFrame | None = None,
    partners_df: pd.DataFrame | None = None,
) -> None:
    mapped_kind = MEDIA_KIND_CHALLENGE if kind in CHALLENGE_MEDIA_KINDS else kind
    if df is not None and partners_df is not None:
        render_photo_upload_panel(
            key_prefix,
            df=df,
            partners_df=partners_df,
            default_kind=mapped_kind,
            default_activity_key=activity_key,
            default_partner_id=partner_id,
            default_location=location,
            default_day_num=day_num,
            label=label,
            compact=compact,
        )
        return
    scope_key = f"{kind}_{activity_key}_{partner_id}_{location}_{day_num}"
    existing = filter_journey_media(
        kind=mapped_kind,
        activity_key=activity_key or None,
        partner_id=partner_id,
        location=location or None,
        day_num=day_num,
    )
    if not existing.empty:
        render_media_thumbnail_grid(existing, f"{key_prefix}_{scope_key}")
    cap_key = f"{key_prefix}_media_cap_{scope_key}"
    up_key = f"{key_prefix}_media_up_{scope_key}"
    with st.expander(label, expanded=not compact and existing.empty):
        caption = st.text_input("Caption (optional)", key=cap_key)
        uploaded = st.file_uploader(
            "Choose photo(s)",
            type=["jpg", "jpeg", "png", "webp", "gif"],
            accept_multiple_files=True,
            key=up_key,
            label_visibility="collapsed",
        )
        if uploaded and st.button(
            "Save photos",
            key=f"{key_prefix}_media_save_{scope_key}",
            type="primary",
            use_container_width=True,
        ):
            save_kind = MEDIA_KIND_CHALLENGE if kind in CHALLENGE_MEDIA_KINDS else kind
            saved = 0
            for file in uploaded:
                ok, _ = save_journey_media(
                    file.getvalue(),
                    file.name,
                    kind=save_kind,
                    activity_key=activity_key,
                    partner_id=partner_id,
                    location=location,
                    day_num=day_num,
                    caption=caption,
                )
                if ok:
                    saved += 1
            if saved:
                st.toast(f"Saved {saved} photo{'s' if saved != 1 else ''} 📸")
                st.rerun()


def render_journey_slideshow(
    df: pd.DataFrame,
    partners_df: pd.DataFrame,
    settings: dict,
) -> None:
    media = load_journey_media_df()
    st.markdown("### 📸 Journey memories")
    if media.empty:
        st.info(
            "Add photos on **Today** (quests & day shots), or under **Partners** — "
            "they collect here as a slideshow you can replay anytime."
        )
        return
    slides: list[dict] = []
    for _, row in media.iterrows():
        path = media_file_path(str(row["filename"]))
        if not path:
            continue
        slides.append(
            {
                "filename": str(row["filename"]),
                "label": media_slide_label(row, df, partners_df, settings),
            }
        )
    if not slides:
        st.warning("Photos were recorded but files are missing on this device.")
        return
    idx_key = "journey_slideshow_idx"
    if idx_key not in st.session_state:
        st.session_state[idx_key] = 0
    idx = int(st.session_state[idx_key]) % len(slides)
    slide = slides[idx]
    path = media_file_path(slide["filename"])
    st.caption(f"{len(slides)} photo{'s' if len(slides) != 1 else ''} · {idx + 1} of {len(slides)}")
    if path:
        st.image(str(path), use_container_width=True)
    st.markdown(f"**{html.escape(slide['label'])}**")
    prev_col, next_col = st.columns(2)
    with prev_col:
        if st.button("← Previous", key="slideshow_prev", use_container_width=True):
            st.session_state[idx_key] = (idx - 1) % len(slides)
            st.rerun()
    with next_col:
        if st.button("Next →", key="slideshow_next", use_container_width=True):
            st.session_state[idx_key] = (idx + 1) % len(slides)
            st.rerun()


def load_encounters_df() -> pd.DataFrame:
    conn = get_conn()
    try:
        df = pd.read_sql_query(
            """
            SELECT e.*, p.display_name, p.auto_label, p.custom_name, p.first_location,
                   a.day_num, a.location AS activity_location, a.title AS activity_title,
                   a.venue_name, a.time_slot
            FROM encounters e
            JOIN partners p ON p.id = e.partner_id
            JOIN activities a ON a.activity_key = e.activity_key
            ORDER BY e.created_at, e.slot_index
            """,
            conn,
        )
    except sqlite3.OperationalError:
        df = pd.DataFrame()
    conn.close()
    return df


def load_encounters_for_activity(activity_key: str) -> pd.DataFrame:
    enc = load_encounters_df()
    if enc.empty:
        return enc
    return enc[enc["activity_key"] == activity_key].sort_values("slot_index")


def location_person_label(location: str) -> str:
    meta = LOCATIONS.get(location, {})
    label = meta.get("label", location.replace("_", " ").title())
    return label


def suggest_partner_label(location: str, slot_index: int = 0) -> str:
    conn = get_conn()
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM partners WHERE first_location = ?",
            (location,),
        ).fetchone()["c"]
    except sqlite3.OperationalError:
        count = 0
    conn.close()
    base = location_person_label(location).lower()
    return f"{base} guy #{count + 1 + slot_index}"


def get_or_create_partner(
    name_input: str,
    auto_label: str,
    location: str,
    day_num: int | None,
    existing_partners: pd.DataFrame,
) -> int:
    name = name_input.strip() or auto_label
    conn = get_conn()
    if not existing_partners.empty and name in existing_partners["display_name"].values:
        pid = int(existing_partners.loc[existing_partners["display_name"] == name, "id"].iloc[0])
        conn.close()
        return pid

    custom = name if name != auto_label else None
    display = name
    now = datetime.now().isoformat(timespec="seconds")
    try:
        cur = conn.execute(
            """
            INSERT INTO partners(display_name, auto_label, custom_name, first_location, first_seen_day, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (display, auto_label, custom, location, day_num, now),
        )
        pid = int(cur.lastrowid)
    except sqlite3.IntegrityError:
        row = conn.execute("SELECT id FROM partners WHERE display_name = ?", (display,)).fetchone()
        pid = int(row["id"])
    conn.commit()
    conn.close()
    return pid


def save_encounters(activity_key: str, encounter_rows: list[dict]):
    conn = get_conn()
    conn.execute("DELETE FROM encounters WHERE activity_key = ?", (activity_key,))
    now = datetime.now().isoformat(timespec="seconds")
    for row in encounter_rows:
        conn.execute(
            """
            INSERT INTO encounters(
                activity_key, partner_id, slot_index, act_types, initiated_by, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                activity_key,
                int(row["partner_id"]),
                int(row["slot_index"]),
                json.dumps(row.get("act_types") or []),
                row.get("initiated_by") or "Mutual",
                row.get("notes") or "",
                now,
            ),
        )
    conn.commit()
    conn.close()


def delete_encounters_for_activity(activity_key: str):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM encounters WHERE activity_key = ?", (activity_key,))
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()


def partner_stats(encounters: pd.DataFrame, partners: pd.DataFrame) -> dict:
    if encounters.empty:
        return {
            "unique_partners": 0,
            "total_encounters": 0,
            "repeat_partners": 0,
            "act_counts": {},
            "by_location": {},
        }

    act_counts: dict[str, int] = {}
    for acts_json in encounters["act_types"]:
        try:
            acts = json.loads(acts_json) if isinstance(acts_json, str) else acts_json
        except json.JSONDecodeError:
            acts = []
        for act in acts:
            act_counts[act] = act_counts.get(act, 0) + 1

    partner_enc_counts = encounters.groupby("partner_id").size()
    repeat_partners = int((partner_enc_counts > 1).sum())

    by_location: dict[str, int] = {}
    for loc, grp in encounters.groupby("activity_location"):
        by_location[loc] = len(grp)

    return {
        "unique_partners": int(encounters["partner_id"].nunique()),
        "total_encounters": len(encounters),
        "repeat_partners": repeat_partners,
        "act_counts": act_counts,
        "by_location": by_location,
    }


def _encounter_partner_row(enc_row: pd.Series) -> dict:
    try:
        acts = json.loads(enc_row["act_types"])
    except (json.JSONDecodeError, TypeError):
        acts = list(DEFAULT_PARTNER_ACTS)
    init = enc_row.get("initiated_by") or "Mutual"
    if init == "Them":
        init = "Him"
    return {
        "display_name": str(enc_row["display_name"]),
        "act_types": acts,
        "initiated_by": init,
        "notes": str(enc_row.get("notes") or ""),
    }


def load_dismissed_presets(activity_key: str) -> set[str]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT preset_id FROM preset_dismissals WHERE activity_key = ?",
            (activity_key,),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return {r["preset_id"] for r in rows}


def dismiss_preset(activity_key: str, preset_id: str):
    conn = get_conn()
    conn.execute(
        """
        INSERT OR REPLACE INTO preset_dismissals(activity_key, preset_id, dismissed_at)
        VALUES (?, ?, ?)
        """,
        (activity_key, preset_id, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def suggested_points_for_location(
    encounters: pd.DataFrame,
    location: str,
    before_day: int,
    planned_points: int,
) -> int:
    """Typical partner/point count at this location from earlier days."""
    if encounters.empty or "activity_location" not in encounters.columns:
        return planned_points
    loc_enc = encounters[
        (encounters["activity_location"] == location) & (encounters["day_num"] < before_day)
    ]
    if loc_enc.empty:
        return planned_points
    per_session = loc_enc.groupby("activity_key").size()
    if per_session.empty:
        return planned_points
    typical = int(round(per_session.median()))
    return max(planned_points, typical)


def build_location_presets(
    df: pd.DataFrame,
    encounters: pd.DataFrame,
    location: str,
    before_day: int,
    target_activity_key: str,
) -> list[dict]:
    if before_day <= 1 or encounters.empty:
        return []
    if location == REPEAT_LOCATION:
        return _build_repeat_presets(df, encounters, before_day, target_activity_key)
    dismissed = load_dismissed_presets(target_activity_key)
    presets: list[dict] = []

    earned = df[
        (df["status"] == "earned")
        & (df["day_num"] < before_day)
        & (df["location"] == location)
    ].sort_values(["day_num", "slot_order"], ascending=[False, True])

    for _, act in earned.iterrows():
        preset_id = str(act["activity_key"])
        if preset_id in dismissed:
            continue
        enc = encounters[encounters["activity_key"] == preset_id].sort_values("slot_index")
        if enc.empty:
            continue
        partners = [_encounter_partner_row(er) for _, er in enc.iterrows()]
        presets.append(
            {
                "preset_id": preset_id,
                "source_day": int(act["day_num"]),
                "source_title": str(act["title"]),
                "location": location,
                "partner_count": len(partners),
                "partners": partners,
                "points": int(act["earned_points"]) if pd.notna(act.get("earned_points")) else int(act["points"]),
                "is_likely": False,
            }
        )

    likely_id = f"likely_{location}"
    if likely_id not in dismissed and location in HISTORY_PRESET_LOCATIONS:
        likely = _build_likely_location_preset(encounters, location, before_day, dismissed)
        if likely:
            presets.insert(0, likely)

    return presets[:6]


def _build_repeat_presets(
    df: pd.DataFrame,
    encounters: pd.DataFrame,
    before_day: int,
    target_activity_key: str,
) -> list[dict]:
    dismissed = load_dismissed_presets(target_activity_key)
    presets: list[dict] = []

    earned = df[
        (df["status"] == "earned")
        & (df["day_num"] < before_day)
        & (~df["location"].isin([GYM_LOCATION, REPEAT_LOCATION]))
    ].sort_values(["day_num", "slot_order"], ascending=[False, True])

    for _, act in earned.iterrows():
        preset_id = str(act["activity_key"])
        if preset_id in dismissed:
            continue
        enc = encounters[encounters["activity_key"] == preset_id].sort_values("slot_index")
        if enc.empty:
            continue
        partners = [_encounter_partner_row(er) for _, er in enc.iterrows()]
        loc_label = location_person_label(str(act["location"]))
        presets.append(
            {
                "preset_id": preset_id,
                "source_day": int(act["day_num"]),
                "source_title": f"{act['title']} · {loc_label}",
                "location": REPEAT_LOCATION,
                "partner_count": len(partners),
                "partners": partners,
                "points": int(act["earned_points"]) if pd.notna(act.get("earned_points")) else int(act["points"]),
                "is_likely": False,
            }
        )

    likely_id = "likely_repeat"
    if likely_id not in dismissed:
        prior = encounters[encounters["day_num"] < before_day]
        if not prior.empty:
            freq = (
                prior.groupby("display_name")
                .agg(
                    count=("display_name", "size"),
                    act_types=("act_types", "last"),
                    initiated_by=("initiated_by", "last"),
                    notes=("notes", "last"),
                )
                .sort_values("count", ascending=False)
            )
            top = freq.head(min(2, len(freq)))
            if not top.empty:
                partners = []
                for name, row in top.iterrows():
                    try:
                        acts = json.loads(row["act_types"])
                    except (json.JSONDecodeError, TypeError):
                        acts = list(DEFAULT_PARTNER_ACTS)
                    init = row.get("initiated_by") or "Mutual"
                    if init == "Them":
                        init = "Him"
                    partners.append(
                        {
                            "display_name": str(name),
                            "act_types": acts,
                            "initiated_by": init,
                            "notes": str(row.get("notes") or ""),
                        }
                    )
                presets.insert(
                    0,
                    {
                        "preset_id": likely_id,
                        "source_day": 0,
                        "source_title": "Most likely reconnects (from your history)",
                        "location": REPEAT_LOCATION,
                        "partner_count": len(partners),
                        "partners": partners,
                        "points": len(partners),
                        "is_likely": True,
                    },
                )

    return presets[:6]


def _build_likely_location_preset(
    encounters: pd.DataFrame,
    location: str,
    before_day: int,
    dismissed: set[str],
) -> dict | None:
    likely_id = f"likely_{location}"
    if likely_id in dismissed:
        return None
    loc_enc = encounters[
        (encounters["activity_location"] == location) & (encounters["day_num"] < before_day)
    ]
    if loc_enc.empty:
        return None
    session_count = loc_enc["activity_key"].nunique()
    if session_count < 1:
        return None

    freq = (
        loc_enc.groupby("display_name")
        .agg(
            count=("display_name", "size"),
            act_types=("act_types", "last"),
            initiated_by=("initiated_by", "last"),
            notes=("notes", "last"),
        )
        .sort_values("count", ascending=False)
    )
    typical_count = int(round(loc_enc.groupby("activity_key").size().median()))
    typical_count = max(1, typical_count)
    partners = []
    for name, row in freq.head(typical_count).iterrows():
        try:
            acts = json.loads(row["act_types"]) if isinstance(row["act_types"], str) else list(DEFAULT_PARTNER_ACTS)
        except (json.JSONDecodeError, TypeError):
            acts = list(DEFAULT_PARTNER_ACTS)
        init = row.get("initiated_by") or "Mutual"
        if init == "Them":
            init = "Him"
        partners.append(
            {
                "display_name": str(name),
                "act_types": acts,
                "initiated_by": init,
                "notes": str(row.get("notes") or ""),
            }
        )
    if not partners:
        return None
    loc_label = location_person_label(location)
    return {
        "preset_id": likely_id,
        "source_day": 0,
        "source_title": f"Most likely at {loc_label}",
        "location": location,
        "partner_count": len(partners),
        "partners": partners,
        "points": len(partners),
        "is_likely": True,
    }


def apply_preset_to_session(
    key_prefix: str,
    activity_key: str,
    preset: dict,
    partners_df: pd.DataFrame,
):
    log_prefix = f"{key_prefix}_log_{activity_key}"
    partner_options = ["— New partner —"]
    if not partners_df.empty:
        partner_options += partners_df["display_name"].tolist()

    st.session_state[f"{key_prefix}_pts_{activity_key}"] = int(
        preset.get("points") or len(preset["partners"])
    )

    for i, partner in enumerate(preset["partners"]):
        name = partner["display_name"]
        pick = name if name in partner_options else "— New partner —"
        st.session_state[f"{log_prefix}_pick_{i}"] = pick
        st.session_state[f"{log_prefix}_name_{i}"] = name
        st.session_state[f"{log_prefix}_acts_{i}"] = partner.get("act_types", list(DEFAULT_PARTNER_ACTS))
        init = partner.get("initiated_by", "Mutual")
        if init == "Them":
            init = "Him"
        st.session_state[f"{log_prefix}_init_{i}"] = init
        st.session_state[f"{log_prefix}_pnotes_{i}"] = partner.get("notes", "")

    st.session_state[f"preset_applied_{key_prefix}_{activity_key}"] = preset["preset_id"]
    st.session_state[f"quest_armed_{key_prefix}_{activity_key}"] = True


def render_history_presets(
    df: pd.DataFrame,
    encounters: pd.DataFrame,
    row: pd.Series,
    day_num: int,
    key_prefix: str,
    partners_df: pd.DataFrame,
    target_activity_key: str | None = None,
):
    location = str(row["location"])
    target_key = target_activity_key or str(row["activity_key"])
    presets = build_location_presets(df, encounters, location, day_num, target_key)
    if not presets:
        return

    loc_label = location_person_label(location)
    st.markdown(f"##### 🔮 Suggested for {loc_label} (from your history)")
    st.caption("Confirm a preset to pre-fill partners and points — or dismiss ones that don't fit today.")

    applied = st.session_state.get(f"preset_applied_{key_prefix}_{target_key}")

    for preset in presets:
        pid = preset["preset_id"]
        if preset.get("is_likely"):
            title = f"⭐ **{preset['source_title']}**"
        else:
            title = f"**Day {preset['source_day']}** · {preset['source_title']}"

        partner_preview = ", ".join(p["display_name"] for p in preset["partners"][:6])
        if len(preset["partners"]) > 6:
            partner_preview += f" +{len(preset['partners']) - 6} more"

        act_sets = [set(p.get("act_types") or []) for p in preset["partners"]]
        common_acts = set.intersection(*act_sets) if act_sets else set()
        acts_hint = ", ".join(sorted(common_acts)[:3]) if common_acts else "mixed acts"

        box_cls = "dl-quest day-met" if applied == pid else "dl-quest pending"
        st.markdown(
            f"<div class='{box_cls}' style='padding:0.65rem 0.85rem;margin-bottom:0.45rem;'>"
            f"{title}<br/>"
            f"<span style='color:#777;font-size:0.82rem;'>"
            f"{len(preset['partners'])} partners · {partner_preview}<br/>"
            f"Usually: {acts_hint} · {preset.get('points', len(preset['partners']))} pts"
            f"</span></div>",
            unsafe_allow_html=True,
        )

        c_use, c_drop = st.columns([1, 1])
        with c_use:
            if st.button(
                "✅ Use preset",
                key=f"{key_prefix}_preset_use_{target_key}_{pid}",
                use_container_width=True,
            ):
                apply_preset_to_session(key_prefix, target_key, preset, partners_df)
                st.rerun()
        with c_drop:
            if st.button(
                "🗑️ Dismiss",
                key=f"{key_prefix}_preset_drop_{target_key}_{pid}",
                use_container_width=True,
            ):
                dismiss_preset(target_key, pid)
                st.rerun()


def render_partner_logging_form(
    activity_key: str,
    location: str,
    day_num: int,
    slot_count: int,
    key_prefix: str,
    partners_df: pd.DataFrame,
    existing: pd.DataFrame | None = None,
) -> list[dict] | None:
    st.markdown(f"**Log {slot_count} partner(s)** — saves automatically; refresh or edit to count XP.")
    if slot_count >= BONUS_STREAK_COUNT:
        loc_name = location_person_label(location)
        st.info(
            f"🔟 Logging **{slot_count}** partners — eligible for "
            f"**+{BONUS_STREAK_POINTS} extra pts** if this is one session at **{loc_name}**."
        )
    partner_options = ["— New partner —"]
    if not partners_df.empty:
        partner_options += partners_df["display_name"].tolist()

    encounter_rows: list[dict] = []
    partner_tabs = st.tabs([f"Partner {i + 1}" for i in range(max(1, slot_count))])

    for i, ptab in enumerate(partner_tabs):
        with ptab:
            auto_label = suggest_partner_label(location, i)
            ex = None
            if existing is not None and not existing.empty and i < len(existing):
                ex = existing.iloc[i]

            default_pick = ex["display_name"] if ex is not None else "— New partner —"
            if default_pick not in partner_options:
                default_pick = "— New partner —"
            pick_idx = partner_options.index(default_pick)

            pick = st.selectbox(
                "Select or new",
                partner_options,
                index=pick_idx,
                key=f"{key_prefix}_pick_{i}",
                help="Pick someone you've logged before, or create a new label.",
            )
            is_repeat = pick != "— New partner —"
            default_name = pick if is_repeat else (ex["display_name"] if ex is not None else auto_label)

            if ex is not None:
                try:
                    default_acts = json.loads(ex["act_types"])
                except (json.JSONDecodeError, TypeError):
                    default_acts = list(DEFAULT_PARTNER_ACTS)
                default_init = ex.get("initiated_by") or "Mutual"
                default_pnotes = ex.get("notes") or ""
            else:
                default_acts = list(DEFAULT_PARTNER_ACTS)
                default_init = "Mutual"
                default_pnotes = ""
            if default_init == "Them":
                default_init = "Him"

            name = st.text_input(
                "Display name",
                value=default_name,
                key=f"{key_prefix}_name_{i}",
                help="Auto-label like «sauna guy #1» unless you rename.",
            )
            if is_repeat:
                st.caption("🔁 Repeat partner")
            else:
                st.caption(f"🆕 Suggested: `{auto_label}`")

            acts = st.multiselect(
                "What happened",
                ACT_TYPES,
                default=default_acts,
                key=f"{key_prefix}_acts_{i}",
            )
            init_idx = INITIATED_BY.index(default_init) if default_init in INITIATED_BY else 3
            initiated = st.selectbox("Initiated by", INITIATED_BY, index=init_idx, key=f"{key_prefix}_init_{i}")
            notes = st.text_input("Notes (optional)", value=default_pnotes, key=f"{key_prefix}_pnotes_{i}")

            encounter_rows.append(
                {
                    "slot_index": i,
                    "name": name,
                    "auto_label": auto_label,
                    "is_repeat": is_repeat,
                    "act_types": acts,
                    "initiated_by": initiated,
                    "notes": notes,
                }
            )

    return encounter_rows


def encounter_rows_ready(encounter_rows: list[dict] | None) -> bool:
    if not encounter_rows:
        return False
    return all(str(row.get("name", "")).strip() for row in encounter_rows)


def quest_log_prefix(key_prefix: str, activity_key: str) -> str:
    return f"{key_prefix}_log_{activity_key}"


def encounter_rows_from_session(
    log_prefix: str,
    location: str,
    slot_count: int,
) -> list[dict]:
    count = max(1, slot_count)
    rows: list[dict] = []
    for i in range(count):
        auto_label = suggest_partner_label(location, i)
        pick = st.session_state.get(f"{log_prefix}_pick_{i}", "— New partner —")
        rows.append(
            {
                "slot_index": i,
                "name": st.session_state.get(f"{log_prefix}_name_{i}", ""),
                "auto_label": auto_label,
                "is_repeat": pick != "— New partner —",
                "act_types": st.session_state.get(f"{log_prefix}_acts_{i}", list(DEFAULT_PARTNER_ACTS)),
                "initiated_by": st.session_state.get(f"{log_prefix}_init_{i}", "Mutual"),
                "notes": st.session_state.get(f"{log_prefix}_pnotes_{i}", ""),
            }
        )
    return rows


def quest_is_preloaded(key_prefix: str, activity_key: str) -> bool:
    return bool(
        st.session_state.get(f"quest_armed_{key_prefix}_{activity_key}")
        or st.session_state.get(f"preset_applied_{key_prefix}_{activity_key}")
    )


def clear_quest_armed(key_prefix: str, activity_key: str) -> None:
    st.session_state.pop(f"quest_armed_{key_prefix}_{activity_key}", None)


def quest_partner_log_count(row, key_prefix: str, extra: int | None = None) -> int:
    if is_before_noon_village(row):
        return 1
    if extra is not None:
        return max(1, int(extra))
    pts_key = f"{key_prefix}_pts_{row['activity_key']}"
    if pts_key in st.session_state:
        return max(1, int(st.session_state[pts_key]))
    return max(1, int(row["points"]))


def quest_quick_complete_preview(encounter_rows: list[dict]) -> str:
    names = [str(r.get("name", "")).strip() for r in encounter_rows if str(r.get("name", "")).strip()]
    if not names:
        return "Partners pre-filled"
    preview = ", ".join(names[:4])
    if len(names) > 4:
        preview += f" +{len(names) - 4} more"
    return f"{len(names)} partner(s) · {preview}"


def render_quest_quick_complete_bar(
    row,
    day_num: int,
    key_prefix: str,
    partners_df: pd.DataFrame,
    encounter_rows: list[dict],
    notes: str,
    points: int,
) -> bool:
    """Top quick-complete action when partners are pre-filled. Returns True if completed."""
    act_key = str(row["activity_key"])
    st.markdown(
        f'<div class="cj-quick-complete-bar">'
        f'<div class="cj-quick-complete-title">Ready — tap to complete</div>'
        f'<div class="cj-quick-complete-sub">{quest_quick_complete_preview(encounter_rows)}'
        f" · +{format_points(points)} XP</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    if st.button(
        complete_quest_button_label(row, points),
        key=f"{key_prefix}_quick_complete_{act_key}",
        type="primary",
        use_container_width=True,
    ):
        if try_auto_complete_direct(
            act_key,
            row["location"],
            day_num,
            encounter_rows,
            partners_df,
            notes,
            points,
        ):
            clear_quest_armed(key_prefix, act_key)
            return True
    return False


def quest_quick_complete_context(
    row,
    key_prefix: str,
    encounters_df: pd.DataFrame,
    day_num: int,
) -> dict | None:
    """Build quick-complete inputs when a preset pre-filled this quest."""
    act_key = str(row["activity_key"])
    if not quest_is_preloaded(key_prefix, act_key):
        return None
    mode_key = f"{key_prefix}_mode_{act_key}"
    if st.session_state.get(mode_key, "Complete as planned") != "Complete as planned":
        return None
    if is_solo_half_point(row):
        return None
    notes_key = f"{key_prefix}_notes_{act_key}"
    pts_key = f"{key_prefix}_pts_{act_key}"
    if is_bring_back_half(row):
        log_count = 1
        points = 1
    else:
        planned = int(row["points"])
        before_noon = is_before_noon_village(row)
        if pts_key in st.session_state:
            points = int(st.session_state[pts_key])
        else:
            points = suggested_points_for_location(
                encounters_df, row["location"], day_num, planned
            )
        if before_noon:
            points = min(points, 1)
        log_count = quest_partner_log_count(row, key_prefix, points)
    return {
        "log_count": log_count,
        "points": points,
        "notes": st.session_state.get(notes_key, ""),
    }


def maybe_render_quest_quick_complete(
    row,
    day_num: int,
    key_prefix: str,
    partners_df: pd.DataFrame,
    encounters_df: pd.DataFrame,
) -> bool:
    """Show quick-complete bar right under the quest card when preset pre-filled."""
    ctx = quest_quick_complete_context(row, key_prefix, encounters_df, day_num)
    if not ctx:
        return False
    act_key = str(row["activity_key"])
    log_prefix = quest_log_prefix(key_prefix, act_key)
    enc_rows = encounter_rows_from_session(
        log_prefix, row["location"], ctx["log_count"]
    )
    if not encounter_rows_ready(enc_rows):
        return False
    if render_quest_quick_complete_bar(
        row,
        day_num,
        key_prefix,
        partners_df,
        enc_rows,
        ctx["notes"],
        ctx["points"],
    ):
        st.rerun()
    return True


def finalize_pending_with_saved_encounters(df: pd.DataFrame) -> bool:
    """Complete pending quests that already have partner rows saved (e.g. after refresh)."""
    changed = False
    for _, row in df[df["status"] == "pending"].iterrows():
        enc = load_encounters_for_activity(row["activity_key"])
        if enc.empty:
            continue
        notes = row["notes"] if pd.notna(row["notes"]) else ""
        earn_activity(row["activity_key"], str(notes), int(row["points"]))
        changed = True
    return changed


def try_auto_complete_direct(
    activity_key: str,
    location: str,
    day_num: int,
    encounter_rows: list[dict],
    partners_df: pd.DataFrame,
    notes: str,
    points: int,
) -> bool:
    if not encounter_rows_ready(encounter_rows):
        return False
    persist_encounter_rows(activity_key, location, day_num, encounter_rows, partners_df)
    complete_quest(activity_key, notes, points)
    return True


def try_auto_complete_substitute(
    slot_key: str,
    substitute_key: str,
    sub_row: pd.Series,
    encounter_rows: list[dict],
    partners_df: pd.DataFrame,
    sub_notes: str,
) -> bool:
    if not encounter_rows_ready(encounter_rows):
        return False
    persist_encounter_rows(
        slot_key,
        sub_row["location"],
        int(sub_row["day_num"]),
        encounter_rows,
        partners_df,
    )
    complete_substitute(slot_key, substitute_key, sub_notes)
    return True


def persist_encounter_rows(
    activity_key: str,
    location: str,
    day_num: int,
    encounter_rows: list[dict],
    partners_df: pd.DataFrame,
):
    saved = []
    for row in encounter_rows:
        pid = get_or_create_partner(
            row["name"],
            row["auto_label"],
            location,
            day_num,
            partners_df,
        )
        saved.append(
            {
                "partner_id": pid,
                "slot_index": row["slot_index"],
                "act_types": row["act_types"],
                "initiated_by": row["initiated_by"],
                "notes": row["notes"],
            }
        )
        partners_df = load_partners_df()
    save_encounters(activity_key, saved)
    before_bonus = snapshot_celebration_state()
    maybe_auto_streak_bonus(day_num, location, len(encounter_rows))
    emit_celebration_diff(before_bonus, snapshot_celebration_state())


def render_encounter_summary(activity_key: str):
    enc = load_encounters_for_activity(activity_key)
    if enc.empty:
        return
    st.markdown("**Partners logged**")
    for _, erow in enc.iterrows():
        try:
            acts = json.loads(erow["act_types"])
        except (json.JSONDecodeError, TypeError):
            acts = []
        acts_txt = ", ".join(acts) if acts else "—"
        repeat = ""
        partner_enc = load_encounters_df()
        if not partner_enc.empty:
            pid = erow["partner_id"]
            if len(partner_enc[partner_enc["partner_id"] == pid]) > 1:
                repeat = " 🔁"
        avatar = partner_avatar_html(int(erow["partner_id"]), str(erow["display_name"]), 32)
        st.markdown(
            f"<div style='display:flex;align-items:center;margin:0.35rem 0;'>"
            f"{avatar}<span><strong>{html.escape(str(erow['display_name']))}</strong> · "
            f"{html.escape(acts_txt)} · <em>{html.escape(str(erow['initiated_by']))} initiated</em>"
            f"{repeat}</span></div>",
            unsafe_allow_html=True,
        )


def _parse_encounter_acts(acts_json) -> list[str]:
    try:
        acts = json.loads(acts_json) if isinstance(acts_json, str) else acts_json
        return list(acts) if acts else []
    except (json.JSONDecodeError, TypeError):
        return []


def encounter_venue_label(row) -> str:
    venue = str(row.get("venue_name") or "").strip()
    if venue:
        return venue
    return location_person_label(str(row.get("activity_location", "")))


def encounter_log_frame(encounters: pd.DataFrame) -> pd.DataFrame:
    if encounters.empty:
        return pd.DataFrame(
            columns=["Day", "Time", "Location", "Activity", "Partner", "Acts", "Initiated", "Notes"]
        )
    rows = []
    for _, er in encounters.iterrows():
        acts = ", ".join(_parse_encounter_acts(er["act_types"]))
        slot = str(er.get("time_slot") or "")
        rows.append(
            {
                "Day": int(er["day_num"]),
                "Time": time_slot_label(slot) if slot else "—",
                "Location": encounter_venue_label(er),
                "Activity": str(er["activity_title"]),
                "Partner": str(er["display_name"]),
                "Acts": acts or "—",
                "Initiated": str(er.get("initiated_by") or "Mutual"),
                "Notes": str(er.get("notes") or ""),
            }
        )
    return pd.DataFrame(rows)


def filter_encounters(
    encounters: pd.DataFrame,
    *,
    partner_id: int | None = None,
    location: str | None = None,
    activity_key: str | None = None,
    day_num: int | None = None,
) -> pd.DataFrame:
    df = encounters
    if df.empty:
        return df
    if partner_id is not None:
        df = df[df["partner_id"] == partner_id]
    if location:
        df = df[df["activity_location"] == location]
    if activity_key:
        df = df[df["activity_key"] == activity_key]
    if day_num is not None:
        df = df[df["day_num"] == int(day_num)]
    return df


def partner_tally_frame(encounters: pd.DataFrame, partners: pd.DataFrame) -> pd.DataFrame:
    if encounters.empty:
        return pd.DataFrame(columns=["Partner", "Encounters", "Days", "Locations", "Top acts"])
    rows = []
    for pid, grp in encounters.groupby("partner_id"):
        prow = partner_row(partners, int(pid))
        if prow is None:
            continue
        acts: list[str] = []
        for aj in grp["act_types"]:
            acts.extend(_parse_encounter_acts(aj))
        act_summary = ", ".join(sorted(set(acts))) if acts else "—"
        locs = sorted({encounter_venue_label(r) for _, r in grp.iterrows()})
        rows.append(
            {
                "Partner": prow["display_name"],
                "Encounters": len(grp),
                "Days": ", ".join(str(d) for d in sorted(grp["day_num"].unique())),
                "Locations": ", ".join(locs),
                "Top acts": act_summary,
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Encounters", "Partner"], ascending=[False, True])
    return out


def render_partners_tab(encounters: pd.DataFrame, partners: pd.DataFrame):
    st.markdown("### Partner ledger")
    stats = partner_stats(encounters, partners)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unique partners", stats["unique_partners"])
    c2.metric("Total encounters", stats["total_encounters"])
    c3.metric("Repeat partners", stats["repeat_partners"])
    c4.metric("Acts logged", sum(stats["act_counts"].values()))

    if encounters.empty:
        st.info("No partners logged yet. Complete an activity and use the partner tabs to log each interaction.")
        return

    st.markdown("#### Filters")
    f1, f2, f3, f4 = st.columns(4)
    partner_opts: dict[str, int | None] = {"All partners": None}
    for _, pr in partners.sort_values("display_name").iterrows():
        partner_opts[str(pr["display_name"])] = int(pr["id"])
    with f1:
        partner_label = st.selectbox("Partner", list(partner_opts.keys()), key="ptn_filter_partner")
    loc_keys = sorted(encounters["activity_location"].unique())
    loc_opts: dict[str, str | None] = {"All locations": None}
    loc_opts.update({location_person_label(k): k for k in loc_keys})
    with f2:
        loc_label = st.selectbox("Location", list(loc_opts.keys()), key="ptn_filter_loc")
    act_keys = encounters.drop_duplicates("activity_key")[["activity_key", "activity_title", "day_num"]]
    act_opts: dict[str, str | None] = {"All activities": None}
    for _, ar in act_keys.sort_values(["day_num", "activity_title"]).iterrows():
        act_opts[f"Day {int(ar['day_num'])} · {ar['activity_title']}"] = str(ar["activity_key"])
    with f3:
        act_label = st.selectbox("Activity", list(act_opts.keys()), key="ptn_filter_act")
    day_opts: dict[str, int | None] = {"All days": None}
    day_opts.update({f"Day {d}": int(d) for d in sorted(encounters["day_num"].unique())})
    with f4:
        day_label = st.selectbox("Day", list(day_opts.keys()), key="ptn_filter_day")

    filtered = filter_encounters(
        encounters,
        partner_id=partner_opts[partner_label],
        location=loc_opts[loc_label],
        activity_key=act_opts[act_label],
        day_num=day_opts[day_label],
    )
    st.caption(f"Showing **{len(filtered)}** of **{len(encounters)}** encounters")

    tab_overview, tab_partner, tab_location, tab_activity, tab_log = st.tabs(
        ["📊 Overview", "👤 By partner", "📍 By location", "🎯 By activity", "📜 Full log"]
    )

    log_df = encounter_log_frame(filtered)
    tally_df = partner_tally_frame(filtered, partners)

    with tab_overview:
        chart_c1, chart_c2 = st.columns(2)
        with chart_c1:
            st.markdown("**Encounters by location**")
            if not filtered.empty:
                loc_counts = (
                    filtered.assign(_loc=filtered.apply(encounter_venue_label, axis=1))
                    .groupby("_loc")
                    .size()
                    .reset_index(name="Count")
                    .sort_values("Count", ascending=False)
                )
                st.bar_chart(loc_counts.set_index("_loc"))
            else:
                st.caption("No data for current filters.")
        with chart_c2:
            st.markdown("**Encounters by activity**")
            if not filtered.empty:
                act_counts = (
                    filtered.groupby("activity_title")
                    .size()
                    .reset_index(name="Count")
                    .sort_values("Count", ascending=False)
                )
                st.bar_chart(act_counts.set_index("activity_title"))
            else:
                st.caption("No data for current filters.")

        chart_c3, chart_c4 = st.columns(2)
        with chart_c3:
            st.markdown("**Partner tally**")
            if not tally_df.empty:
                st.bar_chart(tally_df[["Partner", "Encounters"]].set_index("Partner"))
            else:
                st.caption("No partners in filter.")
        with chart_c4:
            st.markdown("**Act types**")
            if not filtered.empty:
                f_act: dict[str, int] = {}
                for aj in filtered["act_types"]:
                    for act in _parse_encounter_acts(aj):
                        f_act[act] = f_act.get(act, 0) + 1
                act_type_df = pd.DataFrame(
                    [{"Act": k, "Count": v} for k, v in sorted(f_act.items(), key=lambda x: -x[1])]
                )
                if not act_type_df.empty:
                    st.bar_chart(act_type_df.set_index("Act"))
                else:
                    st.caption("No act types logged.")
            else:
                st.caption("No act types logged.")

    with tab_partner:
        focus = st.selectbox(
            "Focus partner (detail view)",
            ["— show all —"] + (tally_df["Partner"].tolist() if not tally_df.empty else []),
            key="ptn_focus_partner",
        )
        if not tally_df.empty:
            st.dataframe(tally_df, use_container_width=True, hide_index=True)
        if focus != "— show all —":
            pid = int(partners.loc[partners["display_name"] == focus, "id"].iloc[0])
            partner_enc = filtered[filtered["partner_id"] == pid]
            st.markdown(f"**{focus}** — {len(partner_enc)} encounter(s)")
            if not partner_enc.empty:
                by_loc = (
                    partner_enc.assign(_loc=partner_enc.apply(encounter_venue_label, axis=1))
                    .groupby("_loc")
                    .size()
                    .reset_index(name="Count")
                )
                st.bar_chart(by_loc.set_index("_loc"))
            st.dataframe(encounter_log_frame(partner_enc), use_container_width=True, hide_index=True)

    with tab_location:
        if filtered.empty:
            st.caption("No encounters for current filters.")
        else:
            for _, grp in filtered.groupby("activity_location"):
                loc_name = encounter_venue_label(grp.iloc[0])
                with st.expander(f"{loc_name} · {len(grp)} encounter(s)", expanded=False):
                    st.bar_chart(
                        grp.groupby("display_name")
                        .size()
                        .reset_index(name="Count")
                        .set_index("display_name")
                    )
                    st.dataframe(encounter_log_frame(grp), use_container_width=True, hide_index=True)

    with tab_activity:
        if filtered.empty:
            st.caption("No encounters for current filters.")
        else:
            for act_title, grp in filtered.groupby("activity_title"):
                day = int(grp.iloc[0]["day_num"])
                with st.expander(f"Day {day} · {act_title} · {len(grp)} partner(s)", expanded=False):
                    st.dataframe(encounter_log_frame(grp), use_container_width=True, hide_index=True)

    with tab_log:
        group_by = st.radio(
            "Group log by",
            ["Flat list", "Day", "Location", "Activity", "Partner"],
            horizontal=True,
            key="ptn_log_group",
        )
        if log_df.empty:
            st.caption("No encounters for current filters.")
        elif group_by == "Flat list":
            st.dataframe(log_df, use_container_width=True, hide_index=True)
        else:
            col_map = {
                "Day": "Day",
                "Location": "Location",
                "Activity": "Activity",
                "Partner": "Partner",
            }
            group_col = col_map[group_by]
            for key, grp in log_df.groupby(group_col, sort=False):
                with st.expander(f"{group_by}: {key} · {len(grp)} row(s)", expanded=(group_by == "Partner")):
                    st.dataframe(grp, use_container_width=True, hide_index=True)


def activity_label(row) -> str:
    meta = activity_meta(row)
    icon = meta.get("icon", "📍")
    pts_label = "½ pt" if row["location"] in HALF_POINT_LOCATIONS else f"{row['points']} pts"
    venue = meta.get("label", row["location"])
    return f"{icon} Day {row['day_num']} · {row['title']} ({pts_label}) · {venue}"


def earn_activity(activity_key: str, notes: str = "", earned_points: int | None = None):
    conn = get_conn()
    row = conn.execute(
        "SELECT points FROM activities WHERE activity_key = ?", (activity_key,)
    ).fetchone()
    pts = earned_points if earned_points is not None else int(row["points"])
    conn.execute(
        """
        UPDATE activities
        SET status='earned', fulfilled_by_key=activity_key,
            earned_points=?, notes=?, earned_at=?
        WHERE activity_key=?
        """,
        (pts, notes, datetime.now().isoformat(timespec="seconds"), activity_key),
    )
    conn.commit()
    conn.close()
    sync_scores(load_activities_df())


def substitute_activity(slot_key: str, substitute_key: str, notes: str = ""):
    conn = get_conn()
    sub = conn.execute(
        "SELECT title FROM activities WHERE activity_key=?",
        (substitute_key,),
    ).fetchone()
    slot = conn.execute(
        "SELECT points FROM activities WHERE activity_key=?",
        (slot_key,),
    ).fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        """
        UPDATE activities
        SET status='earned', fulfilled_by_key=?, earned_points=?, notes=?, earned_at=?
        WHERE activity_key=?
        """,
        (
            substitute_key,
            int(slot["points"]),
            notes or f"Substituted: completed «{sub['title']}» for this slot.",
            now,
            slot_key,
        ),
    )
    conn.commit()
    conn.close()
    sync_scores(load_activities_df())


def undo_activity(activity_key: str):
    delete_encounters_for_activity(activity_key)
    conn = get_conn()
    conn.execute(
        """
        UPDATE activities
        SET status='pending', fulfilled_by_key=NULL, earned_points=NULL, notes='', earned_at=NULL
        WHERE activity_key=?
        """,
        (activity_key,),
    )
    conn.commit()
    conn.close()
    sync_scores(load_activities_df())


def substitution_pool(df: pd.DataFrame, exclude_key: str | None = None) -> pd.DataFrame:
    pool = df[df["status"] == "pending"]
    if exclude_key:
        pool = pool[pool["activity_key"] != exclude_key]
    return pool


def current_journey_day(settings: dict) -> int:
    start = settings.get("journey_start", date.today().isoformat())[:10]
    try:
        elapsed = (date.today() - date.fromisoformat(start)).days + 1
    except ValueError:
        elapsed = 1
    return max(1, min(TOTAL_DAYS, elapsed))


def day_plan_meta(day_num: int) -> dict:
    for d in FOURTEEN_DAY_PLAN:
        if d["day"] == day_num:
            return d
    return {"day": day_num, "title": f"Day {day_num}", "target": 0}


def compute_stats(df: pd.DataFrame, bonus_df: pd.DataFrame | None = None) -> dict:
    bonus_df = bonus_df if bonus_df is not None else load_bonus_df()
    bsum = bonus_summary(bonus_df)
    earned = df[df["status"] == "earned"]
    total_points = int(df["points"].sum())
    earned_points = int(earned["earned_points"].fillna(earned["points"]).sum()) if not earned.empty else 0
    earned_count = len(earned)
    total_count = len(df)
    pct = round(100.0 * earned_count / total_count, 1) if total_count else 0.0

    days_complete = 0
    perfect_days = 0
    max_streak = 0
    streak = 0
    for day_num in range(1, TOTAL_DAYS + 1):
        day_df = df[df["day_num"] == day_num]
        status = day_goal_status(df, day_num)
        if status in ("met", "exceeded"):
            days_complete += 1
            streak += 1
            max_streak = max(max_streak, streak)
            if status == "exceeded":
                perfect_days += 1
        else:
            streak = 0

    collar_earned = earned_count == total_count and total_count > 0

    def _key_done(prefix, loc=None):
        subset = df[(df["day_num"] == int(prefix[1:])) & (df["status"] == "earned")]
        if loc:
            return not subset[subset["location"] == loc].empty
        return len(subset) == len(df[df["day_num"] == int(prefix[1:])])

    dunes_done = len(
        df[(df["location"] == "dunes") & (df["status"] == "earned")]
    )

    badge_state = {
        "days_complete": days_complete,
        "d6_club": _key_done("d6", "club"),
        "d12_club": _key_done("d12", "club"),
        "dunes_done": dunes_done,
        "d9_open": _key_done("d9", "open_door"),
        "d13_chain": bool(
            not df[
                (df["day_num"] == 13)
                & (df["title"].str.contains("Social Chain"))
                & (df["status"] == "earned")
            ].empty
        ),
        "d14_done": _key_done("d14"),
        "perfect_days": perfect_days,
        "max_streak": max_streak,
        "coke_count": bsum["coke_count"],
        "pr_breaks": bsum["pr_breaks"],
        "streak_count": bsum["streak_count"],
    }

    return {
        "total_points": total_points,
        "earned_points": earned_points,
        "goal_points": sum(day_goal_points(df, d) for d in range(1, TOTAL_DAYS + 1)),
        "extra_points": bsum["total_extra"],
        "grand_total": journey_grand_total(df, bonus_df),
        "earned_count": earned_count,
        "total_count": total_count,
        "pct": pct,
        "days_complete": days_complete,
        "collar_earned": collar_earned,
        "badge_state": badge_state,
        "max_streak": max_streak,
        "bonus_summary": bsum,
        "journey_pr": journey_pr_stats(df),
    }


ENCOURAGEMENTS = [
    (0, "Bonjour! Day 1 energy — go say hi to someone new! 👋"),
    (15, "You're warming up! The village is your playground. 🌴"),
    (30, "Halfway to Chosen level — keep that streak alive! 🔥"),
    (50, "Crushing it! Duolingo owl would be jealous. 🦉"),
    (70, "Collar Candidate vibes — the finish line is RIGHT there! 🏃‍♀️"),
    (90, "SO close! One more big day and that collar is HERS. 👑"),
    (100, "LEGENDARY! Collar earned — incroyable! 🎉🔗"),
]


def encouragement_for_pct(pct: float, collar_earned: bool = False) -> str:
    if collar_earned:
        return ENCOURAGEMENTS[-1][1]
    msg = ENCOURAGEMENTS[0][1]
    for threshold, text in ENCOURAGEMENTS:
        if pct >= threshold:
            msg = text
    return msg


def mascot_for_progress(pct: float, collar_earned: bool) -> str:
    if collar_earned:
        return "👑"
    if pct >= 75:
        return "🔥"
    if pct >= 40:
        return "💃"
    if pct >= 15:
        return "😏"
    return "🦜"


def render_compact_hud(stats: dict, journey_day: int, partner_summary: dict):
    total_fmt = format_points(float(stats.get("grand_total", 0)))
    streak = stats.get("max_streak", 0)
    partners = partner_summary.get("unique_partners", 0)
    st.markdown(
        f"""
<div class="cj-compact-bar">
  <div class="cj-compact-stat"><small>Total XP</small>⚡ {total_fmt}</div>
  <div class="cj-compact-stat"><small>Streak</small>🔥 {streak}</div>
  <div class="cj-compact-stat"><small>Journey</small>📅 Day {journey_day}/14</div>
  <div class="cj-compact-stat"><small>Partners</small>👥 {partners}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_game_hud(stats: dict, journey_day: int, partner_summary: dict):
    bsum = stats.get("bonus_summary", {})
    streak_display = stats.get("max_streak", 0)
    activity_xp = stats.get("goal_points", 0)
    bonus_xp = stats.get("extra_points", 0)
    total_xp = stats.get("grand_total", 0)
    activity_fmt = format_points(float(activity_xp))
    bonus_fmt = format_points(float(bonus_xp))
    total_fmt = format_points(float(total_xp))
    st.markdown(
        f"""
<div class="dl-hud">
  <div class="dl-pill xp">
    <div class="dl-pill-icon">⚡</div>
    <div><div class="dl-pill-label">Activity XP</div>
    <div class="dl-pill-value" id="cj-xp-activity" data-xp="{activity_xp}">{activity_fmt}</div></div>
  </div>
  <div class="dl-pill gems">
    <div class="dl-pill-icon">💎</div>
    <div><div class="dl-pill-label">Bonus XP</div>
    <div class="dl-pill-value" id="cj-xp-bonus" data-xp="{bonus_xp}">+{bonus_fmt}</div></div>
  </div>
  <div class="dl-pill xp">
    <div class="dl-pill-icon">🏆</div>
    <div><div class="dl-pill-label">Total XP</div>
    <div class="dl-pill-value" id="cj-xp-total" data-xp="{total_xp}">{total_fmt}</div></div>
  </div>
  <div class="dl-pill streak">
    <div class="dl-pill-icon">🔥</div>
    <div><div class="dl-pill-label">Day streak</div>
    <div class="dl-pill-value">{streak_display}</div></div>
  </div>
  <div class="dl-pill">
    <div class="dl-pill-icon">👥</div>
    <div><div class="dl-pill-label">Partners</div>
    <div class="dl-pill-value">{partner_summary.get('unique_partners', 0)}</div></div>
  </div>
  <div class="dl-pill">
    <div class="dl-pill-icon">📅</div>
    <div><div class="dl-pill-label">Today</div>
    <div class="dl-pill-value">Day {journey_day}</div></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    render_xp_countup(activity_xp, bonus_xp, total_xp)


def render_xp_countup(activity_xp: float, bonus_xp: float, total_xp: float):
    prev = st.session_state.get("_xp_anim_prev", {})
    current = {"activity": activity_xp, "bonus": bonus_xp, "total": total_xp}
    changed = prev and (
        abs(prev.get("activity", 0) - activity_xp) > 0.001
        or abs(prev.get("bonus", 0) - bonus_xp) > 0.001
        or abs(prev.get("total", 0) - total_xp) > 0.001
    )
    st.session_state["_xp_anim_prev"] = current
    if not changed:
        return
    payload = json.dumps(
        {
            "activity": {"from": prev.get("activity", 0), "to": activity_xp, "id": "cj-xp-activity", "prefix": ""},
            "bonus": {"from": prev.get("bonus", 0), "to": bonus_xp, "id": "cj-xp-bonus", "prefix": "+"},
            "total": {"from": prev.get("total", 0), "to": total_xp, "id": "cj-xp-total", "prefix": ""},
        }
    ).replace("<", "\\u003c")
    components.html(
        f"""
<script>
(function() {{
  const cfg = {payload};
  const doc = window.parent.document;
  function fmt(n) {{
    return Math.abs(n - Math.round(n)) < 0.001 ? String(Math.round(n)) : n.toFixed(1);
  }}
  Object.values(cfg).forEach((item, idx) => {{
    setTimeout(() => {{
      const el = doc.getElementById(item.id);
      if (!el) return;
      const from = Number(item.from), to = Number(item.to);
      if (from === to) return;
      const start = performance.now();
      const dur = 700;
      function tick(now) {{
        const t = Math.min(1, (now - start) / dur);
        const eased = 1 - Math.pow(1 - t, 3);
        const val = from + (to - from) * eased;
        el.textContent = (item.prefix || "") + fmt(val);
        if (t < 1) requestAnimationFrame(tick);
      }}
      requestAnimationFrame(tick);
    }}, idx * 120);
  }});
}})();
</script>
""",
        height=0,
        scrolling=False,
    )


def day_path_meta(day_num: int) -> dict:
    plan = day_plan_meta(day_num)
    base = DAY_PATH_META.get(
        day_num,
        {"icon": "🎯", "accent": "#1CB0F6", "kind": "normal", "reward": "Daily XP"},
    )
    return {**base, "title": plan.get("title", f"Day {day_num}"), "target": plan.get("target", 0)}


def path_lane_class(day_num: int) -> str:
    if day_num in (1, 7, 14):
        return "center"
    return "left" if day_num % 2 == 1 else "right"


def path_node_card_html(
    df: pd.DataFrame,
    day_num: int,
    journey_day: int,
    bonus_df: pd.DataFrame,
    prev_banner_image: str | None = None,
) -> str:
    meta = day_path_meta(day_num)
    plan = day_plan_meta(day_num)
    status = day_goal_status(df, day_num)
    is_current = day_num == journey_day
    day_df = df[df["day_num"] == day_num]
    earned = day_df[day_df["status"] == "earned"]
    earned_pts = day_activity_score(df, day_num)
    target = float(plan.get("target", 0))
    act_total = len(day_df)
    act_done = len(earned)
    prog = min(earned_pts / target, 1.0) if target else (act_done / act_total if act_total else 0)
    fill_cls = status if status in ("met", "exceeded") else ("met" if prog >= 1 else "")
    if status == "pending" and is_current:
        fill_cls = ""

    kind = meta.get("kind", "normal")
    card_cls = f"dl-path-node-card {status}"
    if kind == "chest":
        card_cls += " chest"
    if kind == "finale":
        card_cls += " finale"
    if is_current and status == "pending":
        card_cls += " current"

    badge = ""
    if kind == "start":
        badge = "<span class='dl-path-node-badge start'>START</span>"
    elif kind == "chest":
        badge = "<span class='dl-path-node-badge chest'>🎁 CHEST</span>"
    elif kind == "checkpoint":
        badge = "<span class='dl-path-node-badge checkpoint'>CHECKPOINT</span>"
    elif kind == "finale":
        badge = "<span class='dl-path-node-badge finale'>FINALE</span>"

    if is_current and status == "pending":
        status_label = "📍 Today — go!"
    elif status == "exceeded":
        status_label = "⭐ Crushed it!"
    elif status == "met":
        status_label = "✅ Goal met"
    else:
        status_label = "🔓 Open"

    bonus = plan.get("bonus_target")
    bonus_line = f" · 🎯 {bonus}+ stretch" if bonus else ""
    extra = day_bonus_points(bonus_df, day_num)
    extra_line = f" · 💎 +{extra} bonus" if extra else ""

    visual_plan = day_path_visual_plan(df, day_num, prev_banner_image)
    banner = visual_plan.get("banner")
    icon_visual = visual_plan.get("icon")
    if icon_visual:
        node_icon = (
            f'<div class="dl-path-node-icon img">'
            f'{location_meta_icon_html({"image": icon_visual["image"], "icon": "📍"}, 52)}</div>'
        )
    elif banner:
        node_icon = (
            f'<div class="dl-path-node-icon img">'
            f'{location_meta_icon_html({"image": banner["image"], "icon": "📍"}, 52)}</div>'
        )
    else:
        node_icon = f'<div class="dl-path-node-icon">{meta["icon"]}</div>'
    venue_strip = day_venue_strip_html(df, day_num, mode="path")
    photo_banner = path_node_photo_banner_html(df, day_num, prev_banner_image)

    return f"""
<div class="{card_cls}">
  {badge}
  {photo_banner}
  <div class="dl-path-node-top">
    {node_icon}
    <div class="dl-path-node-head">
      <div class="dl-path-node-day">Day {day_num}</div>
      <div class="dl-path-node-title">{meta['title']}</div>
      {venue_strip}
      <div class="dl-path-node-reward">🏆 {meta.get('reward', 'XP')}</div>
    </div>
  </div>
  <div class="dl-path-mini-bar"><div class="dl-path-mini-fill {fill_cls}" style="width:{prog * 100}%;"></div></div>
  <div class="dl-path-node-stats">
    <span>{format_points(earned_pts)} / {format_points(target)} XP{bonus_line}{extra_line}</span>
    <span>{act_done}/{act_total} quests</span>
  </div>
  <span class="dl-path-status-pill {('current' if is_current and status == 'pending' else status)}">{status_label}</span>
</div>
"""


def collar_trail_html(df: pd.DataFrame, journey_day: int) -> str:
    segs = []
    for day_num in range(1, TOTAL_DAYS + 1):
        status = day_goal_status(df, day_num)
        cls = status if status in ("met", "exceeded") else ""
        if day_num == journey_day and status == "pending":
            cls = "current"
        inner = "⭐" if status == "exceeded" else ("✓" if status in ("met", "exceeded") else str(day_num))
        segs.append(f'<div class="dl-collar-seg {cls}">{inner}</div>')
    return f'<div class="dl-collar-trail">{"".join(segs)}<span class="dl-collar-end">🔗</span></div>'


def journey_side_venue_html(df: pd.DataFrame, journey_day: int) -> str:
    """Today's lead venue photo for the right edge of the Journey banner."""
    plan = day_path_visual_plan(df, journey_day)
    banner = plan.get("banner")
    if not banner:
        return ""
    uri = _venue_image_uri(str(banner["image"]))
    if not uri:
        return ""
    label = str(banner.get("label") or banner.get("location") or "Today")
    if len(label) > 14:
        label = label[:12] + "…"
    return (
        f'<div class="cj-journey-unified-photo venue">'
        f'<img src="{uri}" alt="" />'
        f'<div class="cj-journey-venue-cap">{label}</div>'
        f"</div>"
    )


def render_path_hero(df: pd.DataFrame, stats: dict, journey_day: int):
    """Unified Journey banner — level bar + day trail + today's venue in one card."""
    days_done = int(stats.get("days_complete", 0))
    pct = int(stats.get("pct", 0))
    to_collar = max(0, TOTAL_DAYS - days_done)
    total_xp = format_points(float(stats.get("grand_total", 0)))
    level, level_desc, _ = level_for_pct(pct)
    today_meta = day_path_meta(journey_day)
    today_status = day_goal_status(df, journey_day)
    today_line = {
        "exceeded": "Today crushed — overflow → bonus! ⭐",
        "met": "Today's goal done — loot unlocked! ✅",
        "pending": f"Today: {today_meta['title']} — tap today's node to play.",
    }.get(today_status, "")
    stats_line = (
        f"Day {journey_day}/{TOTAL_DAYS} · {days_done} cleared · "
        f"{total_xp} XP · {to_collar} to go"
    )
    level_row = level_progress_html(stats, level, level_desc, compact=True)
    side_photo = journey_side_venue_html(df, journey_day)

    st.markdown(
        f"""
<div class="cj-journey-unified-hero cj-brand-path-hero">
  <div class="cj-journey-unified-body">
    <div class="dl-path-hero-title">Road to the Collar</div>
    <div class="cj-journey-unified-stats">{stats_line}</div>
    <div class="cj-journey-unified-level">{level_row}</div>
    {collar_trail_html(df, journey_day)}
    <div class="cj-journey-unified-today">{today_line}</div>
  </div>
  {side_photo}
</div>
""",
        unsafe_allow_html=True,
    )


def render_journey_path(df: pd.DataFrame, journey_day: int, bonus_df: pd.DataFrame | None = None):
    bonus_df = bonus_df if bonus_df is not None else load_bonus_df()
    st.markdown(
        '<div class="dl-section-head">🗺️ Adventure map</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="dl-adventure-map">', unsafe_allow_html=True)

    prev_status = None
    prev_banner_image: str | None = None
    for day_num in range(1, TOTAL_DAYS + 1):
        if day_num == 7:
            st.markdown(
                '<div class="dl-milestone-banner">🎉 Week 1 checkpoint — halfway there!</div>',
                unsafe_allow_html=True,
            )
        if day_num == 8:
            st.markdown(
                '<div class="dl-milestone-banner gold">✨ Week 2 — The push for the collar begins!</div>',
                unsafe_allow_html=True,
            )

        status = day_goal_status(df, day_num)
        if day_num > 1:
            vline_cls = "met" if prev_status in ("met", "exceeded") else ""
            if status in ("met", "exceeded"):
                vline_cls = "met"
            st.markdown(f'<div class="dl-path-vline {vline_cls}"></div>', unsafe_allow_html=True)

        lane = path_lane_class(day_num)
        st.markdown(f'<div class="dl-path-lane {lane}">', unsafe_allow_html=True)
        st.markdown(
            path_node_card_html(df, day_num, journey_day, bonus_df, prev_banner_image),
            unsafe_allow_html=True,
        )
        day_banner = day_path_visual_plan(df, day_num, prev_banner_image).get("banner")
        if day_banner:
            prev_banner_image = day_banner["image"]
        st.markdown("</div>", unsafe_allow_html=True)

        btn_cols = st.columns([2, 1, 2] if lane == "center" else ([1, 2, 2] if lane == "left" else [2, 2, 1]))
        btn_col = btn_cols[1 if lane == "center" else (0 if lane == "left" else 2)]
        with btn_col:
            label = "▶ Play" if day_num == journey_day else ("Review" if status in ("met", "exceeded") else "Open")
            if st.button(
                f"{label} · Day {day_num}",
                key=f"path_open_day_{day_num}",
                use_container_width=True,
                type="primary" if day_num == journey_day and status == "pending" else "secondary",
            ):
                request_main_tab(TAB_TODAY, day_num)

        prev_status = status

    st.markdown("</div>", unsafe_allow_html=True)


def render_achievements_wall(stats: dict):
    st.markdown('<div class="dl-section-head">🏆 Trophy case</div>', unsafe_allow_html=True)
    cards = ['<div class="dl-rewards-row">']
    for badge_id, name, desc, check in BADGES:
        unlocked = check(stats["badge_state"])
        cls = "unlocked" if unlocked else "locked"
        icon = BADGE_ICONS.get(badge_id, "🏅" if unlocked else "🔒")
        cards.append(
            f'<div class="dl-reward-card {cls}">'
            f'<div class="dl-reward-icon">{icon}</div>'
            f'<div class="dl-reward-name">{name}</div>'
            f'<div class="dl-reward-desc">{desc}</div>'
            f'</div>'
        )
    cards.append("</div>")
    st.markdown("".join(cards), unsafe_allow_html=True)


def render_path_loot_summary(stats: dict, partner_summary: dict):
    bsum = stats.get("bonus_summary", {})
    st.markdown('<div class="dl-section-head">💎 Loot & stats</div>', unsafe_allow_html=True)
    loot_items = [
        ("⚡", f"{stats.get('grand_total', 0)} total XP"),
        ("✅", f"{stats['earned_count']}/{stats['total_count']} quests"),
        ("📅", f"{stats.get('days_complete', 0)}/{TOTAL_DAYS} days"),
        ("👥", f"{partner_summary.get('unique_partners', 0)} partners"),
        ("🥤", f"{bsum.get('coke_count', 0)} cokes"),
        ("💫", f"{bsum.get('overflow_extra', 0)} over-goal"),
        ("🔟", f"{bsum.get('streak_count', 0)} hot streaks"),
        ("🔥", f"{stats.get('max_streak', 0)} day streak"),
    ]
    chips = "".join(
        f'<span class="dl-loot-item">{icon} {label}</span>' for icon, label in loot_items
    )
    st.markdown(f'<div class="dl-loot-bar">{chips}</div>', unsafe_allow_html=True)


TAB_TODAY = "⚡ Today"
TAB_STATS = "📊 Stats"
TAB_JOURNEY = "🗺️ Journey"
TAB_MORE = "⋯ More"
TAB_PHOTOS = "📸 Photos"
MAIN_TABS = [TAB_TODAY, TAB_STATS, TAB_JOURNEY, TAB_MORE, TAB_PHOTOS]

_LEGACY_TAB_ALIASES = {
    "📅 Calendar": TAB_TODAY,
    "✚ Log": TAB_TODAY,
    "🗺️ Path": TAB_JOURNEY,
    "📋 Quests": TAB_TODAY,
    "👥 Partners": TAB_MORE,
    "🔄 Swap": TAB_MORE,
    "⚙️ Settings": TAB_MORE,
    "📸 Memories": TAB_PHOTOS,
}


def apply_pending_navigation(tab_labels: list[str]):
    """Apply tab/day jumps before navigation widgets are drawn."""
    tab_aliases = dict(_LEGACY_TAB_ALIASES)
    pending_tab = st.session_state.pop("_pending_main_tab", None)
    if pending_tab in tab_aliases:
        pending_tab = tab_aliases[pending_tab]
    if pending_tab in tab_labels:
        st.session_state.main_tab_radio = pending_tab
    pending_day = st.session_state.pop("_pending_quests_day", None)
    if pending_day is not None:
        day = int(pending_day)
        st.session_state.quests_day_pick = day
        _set_calendar_day(day, current_journey_day(load_settings()))


def request_main_tab(tab_label: str, quests_day: int | None = None):
    st.session_state["_pending_main_tab"] = tab_label
    if quests_day is not None:
        st.session_state["_pending_quests_day"] = int(quests_day)
    st.rerun()


def level_for_pct(pct: float) -> tuple[str, str, float]:
    title, desc = LEVELS[0][1], LEVELS[0][2]
    nxt = 100.0
    for threshold, name, blurb in LEVELS:
        if pct >= threshold:
            title, desc = name, blurb
    for threshold, name, _ in LEVELS:
        if threshold > pct:
            nxt = float(threshold)
            break
    return title, desc, nxt


def loc_chip(location: str, row=None) -> str:
    meta = activity_meta(row) if row is not None else LOCATIONS.get(location, {"label": location, "icon": "📍", "color": "#1CB0F6"})
    if row is None:
        meta = LOCATIONS.get(location, meta)
    icon = location_meta_icon_html(meta, 26)
    return (
        f"<span class='cj-loc-chip' style='background:{meta['color']}18;color:{meta['color']};"
        f"border:2px solid {meta['color']}88'>{icon} {meta['label']}</span>"
    )


def render_header(
    settings: dict,
    stats: dict,
    journey_day: int,
    partner_summary: dict,
    *,
    compact: bool = False,
    nice: bool = False,
):
    if nice:
        render_nice_app_bar(settings, journey_day, stats, partner_summary)
        if stats["collar_earned"]:
            st.markdown(
                """
<div class="cj-collar-win cj-pop" style="padding:0.65rem 1rem;margin-bottom:0.75rem;">
  <div style="font-family:Fredoka,sans-serif;font-size:1.35rem;font-weight:700;color:#ffc800;">
    🔗 COLLAR EARNED — Legendary run!
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
        return
    if compact:
        render_compact_hud(stats, journey_day, partner_summary)
        if stats["collar_earned"]:
            st.markdown(
                """
<div class="cj-collar-win cj-pop" style="padding:0.65rem 1rem;margin-bottom:0.75rem;">
  <div style="font-family:Fredoka,sans-serif;font-size:1.35rem;font-weight:700;color:#ffc800;">
    🔗 COLLAR EARNED — Legendary run!
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
        return

    level, level_desc, next_level = level_for_pct(stats["pct"])
    ring = brand_ring_class(stats["pct"], stats["collar_earned"])
    brand = brand_portrait_html(172, ring)
    cheer = encouragement_for_pct(stats["pct"], stats["collar_earned"])
    name = settings.get("display_name", "Her journey")
    dom = settings.get("dom_name", "")

    render_game_hud(stats, journey_day, partner_summary)

    dom_line = f"<div class='dl-tagline'>Guided by <strong>{dom}</strong></div>" if dom else ""
    st.markdown(
        f"""
<div class="dl-hero cj-brand-hero">
  {brand}
  <div class="dl-bubble">
    <div class="dl-bubble-title">{APP_NAME}</div>
    <div class="dl-bubble-text">{cheer}</div>
    <div class="dl-tagline">{name} · {APP_TAGLINE}</div>
    {dom_line}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="dl-level-wrap">{level_progress_html(stats, level, level_desc)}</div>',
        unsafe_allow_html=True,
    )
    if next_level < 100:
        st.caption(f"🎯 {next_level - stats['pct']:.0f}% to next level!" if next_level > stats["pct"] else "")

    if stats["collar_earned"]:
        st.markdown(
            f"""
<div class="cj-collar-win cj-pop">
  {brand_portrait_html(220, "earned")}
  <div style="font-family:Fredoka,sans-serif;font-size:2rem;font-weight:700;color:#ffc800;">
    COLLAR EARNED!
  </div>
  <div style="color:#c8b8d0;margin-top:0.5rem;font-weight:600;">
    All 14 days complete. Legendary run. 🏆
  </div>
</div>
""",
            unsafe_allow_html=True,
        )


def journey_date(settings: dict, day_num: int) -> date:
    start_iso = settings.get("journey_start", date.today().isoformat())[:10]
    try:
        start = date.fromisoformat(start_iso)
    except ValueError:
        start = date.today()
    return start + timedelta(days=day_num - 1)


def day_calendar_summary(
    df: pd.DataFrame,
    encounters: pd.DataFrame,
    day_num: int,
    bonus_df: pd.DataFrame | None = None,
    used_cal_images: set[str] | None = None,
) -> dict:
    bonus_df = bonus_df if bonus_df is not None else load_bonus_df()
    meta = day_plan_meta(day_num)
    day_df = df[df["day_num"] == day_num]
    earned = day_df[day_df["status"] == "earned"]
    pending = day_df[day_df["status"] == "pending"]

    earned_pts = day_activity_score(df, day_num)
    extra_pts = day_bonus_points(bonus_df, day_num)
    goal_pts = day_goal_points(df, day_num)
    overflow_pts = day_overflow_points(df, day_num)
    total_pts = goal_pts + extra_pts
    day_bonuses = bonus_df[bonus_df["day_num"] == day_num] if not bonus_df.empty else pd.DataFrame()
    target = float(meta.get("target", 0))
    bonus = meta.get("bonus_target")
    act_total = len(day_df)
    act_done = len(earned)
    pct = round(100 * act_done / act_total) if act_total else 0
    goal_status = day_goal_status(df, day_num)
    complete = goal_status in ("met", "exceeded")
    bonus_hit = bool(bonus and earned_pts >= bonus)

    day_enc = encounters[encounters["day_num"] == day_num] if not encounters.empty else pd.DataFrame()
    partners = int(day_enc["partner_id"].nunique()) if not day_enc.empty else 0
    interactions = len(day_enc)

    achievements: list[dict] = []
    theme = meta.get("title", f"Day {day_num}")
    achievements.append(
        {
            "label": theme,
            "done": complete,
            "icon": "⭐" if goal_status == "exceeded" else ("🏆" if goal_status == "met" else "🎯"),
        }
    )

    special = {
        4: ("Dunes Challenge", "🏜️"),
        6: ("Club Bonus I", "⛓️"),
        9: ("Open Door", "🚪"),
        10: ("Dunes Double", "🏜️"),
        11: ("Party Day", "🎉"),
        12: ("Club Bonus II", "⛓️"),
        13: ("Social Chain", "🔗"),
        14: ("Final Collar Test", "👑"),
    }
    if day_num in special:
        label, icon = special[day_num]
        achievements.append({"label": label, "done": complete, "icon": icon})

    if bonus_hit:
        achievements.append({"label": f"Bonus {bonus}+ pts", "done": True, "icon": "⭐"})

    if not day_bonuses.empty:
        for _, brow in day_bonuses.iterrows():
            icon = bonus_icon(brow["bonus_type"])
            achievements.append(
                {"label": brow["label"], "done": True, "icon": icon, "bonus": True}
            )

    location_hits = []
    for _, row in earned.iterrows():
        loc = LOCATIONS.get(row["location"], {})
        location_hits.append(location_meta_icon_html(loc, 18))

    sort_df = day_df
    if "time_slot" in day_df.columns:
        sort_df = day_df.sort_values(["time_slot", "id"], kind="stable")
    activity_chips = []
    for _, row in sort_df.iterrows():
        loc = LOCATIONS.get(row["location"], {})
        activity_chips.append(
            {
                "title": row["title"],
                "done": row["status"] == "earned",
                "icon": str(loc.get("icon", "📍")),
                "icon_html": location_meta_icon_html(loc, 20),
                "points": format_points(
                    activity_effective_points(row)
                    if row["location"] in HALF_POINT_LOCATIONS
                    else int(row["points"])
                ),
            }
        )

    return {
        "day_num": day_num,
        "title": theme,
        "target": target,
        "bonus_target": bonus,
        "earned_pts": earned_pts,
        "goal_pts": goal_pts,
        "overflow_pts": overflow_pts,
        "extra_pts": extra_pts,
        "total_pts": total_pts,
        "day_bonuses": day_bonuses,
        "pct": pct,
        "goal_status": goal_status,
        "complete": complete,
        "bonus_hit": bonus_hit,
        "act_done": act_done,
        "act_total": act_total,
        "partners": partners,
        "interactions": interactions,
        "achievements": achievements,
        "location_hits": location_hits,
        "activity_chips": activity_chips,
        "pending_count": len(pending),
        "signature_loc": day_signature_location(df, day_num),
        "signature_image": calendar_cell_image(
            df, day_num, used_cal_images if used_cal_images is not None else set()
        ),
        "activity_icons": [
            str(LOCATIONS.get(str(row["location"]), {}).get("icon", "✓"))
            for _, row in earned.iterrows()
        ],
        "pending_icons": [
            str(LOCATIONS.get(str(row["location"]), {}).get("icon", "○"))
            for _, row in pending.head(4).iterrows()
        ],
    }


def _calendar_day_label(settings: dict, day_num: int) -> str:
    return (
        f"Day {day_num} — {day_plan_meta(day_num)['title']} · "
        f"{journey_date(settings, day_num).strftime('%a %b %d')}"
    )


def _ensure_calendar_pick(journey_day: int) -> int:
    if not st.session_state.get("cal_day_custom"):
        st.session_state.cal_day_pick = journey_day
        return journey_day
    pick = int(st.session_state.get("cal_day_pick", journey_day))
    return max(1, min(TOTAL_DAYS, pick))


def _set_calendar_day(day_num: int, journey_day: int) -> None:
    st.session_state.cal_day_pick = day_num
    st.session_state.cal_day_custom = day_num != journey_day


def render_nice_app_bar(
    settings: dict,
    journey_day: int,
    stats: dict | None = None,
    partner_summary: dict | None = None,
):
    """Compact but visually rich header — brand + journey chips."""
    name = settings.get("display_name", "Her journey")
    ring = "start"
    if stats:
        ring = brand_ring_class(stats.get("pct", 0), stats.get("collar_earned", False))
    portrait = brand_portrait_html(72, ring)
    chips = ""
    level_html = ""
    if stats and partner_summary:
        total_fmt = format_points(float(stats.get("grand_total", 0)))
        streak = stats.get("max_streak", 0)
        partners = partner_summary.get("unique_partners", 0)
        chips = (
            f'<div class="cj-rich-bar-chips">'
            f'<span class="cj-rich-chip xp">⚡ {total_fmt} XP</span>'
            f'<span class="cj-rich-chip hot">🔥 {streak} streak</span>'
            f'<span class="cj-rich-chip">👥 {partners}</span>'
            f'<span class="cj-rich-chip">📅 Day {journey_day}/{TOTAL_DAYS}</span>'
            f"</div>"
        )
        level, level_desc, _ = level_for_pct(stats.get("pct", 0))
        level_html = (
            f'<div class="cj-rich-bar-level">'
            f"{level_progress_html(stats, level, level_desc, compact=True)}"
            f"</div>"
        )
    st.markdown(
        f"""
<div class="cj-rich-bar">
  {portrait}
  <div class="cj-rich-bar-center">
    <div class="cj-rich-bar-title">{APP_NAME}</div>
    <div class="cj-rich-bar-sub">{name} · {APP_TAGLINE}</div>
    {chips}
    {level_html}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _rich_cal_qicon_html(chip: dict) -> str:
    done = chip.get("done", False)
    cls = "done" if done else "pending"
    icon = chip.get("icon", "📍")
    title = str(chip.get("title", "")).replace('"', "&quot;")
    return f'<span class="cj-rich-cal-qicon {cls}" title="{title}">{icon}</span>'


def rich_cal_quest_track_html(summary: dict) -> str:
    """Compact quest progress — pending left, completed clustered upper-right."""
    chips = summary.get("activity_chips", [])
    act_total = summary.get("act_total", 0)
    act_done = summary.get("act_done", 0)
    if not chips or not act_total:
        pct = min(int(summary.get("pct", 0)), 100)
        return f'<div class="cj-rich-cal-prog"><div style="width:{pct}%;"></div></div>'
    fill_pct = min(100, round(100 * act_done / act_total))
    pending = [_rich_cal_qicon_html(c) for c in chips if not c.get("done")]
    done = [_rich_cal_qicon_html(c) for c in chips if c.get("done")]
    pending_html = "".join(pending) if pending else ""
    done_html = "".join(done) if done else ""
    icons_row = (
        f'<div class="cj-rich-cal-track-icons split">'
        f'<div class="cj-rich-cal-track-pending">{pending_html}</div>'
        f'<div class="cj-rich-cal-track-done">{done_html}</div>'
        f"</div>"
    )
    return (
        f'<div class="cj-rich-cal-track">'
        f'<div class="cj-rich-cal-track-rail">'
        f'<div class="cj-rich-cal-track-fill" style="width:{fill_pct}%;"></div>'
        f"</div>"
        f"{icons_row}"
        f"</div>"
    )


def rich_cal_done_badge_html(act_done: int, act_total: int) -> str:
    badge_cls = "cj-rich-cal-done-badge"
    if act_total and act_done >= act_total:
        badge_cls += " complete"
    elif not act_done:
        badge_cls += " zero"
    mark = "✅ " if act_done else ""
    return (
        f'<div class="{badge_cls}">'
        f'<div class="cj-rich-cal-done-main">{mark}{act_done}/{act_total}</div>'
        f'<div class="cj-rich-cal-done-sub">done</div>'
        f"</div>"
    )


def rich_cal_day_card_html(
    summary: dict,
    cal_date: date,
    day_num: int,
    journey_day: int,
    view_day: int,
    hero: bool = False,
    *,
    day_title: str = "",
    is_today: bool = False,
    venue_hint: str = "",
) -> str:
    gs = summary.get("goal_status", "pending")
    css = ["cj-rich-cal-day"]
    if hero:
        css.append("hero")
    if gs == "exceeded":
        css.append("exceeded")
    elif gs == "met":
        css.append("met")
    if day_num == view_day:
        css.append("selected")
    if day_num == journey_day:
        css.append("today")
    sig_img = summary.get("signature_image")
    bg_html = '<div class="cj-rich-cal-bg"></div>'
    uri = None
    if sig_img:
        uri = _venue_image_uri(str(sig_img))
    elif summary.get("signature_loc"):
        uri = location_image_uri(str(summary["signature_loc"]))
    if uri:
        bg_html = f'<div class="cj-rich-cal-bg"><img src="{uri}" alt="" /></div>'
    icons = " ".join(summary.get("activity_icons", [])[:5])
    pending = " ".join(summary.get("pending_icons", [])[:2])
    icon_line = icons or pending or "·"
    pct = min(int(summary.get("pct", 0)), 100)
    hero_header = ""
    progress_html = (
        f'<div class="cj-rich-cal-icons">{icon_line}</div>'
        f'<div class="cj-rich-cal-prog"><div style="width:{pct}%;"></div></div>'
    )
    if hero and day_title:
        today_mark = "⚡ Today · " if is_today else ""
        act_done = summary.get("act_done", 0)
        act_total = summary.get("act_total", 0)
        earned_pts = summary.get("earned_pts", 0)
        target = summary.get("target", 0)
        goal_pts = summary.get("goal_pts", earned_pts)
        left_pts = max(0.0, float(target) - float(goal_pts))
        venue_bit = f" · 📍 {venue_hint}" if venue_hint else ""
        if gs == "exceeded":
            status_txt = "⭐ Goal exceeded"
        elif gs == "met":
            status_txt = "✅ Goal achieved"
        elif act_done >= act_total and act_total:
            status_txt = f"All logged · {format_points(left_pts)} XP short"
        elif act_done:
            status_txt = f"{act_total - act_done} left"
        else:
            status_txt = f"{act_total} quests"
        hero_header = (
            f'<div class="cj-rich-cal-kicker">{today_mark}Day {day_num} — {day_title}</div>'
            f'<div class="cj-rich-cal-meta">{cal_date.strftime("%a, %b %d")}{venue_bit} · '
            f'{format_points(goal_pts)}/{format_points(target)} XP · {status_txt}</div>'
        )
        progress_html = rich_cal_quest_track_html(summary)
    done_badge = ""
    if hero and day_title and summary.get("act_total"):
        done_badge = rich_cal_done_badge_html(
            int(summary.get("act_done", 0)),
            int(summary.get("act_total", 0)),
        )
    inner_parts = []
    if hero_header:
        inner_parts.append(hero_header)
    else:
        inner_parts.append(f'<div class="cj-rich-cal-num">{cal_date.day}</div>')
        inner_parts.append(f'<div class="cj-rich-cal-daylabel">Day {day_num}</div>')
    inner_parts.append(progress_html)
    inner_html = "".join(inner_parts)
    return f"""
<div class="{' '.join(css)}">
  {bg_html}
  <div class="cj-rich-cal-scrim"></div>
  {done_badge}
  <div class="cj-rich-cal-inner">{inner_html}</div>
</div>
"""


def render_nice_day_entries(df: pd.DataFrame, day_num: int, encounters: pd.DataFrame) -> None:
    """Activity log rows with venue photo thumbnails."""
    day_df = df[df["day_num"] == day_num].copy()
    if day_df.empty:
        return
    if "time_slot" in day_df.columns:
        day_df = day_df.sort_values(["time_slot", "id"], kind="stable")
    day_enc = encounters[encounters["day_num"] == day_num] if not encounters.empty else pd.DataFrame()
    rows: list[str] = []
    for _, row in day_df.iterrows():
        loc = str(row["location"])
        meta = activity_meta(row)
        loc_meta = LOCATIONS.get(loc, {"icon": "📍", "label": loc, "color": "#8e8e93"})
        earned = row["status"] == "earned"
        cls = "nice-entry-row done" if earned else "nice-entry-row pending"
        partners_n = 0
        if not day_enc.empty:
            partners_n = int(
                day_enc[day_enc["activity_key"] == row["activity_key"]]["partner_id"].nunique()
            )
        meta_bits = [time_slot_label(str(row["time_slot"])), loc_meta.get("label", loc)]
        if partners_n:
            meta_bits.append(f"{partners_n} partner{'s' if partners_n != 1 else ''}")
        meta_line = " · ".join(meta_bits)
        xp = activity_xp_badge(row)
        mark = "✓" if earned else "○"
        img = meta.get("image")
        uri = _venue_image_uri(str(img)) if img else None
        if uri:
            thumb = f'<img class="nice-entry-photo" src="{uri}" alt="" />'
        else:
            thumb = (
                f'<div class="nice-entry-icon" style="background:{loc_meta.get("color", "#8e8e93")}22">'
                f'{loc_meta.get("icon", "📍")}</div>'
            )
        rows.append(
            f"<div class='{cls}'>"
            f"{thumb}"
            f"<div class='nice-entry-body'>"
            f"<div class='nice-entry-title'>{mark} {row['title']}</div>"
            f"<div class='nice-entry-meta'>{meta_line}</div>"
            f"</div>"
            f"<div class='nice-entry-xp'>{xp}</div>"
            f"</div>"
        )
    st.markdown(f"<div class='nice-entry-list'>{''.join(rows)}</div>", unsafe_allow_html=True)


def render_stats_view(
    df: pd.DataFrame,
    encounters: pd.DataFrame,
    bonus_df: pd.DataFrame,
    stats: dict,
    partner_summary: dict,
    settings: dict,
):
    """Nice-style insights with photo hero and colorful stat cards."""
    st.markdown("### Insights")

    earned = df[df["status"] == "earned"]
    hero_uri = None
    if not earned.empty:
        top_loc = str(earned["location"].value_counts().index[0])
        hero_uri = location_image_uri(top_loc)
    hero_layer = (
        f'<div class="cj-stats-hero-layer"><img src="{hero_uri}" alt="" /></div>'
        if hero_uri
        else '<div class="cj-stats-hero-layer"></div>'
    )
    st.markdown(
        f"""
<div class="cj-stats-hero">
  {hero_layer}
  <div class="cj-stats-hero-scrim"></div>
  <div class="cj-stats-hero-text">
    <h4>Your journey in numbers</h4>
    <div style="font-size:0.82rem;font-weight:600;opacity:0.9;">
      {stats['earned_count']} quests logged · {partner_summary.get('unique_partners', 0)} partners
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    bsum = stats.get("bonus_summary", {})
    cards = [
        ("Quests", f"{stats['earned_count']}/{stats['total_count']}", "accent-blue"),
        ("Streak", str(stats.get("max_streak", 0)), "accent-hot"),
        ("Partners", str(partner_summary.get("unique_partners", 0)), ""),
        ("Total XP", format_points(float(stats.get("grand_total", 0))), "accent-xp"),
        ("Days done", f"{stats.get('days_complete', 0)}/{TOTAL_DAYS}", "accent-blue"),
        ("Interactions", str(partner_summary.get("total_encounters", 0)), ""),
    ]
    st.markdown(
        "<div class='nice-stat-grid'>"
        + "".join(
            f"<div class='nice-stat-card {accent}'><div class='nice-stat-value'>{val}</div>"
            f"<div class='nice-stat-label'>{label}</div></div>"
            for label, val, accent in cards
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Weekly progress")
    week_rows = []
    for w, days in enumerate([range(1, 8), range(8, 15)], start=1):
        done = sum(
            1 for d in days if day_goal_status(df, d) in ("met", "exceeded")
        )
        pts = sum(day_activity_score(df, d) + day_bonus_points(bonus_df, d) for d in days)
        week_rows.append(f"Week {w}: **{done}/7** days complete · **{format_points(pts)}** XP")
    st.markdown("\n".join(f"- {r}" for r in week_rows))

    st.markdown("#### Top locations")
    earned = df[df["status"] == "earned"]
    if earned.empty:
        st.caption("Complete quests to see location trends.")
    else:
        loc_counts = earned["location"].value_counts()
        chips = []
        for loc, count in loc_counts.head(8).items():
            meta = LOCATIONS.get(str(loc), {"icon": "📍", "label": str(loc)})
            img = meta.get("image")
            uri = _venue_image_uri(str(img)) if img else None
            img_html = f'<img src="{uri}" alt="" />' if uri else ""
            chips.append(
                f"<span class='nice-loc-chip'>{img_html}"
                f"{meta.get('icon', '📍')} {meta.get('label', loc)} · {count}</span>"
            )
        st.markdown(f"<div class='nice-loc-bar'>{''.join(chips)}</div>", unsafe_allow_html=True)

    st.markdown("#### Bonus loot")
    loot = [
        f"🥤 {bsum.get('coke_count', 0)} cokes",
        f"💫 {bsum.get('overflow_extra', 0)} over-goal",
        f"🔟 {bsum.get('streak_count', 0)} hot streaks",
    ]
    st.markdown(" · ".join(loot))


def render_calendar_cell(
    summary: dict,
    cal_date: date,
    is_today: bool,
    is_future: bool,
    is_selected: bool = False,
) -> str:
    goal_status = summary.get("goal_status", "pending")
    css = ["cj-cal-cell"]
    if goal_status == "exceeded":
        css.append("exceeded")
    elif goal_status == "met":
        css.append("met")
    if is_selected:
        css.append("selected")
    if is_today:
        css.append("today")
    if is_future and goal_status == "pending":
        css.append("future")

    if goal_status == "exceeded":
        trophy = "⭐"
    elif goal_status == "met":
        trophy = "🏆"
    elif is_today:
        trophy = "📍"
    else:
        trophy = ""
    if goal_status in ("met", "exceeded"):
        fill_cls = f"cj-cal-progress-fill {goal_status}"
    else:
        fill_cls = "cj-cal-progress-fill"
    progress_w = min(summary["pct"], 100)

    ach_html = ""
    for ach in summary["achievements"]:
        cls = "cj-cal-ach done"
        if ach.get("bonus"):
            cls += " bonus"
        elif not ach["done"]:
            cls = "cj-cal-ach pending"
        ach_html += f"<span class='{cls}'>{ach['icon']} {ach['label']}</span>"

    locs = "".join(summary["location_hits"][:8])
    if len(summary["location_hits"]) > 8:
        locs += "…"

    pts_line = f"{summary['goal_pts']}/{summary['target']} pts"
    if summary.get("overflow_pts"):
        pts_line += f" · 💫 +{summary['overflow_pts']} bonus"
    elif summary.get("extra_pts") and not summary.get("overflow_pts"):
        pts_line += f" +{summary['extra_pts']} extra"
    if summary.get("bonus_target"):
        pts_line += f" · bonus {summary['bonus_target']}+"

    photo_layers = ""
    sig_img = summary.get("signature_image")
    uri = _venue_image_uri(str(sig_img)) if sig_img else None
    if not uri and summary.get("signature_loc"):
        uri = location_image_uri(str(summary["signature_loc"]))
    if uri:
        css.append("has-photo")
        photo_layers = (
            f"<div class='cj-cal-photo-bg'><img src='{uri}' alt='' /></div>"
            f"<div class='cj-cal-photo-scrim'></div>"
        )

    return f"""
<div class='{" ".join(css)}'>
  {photo_layers}
  <div class='cj-cal-content'>
  <div class='cj-cal-trophy'>{trophy}</div>
  <div class='cj-cal-date'>{cal_date.strftime("%a %b %d")}</div>
  <div class='cj-cal-daynum'>Day {summary['day_num']}</div>
  <div class='cj-cal-title'>{summary['title']}</div>
  <div class='cj-cal-progress'><div class='{fill_cls}' style='width:{progress_w}%;'></div></div>
  <div class='cj-cal-stat'>{pts_line} · {summary['act_done']}/{summary['act_total']} acts</div>
  <div class='cj-cal-stat'>{summary['partners']} partners · {summary['interactions']} logged</div>
  <div>{ach_html}</div>
  <div class='cj-cal-locs'>{locs}</div>
  </div>
</div>
"""


def render_calendar_view(
    df: pd.DataFrame,
    encounters: pd.DataFrame,
    settings: dict,
    journey_day: int,
    bonus_df: pd.DataFrame | None = None,
    partners_df: pd.DataFrame | None = None,
):
    bonus_df = bonus_df if bonus_df is not None else load_bonus_df()
    view_day = _ensure_calendar_pick(journey_day)
    start = journey_date(settings, 1)
    end = journey_date(settings, TOTAL_DAYS)

    used_cal_images: set[str] = set()
    summaries = [
        day_calendar_summary(df, encounters, d, bonus_df, used_cal_images)
        for d in range(1, TOTAL_DAYS + 1)
    ]

    pick = view_day
    is_today = pick == journey_day
    summary = summaries[pick - 1]
    cal_date = journey_date(settings, pick)
    day_title = day_plan_meta(pick)["title"]
    plan = day_path_visual_plan(df, pick)
    venue_hint = ""
    if plan.get("banner"):
        lead = plan["banner"]
        venue_hint = str(lead.get("label") or lead.get("location") or "")
        extra = len(plan.get("all") or []) - 1
        if extra > 0:
            venue_hint = f"{venue_hint} +{extra} more"

    if not is_today:
        if st.button("← Today", key="cal_back_today", use_container_width=True):
            _set_calendar_day(journey_day, journey_day)
            st.rerun()

    st.markdown(
        rich_cal_day_card_html(
            summary,
            cal_date,
            pick,
            journey_day,
            pick,
            hero=True,
            day_title=day_title,
            is_today=is_today,
            venue_hint=venue_hint,
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        day_venue_strip_html(df, pick, max_icons=6, size=36),
        unsafe_allow_html=True,
    )

    with st.expander("📅 Pick another day", expanded=not is_today):
        other = st.selectbox(
            "Day",
            list(range(1, TOTAL_DAYS + 1)),
            index=pick - 1,
            format_func=lambda d: _calendar_day_label(settings, d),
            key="cal_day_select",
            label_visibility="collapsed",
        )
        if other != pick:
            _set_calendar_day(other, journey_day)
            st.rerun()

    if partners_df is None:
        partners_df = load_partners_df()

    st.divider()
    st.markdown("##### Complete quests")
    st.caption("📸 Quest, location & partner photos — upload and tag on the **Photos** tab.")
    render_day_detail(
        df,
        pick,
        partners_df,
        bonus_df,
        encounters,
        key_prefix="calendar",
        show_header=False,
    )


def render_day_extras(df: pd.DataFrame, bonus_df: pd.DataFrame, day_num: int, key_prefix: str = "day"):
    st.markdown("#### ✨ Bonus loot")
    day_score = day_activity_score(df, day_num)
    target = day_target_points(day_num)
    target_met = day_target_met(df, day_num)
    overflow = day_overflow_points(df, day_num)
    extra = day_bonus_points(bonus_df, day_num)

    st.caption(
        f"Daily goal: **{format_points(min(day_score, target))} / {format_points(target)}** activity pts · "
        f"Bonuses today: **+{extra}**"
        + (f" (includes **+{overflow}** converted from scoring above {target})" if overflow else "")
        + (
            f" · 🔒 Bonus loot unlocks once you hit **{target}** pts "
            f"(currently **{format_points(day_score)}**)."
            if not target_met
            else " · ✅ Daily goal reached — bonus loot unlocked."
        )
    )

    day_bonus = bonus_df[bonus_df["day_num"] == day_num] if not bonus_df.empty else pd.DataFrame()
    if not day_bonus.empty:
        chips = "".join(
            f"<span class='cj-extra-chip'>{bonus_icon(row['bonus_type'])} {row['label']} +{row['points']}</span>"
            for _, row in day_bonus.iterrows()
        )
        st.markdown(chips, unsafe_allow_html=True)

    if not target_met:
        st.info(
            f"Reach **{target}** activity pts today before coke, streak, or over-goal bonuses apply. "
            f"Points above **{target}** convert to bonus automatically once the goal is hit."
        )
        return

    has_bay = not df[(df["day_num"] == day_num) & (df["location"] == "bay_of_pigs")].empty
    has_coke = (
        not day_bonus.empty
        and not day_bonus[day_bonus["bonus_type"] == BONUS_COKE_TYPE].empty
    )

    if has_bay:
        if not has_coke:
            if st.button(
                f"🥤 Earned a Coke at Bay of Pigs (+{BONUS_COKE_POINTS} pts)",
                key=f"{key_prefix}_coke_{day_num}",
            ):
                if celebrate_bonus_action(lambda: add_coke_bonus(day_num)):
                    st.rerun()
                else:
                    st.warning(f"Could not add coke bonus (need {target} activity pts today first).")
        else:
            st.success(f"🥤 Coke at Bay of Pigs earned (+{BONUS_COKE_POINTS} pts)")
            if st.button("Remove coke bonus", key=f"{key_prefix}_rmcoke_{day_num}"):
                remove_coke_bonus(day_num)
                st.rerun()
    else:
        st.caption("🥤 Coke bonus available on Bay of Pigs days (Days 1, 2, 12, 14).")

    st.markdown("##### 🔟 10 in a row — one session")
    st.caption(
        f"**+{BONUS_STREAK_POINTS} extra pts** when she hits **{BONUS_STREAK_COUNT} interactions in a row** "
        "at the same location in a single session (sauna, Bay of Pigs, **club / playroom**, party, etc.). "
        "Once per location per day. Auto-awards when you log 10+ partners completing an activity."
    )

    streak_locs = day_streak_locations(df, day_num)

    for loc in streak_locs:
        loc_meta = LOCATIONS.get(loc, {})
        icon = location_meta_icon_html(loc_meta, 20)
        label = location_person_label(loc)
        claimed = has_streak_bonus(bonus_df, day_num, loc)
        col_a, col_b = st.columns([3, 1])
        with col_a:
            if claimed:
                st.markdown(
                    f"{icon} **{label}** — 10-in-a-row earned (+{BONUS_STREAK_POINTS})",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"{icon} **{label}** — not yet claimed today", unsafe_allow_html=True)
        with col_b:
            if claimed:
                if st.button("Remove", key=f"{key_prefix}_rmstreak_{day_num}_{loc}"):
                    remove_streak_bonus(day_num, loc)
                    st.rerun()
            else:
                if st.button(f"+{BONUS_STREAK_POINTS} pts", key=f"{key_prefix}_streak_{day_num}_{loc}"):
                    if celebrate_bonus_action(lambda: add_streak_bonus(day_num, loc)):
                        st.rerun()
                    else:
                        st.warning("Could not add streak bonus (once per location per day).")


def render_dashboard(
    df: pd.DataFrame,
    stats: dict,
    journey_day: int,
    partner_summary: dict,
    bonus_df: pd.DataFrame | None = None,
    partners_df: pd.DataFrame | None = None,
    settings: dict | None = None,
):
    bonus_df = bonus_df if bonus_df is not None else load_bonus_df()
    partners_df = partners_df if partners_df is not None else load_partners_df()
    settings = settings if settings is not None else load_settings()
    render_path_hero(df, stats, journey_day)
    render_journey_path(df, journey_day, bonus_df)
    render_achievements_wall(stats)
    render_path_loot_summary(stats, partner_summary)


def quest_pick_label(day_df: pd.DataFrame, activity_key: str) -> str:
    row = day_df[day_df["activity_key"] == activity_key].iloc[0]
    mark = "✅" if row["status"] == "earned" else "🎯"
    slot = time_slot_label(str(row["time_slot"]))
    return f"{mark} {row['title']} · {slot} · {activity_xp_badge(row)}"


def day_pending_point_total(day_df: pd.DataFrame) -> float:
    pending = day_df[day_df["status"] == "pending"]
    return sum(activity_effective_points(row) for _, row in pending.iterrows())


def sync_open_quest_state(key_prefix: str, day_num: int, quest_keys: list[str]) -> None:
    """Drop stale open-quest state when the day's quest list changes."""
    open_key = f"{key_prefix}_open_quest_{day_num}"
    if not quest_keys:
        st.session_state.pop(open_key, None)
        return
    if st.session_state.get(open_key) not in quest_keys:
        st.session_state.pop(open_key, None)
    # Legacy picker keys from older UI
    st.session_state.pop(f"{key_prefix}_active_quest_{day_num}", None)
    st.session_state.pop(f"{key_prefix}_quest_dropdown_{day_num}", None)


def reset_quest_picker_after_complete(activity_key: str) -> None:
    df = load_activities_df()
    match = df[df["activity_key"] == activity_key]
    if match.empty:
        return
    day_num = int(match.iloc[0]["day_num"])
    for prefix in ("calendar", "day"):
        open_key = f"{prefix}_open_quest_{day_num}"
        if st.session_state.get(open_key) == activity_key:
            st.session_state.pop(open_key, None)
        st.session_state.pop(f"{prefix}_active_quest_{day_num}", None)
        st.session_state.pop(f"{prefix}_quest_dropdown_{day_num}", None)


def scroll_open_quest_panel_into_view() -> None:
    components.html(
        """
<script>
(function() {
  const doc = window.parent.document;
  function scroll() {
    const el = doc.getElementById("cj-open-quest-panel");
    if (!el) return;
    const top = el.getBoundingClientRect().top + doc.documentElement.scrollTop - 72;
    doc.documentElement.scrollTop = Math.max(0, top);
    if (doc.defaultView) doc.defaultView.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
  }
  setTimeout(scroll, 80);
  setTimeout(scroll, 350);
})();
</script>
""",
        height=0,
    )


def _sorted_quest_keys(day_df: pd.DataFrame) -> list[str]:
    ordered = day_df
    if "time_slot" in day_df.columns:
        ordered = day_df.sort_values(["time_slot", "id"], kind="stable")
    return ordered["activity_key"].astype(str).tolist()


def _render_inline_quest_panel(
    row,
    df: pd.DataFrame,
    day_num: int,
    key_prefix: str,
    partners_df: pd.DataFrame,
    encounters_df: pd.DataFrame,
    sub_pool: pd.DataFrame,
) -> None:
    """Expand quest inputs directly under the tapped tile."""
    is_earned = row["status"] == "earned"
    mark_cls = "cj-quest-tile-expand-mark done" if is_earned else "cj-quest-tile-expand-mark"
    lead = "✅" if is_earned else "🎯"
    st.markdown(
        f'<div id="cj-open-quest-panel" class="{mark_cls}">{lead} {row["title"]}</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.caption(str(row["description"]))
        if is_earned:
            _render_quest_done_panel(row, day_num, key_prefix, partners_df)
        else:
            maybe_render_quest_quick_complete(
                row, day_num, key_prefix, partners_df, encounters_df
            )
            _render_quest_log_panel(
                row, df, day_num, key_prefix, partners_df, encounters_df, sub_pool
            )


def render_day_quest_nav(
    day_df: pd.DataFrame,
    day_num: int,
    key_prefix: str,
    target: float,
    earned_pts: float,
    df: pd.DataFrame | None = None,
    partners_df: pd.DataFrame | None = None,
    encounters_df: pd.DataFrame | None = None,
    sub_pool: pd.DataFrame | None = None,
) -> None:
    """Stacked tiles — expand panel opens directly under the tapped quest."""
    open_key = f"{key_prefix}_open_quest_{day_num}"
    quest_keys = _sorted_quest_keys(day_df)
    sync_open_quest_state(key_prefix, day_num, quest_keys)

    if not quest_keys:
        return

    st.markdown(
        '<div class="cj-quest-section-label">🎯 Tap a tile to complete or edit</div>',
        unsafe_allow_html=True,
    )
    open_quest = st.session_state.get(open_key)

    for key in quest_keys:
        row = day_df[day_df["activity_key"] == key].iloc[0]
        is_open = open_quest == key
        st.markdown(quest_day_tile_html(row, is_open), unsafe_allow_html=True)
        if st.button(
            quest_day_tile_button_label(row, is_open),
            key=f"{key_prefix}_tile_{day_num}_{key}",
            use_container_width=True,
            type="primary" if is_open else "secondary",
        ):
            if is_open:
                st.session_state.pop(open_key, None)
            else:
                st.session_state[open_key] = key
            st.rerun()

        if is_open:
            if (
                df is not None
                and partners_df is not None
                and encounters_df is not None
                and sub_pool is not None
            ):
                _render_inline_quest_panel(
                    row,
                    df,
                    day_num,
                    key_prefix,
                    partners_df,
                    encounters_df,
                    sub_pool,
                )
                scroll_open_quest_panel_into_view()
            else:
                st.warning("That quest is no longer available — pick another tile.")


def _render_quest_log_panel(
    row,
    df: pd.DataFrame,
    day_num: int,
    key_prefix: str,
    partners_df: pd.DataFrame,
    encounters_df: pd.DataFrame,
    sub_pool: pd.DataFrame,
) -> None:
    mode = st.radio(
        "How to complete",
        ["Complete as planned", "Substitute another activity"],
        key=f"{key_prefix}_mode_{row['activity_key']}",
        horizontal=True,
    )

    if mode == "Complete as planned":
        if is_solo_half_point(row):
            notes = st.text_area(
                "Notes (optional)",
                key=f"{key_prefix}_notes_{row['activity_key']}",
            )
            label = SOLO_COMPLETE_LABELS.get(str(row["location"]), "Complete (+½ XP)")
            if st.button(f"✅ {label}", key=f"{key_prefix}_solo_{row['activity_key']}", type="primary", use_container_width=True):
                complete_quest(row["activity_key"], notes, 1)
                st.rerun()
        elif is_bring_back_half(row):
            render_history_presets(df, encounters_df, row, day_num, key_prefix, partners_df)
            act_key = str(row["activity_key"])
            notes_key = f"{key_prefix}_notes_{act_key}"
            log_prefix = quest_log_prefix(key_prefix, act_key)
            armed = quest_is_preloaded(key_prefix, act_key)
            if armed:
                with st.expander("Review partner details (optional)", expanded=False):
                    notes = st.text_area("Notes (optional)", key=notes_key)
                    encounter_rows = render_partner_logging_form(
                        act_key, row["location"], day_num, 1, log_prefix, partners_df
                    )
            else:
                notes = st.text_area("Notes (optional)", key=notes_key)
                encounter_rows = render_partner_logging_form(
                    act_key, row["location"], day_num, 1, log_prefix, partners_df
                )
            st.caption("Log who you brought back — half point toward today's goal.")
            if encounter_rows_ready(encounter_rows):
                if st.button(
                    complete_quest_button_label(row, 1),
                    key=f"{key_prefix}_complete_{act_key}",
                    type="primary",
                    use_container_width=True,
                ):
                    if try_auto_complete_direct(
                        act_key, row["location"], day_num, encounter_rows, partners_df, notes, 1
                    ):
                        clear_quest_armed(key_prefix, act_key)
                        st.rerun()
            elif not armed:
                st.info("Fill in partner name(s) above, then hit **Complete quest**.")
        else:
            render_history_presets(df, encounters_df, row, day_num, key_prefix, partners_df)
            act_key = str(row["activity_key"])
            notes_key = f"{key_prefix}_notes_{act_key}"
            pts_key = f"{key_prefix}_pts_{act_key}"
            log_prefix = quest_log_prefix(key_prefix, act_key)
            planned = int(row["points"])
            before_noon_village = is_before_noon_village(row)
            if pts_key not in st.session_state:
                suggested = suggested_points_for_location(
                    encounters_df, row["location"], day_num, planned
                )
            else:
                suggested = int(st.session_state[pts_key])
            if before_noon_village:
                suggested = min(suggested, 1)
            armed = quest_is_preloaded(key_prefix, act_key)
            preset_pts = int(st.session_state.get(pts_key, suggested))
            if armed:
                with st.expander("Adjust points & partners (optional)", expanded=False):
                    notes = st.text_area("Notes (optional)", key=notes_key)
                    extra = st.number_input(
                        "Points earned (default = planned or typical for this location)",
                        min_value=0,
                        max_value=1 if before_noon_village else 30,
                        value=suggested,
                        key=pts_key,
                        help=(
                            "One village encounter before noon."
                            if before_noon_village
                            else "Adapts from your history at this location (club, mousse party, etc.)."
                        ),
                    )
                    log_count = quest_partner_log_count(row, key_prefix, int(extra))
                    encounter_rows = render_partner_logging_form(
                        act_key, row["location"], day_num, log_count, log_prefix, partners_df
                    )
            else:
                notes = st.text_area("Notes (optional)", key=notes_key)
                extra = st.number_input(
                    "Points earned (default = planned or typical for this location)",
                    min_value=0,
                    max_value=1 if before_noon_village else 30,
                    value=suggested,
                    key=pts_key,
                    help=(
                        "One village encounter before noon."
                        if before_noon_village
                        else "Adapts from your history at this location (club, mousse party, etc.)."
                    ),
                )
                log_count = quest_partner_log_count(row, key_prefix, int(extra))
                encounter_rows = render_partner_logging_form(
                    act_key, row["location"], day_num, log_count, log_prefix, partners_df
                )
            if encounter_rows_ready(encounter_rows):
                pts = int(st.session_state.get(pts_key, preset_pts if armed else suggested))
                if st.button(
                    complete_quest_button_label(row, pts),
                    key=f"{key_prefix}_complete_{act_key}",
                    type="primary",
                    use_container_width=True,
                ):
                    if try_auto_complete_direct(
                        act_key,
                        row["location"],
                        day_num,
                        encounter_rows,
                        partners_df,
                        notes,
                        pts,
                    ):
                        clear_quest_armed(key_prefix, act_key)
                        st.rerun()
            elif not armed:
                st.info("Fill in partner name(s) above, then hit **Complete quest**.")
    else:
        st.caption(
            "Do a different activity from the plan to fill this slot. "
            "That activity's own slot stays open — the plan recalibrates."
        )
        pool = substitution_pool(df, exclude_key=row["activity_key"])
        options = pool["activity_key"].tolist()
        if not options:
            st.info("No pending activities left to substitute.")
            return
        subpick_key = f"{key_prefix}_subpick_{row['activity_key']}"
        if st.session_state.get(subpick_key) not in options:
            st.session_state.pop(subpick_key, None)
        choice = st.selectbox(
            "Substitute with",
            options,
            format_func=lambda k, _df=df: (
                activity_label(activity_row(_df, k))
                if activity_row(_df, k) is not None
                else str(k)
            ),
            key=subpick_key,
        )
        sub_row = activity_row(df, choice)
        if sub_row is None:
            st.warning("That substitution target is no longer available — pick another.")
            return
        sub_notes = st.text_area("Notes", key=f"{key_prefix}_subnotes_{row['activity_key']}")
        render_history_presets(
            df,
            encounters_df,
            sub_row,
            day_num,
            f"{key_prefix}_sub",
            partners_df,
            target_activity_key=str(row["activity_key"]),
        )
        sub_log_prefix = f"{key_prefix}_sub_log_{row['activity_key']}"
        sub_pts_key = f"{key_prefix}_sub_pts_{row['activity_key']}"
        if sub_pts_key in st.session_state:
            sub_log_count = max(1, int(st.session_state[sub_pts_key]))
        else:
            sub_log_count = int(row["points"])
        sub_encounters = render_partner_logging_form(
            row["activity_key"],
            sub_row["location"],
            sub_row["day_num"],
            sub_log_count,
            sub_log_prefix,
            partners_df,
        )
        sub_arm_key = f"quest_sub_complete_{key_prefix}_{row['activity_key']}"
        if encounter_rows_ready(sub_encounters):
            if st.button(
                "✅ Complete substitution",
                key=sub_arm_key,
                type="primary",
                use_container_width=True,
            ):
                if try_auto_complete_substitute(
                    row["activity_key"],
                    choice,
                    sub_row,
                    sub_encounters,
                    partners_df,
                    sub_notes,
                ):
                    st.rerun()
        else:
            st.info("Fill in partner name(s) above, then hit **Complete substitution**.")


def _render_quest_done_panel(
    row,
    day_num: int,
    key_prefix: str,
    partners_df: pd.DataFrame,
) -> None:
    render_encounter_summary(row["activity_key"])
    enc = load_encounters_for_activity(row["activity_key"])
    if not enc.empty:
        with st.expander("Edit partner log", expanded=False):
            edit_count = len(enc)
            edit_rows = render_partner_logging_form(
                row["activity_key"],
                row["location"],
                day_num,
                edit_count,
                f"{key_prefix}_edit_{row['activity_key']}",
                partners_df,
                existing=enc,
            )
            if encounter_rows_ready(edit_rows):
                persist_encounter_rows(
                    row["activity_key"],
                    row["location"],
                    day_num,
                    edit_rows,
                    partners_df,
                )
                st.caption("💾 Partner log saved.")
    if st.button("Undo completion", key=f"{key_prefix}_undo_{row['activity_key']}"):
        undo_activity(row["activity_key"])
        st.rerun()


def _quest_card_body_html(row, is_earned: bool, fulfilled: str) -> str:
    return (
        f"<span class='dl-xp-badge'>{activity_xp_badge(row)}</span>"
        f"{loc_chip(str(row['location']), row)}"
        f"<span style='color:#777;font-size:0.78rem;font-weight:700;'>"
        f"{time_slot_label(str(row['time_slot']))}</span>"
        f"<div style='font-family:Fredoka,sans-serif;font-size:1.05rem;font-weight:600;"
        f"color:#3C3C3C;margin:0.35rem 0;'>"
        f"{'✅' if is_earned else '🎯'} {row['title']}</div>"
        f"<div style='color:#777;font-size:0.88rem;'>{row['description']}</div>"
        f"{fulfilled}"
    )


def render_quest_card(
    row,
    df: pd.DataFrame,
    *,
    focused: bool = False,
) -> None:
    is_earned = row["status"] == "earned"
    fulfilled = ""
    if is_earned and is_substitution_fill(row):
        sub_row = substitution_source_row(df, str(row["fulfilled_by_key"]))
        if sub_row is not None:
            fulfilled = (
                f"<div class='cj-sub-pool'>↪ Filled via substitution: {sub_row['title']}</div>"
            )
        else:
            fulfilled = (
                "<div class='cj-sub-pool'>↪ Filled via substitution "
                "(original activity no longer in plan)</div>"
            )

    quest_cls = "dl-quest done" if is_earned else "dl-quest pending"
    if focused:
        quest_cls += " focused"
    is_qakc = str(row["location"]) == "qakc"
    body = _quest_card_body_html(row, is_earned, fulfilled)

    if is_qakc:
        promo = qakc_face_hero_html(featured=focused)
        extra_cls = " cj-qakc-quest" + (" cj-qakc-focused" if focused else "")
        card_html = (
            f"<div class='{quest_cls}{extra_cls}'>"
            f"{promo}"
            f"<div class='cj-quest-body'>{body}</div>"
            f"</div>"
        )
    else:
        hero = venue_hero_html(str(row["location"]), row, featured=focused)
        if hero and focused:
            card_html = (
                f"<div class='{quest_cls}'>"
                f"{hero}<div class='cj-quest-body'>{body}</div>"
                f"</div>"
            )
        elif hero:
            card_html = (
                f"<div class='{quest_cls}'>"
                f"<div class='cj-quest-row'>{hero}<div class='cj-quest-body'>{body}</div></div>"
                f"</div>"
            )
        else:
            card_html = f"<div class='{quest_cls}'><div class='cj-quest-body'>{body}</div></div>"

    if focused and not is_earned:
        st.markdown(
            venue_scene_open_html(str(row["location"]), row) + card_html + VENUE_SCENE_CLOSE_HTML,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(card_html, unsafe_allow_html=True)


def render_day_detail(
    df: pd.DataFrame,
    day_num: int,
    partners_df: pd.DataFrame,
    bonus_df: pd.DataFrame,
    encounters_df: pd.DataFrame,
    key_prefix: str = "day",
    show_header: bool = True,
):
    meta = day_plan_meta(day_num)
    day_df = df[df["day_num"] == day_num].copy()
    earned = day_df[day_df["status"] == "earned"]
    earned_pts = day_activity_score(df, day_num)
    target = meta.get("target", 0)
    bonus = meta.get("bonus_target")
    goal_status = day_goal_status(df, day_num)
    day_box_cls = {"met": "day-met", "exceeded": "day-exceeded"}.get(goal_status, "")
    fill_cls = "dl-level-fill gold" if goal_status == "exceeded" else "dl-level-fill"

    if show_header:
        st.markdown(day_venue_banner_html(df, day_num), unsafe_allow_html=True)
        venue_strip = day_venue_strip_html(df, day_num, max_icons=6, size=36)
        st.markdown(
            f'<div class="dl-path-title">📋 Day {day_num} — {meta["title"]}</div>{venue_strip}',
            unsafe_allow_html=True,
        )
        if goal_status in ("met", "exceeded"):
            banner_cls = "exceeded" if goal_status == "exceeded" else ""
            emoji = "⭐" if goal_status == "exceeded" else "🏆"
            title = "Stretch crushed!" if goal_status == "exceeded" else f"Day {day_num} complete!"
            st.markdown(
                f"""
<div class="cj-day-victory-banner {banner_cls}">
  <div class="cj-day-victory-emoji">{emoji}</div>
  <div class="cj-day-victory-title">{title}</div>
  <div class="cj-day-victory-sub">
    {format_points(earned_pts)} / {format_points(target)} XP · {len(earned)} / {len(day_df)} quests
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
        prog_pct = min(earned_pts / target, 1.0) if target else 0
        overflow = day_overflow_points(df, day_num)
        if earned_pts >= target:
            xp_line = f"{format_points(target)} / {format_points(target)} XP"
            if overflow:
                xp_line += f" · 💫 +{overflow} bonus"
        else:
            xp_line = f"{format_points(earned_pts)} / {format_points(target)} XP"
        status_badge = {
            "exceeded": " · ⭐ <strong>Goal exceeded — overflow → bonus!</strong>",
            "met": " · ✅ <strong>Goal achieved</strong>",
        }.get(goal_status, "")
        st.markdown(
            f"""
<div class="dl-quest {day_box_cls}">
  <strong>{xp_line}</strong> · {len(earned)} / {len(day_df)} quests
  {' · 🎯 Stretch target <strong>' + str(bonus) + '+</strong>' if bonus else ''}{status_badge}
  <div class="dl-level-bar" style="margin-top:0.5rem;">
    <div class="{fill_cls}" style="width:{prog_pct * 100}%;"></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    used_as_sub_keys = valid_substitution_keys(df)
    sub_pool = df[
        df["activity_key"].isin(used_as_sub_keys) & (df["status"] == "pending")
    ]

    render_day_quest_nav(
        day_df,
        day_num,
        key_prefix,
        target,
        earned_pts,
        df,
        partners_df,
        encounters_df,
        sub_pool,
    )

    if not sub_pool.empty:
        st.markdown("#### Still open after substitutions")
        st.caption("These activities were used to fill other slots — their home slot still needs completing.")
        for _, row in sub_pool.iterrows():
            st.markdown(f"- **Day {row['day_num']}** · {row['title']} ({row['points']} pts)")

    render_day_extras(df, bonus_df, day_num, key_prefix)


def render_more_view(
    df: pd.DataFrame,
    encounters_df: pd.DataFrame,
    partners_df: pd.DataFrame,
    settings: dict,
) -> None:
    choice = st.radio(
        "MoreMenu",
        ["👥 Partners", "🔄 Swap", "⚙️ Settings"],
        horizontal=True,
        label_visibility="collapsed",
        key="more_tab_radio",
    )
    if choice == "👥 Partners":
        render_partners_tab(encounters_df, partners_df)
    elif choice == "🔄 Swap":
        render_substitution_pool(df)
    else:
        render_settings(settings)


def render_substitution_pool(df: pd.DataFrame):
    st.markdown("### Substitution pool & recalibration")
    st.markdown(
        "Any pending activity can fill any unfilled slot on any day. "
        "When you substitute, points count toward the **slot's target**, and the plan recalibrates for the rest of the stay."
    )

    pending = substitution_pool(df)
    used_as_sub_keys = valid_substitution_keys(df)
    sub_out = df[df["activity_key"].isin(used_as_sub_keys) & (df["status"] == "pending")]
    earned = df[df["status"] == "earned"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Pending slots", len(pending))
    c2.metric("Deferred (used as sub)", len(sub_out))
    c3.metric("Earned", len(earned))

    st.markdown("#### Remaining by day")
    for day_num in range(1, TOTAL_DAYS + 1):
        meta = day_plan_meta(day_num)
        day_df = df[df["day_num"] == day_num]
        day_pending = day_df[day_df["status"] == "pending"]
        day_earned = day_df[day_df["status"] == "earned"]
        rem_pts = int(day_pending["points"].sum()) if not day_pending.empty else 0
        got_pts = int(day_earned["earned_points"].fillna(day_earned["points"]).sum()) if not day_earned.empty else 0
        if rem_pts > 0 or len(day_pending) > 0:
            st.markdown(
                f"**Day {day_num} ({meta['title']})** — {got_pts}/{meta['target']} pts · "
                f"{len(day_pending)} activities remaining ({rem_pts} pts left)"
            )


def render_settings(settings: dict):
    st.markdown("### Settings")
    with st.form("settings"):
        display_name = st.text_input("Her name / label", value=settings.get("display_name", ""))
        dom_name = st.text_input("Dom's name", value=settings.get("dom_name", ""))
        journey_start = st.date_input(
            "Journey start (Day 1)",
            value=date.fromisoformat(settings.get("journey_start", date.today().isoformat())[:10]),
        )
        celebrations_on = st.checkbox(
            "Quest celebrations (sounds + confetti/fireworks)",
            value=celebrations_enabled(settings),
        )
        if st.form_submit_button("Save"):
            save_setting("display_name", display_name.strip() or "Her journey")
            save_setting("dom_name", dom_name.strip())
            save_setting("journey_start", journey_start.isoformat())
            save_setting("celebrations_enabled", "1" if celebrations_on else "0")
            st.success("Saved.")
            st.rerun()

    st.divider()
    render_activity_manager(load_activities_df())

    st.divider()
    st.markdown("#### Data")
    st.code(str(DB_PATH))
    st.caption("Private local storage — separate from Tellum Ultimum.")

    if st.button("Restore default 14-day plan", type="secondary"):
        restore_default_plan()
        st.warning("Default plan restored. Custom pending activities were removed; earned progress kept.")
        st.rerun()

    if st.button("Reset entire journey", type="secondary"):
        if DB_PATH.exists():
            DB_PATH.unlink()
        init_db()
        st.warning("Journey reset. All progress cleared.")
        st.rerun()


def main():
    brand_icon = BRAND_DIR / BRAND_ICON
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=str(brand_icon) if brand_icon.is_file() else "🔗",
        layout="wide",
    )
    inject_ios_homescreen_meta()
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    password_gate(APP_NAME)
    init_db()
    sync_coke_bonus_points()
    repair_orphaned_activity_refs()

    settings = load_settings()
    df = load_activities_df()
    partners_df = load_partners_df()
    encounters_df = load_encounters_df()
    bonus_df = load_bonus_df()
    sync_scores(df)
    if finalize_pending_with_saved_encounters(df):
        st.rerun()
    df = load_activities_df()
    bonus_df = load_bonus_df()
    stats = compute_stats(df, bonus_df)
    partner_summary = partner_stats(encounters_df, partners_df)
    journey_day = current_journey_day(settings)

    render_pending_celebrations(settings)

    if "main_tab_radio" not in st.session_state:
        st.session_state.main_tab_radio = TAB_TODAY
    elif st.session_state.main_tab_radio in _LEGACY_TAB_ALIASES:
        st.session_state.main_tab_radio = _LEGACY_TAB_ALIASES[st.session_state.main_tab_radio]

    apply_pending_navigation(MAIN_TABS)

    selected_tab = st.radio(
        "AppNavigate",
        MAIN_TABS,
        horizontal=True,
        label_visibility="collapsed",
        key="main_tab_radio",
    )

    if selected_tab not in (TAB_JOURNEY, TAB_PHOTOS):
        render_header(
            settings,
            stats,
            journey_day,
            partner_summary,
            nice=True,
        )

    if selected_tab == TAB_TODAY:
        render_calendar_view(df, encounters_df, settings, journey_day, bonus_df, partners_df)

    elif selected_tab == TAB_STATS:
        render_stats_view(df, encounters_df, bonus_df, stats, partner_summary, settings)

    elif selected_tab == TAB_JOURNEY:
        render_dashboard(
            df, stats, journey_day, partner_summary, bonus_df, partners_df, settings
        )

    elif selected_tab == TAB_MORE:
        render_more_view(df, encounters_df, partners_df, settings)

    elif selected_tab == TAB_PHOTOS:
        render_photos_view(df, partners_df, settings, journey_day)


if __name__ == "__main__":
    main()
