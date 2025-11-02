# RAG系统构建操作文档

## 一、概述

本文档详细记录了AI算命应用中RAG（Retrieval-Augmented Generation，检索增强生成）系统的完整构建流程。RAG系统通过检索传统典籍知识库，为AI模型提供专业的背景知识，显著提升回答的质量和准确性。

## 二、系统架构

### 2.1 核心组件

```
用户提问 → 向量化检索 → 知识库搜索 → 知识注入 → AI生成 → 流式回答
    ↓           ↓           ↓           ↓         ↓
 向量生成    相似度计算   向量数据库   Prompt构建  千问模型
```

### 2.2 技术栈

- **向量数据库**: Supabase (pgvector扩展)
- **向量生成**: 阿里云千问 text-embedding-v4 (1024维)
- **AI生成**: 阿里云千问 qwen-max
- **后端服务**: Supabase Edge Functions
- **前端**: 原生JavaScript + Server-Sent Events

## 三、环境准备

### 3.1 必需的环境变量

```bash
# 阿里云API配置
ALIBABA_API_KEY=your_dashscope_api_key

# Supabase配置
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 3.2 数据库准备

```sql
-- 创建知识库表
CREATE TABLE knowledge_base (
  id SERIAL PRIMARY KEY,
  source TEXT,           -- 书籍来源
  category TEXT,         -- 分类（易经、风水、解梦等）
  content TEXT,          -- 知识内容
  embedding VECTOR(1024) -- 1024维向量
);

-- 创建向量索引
CREATE INDEX idx_embedding ON knowledge_base
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- 创建RPC函数用于向量搜索
CREATE OR REPLACE FUNCTION match_knowledge(
  query_vector VECTOR(1024),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 5,
  category_filter TEXT DEFAULT NULL
) RETURNS TABLE (
  id INT,
  source TEXT,
  category TEXT,
  content TEXT,
  similarity FLOAT
) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    kb.id,
    kb.source,
    kb.category,
    kb.content,
    1 - (kb.embedding <=> query_vector) AS similarity
  FROM knowledge_base kb
  WHERE
    1 - (kb.embedding <=> query_vector) > match_threshold
    AND (category_filter IS NULL OR kb.category = category_filter)
  ORDER BY kb.embedding <=> query_vector
  LIMIT match_count;
END;
$$;
```

## 四、数据准备流程

### 4.1 知识库来源

从以下来源收集传统典籍数据：
- 易经及六十四卦解读
- 梅花易数
- 风水理论
- 面相手相
- 星座命理
- 周公解梦

### 4.2 数据清洗与去重

使用脚本处理原始数据：

```python
# 检查并清理重复数据
python pdf-processing/deduplicate_database.py

# 验证去重结果
python check_duplicates.py
```

**关键步骤**：
1. 以content前200字符作为唯一标识
2. 保留最早出现的记录
3. 批量删除重复项（每次100条）
4. 最终保留1402条唯一记录

## 五、向量生成

### 5.1 批量生成方式

有两种方式生成向量：

#### 方式一：Python脚本（推荐用于大批量）

```bash
# 生成向量并保存到JSON文件
python pdf-processing/generate_embeddings.py
```

**配置参数**：
- 模型：text-embedding-v4
- 向量维度：1024
- 批处理大小：10
- 文本长度限制：8000字符
- API限流：200ms间隔

#### 方式二：Edge Function（推荐用于增量更新）

```bash
# 部署函数后通过HTTP调用
curl -X POST "https://your-project.supabase.co/functions/v1/generate-embeddings" \
  -H "Authorization: Bearer your_service_role_key" \
  -d '{"limit": 100}'
```

### 5.2 关键代码实现

**向量生成函数**：
```python
def generate_embedding(text: str) -> List[float]:
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'text-embedding-v4',
        'input': {'texts': [text]},
        'parameters': {'text_type': 'document'}
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)
    result = response.json()

    return result['output']['embeddings'][0]['embedding']
```

**重要提示**：
- 使用`dimension: 1024`（单数形式）
- 控制API调用频率（QPS限制：20）
- 实现指数退避重试机制

## 六、RAG检索服务

### 6.1 部署rag-search函数

```typescript
// supabase/functions/rag-search/index.ts
// 主要功能：
// 1. 接收用户查询
// 2. 智能识别查询分类
// 3. 生成查询向量
// 4. 执行相似度搜索
// 5. 返回相关知识片段
```

**部署步骤**：
1. 打开Supabase Dashboard
2. 进入Edge Functions
3. 创建新函数`rag-search`
4. 粘贴代码并设置环境变量
5. 部署并测试

### 6.2 智能分类实现

系统通过关键词匹配自动识别查询分类：

```typescript
const categoryKeywords = {
  '易经': ['易经', '卦象', '八卦', '乾坤', '爻', '周易'],
  '风水': ['风水', '堪舆', '阳宅', '阴宅', '罗盘', '方位'],
  '解梦': ['解梦', '梦见', '做梦', '梦境']
  // ... 更多分类
};
```

## 七、AI对话集成

### 7.1 部署ai-chat-with-rag函数

该函数集成RAG检索和AI生成：

1. 接收用户问题和历史对话
2. 调用rag-search获取相关知识（取前3个，阈值0.75）
3. 将知识注入到System Prompt
4. 调用qwen-max生成流式回答
5. 通过SSE返回结果

### 7.2 知识注入格式

```
【参考古籍知识】
以下是与问题相关的古籍内容，请作为参考基础：

【古籍1: 易经 - 易经】
内容片段...

---

请基于以上古籍知识回答用户问题，保持专业性和准确性。
```

## 八、测试验证

### 8.1 测试工具

**Python测试脚本**：
```bash
# 完整RAG功能测试
python test_rag_api.py

# 多查询测试
python test_multiple_queries.py

# 简单单次测试
python test_rag_simple.py
```

**HTML测试界面**：
- 打开`test_rag.html`
- 支持可视化测试RAG搜索和完整对话
- 实时显示知识库统计

### 8.2 测试用例

```python
test_queries = [
    {"query": "梦见蛇是什么意思", "expected_category": "周公解梦"},
    {"query": "乾卦代表什么", "expected_category": "易经"},
    {"query": "家中财位应该怎么布置", "expected_category": "风水"},
    {"query": "生命线短代表什么", "expected_category": "面相手相"}
]
```

## 九、性能优化

### 9.1 数据库优化

- 使用pgvector的ivfflat索引
- 设置合适的lists参数（100）
- 创建复合索引用于分类过滤

### 9.2 检索优化

- 相似度阈值：默认0.7，AI聊天使用0.75
- 返回结果数：搜索返回5个，AI聊天使用3个
- 实现分类过滤减少搜索范围

### 9.3 限流控制

```python
# API调用间隔
time.sleep(0.2)  # 200ms

# 指数退避重试
for attempt in range(retry_count):
    try:
        # API调用
    except:
        time.sleep(2 ** attempt)  # 指数退避
```

## 十、监控与维护

### 10.1 知识库统计

定期检查知识库状态：

```sql
-- 总记录数
SELECT COUNT(*) FROM knowledge_base;

-- 有向量的记录数
SELECT COUNT(*) FROM knowledge_base WHERE embedding IS NOT NULL;

-- 按分类统计
SELECT category, COUNT(*) FROM knowledge_base GROUP BY category;
```

### 10.2 性能监控

Edge Functions中记录关键指标：
- Embedding生成耗时
- 向量检索耗时
- AI生成总耗时
- 返回结果数量

### 10.3 增量更新

对于新增知识，使用Edge Function按需生成向量：

```bash
curl -X POST "https://xxx.supabase.co/functions/v1/generate-embeddings" \
  -H "Authorization: Bearer xxx" \
  -d '{"limit": 10}'
```

## 十一、常见问题与解决方案

### 11.1 向量维度错误

**问题**：`vector must have 1024 dimensions, but has 1536`

**解决**：确保使用text-embedding-v4模型，并设置正确的参数：
```python
payload = {
    'model': 'text-embedding-v4',
    'parameters': {'text_type': 'document'}
}
```

### 11.2 API限流

**问题**：`Requests rate limit exceeded`

**解决**：
- 控制调用频率（QPS < 20）
- 实现指数退避重试
- 使用批量处理

### 11.3 检索结果不准确

**可能原因**：
- 相似度阈值过高（>0.8）
- 向量维度不匹配
- 知识库内容不完整

**解决方案**：
- 调整阈值（0.7-0.75）
- 验证向量生成
- 补充知识库内容

### 11.4 流式响应中断

**问题**：SSE连接中断

**解决**：
- 检查CORS配置
- 确保响应格式正确
- 实现自动重连机制

## 十二、部署清单

### 12.1 生产部署前检查

- [ ] 所有知识库条目已生成向量
- [ ] 向量索引已创建
- [ ] Edge Functions已部署并测试
- [ ] 环境变量已配置
- [ ] CORS已正确设置
- [ ] 性能测试通过

### 12.2 部署步骤

1. **数据库准备**
   ```bash
   # 创建表和索引
   psql -f setup_database.sql
   ```

2. **导入知识库**
   ```bash
   python pdf-processing/import_to_supabase.py
   ```

3. **生成向量**
   ```bash
   # 批量生成
   python pdf-processing/generate_embeddings.py

   # 或使用Edge Function
   curl -X POST ".../generate-embeddings"
   ```

4. **部署Edge Functions**
   - rag-search
   - ai-chat-with-rag
   - generate-embeddings

5. **测试验证**
   ```bash
   python test_rag_api.py
   ```

## 十三、总结

本RAG系统成功实现了传统典籍知识的数字化和智能化检索，为AI算命应用提供了强大的知识支撑。通过向量化的知识库，系统能够准确检索相关内容，显著提升AI回答的专业性和可信度。

**关键成果**：
- ✅ 1402条去重知识库数据
- ✅ 1024维向量全覆盖
- ✅ 智能分类检索
- ✅ 流式AI对话
- ✅ 完整的测试体系

系统已准备好用于生产环境，为用户提供专业的AI算命咨询服务。