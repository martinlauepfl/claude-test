# 后续任务清单

## 📋 当前状态总结

### ✅ 已完成
1. **修复了向量生成问题**
   - 发现参数错误：`dimensions=1024` (错误) → `dimension=1024` (正确)
   - 确认 text-embedding-v4 模型可以生成 1024 维向量
   - 测试通过，API 能正确返回 1024 维向量

2. **修复了 RAG 搜索问题**
   - 发现并修复了 `rag-search` Edge Function 中的硬编码搜索词
   - 将硬编码的 `%乾卦%` 改为动态查询
   - 更新了 `ai-chat-with-rag` 降低了搜索阈值（0.75 → 0.5）
   - 增加了返回结果数量（3 → 5）

3. **知识库去重**
   - 检查发现 4 条完全重复的记录
   - 生成了清理后的文件 `knowledge_base_rag_clean.json`
   - 保留 1,402 条记录（每个独特内容至少保留 1 条）

## 🚀 后续待办任务

### 1. 生成 1024 维向量 🔴 高优先级
**目标**：为所有知识库记录生成正确的 1024 维向量

**可选方案**：
- **方案 A**：使用 Edge Function `generate-embeddings`
  ```bash
  # 在 Supabase Dashboard 中调用 Edge Function
  # 或使用 curl 调用
  curl -X POST 'https://mulrkyqqhaustbojzzes.supabase.co/functions/v1/generate-embeddings' \
    -H 'Authorization: Bearer YOUR_SERVICE_ROLE_KEY' \
    -H 'Content-Type: application/json' \
    -d '{"limit": 100}'
  ```

- **方案 B**：使用 Python 脚本
  ```bash
  cd "/Users/martinlau/Desktop/claude test/pdf-processing"
  python3 fix_vectors_final_working.py
  ```

- **方案 C**：使用 Supabase 批量导入
  - 在本地生成所有向量
  - 通过 Supabase SQL 或 API 批量更新

**注意事项**：
- 使用正确的参数：`dimension: 1024` (单数形式)
- 控制请求频率（阿里云限制：QPS=20）
- 验证向量维度是否正确

### 2. 验证向量生成结果 🟡 中优先级
```sql
-- 检查向量生成进度
SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embedding,
    COUNT(CASE WHEN embedding IS NULL THEN 1 END) as without_embedding,
    ROUND(
        (COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)),
        2
    ) as percentage
FROM knowledge_base;
```

### 3. 测试 RAG 搜索功能 🟡 中优先级
- 使用清理后的知识库进行测试
- 验证搜索结果是否包含《梅花易数》的内容
- 测试不同类型的查询（卦象、解梦、手相、星座等）

### 4. 优化搜索参数 🟢 低优先级
- 根据测试结果调整：
  - `threshold`：相似度阈值（当前 0.5）
  - `limit`：返回结果数量（当前 5）
  - 可能需要为不同类别设置不同的阈值

### 5. 监控和维护 🟢 低优先级
- 设置向量生成失败重试机制
- 监控 API 使用量和成本
- 定期检查数据库性能

## 📁 重要文件位置

### 知识库文件
- 原始文件：`/Users/martinlau/Desktop/claude test/pdf-processing/output/knowledge_base_rag.json`
- 清理后文件：`/Users/martinlau/Desktop/claude test/pdf-processing/output/knowledge_base_rag_clean.json`

### Python 脚本
- `fix_vectors_final_working.py` - 使用正确参数的向量生成脚本
- `generate_all_embeddings.py` - 批量生成向量脚本
- `remove_duplicates.py` - 去重脚本

### Edge Functions
- `supabase/functions/rag-search/index_fixed.ts` - 修复后的 RAG 搜索
- `supabase/functions/ai-chat-with-rag/index_lower_threshold.ts` - 降低阈值的 AI 聊天
- `supabase/functions/generate-embeddings/index.ts` - 向量生成函数

### SQL 脚本
- `check_record_count.sql` - 检查记录数量的 SQL

## 💡 关键提醒

1. **API 参数必须使用单数形式**：`dimension: 1024`，不是 `dimensions`
2. **向量维度必须匹配数据库**：PostgreSQL 列定义为 `VECTOR(1024)`
3. **控制 API 调用频率**：添加 `sleep(0.2)` 避免触发限制
4. **验证向量维度**：生成后检查是否真的是 1024 维
5. **使用清理后的知识库**：`knowledge_base_rag_clean.json`

## 🔗 相关文档

- [阿里云 text-embedding-v4 文档](https://help.aliyun.com/zh/model-studio/developer-reference/text-embedding-v4-api)
- [Supabase pgvector 指南](https://supabase.com/docs/guides/ai/vector-embeddings)
- [RAG 搜索最佳实践](https://supabase.com/docs/guides/ai/ai-assistants/quickstarts/chatgpt-plugin)