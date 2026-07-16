# 全自动每日流程（无需每天跟我说）

## 你只需要做一次配置

在 `.env` 里补上 **LLM_API_KEY**（用于自动生成分析）：

```env
LLM_API_KEY=你的密钥
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

也可用兼容接口，例如 DeepSeek：
```env
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

PushPlus token 你已配置，无需再改。

---

## 每天自动发生什么（无需开 Cursor）

定时任务 `SoccerBallDailyRun` 执行 `full_auto.bat`：

1. **自动生成** `articles/today.json` + `outputs/today_plan.json`
2. **推送公众号草稿**
3. **微信 PushPlus 推送方案**
4. **归档**到 `records/` 供次日复盘

你关掉 Cursor 也没关系，只要 **电脑在设定时间开机**。

---

## 重新设置定时任务（建议 14:30）

```bash
cd D:\Personal\soccerBall
scripts\setup_daily_task.bat 14:30
```

手动测试全流程：

```bash
scripts\full_auto.bat
```

---

## 你还需要手动做的（仅 1 步）

公众号后台 **草稿箱 → 预览 → 发布**（个人号无法 API 自动发布）。

---

## 注意

| 条件 | 说明 |
|------|------|
| 电脑开机 | 睡眠/关机则任务不跑 |
| LLM_API_KEY | 未填则无法自动生成 |
| 网络 | 需访问竞彩数据源 + LLM API |
| IP 白名单 | 微信接口变更时需更新 |

---

## 可选：不想用 API 密钥

可用 **Cursor 自动化**（云端定时生成文件），但微信推送仍要本机 15:00 执行。  
需要的话跟我说「配 Cursor 自动化」。
