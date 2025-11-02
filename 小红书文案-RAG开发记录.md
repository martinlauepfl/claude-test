# 🔮 玄机阁RAG系统开发小红书文案

## 我用1402本古籍让AI算命先生学会引用原文！技术宅的命理应用开发日记

大家好！今天分享一下我的AI算命应用"玄机阁"是怎么让AI学会引用古籍原文的～📚

## 📖 我用的知识库来源：
- 《周公解梦-第二版2003》（387页）- 617条解梦内容
- 《易经[周易]》（53页）- 111条易经智慧
- 《周易六十四卦全解》（72页）- 133条卦象详解
- 《梅花易数-宋-邵雍》（14页）- 98条占卜秘法
- 《面向·手相》（190页）- 245条相术知识
- 《十二星座运势解析》（30页）- 127条星座运势
- 《风水学入门基础知识》（75页）- 75条风水理论

总共1402条传统典籍知识！每条都生成了1024维向量embedding～

## 🛠 技术栈揭秘：
- **前端**：纯HTML单文件（75KB！）
- **后端**：Supabase Edge Functions
- **向量数据库**：pgvector + PostgreSQL
- **AI模型**：阿里云通义千问（qwen-max + text-embedding-v4）
- **部署**：GitHub Pages + Cloudflare CDN

## 🎯 RAG系统实现过程：

### 第一阶段：知识库准备
把PDF转成文本，然后去重清洗，确保每条知识都是唯一的。这里踩了不少坑，比如PDF的OCR识别错误、重复内容等。

### 第二阶段：向量化处理
用阿里云的text-embedding-v4模型生成1024维向量。注意！这里是dimension（单数）不是dimensions（复数），我一开始就卡在这里好几天😅

### 第三阶段：RAG检索系统
创建了一个RPC函数match_knowledge，用余弦相似度搜索相关内容。阈值设为0.5-0.7，返回最相关的3条知识。

### 第四阶段：AI集成（最难的部分！）
一开始调用单独的rag-search函数总是401错误，后来把RAG检索直接集成到ai-chat-with-rag函数里才解决。

现在AI能直接引用：
"梦见蛇是凶兆"
"梦见蛇咬你自己，要交好运"
"乾卦代表天，为纯阳之卦"

## 💡 关键代码实现：
```typescript
// 在ai-chat-with-rag函数里直接做RAG检索
const { data } = await supabase.rpc('match_knowledge', {
  query_embedding: embedding,
  match_threshold: 0.5,
  match_count: 3
});

// 把知识注入到系统提示词
let knowledgeContext = '\n\n## 📚 相关古籍知识\n\n';
knowledgeResults.forEach(result => {
  knowledgeContext += `【来源: ${result.source}】\n${result.content}\n\n`;
});
messages[0].content += knowledgeContext;
```

## 🌟 最终效果：
- AI回复时会引用古籍原文
- 自动标注知识来源
- Markdown渲染，层次分明
- 手机端完美适配（输入框不会遮挡！）

## 💰 成本：
- 域名：¥60/年
- Supabase：免费
- 阿里云API：月均¥50-100
- 总成本：<¥200/月

最开心的是看到用户说："这个AI真的懂古籍！" 💕

#AI开发 #RAG技术 #独立开发 #知识库 #算命应用 #技术分享 #GitHubPages #Supabase #通义千问

---

*发布时间：2025年11月2日*