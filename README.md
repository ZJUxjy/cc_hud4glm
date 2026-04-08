# cc_hud4glm
a status line for claude code with glm-coding plan
## usage

1. 把 ~/.claude/statusline.py 放到用户目录下（你已经有了，新用户直接复制一份）

2. 配置 Claude Code

  编辑 ~/.claude/settings.json，添加：

  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }

## 显示效果：
  <img width="955" height="140" alt="screenshot_2026-04-08_11-07-02" src="https://github.com/user-attachments/assets/d2369b8a-ce2c-422b-8e1a-102606dfaa3f" />
