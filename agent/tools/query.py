import os
import sys
import time
from pathlib import Path
import random
from langchain_core.tools import StructuredTool
from httpx import Client

# 添加 agent 目录到 Python 路径，确保可以导入其他模块
agent_dir = Path(__file__).parent.parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

# 在路径设置之后导入
from tools.queryType.customer import getQueryTypeByPath

# 生成对应格式的随机参数
# unRequired_coefficient_percent对于非必传参数，随机生成一个概率，例如如果概率为1，此时required: false等价于required: true
# count生成多少个参数

def generate_query_params_prompt(path: str):
    query_type = getQueryTypeByPath(path)
    unRequired_coefficient_percent = 3
    count = 3
    
    # 将配置转换为 JSON 字符串，便于 LLM 理解
    import json
    query_type_str = json.dumps(query_type, ensure_ascii=False, indent=2)
    
    # 使用字符串格式化，避免 f-string 中 JSON 花括号的问题
    prompt_template = """
            你是一个专业的参数生成器，需要根据API参数配置生成 {count} 组随机测试参数。

            ## 参数配置
            ```json
            {query_type_str}
            ```

            ## 配置字段说明
            - **name**: 参数名称（必填）
            - **type**: 参数类型（number/string）
            - **required**: 是否必传（true=必须生成，false=可选）
            - **prompt**: 参数生成规则（优先使用此字段）
            - **description**: 参数描述（仅供参考）

            ## 生成规则

            ### 1. 必传参数（required: true）
            - **必须生成**，不能遗漏
            - 严格按照 `prompt` 的要求生成值
            - 确保生成的值符合类型要求（number 类型生成数字，string 类型生成字符串）

            ### 2. 非必传参数（required: false）
            - **严格遵循概率**：每个非必传参数在每个参数组中，按照 {unRequired_coefficient_percent}% 的概率决定是否生成
            - **独立判断**：每个非必传参数都是独立判断的，不能因为其他参数生成了就也生成
            - **概率控制**：在生成 {count} 组参数时，每组参数中的每个非必传参数都要独立进行概率判断
            - **重要**：必须严格按照这个概率执行，不能随意生成非必传参数
            - 如果决定生成，同样严格按照 `prompt` 的要求生成值

            ### 3. 值生成要求
            - **number 类型**：生成数字值（不要加引号）
            - **string 类型**：生成字符串值（需要加引号）
            - **日期格式**：严格按照 "YYYY-MM-DD" 格式
            - **手机号**：生成11位数字字符串
            - **订单号**：生成指定长度的字符串

            ### 4. 输出格式
            - 生成 {count} 组参数，每组参数是一个 JSON 对象
            - 最终输出为 JSON 对象格式，对象包含：path - 路径，json - 参数列表
            - 每组参数对象包含：参数名（name）作为 key，生成的值作为 value

            ## 示例

            ### 示例 1：单个必传参数
            **配置**：
            ```json
            [
                {{
                    "name": "page",
                    "type": "number",
                    "required": true,
                    "prompt": "大于0小于10000的整数",
                    "description": "分页页码"
                }}
            ]
            ```

            **输出**：
            ```json
            {{
                "path": "{path}",
                "json": [
                    {{"page": 100}},
                    {{"page": 1234}},
                    {{"page": 5678}}
                ]
            }}
            ```

            ### 示例 2：必传 + 可选参数
            **配置**：
            ```json
            {{
                "path": "{path}",
                "json": [
                    {{
                        "name": "page",
                        "type": "number",
                        "required": true,
                        "prompt": "大于0小于10000的整数",
                        "description": "分页页码"
                    }},
                    {{
                        "name": "size",
                        "type": "number",
                        "required": false,
                        "prompt": "大于0小于100的整数",
                        "description": "每页条数"
                    }}
                ]
            }}
            ```

            **输出**（size 参数按概率随机出现）：
            ```json
            {{
                "path": "{path}",
                "json": [
                    {{"page": 100, "size": 20}},
                    {{"page": 1234}},
                    {{"page": 5678, "size": 50}}
                ]
            }}
            ```

            ### 示例 3：日期格式参数
            **配置**：
            ```json
            {{
                "path": "{path}",
                "json": [
                    {{
                        "name": "startCreateTime",
                        "type": "string",
                        "required": false,
                        "prompt": "生成一个2026-01-03格式的日期",
                        "description": "开始时间"
                    }}
                ]
            }}
            ```

            **输出**：
            ```json
            {{
                "path": "{path}",
                "json": [
                    {{"startCreateTime": "2026-01-15"}},
                    {{"startCreateTime": "2026-02-20"}},
                    {{"startCreateTime": "2026-03-10"}}
                ]
            }}
            ```

            ## 重要提示
            1. **严格遵循 prompt 要求**：生成的值必须完全符合描述
            2. **类型一致性**：number 类型生成数字，string 类型生成字符串
            3. **格式规范**：日期、手机号等特殊格式必须严格按照要求
            4. **随机性**：每次生成的值应该不同，体现随机性
            5. **完整性**：必传参数必须出现在每一组参数中

            【重要】你的任务是按照上述要求生成参数的json，而不是输出你查询到的配置内容
            【重要】现在请根据上述配置生成JSON, JSON为对象格式，必须包含 path 和 json 两个字段，path 的值为 "{path}"，json 为参数数组。"""
    
    # 使用 .format() 方法进行格式化，避免 f-string 的问题    
    prompt_text = prompt_template.format(
        count=count,
        query_type_str=query_type_str,
        unRequired_coefficient_percent=unRequired_coefficient_percent,
        path=path
    )
    
    return {
        "message": None,
        "data": None,
        "prompt": prompt_text
    }

generateQueryParamsPromptTool = StructuredTool.from_function(
    func=generate_query_params_prompt,
    name="生成接口参数配置",
    description="""
        根据路径生成接口参数配置，
        参数: path - 路径，格式如 "/feisu/manage/rechargeRecord/getRechargeRecordConfigs"
        返回: 包含接口参数提示词的字符串
        """
)

def httpRequestTool(data: dict):
    path = data["path"]
    params = data["json"]
    delay = 1
    method = "POST"
    client = Client()
    headers = {
        "authorization": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsieG1hbGwtcHJvZHVjdCIsInhtYWxsLWF1dGgiXSwiaGVhZEltZyI6bnVsbCwidXNlcl9uYW1lIjpudWxsLCJvcGVuSWQiOm51bGwsInNjb3BlIjpbInNlcnZlciIsInNlbGVjdCJdLCJiaW5kUGhvbmUiOnRydWUsImV4cCI6MTc3MjA1OTI3MiwiZ3JhbnRUeXBlIjoicGFzc3dvcmQiLCJ1c2VySWQiOjE2LCJqdGkiOiJDNDN6c3dhTl8tS3FfUkNHZU93czBSSEhFbTAiLCJjbGllbnRfaWQiOiJmZWlTdUNsaWVudCJ9.kDRYAu12TFmyyKdtlM9LY-NkIHuNYNx2Sdm1dobs0C3ncGVTfB8EpVWqqKt6l_FKsftt2ubDOqbAn7Jdee2pYOt1irslFSOv71bdgXhRT01AxoCgdYqYNY9B3upXnaRM93U6eWHSYhiU15Vxu9Jp-vNTpLi7xu64dIHodaAkBRI"
    }
    # params是个数组，有多少个元素就进行多少次请求，请求间隔为delay
    results = []
    for param in params:
        response = client.request(method, 'https://focus.jdword.com/' + path, headers=headers, json=param)
        time.sleep(delay)
        results.append(response.json())
    return {
        "message": None,
        "data": results,
        "prompt": None
    }
    
httpRequestTool = StructuredTool.from_function(
    func=httpRequestTool,
    name="HTTP请求工具",
    description="""
        根据路径和参数进行HTTP请求
        参数：data - 数据，格式如 {"path": "/feisu/manage/rechargeRecord/getRechargeRecordConfigs", "json": [{"page": 100, "size": 20}, {"page": 1234, "size": 30, "startCreateTime": "2026-01-01"}]}
        返回：请求结果的数组json
        """
)