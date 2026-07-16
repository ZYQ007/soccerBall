"""调用 OpenAI 兼容 API 生成当日文章与方案 JSON。"""
import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
PROMPT_FILE = ROOT / "prompts" / "daily_generate.txt"


def _load_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    return "你是竞彩足球分析师，输出 article 与 plan 两个 JSON 对象。"


def generate_daily_content(
    today: str,
    matches: list[dict],
    yesterday_record: dict | None,
) -> dict:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("未配置 LLM_API_KEY，无法自动生成。请在 .env 中填写。")

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    system = _load_prompt()
    user_payload = {
        "today": today,
        "matches": matches,
        "yesterday_record": yesterday_record,
        "rules": {
            "article": "场次分析为主，昨日回顾仅精选场次，不含核心/价值/彩票仓",
            "plan": "含核心仓/价值仓/彩票仓，昨日回顾含实盘分层命中率",
            "author": os.getenv("ARTICLE_AUTHOR", "张彡"),
            "title_max_chars": 20,
            "digest_max_chars": 30,
        },
    }

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False),
                },
            ],
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)
