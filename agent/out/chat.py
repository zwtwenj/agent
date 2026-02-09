import json
import re
import os
import sys
from pathlib import Path
from flask import jsonify
from app import app

# 添加 agent 目录到 Python 路径
agent_dir = Path(__file__).parent.parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from main import agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

class Time(BaseModel):
    year: int = Field(..., description="年")
    month: int = Field(..., description="月份")
    day: int = Field(..., description="日")
    hour: int = Field(..., description="时")
    minute: int = Field(..., description="分")


def get_time_info() -> dict:
    """
    获取时间信息，返回结构化的 JSON 数据
    """
    prompt = """请返回当前时间数据，并以JSON格式返回，包含以下字段：
    - year: 年（整数）
    - month: 月份（整数，1-12）
    - day: 日（整数）
    - hour: 时（整数，0-23）
    - minute: 分（整数，0-59）

    重要要求：
    1. 只返回JSON格式的数据，不要包含任何其他文字说明
    2. 不要使用markdown代码块标记（不要用```json或```）
    3. 直接返回纯JSON对象，格式如下：
    {"year": 2026, "month": 2, "day": 3, "hour": 11, "minute": 45}
    4. 如果无法获取时间，请返回None
    
    请严格按照以上格式返回，不要添加任何额外的说明文字。"""

    # 调用 agent
    messages =[]
    messages.append(HumanMessage(content='现在是什么时候'))
    messages.append(HumanMessage(content=prompt))
    response=agent.invoke({"messages": messages})
    
    # 获取回复内容
    response_content = response["messages"][-1].content
    
    try:
        # 解析 JSON
        time_data = json.loads(response_content)
        
        # 验证数据是否符合 Time 模型（可选）
        time = Time(**time_data)
        return time.model_dump()
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        print(f"原始回复: {response_content}")
        return None
    except Exception as e:
        print(f"数据验证错误: {e}")
        print(f"原始回复: {response_content}")
        return None

# Flask 接口：获取时间信息
@app.route('/api/get_time', methods=['POST'])
def get_time_api():
    """
    Flask 接口：获取当前时间信息
    路径: /api/get_time
    方法: POST
    """
    try:
        result = get_time_info()
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': '获取时间信息失败'}), 500
    except Exception as e:
        return jsonify({'error': f'获取失败: {str(e)}'}), 500


# # 使用示例
if __name__ == "__main__":
    app.run(debug=True, port=5001)
#     # 运行 Flask 应用
#     app.run(debug=True, port=5001)