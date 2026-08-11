---
name: opencli-troubleshooting
description: "Use when opencli commands fail — CSS selector errors, empty results, login issues, or cronjob model drift. Covers Bilibili, Jike, and other opencli site adapters."
metadata:
  hermes:
    tags: [opencli, troubleshooting, bilibili, jike, cronjob]
---

# opencli 故障排查

opencli 是一个 CLI 工具，用于从各种网站（Bilibili、Jike 等）抓取数据。当网站改版或环境变化时，可能会出现故障。

## 常见故障及解决方案

### 1. CSS 选择器失效

**症状**：`opencli <site> feed` 返回空数组或报错 `Selector not found`

**原因**：网站改版导致 CSS 选择器失效

**解决方案**：
1. 更新 opencli：`npm install -g @jackwener/opencli`
2. 检查登录状态：`opencli auth status --site <site> --full`
3. 尝试前台模式：`opencli <site> feed -f json --window foreground`
4. 如果仍然失败，检查 Chrome 是否已登录对应网站

**已知问题**：
- Jike (即刻)：选择器 `[class*="_post_"]` 可能失效
- Bilibili：选择器可能因网站改版而变化

### 2. 登录状态丢失

**症状**：`opencli auth status --site <site> --full` 显示 `not_logged_in`

**解决方案**：
1. 打开 Chrome 并登录对应网站
2. 使用 `--site-session persistent` 保持登录状态
3. 重新运行 opencli 命令

### 3. Cronjob 模型漂移错误

**症状**：cronjob 报错 `Skipped to prevent unintended spend: global inference config drifted`

**原因**：模型版本变化（如 mimo-v2.5 → mimo-v2.5-pro），系统为防止意外消耗而暂停任务

**解决方案**：
```bash
hermes cron edit <job_id>
```
或通过 cronjob 工具：
```
cronjob action=update job_id=<id> model={"model": "mimo-v2.5-pro", "provider": "custom:xiaomi"}
```

### 4. WeChat 发送限流

**症状**：cronjob 报错 `Weixin send failed: iLink sendmessage rate limited`

**原因**：短时间内连续触发多个任务导致微信接口限流

**解决方案**：
1. 等待几分钟后重试
2. 避免短时间内连续触发多个任务
3. 如果是定时任务，下次执行时应该恢复正常

## 最佳实践

1. **定期更新 opencli**：网站改版频繁，保持 opencli 更新可以避免很多问题
2. **使用持久化会话**：对于需要登录的网站，使用 `--site-session persistent`
3. **检查登录状态**：定期运行 `opencli auth status` 确保登录状态有效
4. **避免频繁触发**：对于定时任务，合理设置间隔，避免触发限流
