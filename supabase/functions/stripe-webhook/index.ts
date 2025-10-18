// Supabase Edge Function: 处理 Stripe Webhook
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import Stripe from 'https://esm.sh/stripe@14.11.0?target=deno'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.7'

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
    const STRIPE_WEBHOOK_SECRET = Deno.env.get('STRIPE_WEBHOOK_SECRET')
    const SUPABASE_URL = Deno.env.get('SUPABASE_URL')
    const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

    if (!STRIPE_SECRET_KEY || !STRIPE_WEBHOOK_SECRET || !SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
      throw new Error('Configuration missing')
    }

    // 初始化 Stripe
    const stripe = new Stripe(STRIPE_SECRET_KEY, {
      apiVersion: '2023-10-16',
      httpClient: Stripe.createFetchHttpClient(),
    })

    // 初始化 Supabase Admin 客户端
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    // 验证 Webhook 签名
    const signature = req.headers.get('stripe-signature')
    const body = await req.text()

    let event
    try {
      event = stripe.webhooks.constructEvent(body, signature!, STRIPE_WEBHOOK_SECRET)
    } catch (err) {
      console.error('Webhook signature verification failed:', err.message)
      return new Response(
        JSON.stringify({ error: 'Webhook signature verification failed' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // 处理 checkout.session.completed 事件
    if (event.type === 'checkout.session.completed') {
      const session = event.data.object as Stripe.Checkout.Session

      const userId = session.metadata?.userId || session.client_reference_id
      const quotaToAdd = parseInt(session.metadata?.quotaToAdd || '50')
      const amountTotal = session.amount_total ? session.amount_total / 100 : 0
      const currency = session.currency || 'usd'

      if (!userId) {
        console.error('No userId in session metadata')
        return new Response(
          JSON.stringify({ error: 'No userId found' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
      }

      console.log(`Payment successful for user ${userId}, adding ${quotaToAdd} quota`)

      // 获取当前用户配额
      const { data: currentQuota, error: fetchError } = await supabase
        .from('user_quotas')
        .select('*')
        .eq('user_id', userId)
        .single()

      if (fetchError) {
        console.error('Error fetching user quota:', fetchError)
        throw fetchError
      }

      // 更新用户配额
      const { error: updateError } = await supabase
        .from('user_quotas')
        .update({
          quota: currentQuota.quota + quotaToAdd,
          total_purchased: currentQuota.total_purchased + quotaToAdd,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)

      if (updateError) {
        console.error('Error updating user quota:', updateError)
        throw updateError
      }

      // 记录支付记录
      const { error: recordError } = await supabase
        .from('payment_records')
        .insert({
          user_id: userId,
          amount: amountTotal,
          currency: currency,
          quota_added: quotaToAdd,
          payment_method: 'stripe',
          stripe_session_id: session.id,
          status: 'completed'
        })

      if (recordError) {
        console.error('Error recording payment:', recordError)
        // 不抛出错误，因为配额已经更新成功
      }

      console.log(`Successfully updated quota for user ${userId}`)
    }

    return new Response(
      JSON.stringify({ received: true }),
      {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      }
    )
  } catch (error) {
    console.error('Webhook error:', error)
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
