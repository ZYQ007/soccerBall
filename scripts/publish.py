import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.article.parser import load_article_json
from src.article.template import render_article_html
from src.wechat.draft import WeChatDraftClient
from src.wechat.material import WeChatMaterialClient
from src.wechat.publisher import WeChatPublisher
from src.wechat.token import WeChatTokenManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="发布竞彩分析文章到微信公众号")
    parser.add_argument(
        "--file",
        required=True,
        help="文章 JSON 文件路径，例如 articles/2026-07-16.json",
    )
    parser.add_argument(
        "--mode",
        choices=["draft_only", "publish"],
        default=None,
        help="覆盖 .env 中的 PUBLISH_MODE",
    )
    return parser


def main() -> None:
    load_dotenv()
    args = build_parser().parse_args()

    app_id = os.getenv("WECHAT_APP_ID", "").strip()
    app_secret = os.getenv("WECHAT_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        raise SystemExit("请先在 .env 中配置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")

    article = load_article_json(args.file)
    html = render_article_html(article)

    author = article.get("author") or os.getenv("ARTICLE_AUTHOR", "足球数据分析")
    source_url = article.get("source_url") or os.getenv("ARTICLE_SOURCE_URL", "")
    cover_path = article.get("cover_image") or os.getenv(
        "COVER_IMAGE_PATH", "assets/cover_default.jpg"
    )

    token_manager = WeChatTokenManager(app_id, app_secret)
    material_client = WeChatMaterialClient(token_manager)
    draft_client = WeChatDraftClient(token_manager)
    publisher = WeChatPublisher(token_manager)

    thumb_media_id = material_client.upload_image(cover_path)
    media_id = draft_client.add_draft(
        title=article["title"],
        author=author,
        digest=article["digest"],
        content_html=html,
        thumb_media_id=thumb_media_id,
        content_source_url=source_url,
    )

    mode = args.mode or os.getenv("PUBLISH_MODE", "draft_only")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{now}] 草稿创建成功")
    print(f"media_id: {media_id}")
    print(f"标题: {article['title']}")

    if mode == "publish":
        try:
            result = publisher.submit_publish(media_id)
            print("已提交发布任务")
            print(result)
            print("请到公众号后台确认发布状态（可能异步完成）")
        except Exception as exc:
            print("自动发布提交失败，草稿仍已创建。")
            print(f"失败原因: {exc}")
            print("请登录公众号后台 -> 草稿箱 -> 手动发布。")
            raise
    else:
        print("当前为 draft_only 模式：请登录公众号后台 -> 草稿箱 -> 检查并发布")


if __name__ == "__main__":
    main()
