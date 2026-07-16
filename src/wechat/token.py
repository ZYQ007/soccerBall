import json
import time
from pathlib import Path

import requests

TOKEN_CACHE_FILE = Path(".cache/token_cache.json")


class WeChatTokenManager:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    def get_access_token(self) -> str:
        cached = self._read_cache()
        if cached and cached["expires_at"] > time.time() + 60:
            return cached["access_token"]

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret,
        }
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if "access_token" not in data:
            raise RuntimeError(f"获取 access_token 失败: {data}")

        self._write_cache(data["access_token"], data.get("expires_in", 7200))
        return data["access_token"]

    def _read_cache(self) -> dict | None:
        if not TOKEN_CACHE_FILE.exists():
            return None
        try:
            return json.loads(TOKEN_CACHE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def _write_cache(self, access_token: str, expires_in: int) -> None:
        payload = {
            "access_token": access_token,
            "expires_at": time.time() + expires_in,
        }
        TOKEN_CACHE_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
