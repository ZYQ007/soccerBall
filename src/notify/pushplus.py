import requests


def send_pushplus(
    token: str,
    title: str,
    content: str,
    template: str = "txt",
    topic: str = "",
) -> dict:
    if not token:
        raise ValueError("未配置 PUSHPLUS_TOKEN")

    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": template,
    }
    if topic:
        payload["topic"] = topic

    resp = requests.post(
        "http://www.pushplus.plus/send",
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"PushPlus 推送失败: {data}")
    return data
