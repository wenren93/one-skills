---
name: social-feeds
description: "Fetch and summarize social media feeds: Bilibili following feed, Jike/即刻 home feed. Use when the user wants to check updates from Chinese social platforms."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bilibili, jike, feed, social-media, content-analysis, chinese]
    category: autofeed
---

# Social Feeds

Fetch and summarize feeds from Chinese social media platforms. All feeds use `opencli` which requires Chrome with Browser Bridge extension.

## Prerequisites

- `opencli` installed: `npm install -g @jackwener/opencli`
- Chrome browser running with OpenCLI Browser Bridge extension enabled
- Logged into the respective platform in Chrome

## Bilibili Feed

Fetch Bilibili following feed — videos from creators you follow.

### Trigger
User says "bilibili", "B站", "看下B站", "刷下B站", or `/bilibili-feed [days]`.

### Parameters
- `$ARGUMENTS` — days to fetch (default: 0 = today only). `/bilibili-feed 1` = yesterday to today.

### Flow
1. Fetch data: `opencli bilibili feed -f json --type video --pages <page>`
2. Loop until time field falls outside target range
3. Strict time filtering (today only when days=0): "X分钟前", "X小时前", "刚刚" = today ✅; "昨天", "N天前" = exclude ❌
4. Output sorted by publish time (earliest first), grouped by author, with clickable links

### Output Format (Chinese)
```
📊 今日概览：共 N 条视频，M 位活跃作者

- **作者A，1条**
1. 发布内容A [🔗](https://www.bilibili.com/video/BVxxxxxx)
```

### Cronjob Config
- Schedule: `0 23 * * *` (daily at 23:00)
- Pure Chinese output, no English management notes

## Jike Feed (即刻)

Fetch Jike home feed — posts from people you follow.

### Trigger
User says "jike", "即刻", "刷下即刻", "看下即刻", or `/jike-feed [limit]`.

### Parameters
- `--limit` — max posts to fetch (default: 20)

### Flow
1. Run: `python3 scripts/jike_daily_feed.py --limit 20`
2. Output sorted by time (newest first), with clickable links

### Output Format (Chinese)
```
☀️ 即刻早报 · {日期}

1. {作者} · {时间}
- {内容摘要} [🔗]({链接})
```

### Cronjob Config
- Schedule: `0 10 * * *` (daily at 10:00)
- Pure Chinese output, no English management notes

## Common Pitfalls

- **BROWSER_CONNECT error (exit code 69)**: Chrome not running or Browser Bridge extension not enabled. User must open Chrome and enable the extension.
- **No data returned**: Check login status on the platform.
- **Time filtering**: Be strict — better to miss one post than include yesterday's content.
- **Output language**: Always pure Chinese, never include English management notes in cronjob output.

## Scripts

- `scripts/jike_daily_feed.py` — Jike feed fetcher with deduplication
