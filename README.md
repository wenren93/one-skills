# one-skills

个人专用的 Claude Code Skills 仓库，包含自定义的自动化工作流技能。

## 目录结构

```
one-skills/
└── autofeed/                    # 社交媒体 Feed 抓取技能集
    ├── bilibili-feed/           # B站关注动态
    │   └── SKILL.md
    └── jike-feed/               # 即刻首页动态
        ├── SKILL.md
        └── scripts/
            └── jike_daily_feed.py
```

## 技能列表

### autofeed

#### bilibili-feed

抓取 Bilibili 关注流中最近 N 天的视频更新，按发布时间从新到旧排序，输出带可点击链接的摘要列表。

- 触发方式：`/bilibili-feed`、快捷命令「bilibili」或「B站」
- 参数：天数（默认 0，即今天）
- 输出格式：按时间倒序，同一作者多条视频合并展示
- Cronjob：每天 23 点自动执行，推送至微信
- 依赖：`opencli` CLI 工具

#### jike-feed

抓取即刻首页动态，按时间倒序排列，输出列表格式摘要。

- 触发方式：`/jike-feed`、快捷命令「jike」或「即刻」
- 参数：条数限制（默认 20）
- 输出格式：列表格式，每条带超链接
- Cronjob：每天 10 点自动执行，推送至微信
- 依赖：`opencli` CLI 工具、Chrome 浏览器（需登录 web.okjike.com）、Browser Bridge

## 使用方式

将本仓库路径添加到 Claude Code 的 skills 搜索路径中，即可通过斜杠命令或自然语言触发对应技能。
