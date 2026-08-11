---
name: bilibili-feed
description: "Fetch Bilibili following feed, triggered when the user wants to check the latest updates on Bilibili."
metadata:
  hermes:
    tags: [bilibili, feed, social-media, content-analysis]
---

# Bilibili Feed 抓取与分析

从 Bilibili 关注流 feed 中抓取最近 N 天的视频数据，按作者分类归纳，并输出表格。

## 使用方式

方式一：用户输入 `/bilibili-feed` 时，执行以下流程。
方式二：用户想要了解今天所关注的up主有哪些更新时执行以下流程。
方式三：用户输入快捷命令「bilibili」或「B站」时，自动触发 bilibili-daily-feed 任务。

## 参数

- `$ARGUMENTS` — 天数，默认为 0（即今天的数据）。例如 `/bilibili-feed 1` 表示抓取最近 1 天的数据，也就是从昨天到今天。

## 当 opencli 不可用时的降级方案

先用 `which opencli` 检查是否安装。如果未安装，提示用户安装。

如果已安装但命令失败，根据错误类型输出对应的中文提示（纯中文，无英文管理说明）：

### BROWSER_CONNECT 错误（exit code 69）
这是最常见的失败场景，尤其在 cron job 或无桌面会话环境中。错误信息为 `Browser Bridge extension not connected`。

输出模板：
```
📊 无法获取今日 Bilibili 关注流数据

原因：浏览器扩展未连接，无法访问 Bilibili 数据源。

请检查以下事项：
1. 确保 Chrome 浏览器已打开并正在运行
2. 确认 OpenCLI 扩展已启用（在 Chrome 地址栏输入 chrome://extensions，开启开发者模式，加载扩展程序）

修复后，您可以通过「bilibili」或「B站」命令重新尝试获取关注流数据。
```

### 其他 opencli 错误
记录错误原文，用中文向用户说明抓取失败，建议检查网络连接和登录状态。

### opencli 未安装
```
📊 无法获取今日 Bilibili 关注流数据

原因：opencli 工具未安装。请运行 npm install -g @jackwener/opencli 安装后重试。
```

## 流程（opencli 可用时）

### 第一步：抓取数据
循环调用以下命令，逐页抓取直到时间字段不再包含目标天数范围内的时间：

```
opencli bilibili feed -f json --type video --pages <页码>
```

时间判断规则（**严格模式**）：
- "X分钟前"、"X小时前" = 今天 ✅
- "刚刚" = 今天 ✅
- "昨天 HH:MM" = 昨天 ❌ **必须排除**
- "N天前" = 必须排除（1天前=昨天，2天前=前天）
- "MM月DD日" = 必须与当前日期比较，不是今天则排除

**重要**：当参数为0（今天）时，必须严格过滤，只保留明确为今天的视频。宁可漏掉，不要误包含昨天的内容。

### 第二步：输出摘要

向用户展示：
1. 数据时间范围、总视频数、活跃作者数
2. **按发布时间从早到晚排序**（最早的在最前面，最新的在最后面），每条必须包含可点击的B站链接：
```
📊 今日概览：共 N 条视频，M 位活跃作者

- **作者A，1条**
1. 发布内容A [🔗](https://www.bilibili.com/video/BVxxxxxx)

- **作者B，1条**
1. 发布内容B [🔗](https://www.bilibili.com/video/BVxxxxxx)
```

**重要**：
- 输出时必须包含每条视频的URL字段，格式为 `[🔗](url)`，确保用户可以直接点击观看。如果某条视频没有url字段，跳过该条不展示。
- **按时间正序排列**（从早到晚），同一作者有多条视频时合并展示。
- cronjob输出时**不要包含任何英文提示语或管理说明**（如"To stop or manage this job..."），只输出中文摘要内容。

## 坑点

### 用户偏好
- 快捷命令：「bilibili」或「B站」→ 触发 bilibili-daily-feed 任务（job_id: c204eabefe25）
- **排序**：按发布时间从早到晚（最早的在前），不要按作者条数降序
- **语言**：纯中文输出，不要英文管理提示语
- **过滤**：严格模式，只保留今天（分钟前/小时前/刚刚），排除昨天和更早的

### Cronjob 配置要点
- schedule: `0 23 * * *`（每天23点）
- deliver: `weixin:o9cq802ldrKRkITfwjh0Xg1j-WXw@im.wechat`
- prompt 中必须强调「不要包含任何英文提示语或管理说明」

### opencli 环境要求
- 所有 `opencli bilibili` 命令都依赖 Chrome 浏览器扩展（Browser Bridge extension）
- 在 cron job 或无桌面会话环境中，Chrome 通常未运行，会触发 `BROWSER_CONNECT` 错误（exit code 69）
- 需要确保 Chrome 浏览器已打开且 OpenCLI 扩展已启用
- opencli 版本：当前 1.8.5，最新 1.8.6（可通过 `npm install -g @jackwener/opencli` 更新）

### Handle Failures（参考 jike-feed skill 的处理方式）
- 如果 opencli 报告 daemon、browser、Browser Bridge 或登录错误，简洁报告错误并保留建议的恢复命令
- 如果没有返回数据，说「没有检测到 Bilibili 动态。」
- 如果时间字段无法解析，保留该条并显示原始时间值