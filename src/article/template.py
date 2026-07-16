from __future__ import annotations

from html import escape

from src.review.yesterday import format_yesterday_review_html

# 公众号正文样式（内联 CSS，兼容微信编辑器）
_STYLE = {
    "section": (
        "font-size:17px;font-weight:bold;color:#1a1a1a;"
        "border-left:4px solid #07c160;padding-left:10px;margin:28px 0 16px;"
    ),
    "intro": "font-size:15px;color:#555;line-height:1.8;margin:0 0 20px;",
    "tip_box": (
        "background:#f6f8f6;border-radius:6px;padding:12px 14px;"
        "font-size:14px;color:#666;line-height:1.7;margin:0 0 24px;"
    ),
    "review_box": (
        "background:#fff9e6;border-radius:8px;padding:16px;"
        "margin:0 0 24px;border:1px solid #f0e6c8;"
    ),
    "match_card": (
        "background:#fafafa;border-radius:8px;padding:16px;"
        "margin:0 0 20px;border:1px solid #eee;"
    ),
    "match_title": "font-size:16px;font-weight:bold;color:#1a1a1a;margin:0 0 4px;",
    "match_meta": "font-size:13px;color:#999;margin:0 0 12px;",
    "label": "font-size:14px;color:#07c160;font-weight:bold;margin:12px 0 6px;",
    "body": "font-size:15px;color:#333;line-height:1.85;margin:0 0 8px;",
    "insight": (
        "font-size:14px;color:#555;line-height:1.75;"
        "background:#fff;border-left:3px solid #07c160;"
        "padding:8px 12px;margin:10px 0 0;"
    ),
    "pred_row": (
        "display:flex;flex-wrap:wrap;font-size:14px;"
        "color:#333;line-height:2;margin:4px 0;"
    ),
    "pred_key": "color:#888;min-width:72px;",
    "pred_val": "color:#1a1a1a;font-weight:500;",
    "divider": "border:none;border-top:1px dashed #e0e0e0;margin:20px 0;",
    "table_wrap": "overflow-x:auto;margin:16px 0;",
    "table": (
        "border-collapse:collapse;width:100%;font-size:13px;"
        "line-height:1.6;"
    ),
    "th": (
        "background:#07c160;color:#fff;padding:8px 6px;"
        "text-align:center;font-weight:normal;white-space:nowrap;"
    ),
    "td": "border:1px solid #e8e8e8;padding:7px 6px;text-align:center;color:#333;",
    "td_left": "border:1px solid #e8e8e8;padding:7px 8px;text-align:left;color:#333;",
    "footer": "font-size:13px;color:#999;line-height:1.8;margin:24px 0 0;",
    "ending": "font-size:15px;color:#07c160;text-align:center;margin:20px 0 0;",
}


def _esc(text: str) -> str:
    return escape(str(text))


def _section(title: str) -> str:
    return f'<p style="{_STYLE["section"]}">{_esc(title)}</p>'


def _p(text: str, style: str = "body") -> str:
    return f'<p style="{_STYLE[style]}">{_esc(text)}</p>'


def _label(text: str) -> str:
    return f'<p style="{_STYLE["label"]}">{_esc(text)}</p>'


def _pred_line(key: str, value: str) -> str:
    return (
        f'<p style="{_STYLE["pred_row"]}">'
        f'<span style="{_STYLE["pred_key"]}">{_esc(key)}</span>'
        f'<span style="{_STYLE["pred_val"]}">{_esc(value)}</span>'
        f"</p>"
    )


def _match_card(analysis: dict) -> str:
    parts: list[str] = []
    parts.append(f'<section style="{_STYLE["match_card"]}">')

    parts.append(f'<p style="{_STYLE["match_title"]}">{_esc(analysis.get("match", ""))}</p>')
    meta = analysis.get("meta", "")
    if meta:
        parts.append(f'<p style="{_STYLE["match_meta"]}">{_esc(meta)}</p>')

    for block_key, block_label in [
        ("fundamentals", "基本面"),
        ("goals_dist", "进球分布"),
        ("unique_view", "独到见解"),
    ]:
        text = analysis.get(block_key, "")
        if text:
            parts.append(_label(block_label))
            parts.append(_p(text))

    wdl = analysis.get("wdl", "")
    half_full = analysis.get("half_full", "")
    goals = analysis.get("goals", "")
    scores = analysis.get("scores", [])
    if wdl or half_full or goals or scores:
        parts.append(_label("参考方向"))
        if wdl:
            parts.append(_pred_line("胜平负", wdl))
        if half_full:
            parts.append(_pred_line("半全场", half_full))
        if goals:
            parts.append(_pred_line("进球数", goals))
        if scores:
            score_text = "  >  ".join(scores[:3])
            parts.append(_pred_line("比分倾向", score_text))

    parts.append("</section>")
    return "\n".join(parts)


def _summary_table(rows: list[dict]) -> str:
    if not rows:
        return ""

    head = (
        "<tr>"
        + "".join(
            f'<th style="{_STYLE["th"]}">{_esc(h)}</th>'
            for h in ["场次", "胜平负", "半全场", "进球", "比分1", "比分2", "比分3"]
        )
        + "</tr>"
    )
    body = ""
    for m in rows:
        scores = m.get("scores", ["", "", ""])
        cells = [
            m.get("match", ""),
            m.get("wdl", ""),
            m.get("half_full", ""),
            m.get("goals", ""),
            scores[0] if len(scores) > 0 else "",
            scores[1] if len(scores) > 1 else "",
            scores[2] if len(scores) > 2 else "",
        ]
        body += "<tr>"
        for i, cell in enumerate(cells):
            style = _STYLE["td_left"] if i == 0 else _STYLE["td"]
            body += f'<td style="{style}">{_esc(cell)}</td>'
        body += "</tr>"

    return (
        f'<div style="{_STYLE["table_wrap"]}">'
        f'<table style="{_STYLE["table"]}"><thead>{head}</thead><tbody>{body}</tbody></table>'
        f"</div>"
    )


def render_article_html(article: dict) -> str:
    """公众号文章：场次分析为主，文末附精选总结表。不含投注方案仓位。"""
    parts: list[str] = []

    intro = article.get("intro", "")
    if intro:
        parts.append(_p(intro, "intro"))

    yesterday = article.get("yesterday_review")
    if yesterday:
        parts.append(
            format_yesterday_review_html(
                yesterday,
                {
                    "section": _STYLE["section"],
                    "body": _STYLE["body"],
                    "label": _STYLE["label"],
                    "review_box": _STYLE["review_box"],
                },
            )
        )

    single_info = article.get("single_match_info", "")
    if single_info:
        parts.append(f'<div style="{_STYLE["tip_box"]}">📋 {_esc(single_info)}</div>')

    analyses = article.get("match_analyses", [])
    if analyses:
        parts.append(_section("场次分析"))
        for i, item in enumerate(analyses):
            parts.append(_match_card(item))
            if i < len(analyses) - 1:
                parts.append(f'<hr style="{_STYLE["divider"]}"/>')

    parts.append(_section("今日精选总结"))
    summary_note = article.get(
        "summary_note",
        "以下为今日筛选场次的快速对照，详细分析见上文。",
    )
    parts.append(_p(summary_note))
    parts.append(_summary_table(article.get("matches_summary", [])))

    disclaimer = article.get(
        "disclaimer",
        "本文内容仅供体育数据分析与娱乐参考，不构成任何投注建议。请理性参与，量力而行。",
    )
    parts.append(_section("风险提示"))
    parts.append(_p(disclaimer, "footer"))

    ending = article.get("ending", "你觉得今天哪场最有看头？评论区聊聊。")
    parts.append(f'<p style="{_STYLE["ending"]}">{_esc(ending)}</p>')

    return "\n".join(parts)
