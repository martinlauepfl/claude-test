// Supabase Edge Function: 阿里云语音合成 (TTS)
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createHmac } from "https://deno.land/std@0.168.0/node/crypto.ts"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // 处理 CORS 预检请求
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // 获取环境变量
    const ALIBABA_APP_KEY = Deno.env.get('ALIBABA_APP_KEY')
    const ALIBABA_ACCESS_KEY_ID = Deno.env.get('ALIBABA_ACCESS_KEY_ID')
    const ALIBABA_ACCESS_KEY_SECRET = Deno.env.get('ALIBABA_ACCESS_KEY_SECRET')

    if (!ALIBABA_APP_KEY || !ALIBABA_ACCESS_KEY_ID || !ALIBABA_ACCESS_KEY_SECRET) {
      throw new Error('Alibaba Cloud credentials missing')
    }

    // 获取请求数据
    const { text, voice = 'zhixiaobai' } = await req.json()

    if (!text) {
      throw new Error('Text is required')
    }

    // 阿里云语音合成API参数
    const url = 'https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts'

    const params = {
      appkey: ALIBABA_APP_KEY,
      token: '', // 使用AccessKey方式,token留空
      text: text,
      format: 'mp3',
      sample_rate: 16000,
      voice: voice, // 可选: zhixiaobai(知小白), aicheng(艾诚), etc.
      volume: 50,
      speech_rate: 0, // 语速,0为正常
      pitch_rate: 0, // 音调,0为正常
    }

    // 构建查询参数
    const queryString = new URLSearchParams(params).toString()
    const requestUrl = `${url}?${queryString}`

    // 发送请求到阿里云
    const response = await fetch(requestUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Alibaba TTS API error: ${errorText}`)
    }

    // 获取音频数据
    const audioBuffer = await response.arrayBuffer()

    // 返回音频数据
    return new Response(audioBuffer, {
      headers: {
        ...corsHeaders,
        'Content-Type': 'audio/mpeg',
        'Content-Length': audioBuffer.byteLength.toString(),
      }
    })

  } catch (error) {
    console.error('TTS error:', error)
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
