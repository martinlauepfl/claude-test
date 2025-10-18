// Supabase Edge Function: 创建 Stripe Checkout Session
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import Stripe from 'https://esm.sh/stripe@14.11.0?target=deno'

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
    const STRIPE_SECRET_KEY = Deno.env.get('STRIPE_SECRET_KEY')
    const STRIPE_PRICE_ID_CNY = Deno.env.get('STRIPE_PRICE_ID_CNY')  // ¥4.99
    const STRIPE_PRICE_ID_USD = Deno.env.get('STRIPE_PRICE_ID_USD')  // $0.99

    if (!STRIPE_SECRET_KEY || !STRIPE_PRICE_ID_CNY || !STRIPE_PRICE_ID_USD) {
      throw new Error('Stripe configuration missing')
    }

    // 初始化 Stripe
    const stripe = new Stripe(STRIPE_SECRET_KEY, {
      apiVersion: '2023-10-16',
      httpClient: Stripe.createFetchHttpClient(),
    })

    // 获取请求数据
    const { userId, userEmail, language } = await req.json()

    if (!userId || !userEmail) {
      throw new Error('Missing required fields')
    }

    // 根据语言选择价格ID
    const priceId = language === 'zh' ? STRIPE_PRICE_ID_CNY : STRIPE_PRICE_ID_USD

    // 创建 Checkout Session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: `${req.headers.get('origin')}?payment=success`,
      cancel_url: `${req.headers.get('origin')}?payment=cancel`,
      customer_email: userEmail,
      client_reference_id: userId,
      metadata: {
        userId: userId,
        quotaToAdd: '50',
      },
    })

    return new Response(
      JSON.stringify({ sessionId: session.id }),
      {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      }
    )
  } catch (error) {
    console.error('Stripe checkout error:', error)
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
