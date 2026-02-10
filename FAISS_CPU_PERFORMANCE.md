# FAISS-CPU 性能评估指南

## 你的 CPU 性能分析

### Intel i7-12700 规格
- **架构**: Alder Lake (12代)
- **核心数**: 12核心（8性能核 + 4能效核）
- **线程数**: 20线程
- **基础频率**: 2.1 GHz
- **最大睿频**: 4.9 GHz
- **性能等级**: 高端桌面 CPU

### 性能评估
✅ **你的 CPU 性能非常强，完全够用！**

## FAISS-CPU 性能要求

### 基本要求
- **最低**: 2核心，4GB 内存（小规模数据 < 1万向量）
- **推荐**: 4核心，8GB 内存（中等规模 1-10万向量）
- **理想**: 8核心+，16GB+ 内存（大规模 > 10万向量）

### 你的配置 vs 要求
| 项目 | 你的配置 | FAISS 要求 | 评估 |
|------|---------|-----------|------|
| 核心数 | 12核心 | 4核心+ | ✅ 超出3倍 |
| 线程数 | 20线程 | 8线程+ | ✅ 超出2.5倍 |
| 性能 | 高端 | 中端+ | ✅ 完全满足 |

## 实际性能表现预估

### 小规模数据（< 1万向量）
- **搜索速度**: < 10ms
- **索引构建**: < 1秒
- **CPU 使用率**: 10-20%
- **结论**: 完全流畅，不会卡

### 中等规模（1-10万向量）
- **搜索速度**: 10-50ms
- **索引构建**: 1-10秒
- **CPU 使用率**: 20-40%
- **结论**: 流畅运行，不会卡

### 大规模（10-100万向量）
- **搜索速度**: 50-200ms
- **索引构建**: 10-60秒
- **CPU 使用率**: 40-70%
- **结论**: 可以运行，偶尔可能稍慢

### 超大规模（> 100万向量）
- **搜索速度**: 200ms+
- **索引构建**: 1分钟+
- **CPU 使用率**: 70-100%
- **结论**: 可能需要优化或使用 GPU 版本

## 性能优化建议

### 1. 选择合适的索引类型

```python
import faiss

# 小规模（< 10万）：使用 IndexFlatL2（精确搜索）
index = faiss.IndexFlatL2(dimension)  # 最准确，但稍慢

# 中等规模（10-100万）：使用 IndexIVFFlat（近似搜索）
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)  # 更快

# 大规模（> 100万）：使用 IndexIVFPQ（压缩索引）
index = faiss.IndexIVFPQ(quantizer, dimension, nlist, m, 8)  # 最快，但需要训练
```

### 2. 调整线程数

```python
import faiss

# FAISS 默认使用所有 CPU 核心
# 可以限制线程数（如果需要）
faiss.omp_set_num_threads(8)  # 使用 8 个线程
```

### 3. 批量处理

```python
# 批量搜索比单个搜索更高效
# 一次搜索多个查询
results = index.search(query_vectors, k)  # query_vectors 是矩阵
```

## 实际测试建议

### 测试脚本
```python
import faiss
import numpy as np
import time

# 测试不同规模的数据
for num_vectors in [1000, 10000, 100000, 1000000]:
    dimension = 384  # 向量维度（如 BGE 模型）
    
    # 创建随机向量
    vectors = np.random.random((num_vectors, dimension)).astype('float32')
    
    # 创建索引
    index = faiss.IndexFlatL2(dimension)
    
    # 添加向量
    start = time.time()
    index.add(vectors)
    add_time = time.time() - start
    
    # 搜索测试
    query = np.random.random((1, dimension)).astype('float32')
    start = time.time()
    distances, indices = index.search(query, 10)
    search_time = time.time() - start
    
    print(f"向量数: {num_vectors:>8}, "
          f"添加时间: {add_time:.3f}s, "
          f"搜索时间: {search_time*1000:.2f}ms")
```

## 与 Chroma 对比

### FAISS-CPU
- **优势**: 性能好，适合大规模数据
- **劣势**: 需要手动管理，API 较复杂
- **适用**: 10万+ 向量，需要高性能

### Chroma
- **优势**: 简单易用，自动管理
- **劣势**: 性能稍差，不适合超大规模
- **适用**: < 10万向量，快速开发

## 针对你的项目建议

### 如果知识库规模 < 10万文档
**推荐使用 Chroma**：
- 你的 CPU 完全够用
- 开发更简单
- 性能足够

### 如果知识库规模 > 10万文档
**考虑使用 FAISS**：
- 你的 CPU 可以支持
- 性能更好
- 需要更多开发工作

### 混合方案
```python
# 小规模用 Chroma，大规模用 FAISS
if num_documents < 100000:
    use_chroma()
else:
    use_faiss()
```

## 内存要求

### 向量存储内存估算
```
内存 = 向量数 × 向量维度 × 4字节（float32）

示例：
- 1万向量 × 384维 = 15.36 MB
- 10万向量 × 384维 = 153.6 MB
- 100万向量 × 384维 = 1.5 GB
```

### 你的情况
- **i7-12700** 通常搭配 16GB+ 内存
- 可以轻松支持 100万+ 向量
- 不会卡

## 总结

### 你的 CPU (i7-12700) 评估
✅ **完全够用，不会卡！**

- 可以轻松处理 10-100万 向量
- 搜索速度 < 100ms（中等规模）
- CPU 使用率通常 < 50%

### 推荐方案
1. **开始阶段**: 使用 Chroma（简单）
2. **数据增长**: 如果超过 10万向量，考虑 FAISS
3. **性能优化**: 根据实际数据规模调整索引类型

### 实际建议
对于你的日常记录助手项目：
- 预计文档数不会超过 10万
- **Chroma 完全够用**
- 你的 CPU 性能绰绰有余
- 不用担心卡顿问题

如果未来数据量真的很大，再考虑迁移到 FAISS。
