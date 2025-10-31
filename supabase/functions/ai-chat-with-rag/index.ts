/**
 * AI聊天Edge Function (集成RAG)
 * 功能: 先检索知识库,再调用AI生成回答
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

// 环境变量
const ALIBABA_API_KEY = Deno.env.get('ALIBABA_API_KEY')!
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

interface Message {
  role: 'system' | 'user' | 'assistant'
  content: string
}

interface KnowledgeResult {
  source: string
  category: string
  content: string
  similarity: number
}

/**
 * 调用RAG检索相关知识
 */
async function searchRelevantKnowledge(userMessage: string): Promise<KnowledgeResult[]> {
  try {
    const response = await fetch(
      `${SUPABASE_URL}/functions/v1/rag-search`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`
        },
        body: JSON.stringify({
          query: userMessage,
          limit: 3,        // 取前3个最相关的片段
          threshold: 0.75  // 提高阈值,只要高质量匹配
        })
      }
    )

    if (!response.ok) {
      console.error(`[RAG] 检索失败: ${response.status}`)
      return []
    }

    const { results, detected_category } = await response.json()

    if (results && results.length > 0) {
      console.log(`[RAG] 检索成功: ${results.length}个结果, 分类: ${detected_category}`)
      return results
    }

    return []

  } catch (error) {
    console.error('[RAG] 检索异常:', error)
    return []
  }
}

/**
 * 格式化知识片段为System Prompt
 */
function formatKnowledgeContext(results: KnowledgeResult[]): string {
  if (results.length === 0) {
    return ''
  }

  const knowledgeParts = results.map((r, i) => {
    return `【古籍${i+1}: ${r.source} - ${r.category}】\n${r.content}`
  })

  return `\n\n【参考古籍知识】\n以下是与问题相关的古籍内容,请作为参考基础:\n\n${knowledgeParts.join('\n\n---\n\n')}\n\n请基于以上古籍知识回答用户问题,保持专业性和准确性。`
}

/**
 * 增强System Prompt
 */
function enhanceSystemPrompt(originalPrompt: string, knowledge: string): string {
  if (!knowledge) {
    return originalPrompt
  }

  // 在原有prompt后追加知识库内容
  return originalPrompt + knowledge
}

/**
 * 提取用户最新消息
 */
function getLatestUserMessage(messages: Message[]): string {
  for (let i = messages.length - 1; i >= 0; i--) {
    if (messages[i].role === 'user') {
      return messages[i].content
    }
  }
  return ''
}

/**
 * 主处理函数
 */
serve(async (req) => {
  // 处理CORS预检
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    if (!ALIBABA_API_KEY) {
      throw new Error('API Key未配置')
    }

    // 获取请求数据
    const { messages } = await req.json()

    if (!messages || messages.length === 0) {
      throw new Error('消息不能为空')
    }

    // 1. 提取用户最新问题
    const userMessage = getLatestUserMessage(messages)
    console.log(`[AI-Chat] 用户问题: "${userMessage.substring(0, 50)}..."`)

    // 2. RAG检索相关知识
    const startRag = Date.now()
    const knowledgeResults = await searchRelevantKnowledge(userMessage)
    const ragTime = Date.now() - startRag
    console.log(`[AI-Chat] RAG检索耗时: ${ragTime}ms, 结果: ${knowledgeResults.length}个`)

    // 3. 格式化知识上下文
    const knowledgeContext = formatKnowledgeContext(knowledgeResults)

    // 4. 增强System Prompt
    let enhancedMessages = [...messages]

    // 找到system消息并增强
    const systemIndex = enhancedMessages.findIndex(m => m.role === 'system')
    if (systemIndex >= 0 && knowledgeContext) {
      enhancedMessages[systemIndex] = {
        ...enhancedMessages[systemIndex],
        content: enhanceSystemPrompt(enhancedMessages[systemIndex].content, knowledgeContext)
      }
      console.log(`[AI-Chat] System Prompt已增强,长度: ${enhancedMessages[systemIndex].content.length}`)
    } else if (knowledgeContext) {
      // 如果没有system消息,在开头添加
      enhancedMessages = [
        {
          role: 'system',
          content: knowledgeContext
        },
        ...enhancedMessages
      ]
    }

    // 5. 调用阿里云AI (流式输出)
    const startAi = Date.now()
    const response = await fetch(
      'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${ALIBABA_API_KEY}`
        },
        body: JSON.stringify({
          model: 'qwen-max',
          messages: enhancedMessages,
          stream: true
        })
      }
    )

    if (!response.ok) {
      throw new Error(`AI API错误: ${response.status}`)
    }

    console.log(`[AI-Chat] AI调用成功, 开始流式返回`)

    // 6. 返回流式响应
    return new Response(response.body, {
      headers: {
        ...corsHeaders,
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      }
    })

  } catch (error) {
    console.error('[AI-Chat] 错误:', error)

    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      }
    )
  }
})
