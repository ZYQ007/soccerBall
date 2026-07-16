import requests


class WeChatPublisher:
    def __init__(self, token_manager):
        self.token_manager = token_manager

    def submit_publish(self, media_id: str) -> dict:
        access_token = self.token_manager.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
        resp = requests.post(url, json={"media_id": media_id}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode", 0) != 0:
            raise RuntimeError(f"提交发布失败: {data}")
        return data
