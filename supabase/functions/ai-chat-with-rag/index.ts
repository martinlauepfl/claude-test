/**
 * AI聊天Edge Function (集成RAG)
 * 功能: 先检索知识库,再调用AI生成回答
 */
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';  // 🔥 新增

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
};

// 环境变量
const ALIBABA_API_KEY = Deno.env.get('ALIBABA_API_KEY');
const SUPABASE_URL = Deno.env.get('SUPABASE_URL');
const SUPABASE_SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

/**
 * 🔥🔥🔥 直接在本函数中实现 RAG 检索（避免 401 错误）
 */
async function searchRelevantKnowledge(userMessage) {
  try {
    console.log(`[RAG] 开始检索: "${userMessage}"`);

    // 1. 生成 embedding
    const embeddingResponse = await fetch('https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${ALIBABA_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'text-embedding-v4',
        input: userMessage,
        dimension: 1024,
        encoding_format: 'float'
      })
    });

    if (!embeddingResponse.ok) {
      console.error('[RAG] Embedding 生成失败');
      return [];
    }

    const embeddingData = await embeddingResponse.json();
    const embedding = embeddingData.data[0].embedding;

    console.log(`[RAG] Embedding 生成成功，长度: ${embedding.length}`);

    // 2. 向量检索
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

    const { data, error } = await supabase.rpc('match_knowledge', {
      query_embedding: embedding,
      match_threshold: 0.5,
      match_count: 3,
      filter_category: null
    });

    if (error) {
      console.error('[RAG] 向量检索失败:', error);
      return [];
    }

    console.log(`[RAG] 检索成功: ${data?.length || 0}个结果`);

    // 格式化返回数据
    return data?.map(item => ({
      id: item.id,
      source: item.source,
      category: item.category,
      content: item.content,
      similarity: item.similarity
    })) || [];

  } catch (error) {
    console.error('[RAG] 检索异常:', error);
    return [];
  }
}

/**
 * 主处理函数
 */
serve(async (req) => {
  // 处理CORS预检
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: corsHeaders
    });
  }

  try {
    if (!ALIBABA_API_KEY) {
      throw new Error('API Key未配置');
    }

    // 获取请求数据
    const { messages } = await req.json();

    if (!messages || messages.length === 0) {
      throw new Error('消息不能为空');
    }

    // 1. 提取用户最新问题
    const userMessage = messages[messages.length - 1].content;
    console.log(`[AI-Chat] 用户问题: "${userMessage.substring(0, 50)}..."`);

    // 2. RAG检索相关知识
    const startRag = Date.now();
    const knowledgeResults = await searchRelevantKnowledge(userMessage);
    const ragTime = Date.now() - startRag;
    console.log(`[AI-Chat] RAG检索耗时: ${ragTime}ms, 结果: ${knowledgeResults.length}个`);

    // 3. 将 RAG 检索结果注入到 AI 的上下文中
    if (knowledgeResults.length > 0) {
      console.log(`[AI-Chat] 使用知识库生成回答，共 ${knowledgeResults.length} 条知识`);

      // 🔥 关键修改：构建知识库上下文
      let knowledgeContext = '\n\n## 📚 相关古籍知识（请基于以下内容回答用户问题）\n\n';

      knowledgeResults.forEach((result, index) => {
        knowledgeContext += `【来源: ${result.source || '古籍'}】\n`;
        knowledgeContext += `${result.content}\n\n`;
        knowledgeContext += `---\n\n`;
      });

      knowledgeContext += `
请根据上述古籍内容，结合你的毒舌算命先生风格，给出专业且接地气的回答。

重要提示：
1. 在回答的【结尾】加上一行：「📚 此回答基于 ${knowledgeResults.length} 条古籍记载」
2. 如果古籍内容不够完整，可以适当补充，但要区分古籍原文和你的解读
`;

      // 🔥 将知识库内容添加到 system prompt
      messages[0].content += knowledgeContext;

      console.log('[AI-Chat] 知识库已注入到 system prompt');
    }

    // 4. 调用 AI（现在无论是否有知识库，都统一调用 AI）
    const response = await fetch('https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${ALIBABA_API_KEY}`
      },
      body: JSON.stringify({
        model: 'qwen-max',
        messages: messages,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`AI API错误: ${response.status}`);
    }

    console.log(`[AI-Chat] AI调用成功, 开始流式返回`);

    // 5. 返回流式响应
    return new Response(response.body, {
      headers: {
        ...corsHeaders,
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      }
    });

  } catch (error) {
    console.error('[AI-Chat] 错误:', error);
    return new Response(JSON.stringify({
      error: error.message
    }), {
      status: 500,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  }
});