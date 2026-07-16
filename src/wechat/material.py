from pathlib import Path

import requests


class WeChatMaterialClient:
    def __init__(self, token_manager):
        self.token_manager = token_manager

    def upload_image(self, image_path: str) -> str:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"封面图不存在: {image_path}")

        access_token = self.token_manager.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"

        with path.open("rb") as f:
            files = {"media": (path.name, f, "image/jpeg")}
            resp = requests.post(url, files=files, timeout=60)

        resp.raise_for_status()
        data = resp.json()
        if "media_id" not in data:
            raise RuntimeError(f"上传封面失败: {data}")
        return data["media_id"]
