import os
import sys
from pathlib import Path

# 添加 agent 目录到 Python 路径，确保可以导入 api 模块
agent_dir = Path(__file__).parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from tools.tools import tools

# 1. 加载环境变量（建议将 API Key 放在 .env 文件中）
load_dotenv()
# 完全禁用 LangSmith 追踪（避免认证错误）
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""  # 清空端点
os.environ["LANGCHAIN_API_KEY"] = ""  # 清空 API Key
ali_key = os.getenv("ali_key")
openai_api_key = os.getenv("OPENAI_API_KEY")

# 3. 配置 LLM（大语言模型）
llm = ChatOpenAI(
    model_name="deepseek-v3.2",
    temperature=0.5,
    api_key=ali_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    streaming=False
)

# ========== LangGraph 实现 ==========
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage, AIMessage
import json

# 1. 定义状态
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. 创建图
graph = StateGraph(State)

# 3. 绑定工具到 LLM
llm_with_tools = llm.bind_tools(tools)

# 4. 定义 chatbot 节点（固定边示例）
def chatbot_node(state: State):
    """处理用户消息，决定是否调用工具"""
    messages = state["messages"]
    print(f"[DEBUG] chatbot_node 收到的消息: {messages}")
    
    # 如果最后一条消息是 ToolMessage，打印调试信息
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, ToolMessage):
            print(f"[DEBUG] chatbot_node 收到的工具结果: {last_msg.content}")
    
    # 所有消息都经过 LLM 处理，让 LLM 根据用户意图和工具结果判断是否需要继续调用接口
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 5. 定义 tools 节点
def tools_node(state: State):
    """执行工具调用"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 执行所有工具调用
    tool_messages = []
    
    for tool_call in last_message.tool_calls:
        # tool_call 可能是对象或字典，兼容处理
        if hasattr(tool_call, "name"):
            tool_name = tool_call.name
            tool_args = tool_call.args if hasattr(tool_call, "args") else {}
            tool_call_id = tool_call.id if hasattr(tool_call, "id") else None
        elif isinstance(tool_call, dict):
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_call_id = tool_call.get("id")
        else:
            continue
        
        # 找到对应的工具
        tool = next((t for t in tools if t.name == tool_name), None)
        if tool:
            # 执行工具
            try:
                result = tool.invoke(tool_args)
                
                # 处理工具返回的三种格式
                content = None
                # 检查返回格式
                if isinstance(result, dict):
                    # 格式1: 包含 prompt 字段 -> 调用 LLM 生成内容
                    if "prompt" in result and result["prompt"]:
                        prompt_text = result["prompt"]
                        
                        # 调用 LLM 生成参数（直接使用工具返回的提示词，只添加最关键的指令）
                        generate_message = HumanMessage(
                            content=f"""{prompt_text}

                            【重要】请严格按照上述要求执行，不要有任何解释、说明、描述或 markdown 代码块。"""
                        )
                        
                        # 调用 LLM 生成参数（不使用工具绑定，直接生成）
                        response = llm.invoke([generate_message])
                        
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
                        content = generated_content
                    
                    # 格式2: 包含 message 字段 -> 直接使用文本内容
                    elif "message" in result and result["message"]:
                        content = str(result["message"])
                    
                    # 格式3: 包含 data 字段 -> 序列化为 JSON
                    elif "data" in result and result["data"] is not None:
                        content = json.dumps(result["data"], ensure_ascii=False)
                    
                    # 如果字典中没有这三个字段，尝试序列化整个字典
                    else:
                        content = json.dumps(result, ensure_ascii=False)
                
                # 如果返回的是字符串，直接使用（兼容旧格式）
                elif isinstance(result, str):
                    content = result
                
                # 其他类型，转换为字符串
                else:
                    content = json.dumps(result, ensure_ascii=False) if result is not None else ""
                
                # 创建工具消息
                tool_messages.append(
                    ToolMessage(
                        content=content,
                        tool_call_id=tool_call_id
                    )
                )
            except Exception as e:
                # 如果工具执行失败，返回错误信息
                tool_messages.append(
                    ToolMessage(
                        content=json.dumps({"error": str(e)}, ensure_ascii=False),
                        tool_call_id=tool_call_id
                    )
                )
    
    return {"messages": tool_messages}

def should_continue(state: State):
    """判断是否需要调用工具或继续循环"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 如果最后一条消息包含工具调用，去 tools 节点
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # 如果没有工具调用，检查是否有新的工具结果需要 LLM 处理
    # 如果最后一条消息是 ToolMessage，说明刚执行完工具，需要让 LLM 处理结果
    if isinstance(last_message, ToolMessage):
        # 有工具结果，继续循环让 LLM 处理
        return "chatbot"
    
    # 如果最后一条消息是 AIMessage 且没有工具调用，说明 LLM 已经给出了最终回复
    # 检查是否有内容
    has_content = False
    if hasattr(last_message, "content"):
        content = last_message.content
        if content and content.strip():
            has_content = True
    
    # 如果有内容，说明 LLM 已经给出了回复，结束
    if has_content:
        return "end"
    else:
        # 如果没有内容，继续循环（让 LLM 重新处理）
        return "chatbot"

graph.add_node("tools", tools_node)
graph.add_node("chatbot", chatbot_node)
graph.add_edge(START, "chatbot")
graph.add_edge("tools", "chatbot")  # 工具执行后回到 chatbot
graph.add_conditional_edges(
    "chatbot",
    should_continue,
    {
        "tools": "tools",      # 需要工具 -> 去 tools 节点
        "chatbot": "chatbot",   # 继续循环 -> 回到 chatbot 节点
        "end": END              # 有最终答案 -> 结束
    }
)

# 10. 编译图
app = graph.compile()

# ========== 使用示例 ==========
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    
    print("=" * 60)
    print("LLM Agent 已启动，输入 'exit' 或 'quit' 退出")
    print("=" * 60)
    
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
            
            # 调用 agent
            result = app.invoke({
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
                    msg_type = type(msg).__name__
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
    