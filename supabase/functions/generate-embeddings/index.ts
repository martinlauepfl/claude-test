/**
 * 批量生成向量的Edge Function
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const ALIBABA_API_KEY = Deno.env.get('ALIBABA_API_KEY')!
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

/**
 * 生成单个文本的向量
 */
async function generateEmbedding(text: string): Promise<number[]> {
  const response = await fetch(
    'https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${ALIBABA_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'text-embedding-v4',
        input: text,
        dimension: 1024,
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

serve(async (req) => {
  // 处理CORS
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
      }
    })
  }

  try {
    const { limit = 10 } = await req.json()

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    // 获取没有向量的记录
    const { data: records, error } = await supabase
      .from('knowledge_base')
      .select('id, content')
      .is('embedding', 'null')
      .limit(limit)

    if (error) throw error

    if (!records || records.length === 0) {
      return new Response(
        JSON.stringify({ message: '所有记录都已有向量' }),
        { headers: { 'Content-Type': 'application/json' } }
      )
    }

    // 批量生成向量
    let success = 0
    let failed = 0

    for (const record of records) {
      try {
        const embedding = await generateEmbedding(record.content || '')

        const { error: updateError } = await supabase
          .from('knowledge_base')
          .update({ embedding })
          .eq('id', record.id)

        if (!updateError) {
          success++
        } else {
          failed++
        }
      } catch (e) {
        failed++
        console.error(`更新记录 ${record.id} 失败:`, e)
      }

      // 避免超限
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    return new Response(
      JSON.stringify({
        success: true,
        message: `成功更新 ${success} 条记录，失败 ${failed} 条`,
        processed: records.length
      }),
      { headers: { 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
})