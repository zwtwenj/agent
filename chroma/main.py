import chromadb
from pathlib import Path

# 方式1：使用默认路径（当前目录下的 chroma_db 文件夹）
# client = chromadb.PersistentClient(path="./chroma_db")

# 方式2：指定自定义路径
chroma_db_path = Path(__file__).parent / "chroma_db"  # 在 chroma 目录下创建
# chroma_db_path = "D:/study/jihua/knowledge_base/chroma_db"  # 绝对路径
# chroma_db_path = "../knowledge_base/chroma_db"  # 相对路径

client = chromadb.PersistentClient(path=str(chroma_db_path))
print(f"数据库存储路径: {chroma_db_path.absolute()}")

collection = client.get_or_create_collection("test")

print("正在添加文档到数据库...")
collection.add(
    documents=[
        "Chroma 是 AI 原生向量数据库，支持自动嵌入与语义搜索",
        "RAG 系统常用 Chroma 做知识库检索",
        "向量数据库用于大模型上下文增强"
    ],
    metadatas=[
        {"category": "intro", "source": "doc"},
        {"category": "use_case", "source": "doc"},
        {"category": "concept", "source": "doc"}
    ],
    ids=["doc1", "doc2", "doc3"]  # 必须唯一
)
print("文档添加完成！")

# 验证数据是否存储成功
print("\n验证数据存储...")
count = collection.count()
print(f"数据库中的文档数量: {count}")

# 查询测试
print("\n测试搜索功能...")
results = collection.query(
    query_texts=["什么是向量数据库"],
    # n_results: 返回结果数量
    n_results=1
)
print(f"搜索结果数量: {len(results['ids'][0])}")
print(f"找到的文档ID: {results['ids'][0]}")
print(f"文档内容: {results['documents'][0]}")
print("\n数据存储和查询功能正常！")