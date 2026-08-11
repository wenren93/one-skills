# Esports Schedule Sources

## LPL (英雄联盟职业联赛)
- **Official site**: lplgw.org.cn — may show stale/demo data; not always reliable for live schedules
- **Best search snippets**: zhibo8.com (直播吧), weibo team accounts, huya.com
- **Pattern**: Search `"BLG vs WE 6月13日 时间 几点"` → snippets usually include exact kickoff time
- **Event context (2026)**: LPL has 3 stages per year; finals are offline events in major cities

## Key lesson from 2026-06-13 session
- Official LPL site showed 2024 demo data, not real 2026 schedule
- Weibo team account (BLG) posted exact time: "2026年6月13日16:00 BLG vs WE"
- Cross-reference with 2+ sources before confirming match times

## General esports search tips
- Include team names + exact date in query
- Chinese esports sites often timeout in browser — use web_search snippets
- Convert times to 北京时间 for the user

## World Cup / FIFA schedule sources (2026)
- **ESPN** (`espn.com/soccer/story/...`): reliable for match schedule, includes group info and kickoff times
- **Yahoo Sports** (`sports.yahoo.com/soccer/article/...`): lists matches with US Eastern times
- **Fox Sports** (`foxsports.com/stories/soccer/...`): schedule articles with dates
- **FIFA.com** (`fifa.com/en/tournaments/.../scores-fixtures`): official but dynamic, hard to scrape
- **Wikipedia**: good for group composition and match dates
- **Ticketmaster**: confirms exact match dates and venues
- **lineups.com**: match previews with date/time
- Browser tools often timeout on sports sites — prefer web_search snippets
- Always convert US Eastern (EDT, UTC-4 in June) to 北京时间 (UTC+8) = +12 hours

## Proven search patterns (2026-06-13 session)
```
# LPL
"BLG vs WE 6月13日 时间 几点"     → zhibo8.com snippet: "2026年6月13日16:00"
"2026 LPL 第二赛段 败者组决赛 6月13日 时间"  → multiple sources

# World Cup
"Brazil vs Morocco June 13 2026 World Cup"  → Wikipedia, ESPN, ticket sites
"June 13 2026 World Cup matches schedule"   → Yahoo Sports with exact times
"Qatar June 13 2026 World Cup match"        → lineups.com, foxsports.com
```
