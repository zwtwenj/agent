from langchain_core.tools import StructuredTool

# 模拟生日数据库（实际应该从数据库或API获取）
BIRTHDAY_DATABASE = {
    "2026-02-24": "小明的生日",
    "2026-03-15": "小红的生日",
    "2026-12-25": "圣诞节约翰的生日",
}

def get_birthday_info(date_str: str) -> dict:
    """
    根据日期查询生日信息
    参数: date_str - 日期字符串，格式如 "2026-02-24"
    返回: 生日信息字典
    """
    # 格式化日期字符串（处理可能的格式差异）
    date_key = date_str.strip()
    
    # 查询生日信息
    birthday_info = BIRTHDAY_DATABASE.get(date_key, None)
    
    if birthday_info:
        return {
            "date": date_key,
            "birthday": birthday_info,
            "found": True
        }
    else:
        return {
            "date": date_key,
            "birthday": None,
            "found": False,
            "message": f"{date_key} 没有找到生日信息"
        }

get_birthday_tool = StructuredTool.from_function(
    func=get_birthday_info,
    name="查询生日信息",
    description="""
        根据日期查询是否有生日信息。
        参数: date_str - 日期字符串，格式如 "2026-02-24"
        返回: 包含生日信息的字典
    """,
)
