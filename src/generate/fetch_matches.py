"""抓取竞彩足球开售场次（网易彩票页面）。"""
import re
from datetime import datetime

import requests

URL = "https://sports.163.com/caipiao/match/football/jczq"


def fetch_today_matches() -> list[dict]:
    resp = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    text = resp.text

    rows: list[dict] = []
    # 匹配表格行：周四201 | 挪超 | ... | 07-17 01:00 | 未 | 主队 | VS | 客队 | ... | 主胜 1.53 ...
    pattern = re.compile(
        r"周[一二三四五六日]\d{3}.*?"
        r"(\d{2}-\d{2}\s+\d{2}:\d{2}).*?"
        r"未.*?"
        r"([^|<>]+?)\s*</td>.*?VS.*?([^|<>]+?)\s*</td>.*?"
        r"主胜\s+([\d.]+)\s+平\s+([\d.]+)\s+客胜\s+([\d.]+)",
        re.S,
    )

    # 备用：按行块解析
    blocks = re.findall(
        r"周[一二三四五六日](\d{3})[^|]*\|[^|]*\|[^|]*\|"
        r"(\d{2}-\d{2}\s+\d{2}:\d{2})[^|]*\|[^|]*未[^|]*\|"
        r"([^|]+)\|[^|]*VS[^|]*([^|]+)\|[^|]*\|"
        r"主胜\s+([\d.]+)\s+平\s+([\d.]+)\s+客胜\s+([\d.]+)",
        text,
    )

    for block in blocks:
        code, kickoff, home, away, w, d, l = block
        home = re.sub(r"<[^>]+>", "", home).strip()
        away = re.sub(r"<[^>]+>", "", away).strip()
        rows.append(
            {
                "code": f"周{code}",
                "kickoff": kickoff.strip(),
                "home": home,
                "away": away,
                "odds": {"win": w, "draw": d, "lose": l},
            }
        )

    if not rows:
        # 极简兜底：至少返回日期供 LLM 自行说明
        rows.append(
            {
                "code": "未知",
                "kickoff": datetime.now().strftime("%m-%d %H:%M"),
                "home": "请手动核对开售",
                "away": "",
                "odds": {},
                "note": "自动抓取失败，请检查网络或稍后重试",
            }
        )

    return rows
