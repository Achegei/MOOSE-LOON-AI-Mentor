"""Simple DB smoke test to create tables using `init_db`.

Run with: python tests/db_smoke.py
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.session import init_db


def main():
    try:
        init_db()
        print("SUCCESS: init_db() ran — tables created or verified.")
    except Exception as e:
        print("ERROR: init_db() failed:", e)


if __name__ == "__main__":
    main()
