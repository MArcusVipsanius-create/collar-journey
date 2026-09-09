"""Smoke tests for Collar Journey quest layout helpers (no Streamlit runtime)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("collar_progress", ROOT / "collar_progress.py")
cj = importlib.util.module_from_spec(spec)
sys.modules["collar_progress"] = cj
spec.loader.exec_module(cj)


def _sample_row(**overrides):
    base = {
        "activity_key": "d13_sauna_1",
        "title": "Histoires d'O — Afternoon",
        "description": "Steam session after 2 PM.",
        "status": "pending",
        "location": "histoire_do",
        "time_slot": "afternoon",
        "points": 2,
        "day_num": 13,
        "id": 1,
    }
    base.update(overrides)
    return pd.Series(base)


def test_quest_grid_cols():
    assert cj._quest_grid_cols(1) == 1
    assert cj._quest_grid_cols(2) == 2
    assert cj._quest_grid_cols(4) == 2
    assert cj._quest_grid_cols(5) == 3
    assert cj._quest_grid_cols(8) == 4


def test_slot_grouping():
    df = pd.DataFrame(
        [
            {"activity_key": "a", "status": "pending", "time_slot": "morning", "id": 1},
            {"activity_key": "b", "status": "pending", "time_slot": "afternoon", "id": 2},
            {"activity_key": "c", "status": "pending", "time_slot": "evening", "id": 3},
        ]
    )
    grouped = cj._pending_by_slot_group(df)
    assert grouped["morning"] == ["a"]
    assert grouped["afternoon"] == ["b"]
    assert grouped["evening"] == ["c"]


def test_tile_html_includes_title_and_media():
    original = cj.challenge_media_uri
    cj.challenge_media_uri = lambda _key: None
    try:
        html = cj.quest_day_tile_html(_sample_row(), selected=True)
    finally:
        cj.challenge_media_uri = original
    assert "cj-quest-day-tile-media" in html
    assert "cj-quest-day-tile-overlay" in html
    assert "Histoires" in html
    assert "selected" in html


def test_open_panel_skips_log_when_quick_complete():
    """maybe_render_quest_quick_complete True => caller should skip log panel."""
    row = _sample_row()
    # Not preloaded => quick complete unavailable => log panel path
    assert cj.quest_quick_complete_context(row, "calendar", pd.DataFrame(), 13) is None


def test_sorted_quest_keys_respect_time_order():
    df = pd.DataFrame(
        [
            {"activity_key": "eve", "time_slot": "evening", "id": 3, "status": "pending"},
            {"activity_key": "am", "time_slot": "morning", "id": 1, "status": "pending"},
            {"activity_key": "pm", "time_slot": "afternoon", "id": 2, "status": "pending"},
        ]
    )
    assert cj._sorted_quest_keys(df) == ["am", "pm", "eve"]


def main() -> int:
    tests = [
        test_quest_grid_cols,
        test_slot_grouping,
        test_tile_html_includes_title_and_media,
        test_open_panel_skips_log_when_quick_complete,
        test_sorted_quest_keys_respect_time_order,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"OK  {test.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
