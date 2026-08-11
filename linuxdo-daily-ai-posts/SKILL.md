---
name: linuxdo-daily-ai-posts
description: 通过真实浏览器访问 Linux.do 分类页，查找活动日期为今天且与 AI 相关的帖子，并输出标题、链接和活动时间。用于用户要求浏览、筛选或汇总 Linux.do 今日 AI、人工智能、AIGC、GPT、Agent、Codex、大模型等相关资源帖时；默认分类为“网盘资源” https://linux.do/c/resource/cloud-asset/94，也支持用户指定其他 Linux.do 分类链接。
---

# Linux.do 今日 AI 帖子

使用 `ego-browser` 在浏览器登录态中读取页面及其分类分页。不要用普通 HTTP 抓取、搜索引擎结果或仅凭首屏作答。

## 工作流

1. 读取并遵循 `ego-browser` Skill。创建或复用与当前目标对应的 task space。
2. 打开用户指定的 Linux.do 分类页；未指定时使用 `https://linux.do/c/resource/cloud-asset/94`。
3. 先观察页面，确认分类加载成功。若需要登录、验证码或用户接管，严格按 `ego-browser` 的 handoff 流程处理。
4. 在同一浏览器上下文中用 `browserFetch` 读取分类的 `/l/latest.json?page=N` 分页。**注意：`browserFetch` 返回的是 JSON 字符串（不是已解析对象），必须先 `JSON.parse(resp)` 再访问 `resp.topic_list.topics`。** 保留浏览器会话，不要改用 `curl`。
5. 按帖子 ID 去重，跳过置顶帖。将 `bumped_at` 转为用户时区的本地日期；默认使用 `Asia/Shanghai`。
6. 逐页读取并处理完整页，直到至少读取到一个所有非置顶帖子都早于今天的分页。不要因首页的旧置顶帖停止，也不要在混合了今天和昨天帖子的分页中提前停止。最多读取 20 页，超限时在结果中说明。
7. 保留活动日期恰好为今天且满足以下任一条件的帖子：
   - 标签包含“人工智能”或“AIGC”；
   - 标题明确包含 AI、人工智能、AIGC、大模型、LLM、GPT、Agent、Codex、Claude、Gemini、DeepSeek、提示词等 AI 关键词。
8. 按 `bumped_at` 从新到旧排序，输出编号列表：可点击标题、帖子链接和本地活动时间。
9. 若仅因网站的“人工智能/AIGC”标签入选而标题本身看不出 AI 关系，单独注明，避免把网站标签判断伪装成内容判断。
10. 完成后在独立的最终浏览器命令中调用 `completeTaskSpace(..., { keep: false })`；只有用户明确要求保留页面时才使用 `keep: true`。

## 浏览器内分页要点

从分类 URL 构造 JSON 地址。例如默认分类使用：

```text
https://linux.do/c/resource/cloud-asset/94/l/latest.json?page=0
https://linux.do/c/resource/cloud-asset/94/l/latest.json?page=1
```

分类路径不固定时，删除末尾斜杠，再追加 `/l/latest.json?page=N`。每页读取 `topic_list.topics` 的 `id`、`title`、`bumped_at`、`tags` 和 `pinned`。帖子链接统一输出为：

```text
https://linux.do/t/topic/{id}
```

日期判断必须比较完整的本地日历日期，不能用“24 小时以内”代替“今天”。

### 已知坑（必须规避）

- **`tags` 是对象数组**，形如 `[{ id, name, slug }]`，不是字符串数组。做标签匹配时必须取 `tag.name`；直接 `String(tag)` 会得到 `[object Object]`，导致“仅靠标签命中”的帖子被全部漏掉。

  ```js
  const tagNames = tags => (tags || []).map(t => (t && typeof t === 'object') ? (t.name || t.slug || '') : String(t)).filter(Boolean)
  ```

- **heredoc 内禁止 `require()`**：与 top-level `await` 冲突，会报 “Cannot determine intended module format”。需要写文件时用 `const fs = await import('node:fs')`。
- **heredoc 内禁止 JS 模板字符串的 `${...}`**：即使用 `<<'EOF'` 引号定界，执行环境仍可能先做一层 shell 解析，遇到 `${h.tags.join(',')}` 这类含点号/括号的表达式会直接报 `Bad substitution`，脚本根本不会运行。一律改成字符串拼接：

  ```js
  // ✗ console.log(`page ${p}: ${t.title}`)
  // ✓
  console.log('page ' + p + ': ' + t.title)
  ```

- **不要 `console.log` 全量帖子 JSON**：单页 100 条、多页累计后输出常超 40KB 被截断。应在脚本内完成日期过滤与 AI 筛选，只输出精简结果（或写本地 JSON 文件再读）。
- 匹配英文关键词 `AI` 时用词边界正则 `/(^|[^A-Za-z])AI([^A-Za-z]|$)/`，避免 `SAID`、`MAIN`、`TRAINING` 之类误命中。

## 输出要求

- 先说明筛选日期、时区和结果数量。
- 每项只保留标题、链接和活动时间；除非用户要求，不展开帖子正文。
- 明确说明筛选口径是“活动日期”，不是“发帖日期”。
- 没有结果时直接说明未找到，并报告已读取到跨过今天边界的分页。
