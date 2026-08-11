#!/usr/bin/env python3
"""
WorkBuddy 每日自动签到脚本（跨平台版）
- 读取本地 auth 文件获取 accessToken
- 调用签到 API 领取每日免费 Credits
- 以 API 返回为准，不信任本地日志
- 记录日志到 ~/.workbuddy/logs/checkin/
- 支持 macOS 和 Windows
"""

import json
import os
import sys
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta


# 跨平台配置

def get_auth_file_path() -> str:
    """根据操作系统返回 WorkBuddy auth 文件路径"""
    if os.name == 'nt':  # Windows
        base = os.environ.get('APPDATA', os.path.expanduser('~\AppData\Roaming'))
        return os.path.join(base, 'CodeBuddyExtension', 'Data', 'Public', 'auth', 'workbuddy-desktop.info')
    else:  # macOS / Linux
        return os.path.expanduser(
            "~/Library/Application Support/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info"
        )


AUTH_FILE = get_auth_file_path()
LOG_DIR = os.path.expanduser("~/.workbuddy/logs/checkin")
BASE_URL = "https://copilot.tencent.com"
CHECKIN_STATUS_URL = f"{BASE_URL}/v2/billing/meter/checkin-activity-status"
CHECKIN_CLAIM_URL = f"{BASE_URL}/v2/billing/meter/daily-checkin"
BJS_TZ = timezone(timedelta(hours=8))


def log(msg: str) -> None:
    """打印日志到 stdout + 写入日志文件 + daily.log"""
    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.now(BJS_TZ)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    line = f"[{timestamp}] {msg}"
    print(line)
    log_file = os.path.join(LOG_DIR, f"checkin-{date_str}.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    daily_log = os.path.join(LOG_DIR, "daily.log")
    with open(daily_log, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_session() -> dict:
    """从 auth 文件读取 session 数据"""
    if not os.path.exists(AUTH_FILE):
        raise FileNotFoundError(f"Auth 文件不存在: {AUTH_FILE}\n请先打开 WorkBuddy 并登录。")
    with open(AUTH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def api_post(url: str, session: dict) -> dict:
    """调用 API"""
    access_token = session["auth"]["accessToken"]
    uid = session["account"]["uid"]
    domain = session["auth"].get("domain", "")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-User-Id": uid,
    }
    if domain:
        headers["X-Domain"] = domain

    req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"http_error": e.code, "body": body}


def check_status(session: dict) -> dict:
    """查询签到状态"""
    return api_post(CHECKIN_STATUS_URL, session)


def do_checkin(session: dict) -> dict:
    """执行签到"""
    return api_post(CHECKIN_CLAIM_URL, session)


def main() -> int:
    log("=" * 50)
    log("WorkBuddy 每日签到任务开始")
    log(f"平台: {os.name} ({'Windows' if os.name == 'nt' else 'macOS/Linux'})")
    log(f"Auth 文件: {AUTH_FILE}")

    try:
        # 1. 加载 session
        session = load_session()
        uid = session["account"]["uid"]
        nickname = session["account"].get("nickname", "unknown")
        log(f"用户: {nickname} ({uid})")

        # 2. 查询签到状态（以 API 返回为准，不信任本地日志）
        status = check_status(session)
        log(f"API 状态查询: {json.dumps(status, ensure_ascii=False)}")

        if status.get("code") != 0:
            error_msg = status.get("msg", "未知错误")
            log(f"❌ 查询状态失败: {error_msg}")
            return 1

        data = status.get("data", {})

        # 3. 如果今天还没签到，执行签到
        if not data.get("today_checked_in"):
            log("📌 今日尚未签到，开始领取...")
            claim_result = do_checkin(session)
            log(f"API 签到结果: {json.dumps(claim_result, ensure_ascii=False)}")

            if claim_result.get("code") == 0 or "credit" in claim_result:
                credit = claim_result.get("credit", claim_result.get("data", {}).get("credit", "?"))
                log(f"✅ 签到成功! 本次获得 {credit} Credits")
                # 签到成功后重新查询，获取最新的连续天数和累计额度
                status2 = check_status(session)
                data2 = status2.get("data", {})
                streak = data2.get("streak_days", "?")
                total = data2.get("total_credits", "?")
                log(f"📊 连续签到 {streak} 天, 累计 {total} Credits")
                return 0
            else:
                error_msg = claim_result.get("msg", "未知错误")
                log(f"❌ 签到失败: {error_msg}")
                return 1
        else:
            # API 确认今日已签到
            streak = data.get("streak_days", "?")
            total = data.get("total_credits", "?")
            log(f"✅ 今日已签到 (API确认) | 连续 {streak} 天 | 累计 {total} Credits")
            return 0

    except FileNotFoundError as e:
        log(f"错误: {e}")
        log("请先登录 WorkBuddy 后再运行此脚本")
        return 2
    except Exception as e:
        log(f"异常: {type(e).__name__}: {e}")
        return 3
    finally:
        log("WorkBuddy 每日签到任务结束")
        log("=" * 50)


if __name__ == "__main__":
    sys.exit(main())
