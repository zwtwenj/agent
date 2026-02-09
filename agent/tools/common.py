from langchain_core.tools import StructuredTool
from datetime import datetime


def get_time():
    """
    获取当前时间，返回格式化的字典
    返回格式: {年: , 月: , 日: , 时: , 分: }
    """
    now = datetime.now()
    return {
        '年': now.year,
        '月': now.month,
        '日': now.day,
        '时': now.hour,
        '分': now.minute
    }

get_time_tool = StructuredTool.from_function(
    func=get_time,
    name="获取当前时间",
    description="""
        当你需要获取当前时间时，使用这个工具。
        返回格式: {年: , 月: , 日: , 时: , 分: }
    """,
)

tools = [
    get_time_tool
]