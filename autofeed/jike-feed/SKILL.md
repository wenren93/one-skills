---
name: jike-feed
description: Fetch and summarize the latest Jike/即刻 home feed snapshot with `opencli jike feed`. Use when the user asks to刷下即刻、看下即刻、查看即刻首页动态、拉取即刻 feed、or wants the latest Jike updates sorted by time with post links and publish time.
---

# Jike Daily Feed

Use the bundled script to fetch the latest Jike home feed snapshot, deduplicate posts, sort by time (newest first), and render a Markdown table.

## Run

Resolve the script relative to this skill directory:

```bash
python3 scripts/jike_daily_feed.py --limit N
```

- Use `--limit 30` when the user does not specify a count, and state that default briefly.
- Increase `--limit` when the user asks for broader coverage; `opencli jike feed` has no page option and returns a scrolled snapshot up to the requested limit.
- Prerequisites: Chrome must be running, logged into `web.okjike.com`, and Browser Bridge must be available.

## Present

Return the script's Markdown directly:

```markdown
| 作者 | 内容 | 时间 |
|---|---|---|
| 示例用户 | 动态内容，<https://web.okjike.com/originalPost/...> | 21:43 |
```

One row per post, sorted by time (newest first). Do not invent context beyond the post text returned by OpenCLI.

## Handle Failures

- If OpenCLI reports a daemon, browser, Browser Bridge, or login error, report the error concisely and preserve its suggested recovery command when present.
- If a row has an unparseable `time`, keep the post and display the raw time value when present.
- If no rows are returned, say `没有检测到即刻动态。`
- Mention that results are limited by the requested `--limit` snapshot; do not claim the feed is complete beyond that.
