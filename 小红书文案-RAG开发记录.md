让AI真的学会算命，RAG知识库部署教程
之前花了一晚上做了AI算命网站，这次用一周时间升级了RAG知识库，现在AI的回答有理有据，再也不是瞎编了。按照下面的流程，大家实操下来，应该在一小时左右。
	
⚠️ 这是通用的RAG部署教程，不限于玄学，任何知识领域都能用！
	
📚 知识库准备（7本玄学书籍）
- 《周公解梦》 → 617条解梦智慧
- 《易经[周易]》 → 111条易经精髓
- 《周易六十四卦全解》 → 133条卦象详解
- 《梅花易数-宋-邵雍》 → 98条占卜秘法
- 《面相手相》 → 245条相术知识
- 《十二星座运势解析》 → 127条星座运势
- 《风水学入门》 → 75条风水理论
	
🛠️ 技术栈（全部免费或低成本）
- 前端：HTML文件
- 后端：Supabase（免费额度）
- 向量数据库：Supabase pgvector
- AI对话大模型：qwen-max
- 文本信息向量化大模型：text-embedding-v4
- 部署：GitHub Pages免费托管 + Cloudflare加速
	
🚀 三步部署流程
1️⃣ PDF文字识别
交给Claude Code处理，一句话指令就帮我生成了1400多条知识点的JSON文件！OCR识别 + 去重 + 格式化，全自动完成。
	
2️⃣ 向量化
这里最关键！每条知识转成1024维向量：用text-embedding-v4模型，1400多条数据仅需5分钟。
	
3️⃣ 创建检索系统
在Supabase创建Edge Function，直接复制下面的核心代码！

📝 **核心代码分享**（直接复制可用）：

**1️⃣ 向量生成代码**（阿里云官方示例）
```typescript
// 生成1024维向量 - 基于阿里云官方示例改写
async function getEmbedding(text: string) {
  const response = await fetch(
    'https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${DASHSCOPE_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'text-embedding-v4',
        input: text,
        // ⚠️ 注意：text-embedding-v4模型不需要手动指定dimension参数！
        // 模型会自动生成1024维向量
      })
    }
  )

  const result = await response.json()
  console.log('向量结果:', JSON.stringify(result, null, 2))
  return result.data[0].embedding
}

// 使用示例
const inputText = "衣服的质量杠杠的"
const embedding = await getEmbedding(inputText)
console.log('向量长度:', embedding.length)  // 输出: 1024
```

**2️⃣ 向量检索SQL函数**
```sql
-- 在Supabase执行这个SQL
CREATE OR REPLACE FUNCTION match_knowledge(
  query_embedding VECTOR(1024),
  match_threshold FLOAT DEFAULT 0.5,
  match_count INT DEFAULT 3
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
    1 - (kb.embedding <=> query_embedding) AS similarity
  FROM knowledge_base kb
  WHERE
    1 - (kb.embedding <=> query_embedding) > match_threshold
  ORDER BY kb.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

**3️⃣ RAG增强的AI聊天**
```typescript
// 先检索知识，再调用AI
async function chatWithRAG(messages) {
  // 1. 获取用户问题
  const userMessage = messages[messages.length - 1].content

  // 2. 生成查询向量
  const embedding = await getEmbedding(userMessage)

  // 3. 检索相关知识
  const { data: knowledge } = await supabase
    .rpc('match_knowledge', {
      query_embedding: embedding,
      match_threshold: 0.5,
      match_count: 3
    })

  // 4. 构建带知识的prompt
  let knowledgeContext = '\n\n📚 相关古籍：\n'
  knowledge.forEach(item => {
    knowledgeContext += `【${item.source}】${item.content}\n`
  })

  // 5. 注入到system消息
  messages[0].content += knowledgeContext

  // 6. 调用AI生成回答
  // ... AI调用代码
}
```
	
🎪 踩坑经验（血泪教训！）
1️⃣ 相似度阈值
一开始设0.75，啥都搜不到，设为0.5，效果完美。
2️⃣ 401认证错误
单独调用RAG函数总是401，后来把RAG检索直接集成到ai-chat函数里，终于成功了。
3️⃣ 参数名错误
dimensions（复数）❌
dimension（单数）✅
就差一个字母，卡了我3天！
	
🎉 成果展示
- AI现在能回复时自动引用知识库原文。
- 每句话都可以标注出处，有理有据。
	
如果你也喜欢用代码做一些有趣的事，点个赞让我看到你！
	
#AI工具 #人工智能 #算法 #大模型 #个人开发者 #一人公司