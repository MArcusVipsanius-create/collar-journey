"""Generate COLLAR_PASSWORD_HASH for local env or deployment secrets.

Usage:
  python scripts/hash_collar_password.py "your-chosen-password"
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from collar_auth import hash_password  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print("Usage: python scripts/hash_collar_password.py \"your-password\"")
        sys.exit(1)
    hashed = hash_password(sys.argv[1].strip())
    print("\nAdd this to your environment or hosting secrets:\n")
    print(f"COLLAR_PASSWORD_HASH={hashed}\n")
    print("Never commit the plain password or this line to git if it includes the real password.")


if __name__ == "__main__":
    main()
