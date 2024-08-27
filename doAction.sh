#!/bin/bash

# 激活虚拟环境
source /Users/george/IdeaProjects/mytest/venv/bin/activate

# 路径到你要运行的Python脚本
SCRIPT_PATH="./toolsUI.py"

# 使用osascript运行AppleScript，使脚本在后台运行而不弹出终端窗口
osascript -e "do shell script \"python3 $SCRIPT_PATH &> /dev/null &\""
