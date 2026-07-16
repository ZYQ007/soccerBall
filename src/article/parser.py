import json
import re
from pathlib import Path


UNICODE_ESCAPE_RE = re.compile(r"\\u[0-9a-fA-F]{4}")


def _decode_unicode_escapes(text: str) -> str:
    # 兼容外部来源把中文写成 "\u4e2d\u6587" 的情况
    if not UNICODE_ESCAPE_RE.search(text):
        return text
    try:
        return text.encode("utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        return text


def _normalize(value):
    if isinstance(value, str):
        return _decode_unicode_escapes(value)
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    return value


def load_article_json(path: str | Path) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"文章 JSON 不存在: {file_path}")

    data = json.loads(file_path.read_text(encoding="utf-8"))
    data = _normalize(data)
    required = ["title", "digest", "matches_summary"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"文章 JSON 缺少字段: {', '.join(missing)}")
    return data
