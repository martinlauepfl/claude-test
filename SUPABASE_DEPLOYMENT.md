# Supabase Edge Function 部署指南（网页版 - 无需 CLI）

## 第一步：登录 Supabase Dashboard

1. 访问 https://supabase.com/dashboard
2. 登录你的账号
3. 选择项目 `mulrkyqqhaustbojzzes`

## 第二步：创建 Edge Function

1. 点击左侧菜单的 **"Edge Functions"**
2. 点击右上角 **"Create a new function"**
3. Function name 输入：`ai-chat`
4. 点击 **"Create function"**

## 第三步：粘贴代码

在代码编辑器中，删除所有默认代码，粘贴以下内容：

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const API_KEY = Deno.env.get('ALIBABA_API_KEY')
    if (!API_KEY) {
      throw new Error('API Key not configured')
    }

    const { messages } = await req.json()

    const response = await fetch('https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        model: 'qwen-plus',
        messages: messages
      })
    })

    const data = await response.json()

    return new Response(
      JSON.stringify(data),
      {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      }
    )
  } catch (error) {
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
```

点击 **"Deploy"** 按钮。

## 第四步：设置环境变量（重要！）

1. 在左侧菜单点击 **"Edge Functions"**
2. 找到刚创建的 `ai-chat` function，点击进入
3. 点击 **"Settings"** 标签
4. 找到 **"Secrets"** 部分
5. 点击 **"Add new secret"**
6. 输入：
   - Secret name: `ALIBABA_API_KEY`
   - Secret value: `sk-dd0415392eba4dd1856f2b29560b0035`
7. 点击 **"Save"**

## 第五步：验证部署

部署完成后，你的 Edge Function URL 是：
```
https://mulrkyqqhaustbojzzes.supabase.co/functions/v1/ai-chat
```

前端代码已经配置好了这个 URL，无需修改。

## 第六步：提交并推送到 GitHub

```bash
git add .
git commit -m "使用 Supabase Edge Function 保护 API keys"
git push
```

## 测试

访问 www.ai-fortune.top 测试对话功能。

---

## 费用说明

Supabase 免费套餐：
- 每月 500,000 次 Edge Function 调用
- 完全够用

## 安全性

✅ API Key 存储在 Supabase Secrets 中，加密保存
✅ 用户浏览器无法看到 API Key
✅ GitHub 代码中不包含任何密钥
✅ 所有服务在同一个平台，管理更方便
