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
友好提示不可用原因

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
2. **按发布时间从新到旧排序**（最新的在最前面），每条必须包含可点击的B站链接：
```
📊 今日概览：共 N 条视频，M 位活跃作者

- **作者A，1条**
1. 发布内容A [🔗](https://www.bilibili.com/video/BVxxxxxx)

- **作者B，1条**
1. 发布内容B [🔗](https://www.bilibili.com/video/BVxxxxxx)
```

**重要**：
- 输出时必须包含每条视频的URL字段，格式为 `[🔗](url)`，确保用户可以直接点击观看。如果某条视频没有url字段，跳过该条不展示。
- **按时间倒序排列**，同一作者有多条视频时合并展示。
- cronjob输出时**不要包含任何英文提示语或管理说明**（如"To stop or manage this job..."），只输出中文摘要内容。

## 坑点

### 用户偏好
- 快捷命令：「bilibili」或「B站」→ 触发 bilibili-daily-feed 任务（job_id: c204eabefe25）
- **排序**：按发布时间从新到旧，不要按作者条数降序
- **语言**：纯中文输出，不要英文管理提示语
- **过滤**：严格模式，只保留今天（分钟前/小时前/刚刚），排除昨天和更早的

### Cronjob 配置要点
- schedule: `0 23 * * *`（每天23点）
- deliver: `weixin:o9cq802ldrKRkITfwjh0Xg1j-WXw@im.wechat`
- prompt 中必须强调「不要包含任何英文提示语或管理说明」