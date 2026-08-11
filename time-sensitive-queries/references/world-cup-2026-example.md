# Example: 2026 World Cup Schedule Query

## Session context (2026-06-13)
- Date: 2026-06-13 00:00 (midnight boundary)
- User asked: "查下今天足球世界杯比赛有谁" (check today's football World Cup matches)
- I searched for "今天" and got June 12 results (already outdated)
- User corrected: "时间不对吧，现在已经是13号零点了" (the time is wrong, it's already midnight on the 13th)

## Session context (2026-07-10)
- User asked: "帮我查询明天的世界杯赛程" (check tomorrow's World Cup schedule)
- I found matches via ESPN (US Eastern dates) and fifawatch.com/zh (Beijing dates)
- **Key pitfall**: ESPN listed "July 11: Norway vs England, 5 PM ET" but in Beijing time this is **July 12 at 5:00 AM**. The dates disagreed because ESPN uses US Eastern dates, not Beijing dates.
- **Resolution**: Used fifawatch.com/zh/schedule/ as primary source — it shows Beijing time AND correct Beijing dates.

## Correct approach
1. Search with explicit date: `\"6月13日\" 2026 世界杯 赛程`
2. Include year in query for annual events
3. Check multiple sources for consistency (CCTV, wc-2026.com, Wikipedia)
4. **Always convert BOTH time AND date** when using English-language sources
5. Prefer Chinese-language schedule sites for Beijing-timezone output

## Key sources for World Cup 2026
- **fifawatch.com/zh/schedule/** — BEST for Beijing timezone: shows Beijing time, correct dates, match stage, teams, venue. Single source of truth.
- CCTV World Cup site: worldcup.cctv.com/2026/
- Dedicated schedule site: wc-2026.com/schedule/
- Wikipedia: zh.wikipedia.org/zh-hans/2026年國際足協世界盃
- ESPN: espn.com/soccer/schedule/ (date dropdown shows only match days — missing dates = rest days)
- SI.com: si.com/soccer/ (best single source for knockout bracket: all matches, dates, venues, analysis)
- NBC Sports: nbcsports.com/soccer/ (comprehensive bracket articles with ET times)
- Yahoo Sports: sports.yahoo.com/soccer/article/... (lists US Eastern times clearly)
- Fox Sports: foxsports.com/stories/soccer/ (schedule articles)
- lineups.com: match previews with kickoff times
- Ticketmaster: confirms venues and dates for specific matches

## Proven search patterns (2026-06-13 session)
```
"Brazil vs Morocco June 13 2026 World Cup"  → Wikipedia C group page, ESPN live score
"June 13 2026 World Cup matches schedule"   → Yahoo Sports: "6 p.m. Brazil vs Morocco, 9 p.m. Haiti vs Scotland"
"Qatar June 13 2026 World Cup match"        → lineups.com: "Qatar vs Switzerland"
```
Three matches found for June 13: Qatar vs Switzerland (B), Brazil vs Morocco (C), Haiti vs Scotland (C).

## Proven search patterns (2026-07-08 session — quarterfinals)
```
"FIFA World Cup 2026 schedule July 9 2026"     → ESPN, NBC Sports, FIFA.com
"2026 World Cup quarterfinal July 9 schedule"  → SI.com (detailed all 4 QF matches)
"Argentina vs Switzerland quarterfinal 2026"   → confirmed July 11, 9 PM ET
```
SI.com was the best single source for knockout bracket — all 4 QF matches with dates, times, venues, and analysis in one article.

## Note on web_extract
- DuckDuckGo backend (default) cannot extract page content
- Fall back to web_search with specific queries when extraction fails
- Use search result snippets as primary data source

## Detecting rest days (no matches)
- **ESPN schedule page** (`espn.com/soccer/schedule/_/league/fifa.world`) has a date dropdown that only shows dates WITH matches
- If a date is missing from the dropdown (e.g., Jul 8 → Jul 10, skipping Jul 9), that date is a rest day
- Useful for confirming "明天没有比赛" without exhaustive searching

## Knockout-stage schedule patterns (2026)
- Round of 16: 2 matches/day for 6 days
- Quarterfinals: 1 match/day for 3 days, then 2 matches on day 4
- Semifinals: 1 match/day for 2 days
- Always verify against ESPN or official source; patterns can change

## ⚠️ Critical lesson: Cross-site timezone date-shift (2026-07-10)

**Problem**: ESPN showed "Saturday, July 11: Norway vs England, 5 PM ET" — but in Beijing time this is **July 12 at 5:00 AM**. Meanwhile fifawatch.com/zh/schedule/ showed the same match under "7月12日". The dates disagreed because ESPN uses US Eastern dates.

**Why this matters**: When the user asks "明天的比赛" (tomorrow's matches), using the US date directly gives the WRONG Beijing date. A match on "July 11" in the US is often "July 12" in Beijing.

**Lesson**: Always convert BOTH the time AND the date. The formula: Beijing date = US date + 1 if (US hour + 12) ≥ 24.

**Best practice**: Use fifawatch.com/zh/schedule/ as the primary source — it already shows Beijing time and correct Beijing dates, eliminating the conversion error entirely.
