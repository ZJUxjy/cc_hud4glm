#!/usr/bin/env python3
"""
Claude Code status line 
"""

import sys
import json
import os
import time
from datetime import datetime, timezone, timedelta

import requests

# ANSI 颜色代码
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[90m"  # 灰色/暗淡
CYAN = "\033[36m"

# GLM 用量缓存
_glm_cache = {"data": None, "ts": 0}
_GLM_CACHE_TTL = 120  # 秒

def format_battery_icon(percentage, max_blocks=10):
    """根据百分比生成带颜色的电池/进度条图标"""
    filled = int((percentage / 100) * max_blocks)
    empty = max_blocks - filled

    # 根据使用量选择颜色
    if percentage < 60:
        color = GREEN
        symbol = "█"  # 充足 - 绿色
    elif percentage < 80:
        color = YELLOW
        symbol = "▓"  # 中等 - 黄色
    else:
        color = RED
        symbol = "▓"  # 高用量 - 红色

    filled_part = symbol * filled
    empty_part = "░" * empty

    # 彩色输出：填充部分着色，空部分灰色
    bar = f"{color}{filled_part}{DIM}{empty_part}{RESET}"
    return f"[{bar}] {color}{percentage:.0f}%{RESET}"

def format_token_count(n):
    """格式化token数为易读形式"""
    if n >= 1000000:
        return f"{n/1000000:.1f}M"
    elif n >= 1000:
        return f"{n/1000:.1f}K"
    else:
        return str(n)

def fetch_glm_usage():
    """查询 GLM plan 用量（带缓存），返回 (token_info, mcp_info) 或 (None, None)"""
    now = time.time()
    if _glm_cache["data"] is not None and now - _glm_cache["ts"] < _GLM_CACHE_TTL:
        return _glm_cache["data"]

    token = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://open.bigmodel.cn/api/anthropic")
    if not token:
        return None

    monitor_base = base_url.replace("/api/anthropic", "/api").replace("/anthropic", "").rstrip("/")
    url = f"{monitor_base}/monitor/usage/quota/limit"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        data = resp.json()
        if not data.get("success"):
            return None

        token_info = None
        mcp_info = None
        for item in data["data"].get("limits", []):
            if item.get("type") == "TOKENS_LIMIT" and item.get("unit") == 3:
                reset_ms = item.get("nextResetTime")
                reset_time = None
                if reset_ms:
                    tz = timezone(timedelta(hours=8))
                    reset_time = datetime.fromtimestamp(reset_ms / 1000, tz=tz).strftime("%H:%M")
                token_info = {"pct": item.get("percentage", 0), "reset": reset_time}
            elif item.get("type") == "TIME_LIMIT":
                mcp_info = {"current": item.get("currentValue", 0), "limit": item.get("usage", 0)}

        result = (token_info, mcp_info)
        _glm_cache["data"] = result
        _glm_cache["ts"] = now
        return result
    except Exception:
        return None

def main():
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            print("Claude Code", end="")
            return

        data = json.loads(stdin_data)

        # 获取模型信息
        model_info = data.get("model", {})
        model_id = model_info.get("id", "unknown")
        model_short = model_id

        # 获取上下文窗口信息
        ctx_window = data.get("context_window", {})
        used_percentage = ctx_window.get("used_percentage", 0)

        # 获取会话累计使用的token数（total_*_tokens）
        total_input = ctx_window.get("total_input_tokens", 0)
        total_output = ctx_window.get("total_output_tokens", 0)
        total_tokens = total_input + total_output

        # 生成状态栏
        battery = format_battery_icon(used_percentage)
        tokens_str = format_token_count(total_tokens)

        # GLM 用量
        glm_parts = []
        token_info, mcp_info = fetch_glm_usage()
        if token_info:
            pct = token_info["pct"]
            reset = token_info["reset"] or "??:??"
            c = GREEN if pct < 60 else YELLOW if pct < 80 else RED
            glm_parts.append(f"{CYAN}Token usage{RESET} {c}{pct}%{DIM} (reset at {reset}){RESET}")
        if mcp_info:
            cur, lim = mcp_info["current"], mcp_info["limit"]
            glm_parts.append(f"{CYAN}MCP{RESET} {cur}/{lim}")

        glm_str = " | ".join(glm_parts)
        parts = [f"Context:{battery}", model_short, tokens_str, glm_str]
        status = " | ".join(p for p in parts if p)
        print(status, end="")

    except Exception as e:
        print(f"Claude Code", end="")

if __name__ == "__main__":
    main()
