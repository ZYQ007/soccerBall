# 竞彩公众号自动发布脚本

已按你的公众号信息配置完成基础脚本。

## 已配置项

- 公众号：张彡足球（订阅号，个人主体，未认证）
- 默认作者：张彡足球
- 发布模式：`publish`

> 注意：未认证/个人主体账号可能被微信限制发布接口能力。若自动发布报错 `48001`，请改用草稿模式。

## 首次运行

```bash
cd D:\Personal\soccerBall
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

准备封面图：

- 把图片放到 `assets/cover_default.jpg`

执行发布：

```bash
python scripts/publish.py --file articles/2026-07-16.json
```

或：

```bash
scripts\publish.bat articles\2026-07-16.json
```

## 设置每天自动执行

先准备当天文章文件：`articles/today.json`

创建 15:00 定时任务示例：

```bash
scripts\setup_daily_task.bat 15:00
```

## 常见问题

1. `48001 api unauthorized`
   - 说明账号没有该接口权限，建议改为草稿模式：
   - 修改 `.env`：`PUBLISH_MODE=draft_only`

2. 封面报错
   - 确认 `assets/cover_default.jpg` 存在且可读取。

3. 定时任务不执行
   - 以管理员权限运行终端后重建任务。
