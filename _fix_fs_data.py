import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

APP = Path(__file__).with_name("app.py")
code = APP.read_text(encoding="utf-8").split("\ninit_db()\ns = settings()")[0]
ns = {"__name__": "fix"}
exec(code, ns)

DB = Path.home() / "Desktop/Programs/TellumUltimumData/tellum_ultimum.sqlite3"
c = sqlite3.connect(str(DB))

row = c.execute("""
  SELECT oq.file_hash, oq.parsed_json, oq.ocr_text, fr.file_name
  FROM ocr_queue oq LEFT JOIN file_registry fr ON fr.file_hash=oq.file_hash
  WHERE fr.file_name LIKE '%2026-06-22%'
""").fetchone()
assert row, "June 22 OCR row not found"
fh, old_parsed, ocr_text, fname = row

print("=== BEFORE ===")
print("daily_log:", c.execute("SELECT log_date, calories, protein_g, carbs_g, notes FROM daily_log WHERE log_date='2026-06-22'").fetchone())
print("parsed_json:", old_parsed)

parsed = ns["parse_fatsecret_ocr"](ocr_text)
print("\n=== RE-PARSE ===")
print(parsed)

expected = {
    "calories": 2154.0,
    "protein_g": 175.53,
    "carbs_g": 211.28,
    "fiber_g": 14.2,
    "sodium_mg": 1769.0,
}
for k, v in expected.items():
    assert parsed.get(k) == v, f"{k}: got {parsed.get(k)}, want {v}"

notes = ns["fatsecret_screenshot_notes"](parsed)
new_parsed_json = json.dumps(parsed)
c.execute(
    "UPDATE ocr_queue SET parsed_json = ? WHERE file_hash = ?",
    (new_parsed_json, fh),
)
c.execute(
    """
    UPDATE daily_log SET calories=?, protein_g=?, carbs_g=?, notes=?
    WHERE log_date='2026-06-22'
    """,
    (parsed["calories"], parsed["protein_g"], parsed["carbs_g"], f"[FatSecret] {notes}"),
)
c.commit()

print("\n=== AFTER ===")
print("daily_log:", c.execute("SELECT log_date, calories, protein_g, carbs_g, notes FROM daily_log WHERE log_date='2026-06-22'").fetchone())
print("parsed_json:", c.execute("SELECT parsed_json FROM ocr_queue WHERE file_hash=?", (fh,)).fetchone()[0])
c.close()
print("\nOK: live database updated")
