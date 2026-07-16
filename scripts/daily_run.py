"""每日自动任务：推公众号草稿 + 微信推送今日方案。"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.notify.format_push import format_push_markdown
from src.notify.pushplus import send_pushplus
from src.review.archive import archive_daily_plan

PLAN_JSON = ROOT / "outputs" / "today_plan.json"
PLAN_FILE = ROOT / "outputs" / "today_plan.md"
ARTICLE_FILE = ROOT / "articles" / "today.json"
LOG_DIR = ROOT / "outputs" / "logs"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


def _load_plan() -> dict:
    if PLAN_JSON.exists():
        return json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    if PLAN_FILE.exists():
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "market": "",
            "single_match_info": "",
            "raw_markdown": PLAN_FILE.read_text(encoding="utf-8"),
        }
    raise FileNotFoundError("未找到 today_plan.json 或 today_plan.md")


def _log(msg: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with (LOG_DIR / "daily_run.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _windows_toast(title: str, message: str) -> None:
    try:
        safe_title = title.replace('"', "'")
        safe_msg = message.replace('"', "'")
        ps = (
            "[Windows.UI.Notifications.ToastNotificationManager, "
            "Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; "
            "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, "
            "ContentType = WindowsRuntime] | Out-Null; "
            f'$t="{safe_title}"; $m="{safe_msg}"; '
            '$xml = New-Object Windows.Data.Xml.Dom.XmlDocument; '
            '$xml.LoadXml("<toast><visual><binding template=\"ToastText02\">'
            '<text id=\"1\">$t</text><text id=\"2\">$m</text>'
            '</binding></visual></toast>"); '
            "$n = [Windows.UI.Notifications.ToastNotification]::new($xml); "
            "[Windows.UI.Notifications.ToastNotificationManager]::"
            "CreateToastNotifier('张彡足球').Show($n)"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            check=False,
            capture_output=True,
        )
    except Exception:
        pass


def _publish_draft() -> tuple[bool, str]:
    if not ARTICLE_FILE.exists():
        return False, "articles/today.json 不存在"

    if not PYTHON.exists():
        return False, "Python 虚拟环境未安装，请先运行 pip install"

    result = subprocess.run(
        [str(PYTHON), str(ROOT / "scripts" / "publish.py"), "--file", str(ARTICLE_FILE)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode == 0:
        return True, "公众号草稿已创建"
    return False, f"草稿失败: {output[-300:]}"


def main() -> None:
    load_dotenv()
    token = os.getenv("PUSHPLUS_TOKEN", "").strip()

    try:
        plan = _load_plan()
    except FileNotFoundError as exc:
        now = datetime.now().strftime("%Y-%m-%d")
        msg = str(exc)
        _log(msg)
        if token:
            send_pushplus(token, f"【张彡足球】{now} 方案未生成", msg)
        _windows_toast("张彡足球", "今日方案文件缺失")
        raise SystemExit(1) from exc

    now = plan.get("date") or datetime.now().strftime("%Y-%m-%d")
    draft_ok, draft_msg = _publish_draft()
    _log(draft_msg)

    if plan.get("raw_markdown"):
        status = "成功" if draft_ok else "失败"
        push_body = (
            f"**草稿推送{status}**：{draft_msg}\n\n---\n\n"
            f"{plan['raw_markdown']}\n\n---\n\n"
            f"📌 公众号文章已入草稿箱，请后台确认发布。"
        )
    else:
        push_body = format_push_markdown(plan, draft_ok, draft_msg)

    push_title = f"【张彡足球】{now} 今日方案"

    if token:
        send_pushplus(token, push_title, push_body, template="markdown")
        _log("PushPlus 微信推送成功（Markdown）")

    if not plan.get("raw_markdown"):
        try:
            archive_path = archive_daily_plan(plan)
            _log(f"方案已归档: {archive_path.name}")
        except ValueError as exc:
            _log(f"方案归档跳过: {exc}")
    else:
        _log("使用 raw_markdown 方案，跳过归档")

    if not token:
        _log("未配置 PUSHPLUS_TOKEN，仅本地通知")

    _windows_toast("张彡足球", "今日方案已更新，请查看微信/outputs")
    _log("每日任务完成")


if __name__ == "__main__":
    main()
