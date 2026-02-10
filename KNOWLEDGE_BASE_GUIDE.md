# 智能体知识库实现指南

## 技术栈概览

### 核心组件
1. **向量数据库** - 存储文档向量
2. **文本嵌入模型** - 将文本转换为向量
3. **文档处理** - 加载、分割、预处理
4. **检索器** - 相似度搜索
5. **Agent 集成** - 将知识库作为工具

## 1. 技术选型

### 向量数据库选择

#### 选项 1：Chroma（推荐，简单易用）
```python
# 优点：轻量级，易于集成，支持本地部署
# 缺点：不适合大规模数据
pip install chromadb
```

#### 选项 2：FAISS（Facebook AI Similarity Search）
```python
# 优点：性能好，适合大规模数据
# 缺点：需要手动管理索引
pip install faiss-cpu  # CPU版本
pip install faiss-gpu  # GPU版本（需要CUDA）
```

#### 选项 3：Milvus（生产环境推荐）
```python
# 优点：高性能，支持分布式，生产级
# 缺点：部署复杂，需要单独服务
# 需要 Docker 部署
```

#### 选项 4：Qdrant（云原生）
```python
# 优点：性能好，支持云部署
# 缺点：需要单独服务
pip install qdrant-client
```

### 嵌入模型选择

#### 选项 1：OpenAI Embeddings（推荐）
```python
# 优点：效果好，API 简单
# 缺点：需要 API Key，有费用
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()
```

#### 选项 2：本地模型（免费）
```python
# 选项 A: sentence-transformers
pip install sentence-transformers
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 选项 B: BGE 模型（中文效果好）
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5"  # 中文嵌入模型
)
```

#### 选项 3：阿里云 DashScope（你的项目已在使用）
```python
# 如果 DashScope 支持嵌入模型，可以直接使用
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-v1",  # 需要确认模型名
    openai_api_key=ali_key,
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```

## 2. 完整实现方案

### 方案 A：使用 Chroma + 本地嵌入模型（推荐开始）

#### 安装依赖
```bash
pip install chromadb
pip install sentence-transformers
pip install langchain-community
```

#### 代码实现
```python
# agent/knowledge_base/vector_store.py
import os
import sys
from pathlib import Path

# 添加路径
agent_dir = Path(__file__).parent.parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.schema import Document

class KnowledgeBase:
    def __init__(self, persist_directory="./knowledge_base/chroma_db"):
        """
        初始化知识库
        persist_directory: 向量数据库存储路径
        """
        # 使用中文嵌入模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={'device': 'cpu'}  # 使用 CPU，如果有 GPU 可以改为 'cuda'
        )
        
        # 初始化向量数据库
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,      # 每个块 500 字符
            chunk_overlap=50,    # 重叠 50 字符
            length_function=len,
        )
    
    def add_documents(self, documents):
        """
        添加文档到知识库
        documents: Document 对象列表
        """
        # 分割文档
        splits = self.text_splitter.split_documents(documents)
        
        # 添加到向量数据库
        self.vector_store.add_documents(splits)
        self.vector_store.persist()
        
        return len(splits)
    
    def add_text(self, text: str, metadata: dict = None):
        """
        添加文本到知识库
        text: 文本内容
        metadata: 元数据（如来源、标题等）
        """
        doc = Document(page_content=text, metadata=metadata or {})
        return self.add_documents([doc])
    
    def add_file(self, file_path: str):
        """
        从文件添加文档
        file_path: 文件路径
        """
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        return self.add_documents(documents)
    
    def add_directory(self, directory_path: str, glob_pattern="**/*.txt"):
        """
        从目录批量添加文档
        directory_path: 目录路径
        glob_pattern: 文件匹配模式
        """
        loader = DirectoryLoader(
            directory_path,
            glob=glob_pattern,
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        documents = loader.load()
        return self.add_documents(documents)
    
    def search(self, query: str, k: int = 4):
        """
        搜索相关知识
        query: 查询文本
        k: 返回最相关的 k 条结果
        """
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def search_with_score(self, query: str, k: int = 4):
        """
        搜索并返回相似度分数
        """
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results
    
    def get_retriever(self, k: int = 4):
        """
        获取检索器（用于 Agent 工具）
        """
        return self.vector_store.as_retriever(search_kwargs={"k": k})
```

### 方案 B：使用 FAISS（适合大规模数据）

```python
# agent/knowledge_base/faiss_store.py
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class KnowledgeBaseFAISS:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5"
        )
        self.vector_store = None
    
    def create_from_documents(self, documents, persist_directory="./knowledge_base/faiss_index"):
        """从文档创建 FAISS 索引"""
        splits = self.text_splitter.split_documents(documents)
        self.vector_store = FAISS.from_documents(splits, self.embeddings)
        self.vector_store.save_local(persist_directory)
    
    def load(self, persist_directory="./knowledge_base/faiss_index"):
        """加载已有索引"""
        self.vector_store = FAISS.load_local(
            persist_directory,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
    
    def search(self, query: str, k: int = 4):
        """搜索"""
        return self.vector_store.similarity_search(query, k=k)
```

## 3. 创建 Agent 工具

```python
# agent/tools/knowledge.py
import os
import sys
from pathlib import Path
from langchain_core.tools import StructuredTool

# 添加路径
agent_dir = Path(__file__).parent.parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from knowledge_base.vector_store import KnowledgeBase

# 初始化知识库
kb = KnowledgeBase()

def search_knowledge_base(query: str) -> str:
    """
    从知识库中搜索相关信息
    
    参数:
        query: 查询问题
    
    返回:
        相关知识内容
    """
    try:
        results = kb.search(query, k=3)
        
        if not results:
            return "知识库中没有找到相关信息。"
        
        # 整理结果
        answer_parts = []
        for i, doc in enumerate(results, 1):
            content = doc.page_content
            metadata = doc.metadata
            source = metadata.get('source', '未知来源')
            
            answer_parts.append(f"[来源: {source}]\n{content}")
        
        return "\n\n---\n\n".join(answer_parts)
    except Exception as e:
        return f"搜索知识库时出错: {str(e)}"

# 创建工具
search_knowledge_tool = StructuredTool.from_function(
    func=search_knowledge_base,
    name="搜索知识库",
    description="""
    当你需要查找特定信息、回答用户问题或需要参考文档时，使用这个工具。
    
    参数说明:
    - query: 要搜索的问题或关键词（字符串）
    
    使用场景:
    - 用户询问特定知识
    - 需要查找文档中的信息
    - 回答需要参考文档的问题
    """
)
```

## 4. 集成到 Agent

```python
# agent/main.py 修改
from tools.knowledge import search_knowledge_tool
from tools.tools import tools

# 添加知识库工具
all_tools = tools + [search_knowledge_tool]

agent = create_agent(
    model=llm,
    system_prompt=system_prompt,
    tools=all_tools,  # 包含知识库工具
    debug=False
)
```

## 5. 更新系统提示词

```python
system_prompt = """
你是一个帮助用户进行日常记录的智能助手，同时拥有知识库查询能力。

【核心功能】
1. 记录：使用 add_user_history 工具记录用户的行为
2. 查询：使用 get_user_chat_history 工具查询历史记录
3. 时间：使用 get_time 工具获取当前时间
4. 知识库：使用 search_knowledge_base 工具查询知识库

【知识库使用规则】
- 当用户询问知识性问题时，使用 search_knowledge_base 工具
- 搜索后，结合知识库内容回答用户
- 如果知识库没有相关信息，如实告知用户

【示例】
用户："什么是机器学习？"
你：调用 search_knowledge_base("机器学习")
    根据搜索结果回答用户
"""
```

## 6. 添加文档到知识库

```python
# agent/knowledge_base/init_kb.py
from knowledge_base.vector_store import KnowledgeBase

def init_knowledge_base():
    """初始化知识库，添加文档"""
    kb = KnowledgeBase()
    
    # 方式1：添加文本
    kb.add_text(
        "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。",
        metadata={"source": "AI基础", "category": "概念"}
    )
    
    # 方式2：添加文件
    kb.add_file("documents/ai_basics.txt")
    
    # 方式3：批量添加目录
    kb.add_directory("documents/", glob_pattern="**/*.txt")
    
    print("知识库初始化完成！")

if __name__ == "__main__":
    init_knowledge_base()
```

## 7. 完整项目结构

```
agent/
├── knowledge_base/
│   ├── __init__.py
│   ├── vector_store.py      # 向量数据库封装
│   ├── init_kb.py           # 初始化知识库
│   └── chroma_db/           # Chroma 数据库文件（自动生成）
├── tools/
│   ├── knowledge.py         # 知识库工具
│   ├── user.py
│   └── common.py
├── documents/               # 知识库文档目录
│   ├── ai_basics.txt
│   ├── langchain_guide.txt
│   └── ...
└── main.py
```

## 8. 技术选型建议

### 小型项目（< 1000 文档）
- **向量数据库**: Chroma
- **嵌入模型**: BAAI/bge-small-zh-v1.5（中文）
- **优点**: 简单易用，无需额外服务

### 中型项目（1000-10000 文档）
- **向量数据库**: FAISS 或 Chroma
- **嵌入模型**: BAAI/bge-base-zh-v1.5
- **优点**: 性能好，支持本地部署

### 大型项目（> 10000 文档）
- **向量数据库**: Milvus 或 Qdrant
- **嵌入模型**: BAAI/bge-large-zh-v1.5 或 OpenAI Embeddings
- **优点**: 高性能，支持分布式

## 9. 成本考虑

### 免费方案（推荐开始）
- Chroma（免费）
- HuggingFace Embeddings（免费，本地运行）
- 适合：个人项目、小规模数据

### 付费方案
- OpenAI Embeddings: $0.0001 / 1K tokens
- 适合：需要高质量嵌入、大规模数据

## 10. 实施步骤

1. **安装依赖**
   ```bash
   pip install chromadb sentence-transformers langchain-community
   ```

2. **创建知识库模块**
   - 创建 `agent/knowledge_base/` 目录
   - 实现 `vector_store.py`

3. **创建工具**
   - 在 `agent/tools/knowledge.py` 中创建工具

4. **集成到 Agent**
   - 在 `main.py` 中添加工具
   - 更新系统提示词

5. **添加文档**
   - 准备文档文件
   - 运行初始化脚本

6. **测试**
   - 测试知识库搜索
   - 测试 Agent 使用知识库

## 11. 高级功能

### 混合检索（Hybrid Search）
```python
# 结合关键词搜索和向量搜索
from langchain.retrievers import BM25Retriever

# 关键词检索
bm25_retriever = BM25Retriever.from_documents(documents)
# 向量检索
vector_retriever = vector_store.as_retriever()
# 混合检索
```

### 重排序（Reranking）
```python
# 使用重排序模型提升结果质量
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
```

### 多模态支持
```python
# 支持图片、PDF 等格式
from langchain_community.document_loaders import PyPDFLoader, ImageCaptionLoader
```

## 总结

**最小可行方案（MVP）**：
1. Chroma + BGE 中文嵌入模型
2. 简单的文档加载和分割
3. 基础的相似度搜索
4. 作为 Agent 工具集成

**推荐开始使用的技术**：
- 向量数据库：Chroma
- 嵌入模型：BAAI/bge-small-zh-v1.5
- 文档处理：LangChain Document Loaders
- 集成方式：作为 Agent 工具

这样可以快速搭建一个可用的知识库系统！
