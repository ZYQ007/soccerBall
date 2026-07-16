"""归档每日方案，供次日昨日回顾使用。"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS_DIR = ROOT / "records"


def archive_daily_plan(plan: dict) -> Path:
    date = plan.get("date")
    if not date:
        raise ValueError("plan 缺少 date 字段，无法归档")

    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    path = RECORDS_DIR / f"{date}.json"

    record = {
        "date": date,
        "archived_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "plan": plan,
        "results_filled_at": None,
        "review": None,
    }

    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        record["results_filled_at"] = existing.get("results_filled_at")
        record["review"] = existing.get("review")

    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_record(date: str) -> dict | None:
    path = RECORDS_DIR / f"{date}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
