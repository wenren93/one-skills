---
name: buddy-checkin
description: WorkBuddy 每日签到自动领取免费 Credits。当用户说"签到"、"领取积分"、"领取额度"、"领 credits"、"checkin"、"加油站"时触发。也适用于设置每日自动签到的定时任务或自动化。支持 macOS 和 Windows。
---

# Buddy 每日签到

自动领取 WorkBuddy（Buddy 加油站）的每日免费 Credits。脚本以 API 返回为准，不信任本地日志，确保每次执行都有真实验证。支持 macOS 和 Windows 双平台。

## 快速使用

用户说"帮我签到"或"领取积分"时，立即执行签到脚本：

```bash
python3 ~/.workbuddy/scripts/daily_checkin.py
```

如果脚本不存在，先将其从本 skill 的 `scripts/daily_checkin.py` 复制到 `~/.workbuddy/scripts/` 目录：

```bash
mkdir -p ~/.workbuddy/scripts
cp <skill-dir>/scripts/daily_checkin.py ~/.workbuddy/scripts/daily_checkin.py
```

其中 `<skill-dir>` 是本 skill 的目录路径（可通过读取 SKILL.md 的路径推断）。

## 执行流程

1. **定位 Python**: 检测可用的 python3（优先 `/opt/homebrew/bin/python3`，其次 `/usr/local/bin/python3`，最后 `python3`）
2. **运行脚本**: 执行 `python3 ~/.workbuddy/scripts/daily_checkin.py`
3. **解读输出**: 根据脚本输出向用户汇报结果：
   - ✅ 签到成功 → 提示获得多少 Credits、连续天数、累计总额
   - ✅ 今日已签到 → 提示连续天数和累计总额（API 确认）
   - ❌ 失败 → 说明原因（token 过期 / 网络错误 / 未登录）
4. **处理异常**:
   - 如果 auth 文件不存在 → 提示用户先登录 WorkBuddy
   - 如果 token 过期 → 提示用户重新登录 WorkBuddy（token 由 app 自动刷新）

## 跨平台说明

脚本会根据当前操作系统自动判断 auth 文件位置：

- **macOS**: `~/Library/Application Support/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info`
- **Windows**: `%APPDATA%\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info`

## 设置自动化定时任务

如果用户想要每天自动签到（无需手动触发），按以下步骤配置：

### 方案一：WorkBuddy 内置自动化（推荐，跨平台通用）

在 WorkBuddy 的「自动化」面板中创建 4 个定时任务，覆盖全天时段：

| 名称 | 时间 | RRULE |
|------|------|-------|
| [09:05] 签到 | 上午 | `FREQ=DAILY;BYHOUR=9;BYMINUTE=5` |
| [13:05] 签到 | 下午 | `FREQ=DAILY;BYHOUR=13;BYMINUTE=5` |
| [19:05] 签到 | 傍晚 | `FREQ=DAILY;BYHOUR=19;BYMINUTE=5` |
| [23:05] 签到 | 夜间兜底 | `FREQ=DAILY;BYHOUR=23;BYMINUTE=5` |

每个自动化任务的 prompt 内容：

> 执行签到: `python3 ~/.workbuddy/scripts/daily_checkin.py`
> 汇报结果：成功/已签到/失败 + 原因。脚本以 API 为准，已签到自动跳过。

脚本内置 API 状态验证，4 个时段中只要任意一个成功，其余会自动跳过（API 返回 `today_checked_in: true`）。

### 方案二：系统级定时任务（可选）

- **macOS**: 使用 `launchd`，将 `StartCalendarInterval` 设置为 9:05，支持休眠后补跑。
- **Windows**: 使用「任务计划程序」，创建每天 9:05 运行 `python3 %USERPROFILE%\.workbuddy\scripts\daily_checkin.py` 的任务。

注意：系统级定时任务需要用户根据自己操作系统手动配置，技能本身不自动创建。

## 日志

所有签到记录保存在 `~/.workbuddy/logs/checkin/`：
- `daily.log` — 汇总日志
- `checkin-{YYYY-MM-DD}.log` — 每日详细日志
- 系统级定时任务可能额外生成 stdout/stderr 日志
