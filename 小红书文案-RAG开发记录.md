之前分享过一篇3小时上线AI对话网站的方法，这次和大家分享一下部署专属知识库的方法，我在图片里面也贴了示例代码。通过部署知识库，我们可以定制化AI的回复。

按照上面的流程走下来，差不多1小时左右可以完成。注：这是通用的部署知识库的方法，不限于玄学，任何知识领域都能用。

过200赞更新：如何快速上线一款APP

📚 知识库准备

《周公解梦》、《易经》、《周易六十四卦全解》、《梅花易数-宋-邵雍》、《面相手相》、《十二星座运势解析》、《风水学入门》

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

📝 核心代码分享

1️⃣ 向量生成代码

// 生成1024维向量

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

        input: [text],

        dimensions: 1024  

      })

    }

  )
const result = await response.json()

return result.data[0].embedding

}

// 使用示例 - 玄学领域

const inputText = "梦见蛇是吉兆还是凶兆？"

const embedding = await getEmbedding(inputText)

console.log(`向量维度: ${embedding.length}`)  // 输出: 向量维度: 1024

// 批量生成向量

for (const text of fortuneTexts) {

const vector = await getEmbedding(text)

  console.log(`"${text}" -> 向量长度: ${vector.length}`)

}

2️⃣ 向量检索SQL函数

-- 在Supabase执行这个SQL

CREATE OR REPLACE FUNCTION match_knowledge(

  query_embedding VECTOR(1024),  -- 根据你的向量维度调整

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

3️⃣ RAG增强的AI聊天

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

let knowledgeContext = '\n\n📚 相关PDF文件：\n'

  knowledge.forEach(item => {

    knowledgeContext += `【${item.source}】${item.content}\n`

  })

// 5. 注入到system消息

  messages[0].content += knowledgeContext

// 6. 调用AI生成回答

// ... AI调用代码

}