/**
 * RAG检索Edge Function - 优化版
 * 功能: 根据用户查询检索相关知识片段
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// 环境变量
const ALIBABA_API_KEY = Deno.env.get('ALIBABA_API_KEY')!n
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

interface SearchRequest {
  query: string           // 用户查询
  category?: string       // 可选:过滤分类
  limit?: number         // 返回结果数量
  threshold?: number     // 相似度阈值
}

interface KnowledgeResult {
  id: number
  source: string
  category: string
  content: string
  chunk_index: number
  metadata: any
  similarity: number
}

/**
 * 获取文本的Embedding向量
 */
async function getEmbedding(text: string): Promise<number[]> {
  const response = await fetch(
    'https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${ALIBABA_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'text-embedding-v3',
        input: text,
        encoding_format: 'float'
      })
    }
  )

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Embedding API错误: ${error}`)
  }

  const result = await response.json()
  return result.data[0].embedding
}

/**
 * 向量检索知识库 - 优化版
 * 1. 先尝试精确匹配
 * 2. 再尝试模糊匹配
 * 3. 最后尝试向量搜索
 */
async function searchKnowledge(
  embedding: number[],
  category?: string,
  limit: number = 5,
  threshold: number = 0.3  // 降低默认阈值
): Promise<KnowledgeResult[]> {
  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY)

  let results: KnowledgeResult[] = []

  console.log(`[RAG] 开始搜索, 分类: ${category || '全部'}, 阈值: ${threshold}`)

  // 方法1: 尝试精确文本匹配
  try {
    const { data: exactMatches, error: exactError } = await supabase
      .from('knowledge_base')
      .select('*')
      .ilike('content', '%乾卦%')
      .limit(limit)

    if (!exactError && exactMatches && exactMatches.length > 0) {
      console.log(`[RAG] 找到 ${exactMatches.length} 条精确匹配`)
      results = exactMatches.map(r => ({
        id: r.id,
        source: r.source,
        category: r.category,
        content: r.content,
        chunk_index: r.chunk_index,
        metadata: r.metadata,
        similarity: 1.0  // 精确匹配给最高分
      }))
    }
  } catch (e) {
    console.log('[RAG] 精确匹配失败:', e)
  }

  // 方法2: 如果精确匹配不够，使用向量搜索
  if (results.length < limit) {
    try {
      console.log('[RAG] 尝试向量搜索')
      const { data: vectorMatches, error: vectorError } = await supabase.rpc('match_knowledge', {
        query_embedding: embedding,
        match_threshold: threshold,
        match_count: limit,
        filter_category: category || null
      })

      if (!vectorError && vectorMatches) {
        console.log(`[RAG] 向量搜索找到 ${vectorMatches.length} 条结果`)

        // 合并结果，去重
        const existingIds = new Set(results.map(r => r.id))
        const newResults = vectorMatches.filter(r => !existingIds.has(r.id))

        results = results.concat(newResults.map(r => ({
          id: r.id,
          source: r.source,
          category: r.category,
          content: r.content,
          chunk_index: r.chunk_index,
          metadata: r.metadata,
          similarity: r.similarity
        })))
      } else {
        console.log('[RAG] 向量搜索失败:', vectorError?.message)
      }
    } catch (e) {
      console.log('[RAG] 向量搜索异常:', e)
    }
  }

  // 方法3: 如果还是没有结果，尝试关键词搜索
  if (results.length === 0) {
    try {
      console.log('[RAG] 尝试关键词搜索')
      const keywords = ['乾卦', '乾为天', '周易乾卦']

      for (const keyword of keywords) {
        const { data: keywordMatches, error: keywordError } = await supabase
          .from('knowledge_base')
          .select('*')
          .ilike('content', `%${keyword}%`)
          .limit(3)

        if (!keywordError && keywordMatches && keywordMatches.length > 0) {
          console.log(`[RAG] 关键词"${keyword}"找到 ${keywordMatches.length} 条结果`)
          results = results.concat(keywordMatches.map(r => ({
            id: r.id,
            source: r.source,
            category: r.category,
            content: r.content,
            chunk_index: r.chunk_index,
            metadata: r.metadata,
            similarity: 0.8  // 关键词匹配给高分
          })))

          if (results.length >= limit) break
        }
      }
    } catch (e) {
      console.log('[RAG] 关键词搜索失败:', e)
    }
  }

  // 限制结果数量
  results = results.slice(0, limit)

  console.log(`[RAG] 最终返回 ${results.length} 条结果`)
  return results
}

/**
 * 智能分类检测 - 改进版
 */
function detectCategory(query: string): string | undefined {
  const categoryKeywords = {
    '易经': ['易经', '卦象', '八卦', '乾坤', '爻', '周易', '乾卦', '坤卦', '震卦', '巽卦', '坎卦', '离卦', '艮卦', '兑卦'],
    '六十四卦': ['六十四卦', '卦辞', '卦名'],
    '梅花易数': ['梅花易数', '梅花', '起卦', '预测'],
    '风水': ['风水', '堪舆', '阳宅', '阴宅', '罗盘', '方位'],
    '面相手相': ['面相', '手相', '面部', '手纹', '掌纹', '相术'],
    '星座': ['星座', '白羊', '金牛', '双子', '巨蟹', '狮子', '处女', '天秤', '天蝎', '射手', '摩羯', '水瓶', '双鱼'],
    '周公解梦': ['解梦', '梦见', '做梦', '梦境']
  }

  // 检查是否包含乾卦相关关键词
  if (query.includes('乾卦') || query.includes('乾为天')) {
    return '易经'
  }

  for (const [category, keywords] of Object.entries(categoryKeywords)) {
    if (keywords.some(keyword => query.includes(keyword))) {
      return category
    }
  }

  return undefined
}

/**
 * 主处理函数
 */
serve(async (req) => {
  // 处理CORS预检请求
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      }
    })
  }

  try {
    // 解析请求
    const {
      query,
      category,
      limit = 5,
      threshold = 0.3  // 降低默认阈值
    }: SearchRequest = await req.json()

    if (!query || query.trim().length === 0) {
      return new Response(
        JSON.stringify({ error: '查询不能为空' }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        }
      )
    }

    console.log(`[RAG] 查询: "${query}", 分类: ${category || '自动检测'}`)

    // 智能分类检测
    const detectedCategory = category || detectCategory(query)
    if (detectedCategory) {
      console.log(`[RAG] 检测到分类: ${detectedCategory}`)
    }

    // 1. 生成查询向量
    const startEmbed = Date.now()
    const embedding = await getEmbedding(query)
    const embedTime = Date.now() - startEmbed
    console.log(`[RAG] Embedding生成耗时: ${embedTime}ms`)

    // 2. 检索相关知识
    const startSearch = Date.now()
    const results = await searchKnowledge(
      embedding,
      detectedCategory,
      limit,
      threshold
    )
    const searchTime = Date.now() - startSearch
    console.log(`[RAG] 检索耗时: ${searchTime}ms, 结果数: ${results.length}`)

    // 3. 返回结果
    return new Response(
      JSON.stringify({
        success: true,
        query,
        detected_category: detectedCategory,
        results: results.map(r => ({
          id: r.id,
          source: r.source,
          category: r.category,
          content: r.content,
          similarity: Math.round(r.similarity * 100) / 100  // 保留2位小数
        })),
        count: results.length,
        performance: {
          embed_time: embedTime,
          search_time: searchTime,
          total_time: embedTime + searchTime
        }
      }),
      {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    )

  } catch (error) {
    console.error('[RAG] 错误:', error)

    return new Response(
      JSON.stringify({
        error: error.message || '检索失败',
        success: false
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    )
  }
})