query_type = {
    '/feisu/manage/rechargeRecord/getRechargeRecordConfigs': [
        {
            "name": "page",
            "type": "number",
            "required": True,
            "prompt": "大于0小于100的整数",
            "description": "分页页码"
        },
        {
            "name": "size",
            "type": "number",
            "required": True,
            "prompt": "大于0小于20的整数",
            "description": "每页条数"
        },
        {
            "name": "startCreateTime",
            "type": "string",
            "required": False,
            "prompt": "生成一个2026-01-03格式的日期",
            "description": "开始时间"
        },
        {
            "name": "endCreateTime",
            "type": "string",
            "required": False,
            "prompt": "生成一个2026-01-03格式的日期",
            "description": "结束时间"
        },
        {
            "name": "mobile",
            "type": "string",
            "required": False,
            "prompt": "生成一个11位手机号",
            "description": "手机号"
        }, 
        {
            "name": "orderNo",
            "type": "string",
            "required": False,
            "prompt": "生成一个15位订单编号",
            "description": "订单编号"
        },
        {
            "name": "channel",
            "type": "number",
            "required": False,
            "prompt": "随机生成0-6之间的整数",
            "description": "充值渠道"
        }
    ]
}

def getQueryTypeByPath(path: str):
    return query_type.get(path, [])
