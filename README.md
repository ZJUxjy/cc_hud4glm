# cc_hud4glm
a status line for claude code with glm-coding plan
## usage

1. 把statusline.py 放到 `~/.claude/` 目录下

2. 配置 Claude Code

  编辑 ~/.claude/settings.json，添加：
```json
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }
```
## 显示效果：
  <img width="955" height="140" alt="screenshot_2026-04-08_11-07-02" src="https://github.com/user-attachments/assets/d2369b8a-ce2c-422b-8e1a-102606dfaa3f" />
