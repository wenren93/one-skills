---
name: time-sensitive-queries
description: Handling queries where date/time precision matters — sports schedules, event listings, "today" near midnight, timezone-aware lookups
category: general
triggers:
  - User asks about "today's" events near midnight or day boundaries
  - User asks about live sports schedules, match results, event times
  - Any query where the answer depends on which calendar day "today" refers to
---

# Time-Sensitive Queries

## Core Principle
When a user asks "今天" (today) or "today's" near midnight (±2 hours of 00:00), the date may have already changed or be about to change. **Always check the current date first** and clarify if ambiguous.

## Pitfalls

### 1. Date boundary confusion
- **Problem**: At 00:00 on June 13, a user asking "today's matches" means June 13, not June 12.
- **Fix**: Before searching, note the current date from the system context. If the conversation started before midnight but the question is asked after, the user likely means the new day.
- **User correction signal**: "时间不对吧，现在已经是13号零点了" — user explicitly corrected this.

### 2. Never assume the time of day
- **Problem**: Stating "现在已经是晚上7点半了" when the actual time is 9:24am. Fabricating or guessing the current time causes confusion and erodes trust.
- **Fix**: **Always run `date` via terminal** before stating or implying the current time. Never estimate, guess, or hallucinate the time of day. The system context header shows conversation start date but NOT the current clock time — you must check.
- **User correction signal**: "那你这个时间哪里的" — user questioned the fabricated time.

### 3. Sports schedule specificity
- **Problem**: Generic searches like "today's World Cup matches" may return yesterday's results or preview articles.
- **Fix**: Search with the **exact date** in the query: `"6月13日" 世界杯 赛程` rather than "今天世界杯比赛". Include year for annual events.

### 3. Over-relying on "today" in search queries
- **Problem**: Search engines may not interpret "today" correctly, especially for events in different timezones.
- **Fix**: Always use explicit dates (YYYY-MM-DD or "M月D日") in search queries for event schedules.

## Workflow

1. **Determine current date and time** — the system context header shows conversation start date but NOT the current clock time. **Always run `date` via terminal** to get the exact current date and time before making any time-related statements or calculations.
2. **Clarify if near midnight** — if user asks "today" and it's 23:00-01:00, confirm which day they mean OR use the most recent calendar date.
3. **Search with explicit dates** — never rely on "今天" in search queries.
4. **Cross-reference multiple sources** — sports schedules benefit from checking 2-3 search results for consistency.
5. **Show timezone context** — when listing match times, always specify "北京时间" or relevant timezone.
6. **Use browser_console for structured extraction** — when a long sports article is truncated in the snapshot, use `browser_console` with JS queries (e.g., `querySelectorAll('h3')` to get match headings + sibling list items) instead of scrolling through pages of truncated content.

## Search Patterns for Sports & Esports Schedules

Good queries:
- `"6月13日" 2026 世界杯 赛程 比赛`
- `FIFA World Cup June 13 2026 schedule`
- `世界杯 6月13日 北京时间 对阵`
- `BLG vs WE 6月13日 时间 几点` (esports with team names + date)
- `"2026 LPL" 败者组决赛 6月13日 时间`

Bad queries:
- `今天足球世界杯比赛有谁` (ambiguous date)
- `今天的比赛` (too generic)
- `LPL比赛` (no date, returns stale results)

### Reliable sources for World Cup / FIFA schedules
- **fifawatch.com/zh/schedule/** — Chinese version displays all times in Beijing time, grouped by date. Best single source for a Beijing-timezone user. Shows match stage, teams, venue, and date in one view.
- **ESPN (espn.com/soccer/story/...)** — comprehensive but times in US Eastern; must convert.
- **FIFA.com official schedule** — authoritative but may require browser extraction.
- Search snippets from these sites often contain enough info (date + time + teams + venue) without needing to load the full page.

### Esports schedules (LPL, LCK, etc.)
- Include team names + exact date for precision
- Search result snippets from zhibo8.com, weibo, huya are reliable for match times
- Official LPL site (lplgw.org.cn) may show stale data; prefer search snippets
- Browser tools may timeout on Chinese sports sites — rely on web_search snippets instead

### Timezone conversion for international events
- Beijing (CST) = UTC+8, always
- US Eastern (EDT in summer) = UTC-4 → **+12 hours** to Beijing
- US Eastern (EST in winter) = UTC-5 → **+13 hours** to Beijing
- Convert and always label "北京时间" in output

### ⚠️ Cross-site timezone / date-shift confusion (critical pitfall)
**Problem**: Different schedule sites display times AND dates in their own timezone. A match listed as "July 11" on ESPN (US Eastern) may actually be "July 12" in Beijing time. The DATE LABEL on each site corresponds to the site's display timezone, not the user's timezone.

**This session's example**: ESPN showed "Saturday, July 11: Norway vs England, 5 PM ET" — but in Beijing time this is **July 12 at 5:00 AM** (5 PM EDT + 12h = 5 AM next day). Meanwhile, fifawatch.com/zh showed the same match under "7月12日" (Beijing date). The date shifted by +1 because the US evening kickoff crosses midnight in Beijing.

**Fix**:
1. Always convert to Beijing time AND Beijing date before reporting.
2. Formula: if ET hour + 12 ≥ 24, the Beijing date = ET date + 1.
3. Prefer Chinese-language schedule sites (e.g. fifawatch.com/zh/schedule/) that already display Beijing time with correct date grouping — these are the single source of truth for the output.
4. When using English-language sources (ESPN, FIFA.com), always mentally convert the date, not just the time.

**Quick reference for US → Beijing date shift**:
- US afternoon matches (12 PM–7 PM ET) → Beijing **early morning next day** (date +1)
- US evening matches (8 PM–11 PM ET) → Beijing **morning next day** (date +1)
- US late-night matches (12 AM–6 AM ET) → Beijing **same day** afternoon/evening

## Related Skills

- `weather` — weather forecasts are time-sensitive; use explicit dates, not "今天"
