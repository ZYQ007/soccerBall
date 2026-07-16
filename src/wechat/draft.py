import json

import requests


class WeChatDraftClient:
    def __init__(self, token_manager):
        self.token_manager = token_manager

    def add_draft(
        self,
        title: str,
        author: str,
        digest: str,
        content_html: str,
        thumb_media_id: str,
        content_source_url: str = "",
        need_open_comment: int = 1,
        only_fans_can_comment: int = 0,
    ) -> str:
        access_token = self.token_manager.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content_html,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": need_open_comment,
            "only_fans_can_comment": only_fans_can_comment,
        }
        if content_source_url:
            article["content_source_url"] = content_source_url

        payload = {"articles": [article]}
        resp = requests.post(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        if "media_id" not in data:
            raise RuntimeError(f"创建草稿失败: {data}")
        return data["media_id"]
