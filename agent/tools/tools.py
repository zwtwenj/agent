import os
import sys
from pathlib import Path
from datetime import datetime


# 添加 agent 目录到 Python 路径，确保可以导入其他模块
agent_dir = Path(__file__).parent.parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

# 导入用户工具
from tools.common import get_time_tool
from tools.query import generateQueryParamsPromptTool, httpRequestTool




# 合并所有工具列表
tools = [
    get_time_tool,
    generateQueryParamsPromptTool,
    httpRequestTool
]