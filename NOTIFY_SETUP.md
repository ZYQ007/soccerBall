# 每日自动推送说明

## 你能收到什么（不用开 Cursor）

每天 **15:00**（电脑需开机）自动执行：

1. 推送公众号草稿（`articles/today.json`）
2. **微信推送今日实战方案**（`outputs/today_plan.md`）→ 通过 PushPlus 发到手机
3. Windows 电脑右下角弹窗提醒

## 第一步：配置 PushPlus（5 分钟）

1. 打开 [https://www.pushplus.plus](https://www.pushplus.plus)
2. 微信扫码登录
3. 复制你的 **token**
4. 填入 `D:\Personal\soccerBall\.env`：
   ```env
   PUSHPLUS_TOKEN=你的token
   ```

完成后，方案会直接推到你微信，无需打开 Cursor。

## 第二步：确认定时任务

已创建任务：`SoccerBallDailyRun`，每天 15:00 执行。

手动测试一次：
```bash
cd D:\Personal\soccerBall
scripts\daily_run.bat
```

## 每天两个文件

| 文件 | 用途 | 谁生成 |
|------|------|--------|
| `articles/today.json` | 公众号文章（场次分析） | 我帮你生成 |
| `outputs/today_plan.json` | 微信推送方案（结构化，Markdown 排版） | 我帮你生成 |
| `outputs/today_plan.md` | 方案备份（可选） | 我帮你生成 |

你说「今天的方案」，我会同时更新 `today.json` 和 `today_plan.json`。

## 完全不用找我的方式（可选升级）

若希望连消息都不用发，可再配 **Cursor 自动化**：
- 每天 14:00 云端自动生成两个文件
- 15:00 本机定时任务推送

需要时跟我说「配自动化」，我帮你开。

## 注意

- 电脑 15:00 需开机（睡眠/关机则任务不跑）
- 未配置 `PUSHPLUS_TOKEN` 时只有电脑弹窗，没有微信推送
