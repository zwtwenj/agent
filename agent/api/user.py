from .httpx import httpx_client

# 获取用户chat历史
def get_user_chat_history_api(user_id: int, date: str):
    # 获取用户chat历史
    """
    获取用户chat历史
    参数说明：
    - user_id: 用户ID
    - date: 日期，格式为YYYY-MM-DD
    """
    try:
        option={
            "userId": user_id,
            "date": date
        }
        response=httpx_client.post("http://localhost:5000/api/user/chat/history", json=option)
        result=response.json()
        data=[]
        for item in result["data"]["content"]:
            info = {
                "时间": item.get("time", ""),
                "内容": item.get("text", ""),
                "日期": item.get("date", ""),
            }
            data.append(info)
        result["data"]=data
        return result
    except Exception as e:
        print(f"获取用户chat历史失败: {e}")
        return None