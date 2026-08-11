---
name: weather
description: "Get weather forecasts and current conditions reliably via CLI — wttr.in API, structured JSON, multi-day forecasts, and timezone-aware lookups."
category: productivity
triggers:
  - User asks about weather (rain, temperature, forecast) for any location
  - User asks "会下雨吗" / "明天天气" / "what's the weather"
  - Any query needing real-time or forecast weather data
---

# Weather Queries

## Core Approach

Use `curl https://wttr.in/` — a free, no-auth weather API that returns structured data. This is the primary method because `web_extract` consistently fails on weather sites (DuckDuckGo backend cannot extract them).

## Quick Commands

### Current conditions (one-liner)
```bash
curl -s "https://wttr.in/Beijing?format=%c+%t+%h+%w+%p&lang=zh"
```
Output: `✨  +24°C 61% ↙16km/h 0.0mm` (emoji + temp + humidity + wind + precip)

### Multi-day visual forecast
```bash
curl -s "https://wttr.in/Beijing?lang=zh&format=v2"
```
Returns an ASCII-art chart with 3-day forecast, temperature curves, precipitation bars, and hourly weather icons.

### Structured JSON (for programmatic parsing)
```bash
curl -s "https://wttr.in/Beijing?format=j1"
```
Returns full JSON with `weather[]` array (3 days), each containing:
- `date`, `maxtempC`, `mintempC`
- `hourly[]` with: `time`, `tempC`, `weatherDesc`, `chanceofrain`, `humidity`, `windspeedKmph`

Parse with python/jq to extract specific day forecasts.

## Workflow

1. **Identify location** — city name in English or Chinese pinyin (e.g., `Beijing`, `Shanghai`, `Guangzhou`)
2. **Determine query type**:
   - Quick check → use format string (`%c+%t+%h+%w+%p`)
   - Visual overview → use `format=v2`
   - Detailed/programmatic → use `format=j1` + parse
3. **Handle ambiguity** — if user says "朝阳" (could be Beijing Chaoyang or Liaoning Chaoyang), clarify or default to the more common one
4. **Present clearly** — use a simple table for forecast, mention rain probability prominently if user asked about rain

## Pitfalls

### 1. web_extract fails on weather sites
- **Problem**: DuckDuckGo backend cannot extract content from weather.com.cn, qweather.com, etc.
- **Fix**: Always use `curl https://wttr.in/` instead. Do not attempt web_extract on weather URLs.

### 2. Chinese city names
- **Problem**: wttr.in expects English or pinyin names.
- **Fix**: Use `Beijing` not `北京`, `Shanghai` not `上海`. For districts like `朝阳区`, use `Chaoyang+Beijing`.

### 3. Tomorrow vs today at midnight
- **Problem**: At 00:00, "明天" means the next calendar day, not "later today."
- **Fix**: Check current date from system context header. Index into `weather[]` array: `[0]` = today, `[1]` = tomorrow, `[2]` = day after.

### 4. Rate limiting
- **Problem**: wttr.in may rate-limit frequent requests.
- **Fix**: Cache results within a session. One request per city per conversation is usually sufficient.

## Example Output Template

```
## 🌤️ {City}天气 - {Date}

| 项目 | 详情 |
|---|---|
| 🌡️ 温度 | {min}°C ~ {max}°C |
| 🌧️ 降水 | {amount}，概率 {percent}% |
| 💨 风向 | {direction} |

**时段预报**:
- 上午: {condition}
- 下午: {condition}
- 晚上: {condition}
```

## Related Skills

- `time-sensitive-queries` — weather forecasts are time-sensitive; use explicit dates, not "今天"
