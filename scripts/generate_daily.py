"""自动生成今日文章与方案 JSON。"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate.fetch_matches import fetch_today_matches
from src.generate.llm import generate_daily_content
from src.review.archive import load_record

ARTICLE_FILE = ROOT / "articles" / "today.json"
PLAN_FILE = ROOT / "outputs" / "today_plan.json"
LOG_DIR = ROOT / "outputs" / "logs"


def _log(msg: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with (LOG_DIR / "generate.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> None:
    load_dotenv()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    _log("开始自动生成...")
    matches = fetch_today_matches()
    _log(f"抓取场次 {len(matches)} 场")

    yesterday_record = load_record(yesterday)
    if yesterday_record:
        _log(f"已加载昨日归档: {yesterday}")

    result = generate_daily_content(today, matches, yesterday_record)
    article = result.get("article")
    plan = result.get("plan")

    if not article or not plan:
        raise SystemExit("LLM 返回缺少 article 或 plan 字段")

    article["date"] = article.get("date") or today
    plan["date"] = plan.get("date") or today

    ARTICLE_FILE.write_text(
        json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    PLAN_FILE.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    dated = ROOT / "articles" / f"{today}.json"
    dated.write_text(
        json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    _log(f"已写入 {ARTICLE_FILE.name} 与 {PLAN_FILE.name}")


if __name__ == "__main__":
    main()
