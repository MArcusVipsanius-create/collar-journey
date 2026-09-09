import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DB = Path.home() / "Desktop/Programs/TellumUltimumData/tellum_ultimum.sqlite3"
c = sqlite3.connect(str(DB))
print("=== daily_log 2026-06-22 ===")
print(c.execute("SELECT log_date, calories, protein_g, carbs_g, fat_g, notes FROM daily_log WHERE log_date='2026-06-22'").fetchone())
print("\n=== ocr_queue June 22 ===")
row = c.execute("""
  SELECT oq.parsed_json, oq.ocr_text, fr.file_name
  FROM ocr_queue oq LEFT JOIN file_registry fr ON fr.file_hash=oq.file_hash
  WHERE fr.file_name LIKE '%2026-06-22%'
""").fetchone()
if row:
    print("file:", row[2])
    print("parsed_json:", row[0])
    print("ocr_text:\n", row[1])
c.close()
