import os
import sys
from pathlib import Path
from typing import Any

# 添加 agent 目录到 Python 路径，确保可以导入其他模块
agent_dir = Path(__file__).parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from tools.tools import tools
import json

# 1. 加载环境变量
load_dotenv()

# 完全禁用 LangSmith 追踪（避免认证错误）
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""

ali_key = os.getenv("ali_key")
openai_api_key = os.getenv("OPENAI_API_KEY")

# 2. 配置 LLM（大语言模型）
llm = ChatOpenAI(
    model_name="deepseek-v3.2",
    temperature=0.5,
    api_key=ali_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    streaming=False
)

# 3. 创建 Agent（使用 create_agent）
agent = create_agent(llm, tools)

# 4. 工具结果处理函数（处理三种格式：prompt、message、data）
def process_tool_result(result, llm_instance):
    """处理工具返回的三种格式"""
    if isinstance(result, dict):
        # 格式1: 包含 prompt 字段 -> 调用 LLM 生成内容
        if "prompt" in result and result["prompt"]:
            prompt_text = result["prompt"]
            
            # 调用 LLM 生成参数
            generate_message = HumanMessage(
                content=f"""{prompt_text}

                【重要】请严格按照上述要求执行，不要有任何解释、说明、描述或 markdown 代码块。"""
            )
            
            # 调用 LLM 生成参数
            response = llm_instance.invoke([generate_message])
            
            # 提取生成的参数内容
            generated_content = response.content if hasattr(response, 'content') else str(response)
            
            # 清理内容：移除可能的 markdown 代码块标记和多余文字
            generated_content = generated_content.strip()
            
            # 移除 markdown 代码块
            if generated_content.startswith('```'):
                lines = generated_content.split('\n')
                # 移除第一行（```json 或 ```）
                if lines[0].startswith('```'):
                    lines = lines[1:]
                # 移除最后一行（```）
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                generated_content = '\n'.join(lines).strip()
            return generated_content
        
        # 格式2: 包含 message 字段 -> 直接使用文本内容
        elif "message" in result and result["message"]:
            return str(result["message"])
        
        # 格式3: 包含 data 字段 -> 序列化为 JSON
        elif "data" in result and result["data"] is not None:
            return json.dumps(result["data"], ensure_ascii=False)
        
        # 如果字典中没有这三个字段，尝试序列化整个字典
        else:
            return json.dumps(result, ensure_ascii=False)
    
    # 如果返回的是字符串，直接使用（兼容旧格式）
    elif isinstance(result, str):
        return result
    
    # 其他类型，转换为字符串
    else:
        return json.dumps(result, ensure_ascii=False) if result is not None else ""

class AccumulatorService:
    def __init__(self, agent: Any):
        self.agent = agent
    
    def run_accumulator_loop(self):
        while True:
            try:
                # 获取用户输入
                user_input = input("\n你: ").strip()
                
                # 检查退出命令
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("\n再见！")
                    break
                
                if not user_input:
                    continue
                
                print("\n正在处理...")
                
                # 调用 agent（create_agent 返回的图使用 messages 格式）
                result = agent.invoke({
                    "messages": [HumanMessage(content=user_input)]
                })
                
                # 提取并显示最终回复
                messages = result.get("messages", [])
                
                # 查找最后一条 AIMessage（LLM 的最终回复）
                final_response = None
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage):
                        # 检查是否有工具调用
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            print("\n[工具调用]")
                            for tool_call in msg.tool_calls:
                                tool_name = tool_call.name if hasattr(tool_call, "name") else tool_call.get("name", "未知")
                                tool_args = tool_call.args if hasattr(tool_call, "args") else tool_call.get("args", {})
                                print(f"  - 工具: {tool_name}")
                                print(f"    参数: {tool_args}")
                        else:
                            # 这是最终回复
                            final_response = msg
                            break
                
                # 显示最终回复
                if final_response and hasattr(final_response, "content"):
                    content = final_response.content
                    if content:
                        print(f"\n助手: {content}")
                    else:
                        print("\n助手: (无回复内容)")
                else:
                    # 如果没有找到最终回复，显示所有消息
                    print("\n[完整对话历史]")
                    for i, msg in enumerate(messages, 1):
                        if isinstance(msg, HumanMessage):
                            print(f"{i}. [用户] {msg.content}")
                        elif isinstance(msg, AIMessage):
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                print(f"{i}. [助手-工具调用] {len(msg.tool_calls)} 个工具")
                            else:
                                print(f"{i}. [助手] {msg.content if hasattr(msg, 'content') else '(无内容)'}")
                        elif isinstance(msg, ToolMessage):
                            print(f"{i}. [工具结果] {msg.content[:100]}..." if len(str(msg.content)) > 100 else f"{i}. [工具结果] {msg.content}")
                
                print("\n" + "-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n程序已中断，再见！")
                break
            except Exception as e:
                print(f"\n错误: {e}")
                import traceback
                traceback.print_exc()

# ========== 使用示例 ==========
if __name__ == "__main__":
    service = AccumulatorService(agent)
    service.run_accumulator_loop()
