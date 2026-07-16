"""将结构化方案格式化为 PushPlus Markdown 推送正文。"""

from src.review.yesterday import format_yesterday_review_markdown


def _stars(level: int, maximum: int = 5) -> str:
    level = max(0, min(maximum, int(level)))
    return "★" * level + "☆" * (maximum - level)


def _conf_suffix(item: dict) -> str:
    level = item.get("confidence")
    if level is None:
        return ""
    return f" {_stars(level)}"


def format_push_markdown(plan: dict, draft_ok: bool, draft_msg: str) -> str:
    market = plan.get("market", "")
    budget = plan.get("budget_note", "")
    lines: list[str] = []

    status = "✅" if draft_ok else "⚠️"
    lines.append(f"**{status} 公众号草稿**：{draft_msg}")
    lines.append("")
    lines.append("---")
    lines.append("")

    if market or budget:
        meta_parts = [p for p in [f"行情 **{market}**" if market else "", budget] if p]
        lines.append(" · ".join(meta_parts))
        lines.append("")

    yesterday = plan.get("yesterday_review")
    if yesterday:
        lines.extend(format_yesterday_review_markdown(yesterday))

    single = plan.get("single_match_info", "")
    if single:
        lines.append("### 📋 开售提示")
        lines.append(single)
        lines.append("")

    core = plan.get("core", [])
    if core:
        lines.append("### 🎯 核心仓")
        for item in core:
            match = item.get("match", "")
            pick = item.get("pick", "")
            detail = item.get("detail", "")
            note = item.get("note", "")
            head = f"**{match}** {pick}" if match else f"**{pick}**"
            lines.append(f"- {head}{_conf_suffix(item)}")
            if detail:
                lines.append(f"  - {detail}")
            if note:
                lines.append(f"  - _{note}_")
        lines.append("")

    value = plan.get("value", [])
    if value:
        lines.append("### 💎 价值仓")
        for i, item in enumerate(value, 1):
            title = item.get("title", "推荐")
            content = item.get("content", "")
            reason = item.get("reason", "")
            lines.append(f"{i}. **{title}**{_conf_suffix(item)}：{content}")
            if reason:
                lines.append(f"   > {reason}")
        lines.append("")

    lottery = plan.get("lottery", [])
    if lottery:
        lines.append("### 🎲 彩票仓（自行配置金额）")
        for item in lottery:
            title = item.get("title", "方案")
            rating = item.get("rating", "")
            content = item.get("content", "")
            risk = item.get("risk", "")
            tag = f" `{rating}`" if rating else ""
            lines.append(f"- **{title}**{tag}{_conf_suffix(item)}：{content}")
            if risk:
                lines.append(f"  - 风险：{risk}")
        lines.append("")

    summary = plan.get("summary", [])
    if summary:
        lines.append("### 📊 精选总结")
        lines.append("")
        lines.append("| 场次 | 信心 | 胜平负 | 半全场 | 进球 | 比分倾向 |")
        lines.append("| :--- | :---: | :--- | :--- | :--- | :--- |")
        for row in summary:
            conf = _stars(row["confidence"]) if row.get("confidence") is not None else "-"
            lines.append(
                "| {match} | {conf} | {wdl} | {half_full} | {goals} | {scores} |".format(
                    match=row.get("match", ""),
                    conf=conf,
                    wdl=row.get("wdl", ""),
                    half_full=row.get("half_full", ""),
                    goals=row.get("goals", ""),
                    scores=row.get("scores", ""),
                )
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    disclaimer = plan.get(
        "disclaimer",
        "仅供体育数据分析与娱乐参考，不构成投注建议。理性参与，量力而行。",
    )
    lines.append(f"_{disclaimer}_")
    lines.append("")
    if draft_ok:
        lines.append("📌 公众号深度分析已入草稿箱，请后台预览后发布。")

    return "\n".join(lines)
