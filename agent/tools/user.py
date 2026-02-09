import os
import sys
from pathlib import Path
# 添加 agent 目录到 Python 路径，确保可以导入 api 模块
agent_dir = Path(__file__).parent.parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))
from langchain_core.tools import StructuredTool
from api.user import get_user_chat_history_api


def get_user_chat_history(user_id: int, date: str):
    result=get_user_chat_history_api(user_id, date)
    return result
get_user_chat_history_tool=StructuredTool.from_function(
    func=get_user_chat_history,
    name="获取用户行为记录历史",
    description="""
        当你需要查询用户行为记录时，使用这个工具。当用户没有说明参数时，参数取默认值
        参数说明：
        - user_id: 用户ID，默认为1000001
        - date: 日期，格式为YYYY-MM-DD，默认为空字符串
    """,
)

# 扁平化所有工具列表
tools = [
    get_user_chat_history_tool
]