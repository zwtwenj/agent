import httpx 
from dotenv import load_dotenv

# 创建 Client 并绑定钩子
def create_client():
    def request_interceptor(request):
        return request
    client = httpx.Client(
        event_hooks={
            "request": [request_interceptor]
        }
    )
    return client

httpx_client = create_client()