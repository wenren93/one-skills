---
name: jike-feed
description: "Fetch and summarize the latest Jike/即刻 home feed snapshot with `opencli jike feed`. Use when the user asks to刷下即刻、看下即刻、查看即刻首页动态、拉取即刻 feed、or wants the latest Jike updates sorted by time with post links and publish time."
---

# Jike Daily Feed

Use the bundled script to fetch the latest Jike home feed snapshot, deduplicate posts, sort by time (newest first), and render output.

## 使用方式

方式一：用户输入「即刻」或「jike」时，自动触发即刻每日早报任务。
方式二：用户说「刷下即刻」「看下即刻」时执行此流程。

## Run

Resolve the script relative to this skill directory:

```bash
python3 scripts/jike_daily_feed.py --limit 20
```

- 默认 `--limit 20`（用户觉得50条太多）
- Prerequisites: Chrome must be running, logged into `web.okjike.com`, and Browser Bridge must be available.

## Present

用户偏好格式（**不要用表格，用列表格式**）：

```
☀️ 即刻早报 · {日期}

1. {作者} · {时间}
- {内容摘要} [🔗]({链接})

2. {作者} · {时间}
- {内容摘要} [🔗]({链接})
```

- 按时间从新到旧排序
- 内容摘要保留核心信息，不要太长
- 每条必须有超链接
- 最后一行：「共获取到 X 条动态，祝你今天愉快！🎉」
- **不要包含任何英文提示语或管理说明**

## 用户偏好

- 快捷命令：「jike」或「即刻」→ 触发即刻每日早报任务（job_id: f99889bc3b69）
- **条数限制**：默认 20 条（--limit 20），用户觉得 50 条太多
- **格式**：列表格式，不要表格
- **语言**：纯中文输出，不要英文管理提示语
- **排序**：按时间从新到旧

## Cronjob 配置要点

- schedule: `0 10 * * *`（每天10点）
- deliver: `weixin:o9cq802ldrKRkITfwjh0Xg1j-WXw@im.wechat`
- script path: `/Users/one/.hermes/skills/autofeed/jike-feed/scripts/jike_daily_feed.py`
- prompt 中必须包含格式示例，否则输出可能不符合预期

## Handle Failures

- If OpenCLI reports a daemon, browser, Browser Bridge, or login error, report the error concisely and preserve its suggested recovery command when present.
- If a row has an unparseable `time`, keep the post and display the raw time value when present.
- If no rows are returned, say `没有检测到即刻动态。`
- Mention that results are limited by the requested `--limit` snapshot; do not claim the feed is complete beyond that.