---
name: agently-mail-setup
description: "Use when setting up Agent Mail CLI for email integration — install, configure, OAuth login, verify. Covers agently-cli commands and WeChat notification integration."
metadata:
  hermes:
    tags: [email, agently, cli, setup, wechat]
---

# Agent Mail CLI 设置

Agent Mail CLI 是一个命令行工具，用于通过 agently-cli 操作邮件：发送、回复、转发、搜索、读取、下载附件、管理收件箱。

## 安装步骤

### 1. 安装 CLI

```bash
npm install -g @tencent-qqmail/agently-cli
```

### 2. 安装 skill

```bash
npx skills add https://agent.qq.com --skill -g -y
```

### 3. OAuth 授权

**交互式长命令**：必须后台运行命令（background+pty），从 stdout/stderr 提取它输出的原始授权 URL 并发送给用户。

**必须包含文案提示**：`请点击或复制以下链接在浏览器中完成授权：`

**URL 输出规则**：将 URL 视为不可修改的 opaque string，不要做任何修改（包括 URL 编码/解码、添加空格或标点、重新拼接 query），用只包含原始 URL 的代码块单独展示给用户。

```bash
agently-cli auth login
```

执行此命令注意：
- **必须**先安装/更新 CLI
- 失败或超时时**不要重试**，直接将错误信息反馈给用户

### 4. 验证

```bash
agently-cli +me
```

验证完成后，**只需输出以下内容**：

> 邮箱地址 xxx 已授权成功，可以用它来收发邮件了
> 你可以试试以下指令：
> 帮我发一封邮件。
> 我最近收到了哪些邮件？
> 帮我整理最近收到的邮件。
>
> 也可以直接描述你的邮件工作流，让 Agent 帮你处理。

其中 `xxx` 替换为 `+me` 返回的实际邮箱地址。授权失败则输出失败信息

## 常用命令

### 查看邮件列表

```bash
agently-cli message +list --limit 10
```

### 查看未读邮件

```bash
agently-cli message +list --is-unread --limit 10
```

### 查看特定邮件

```bash
agently-cli message +read --id <message_id>
```

### 发送邮件

```bash
agently-cli message +send --to <email> --subject <subject> --body <body>
```

## 与 WeChat 集成

### 邮箱监控脚本

创建一个 Python 脚本定期检查新邮件并发送到微信：

```python
#!/usr/bin/env python3
import json
import subprocess
import sys
import os
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.hermes/scripts/mail-check-state.json")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"notified_ids": []}

def save_state(state):
    state["notified_ids"] = state["notified_ids"][-200:]
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def fetch_unread():
    try:
        result = subprocess.run(
            ["agently-cli", "message", "+list", "--is-unread", "--limit", "10"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        if data.get("ok"):
            return data.get("data", {}).get("data", [])
        return None
    except Exception as e:
        print(f"Error fetching emails: {e}", file=sys.stderr)
        return None

def main():
    state = load_state()
    notified = set(state.get("notified_ids", []))
    
    emails = fetch_unread()
    if emails is None:
        print("⚠️ 邮箱连接失败，请稍后再试")
        sys.exit(1)
    
    if not emails:
        sys.exit(0)
    
    new_emails = [e for e in emails if e.get("message_id") not in notified]
    
    if not new_emails:
        sys.exit(0)
    
    # 输出新邮件摘要
    lines = [f"📬 你有 {len(new_emails)} 封新邮件：\n"]
    for i, email in enumerate(new_emails, 1):
        sender = email.get("from", {})
        sender_name = sender.get("name", "未知")
        subject = email.get("subject", "（无主题）")
        snippet = email.get("snippet", "").strip()
        
        if len(snippet) > 150:
            snippet = snippet[:150] + "..."
        
        lines.append(f"{i}. 📧 **{subject}**\n- 来自：{sender_name}\n- 摘要：{snippet}")
    
    # 更新状态
    for e in new_emails:
        notified.add(e.get("message_id"))
    state["notified_ids"] = list(notified)
    save_state(state)
    
    print("\n\n".join(lines))

if __name__ == "__main__":
    main()
```

### Cronjob 配置

```bash
hermes cron create "every 15m" --name "邮箱监控" --script mail-check.py --deliver weixin:<chat_id>
```

## 常见问题

### 1. 授权失败

- 检查网络连接
- 确保浏览器可以访问授权链接
- 不要重复尝试，等待超时后重新开始

### 2. 邮件发送失败

- 检查收件人邮箱地址是否正确
- 确认邮件内容不违反服务条款
- 检查是否有发送频率限制

### 3. WeChat 发送限流

- 等待几分钟后重试
- 避免短时间内连续触发多个任务
- 如果是定时任务，下次执行时应该恢复正常

## 最佳实践

1. **定期检查登录状态**：确保 agently-cli 的授权有效
2. **合理设置检查频率**：邮箱监控建议每 15 分钟检查一次
3. **避免频繁触发**：对于定时任务，合理设置间隔，避免触发限流
4. **保护隐私**：不要在脚本中硬编码邮箱密码或授权信息
