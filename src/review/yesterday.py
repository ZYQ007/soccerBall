"""昨日回顾：公众号（场次分析）与方案推送（含实盘分层）分开渲染。"""

from html import escape

HIT_LABELS = {
    "hit": "命中",
    "partial": "部分命中",
    "miss": "未中",
    "pending": "待开奖",
}

TIER_LABELS = {
    "core": "核心仓",
    "value": "价值仓",
    "lottery": "彩票仓",
}


def _render_items_markdown(items: list[dict]) -> list[str]:
    lines: list[str] = []
    for item in items:
        match = item.get("match", "")
        prediction = item.get("prediction", "")
        result = item.get("result", "")
        outcome = item.get("outcome", "")
        label = item.get("outcome_label") or HIT_LABELS.get(outcome, outcome)
        note = item.get("note", "")

        icon = {"hit": "✅", "partial": "🟡", "miss": "❌", "pending": "⏳"}.get(outcome, "▪️")
        lines.append(f"- {icon} **{match}**")
        lines.append(f"  - 预测：{prediction}")
        lines.append(f"  - 赛果：{result}")
        lines.append(f"  - 结果：{label}")
        if note:
            lines.append(f"  - 复盘：{note}")
    return lines


def _render_portfolio_markdown(review: dict) -> list[str]:
    """仅用于微信方案推送，公众号文章不调用。"""
    lines: list[str] = []
    portfolio = review.get("portfolio_stats") or {}
    summary = portfolio.get("summary_text", "")
    if summary:
        lines.append(f"**实盘战绩**：{summary}")
        lines.append("")

    for key in ("core", "value", "lottery"):
        tier = portfolio.get(key)
        if not tier:
            continue
        name = TIER_LABELS.get(key, key)
        hit = tier.get("hit", 0)
        total = tier.get("total", 0)
        detail = tier.get("detail", "")
        lines.append(f"- **{name}**：{hit}/{total}")
        if detail:
            lines.append(f"  - {detail}")

    for item in review.get("portfolio_items", []):
        tier = item.get("tier", "")
        title = item.get("title", "")
        content = item.get("content", "")
        outcome = item.get("outcome", "")
        label = item.get("outcome_label") or HIT_LABELS.get(outcome, outcome)
        icon = {"hit": "✅", "partial": "🟡", "miss": "❌", "pending": "⏳"}.get(outcome, "▪️")
        tier_name = TIER_LABELS.get(tier, tier)
        lines.append(f"  {icon} [{tier_name}] {title}：{content} → {label}")

    if lines and not summary:
        lines.insert(0, "**实盘分层**")
        lines.insert(1, "")
    elif portfolio:
        lines.insert(0, "### 💼 实盘分层")
        lines.insert(1, "")

    if lines:
        lines.append("")
    return lines


def format_yesterday_review_markdown(review: dict, *, include_portfolio: bool = True) -> list[str]:
    """方案推送用：场次回顾 + 可选实盘分层。"""
    if not review:
        return []

    lines: list[str] = []
    lines.append("### 📅 昨日回顾")
    lines.append("")

    review_date = review.get("review_date", "")
    headline = review.get("headline", "")
    if review_date:
        lines.append(f"**复盘日期**：{review_date}")
    if headline:
        lines.append(headline)
    lines.append("")

    stats = review.get("stats") or {}
    stats_text = stats.get("summary_text", "")
    if stats_text:
        lines.append(f"**精选场次**：{stats_text}")
        lines.append("")

    items = review.get("items", [])
    if items:
        lines.append("**场次复盘**")
        lines.extend(_render_items_markdown(items))
        lines.append("")

    if include_portfolio and (
        review.get("portfolio_stats") or review.get("portfolio_items")
    ):
        lines.extend(_render_portfolio_markdown(review))

    learnings = review.get("learnings", [])
    if learnings:
        lines.append("**经验沉淀**")
        for tip in learnings:
            lines.append(f"- {tip}")
        lines.append("")

    return lines


def format_yesterday_review_html(review: dict, styles: dict) -> str:
    """公众号文章用：仅场次分析回顾，不含实盘分层。"""
    if not review:
        return ""

    parts: list[str] = []
    box = styles.get(
        "review_box",
        "background:#fff9e6;border-radius:6px;padding:14px;margin:0 0 24px;border:1px solid #f0e6c8;",
    )
    section = styles.get("section", "")
    body = styles.get("body", "")
    label = styles.get("label", "")

    parts.append(f'<div style="{box}">')
    parts.append(f'<p style="{section}">昨日回顾</p>')

    review_date = review.get("review_date", "")
    headline = review.get("headline", "")
    if review_date:
        parts.append(f'<p style="{body}">复盘日期：{escape(review_date)}</p>')
    if headline:
        parts.append(f'<p style="{body}">{escape(headline)}</p>')

    stats = review.get("stats") or {}
    stats_text = stats.get("summary_text", "")
    if stats_text:
        parts.append(
            f'<p style="{body}"><strong>精选场次：</strong>{escape(stats_text)}</p>'
        )

    items = review.get("items", [])
    if items:
        parts.append(f'<p style="{label}">场次复盘</p>')
        for item in items:
            match = item.get("match", "")
            prediction = item.get("prediction", "")
            result = item.get("result", "")
            outcome = item.get("outcome", "")
            label_text = item.get("outcome_label") or HIT_LABELS.get(outcome, outcome)
            note = item.get("note", "")

            parts.append(f'<p style="{label}">{escape(match)} · {escape(label_text)}</p>')
            parts.append(f'<p style="{body}">预测：{escape(prediction)}</p>')
            parts.append(f'<p style="{body}">赛果：{escape(result)}</p>')
            if note:
                parts.append(f'<p style="{body}">复盘：{escape(note)}</p>')

    learnings = review.get("learnings", [])
    if learnings:
        parts.append(f'<p style="{label}">经验沉淀</p>')
        for tip in learnings:
            parts.append(f'<p style="{body}">· {escape(tip)}</p>')

    parts.append("</div>")
    return "\n".join(parts)
