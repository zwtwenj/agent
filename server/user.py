import json
from flask import Flask, request, jsonify, Response
from connect import db, app

class User(db.Model):
    __tablename__ = 'user'
    userId = db.Column(db.Integer, primary_key=True)
    nickName = db.Column(db.String(255))

class Content(db.Model):
    __tablename__ = 'content'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String(255))
    text = db.Column(db.Text)
    userId = db.Column(db.Integer)
    date = db.Column(db.String(255))  # 添加date字段

# 标准化响应格式函数
def standard_response(code, data=None, message=''):
    """
    生成标准化响应格式
    code: 1-成功, 2-参数错误, 3-数据库错误, 4-未找到, 5-其他错误
    data: 返回的数据
    message: 响应消息
    """
    response = {
        'code': code,
        'data': data if data is not None else {},
        'message': message
    }
    return Response(
        json.dumps(response, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

# 获取用户chat历史
@app.route('/api/user/chat/history', methods=['POST'])
def get_user_chat_history():
    try:
        data = request.get_json()
        if not data:
            return standard_response(code=2, data={}, message='请求参数不能为空')
        
        if 'userId' not in data:
            return standard_response(code=2, data={}, message='缺少必需参数: userId')
        
        user_id = data['userId']
        date = data.get('date')  # 获取date参数，如果没有则返回None
        
        # 构建查询条件字典（动态添加筛选条件）
        filter_conditions = {'userId': user_id}
        if date:  # 如果传了date参数且不为空，则添加date筛选条件
            filter_conditions['date'] = date
        
        # 执行查询并排序（只执行一次数据库查询）
        contents = Content.query.filter_by(**filter_conditions).order_by(Content.id.desc()).all()
        # 查询该用户的最新的10条 content（按 id 降序）
        # contents = Content.query.filter_by(userId=user_id).order_by(Content.id.desc()).limit(10).all()
        
        # 整理成你需要的格式
        content_list = [{'id': c.id, 'time': c.time, 'text': c.text, 'date': c.date if c.date else ''} for c in contents]
        
        # 返回标准化格式
        response_data = {
            "userId": user_id,
            "content": content_list
        }
        return standard_response(code=1, data=response_data, message='success')
    except Exception as e:
        return standard_response(code=5, data={}, message=f'获取失败: {str(e)}')

# 添加用户chat历史
@app.route('/api/user/chat/history/add', methods=['POST'])
def add_user_chat_history():
    try:
        data = request.get_json()
        if not data:
            return standard_response(code=2, data={}, message='请求参数不能为空')
        
        # 验证必需参数
        required_fields = ['time', 'text', 'userId']
        for field in required_fields:
            if field not in data:
                return standard_response(code=2, data={}, message=f'缺少必需参数: {field}')
        
        time = data['time']
        text = data['text']
        userId = data['userId']
        date = data.get('date', '')  # 使用get方法，如果不存在则默认为空字符串
        
        # 创建新记录
        content = Content(time=time, text=text, userId=userId, date=date)
        db.session.add(content)
        db.session.commit()
        
        return standard_response(code=1, data={'id': content.id}, message='添加成功')
    except Exception as e:
        db.session.rollback()
        return standard_response(code=5, data={}, message=f'添加失败: {str(e)}')
