# Stripe 支付集成指南

## 🎉 代码已集成完成！

前端和后端代码已经准备好，现在需要你完成以下配置步骤。

## 架构说明

我们使用 Stripe Checkout 模式，这是最安全和简单的集成方式：

1. **前端**：使用 Stripe.js 创建 Checkout Session
2. **后端**：Supabase Edge Function 创建支付会话和处理 Webhook
3. **流程**：
   - 用户点击支付 → 调用 Edge Function → 创建 Stripe Checkout Session
   - 跳转到 Stripe 支付页面 → 用户完成支付
   - Stripe 发送 Webhook → Edge Function 更新用户配额

## 定价设置

- 🇨🇳 中国用户：¥4.99 CNY = 50次对话
- 🌎 海外用户：$0.99 USD = 50次对话

---

## 第一步：获取 Stripe API 密钥

1. 登录 Stripe Dashboard：https://dashboard.stripe.com/
2. 点击 **Developers** → **API keys**
3. 复制以下密钥：
   - **Publishable key** (pk_test_... 或 pk_live_...)
   - **Secret key** (sk_test_... 或 sk_live_...)

⚠️ 建议先使用测试模式（test keys），确认一切正常后再切换到生产模式。

## 第二步：配置 Stripe 产品和价格

你需要在 Stripe 中创建两个产品价格：

### 产品 1：中国用户（CNY）

1. 在 Stripe Dashboard 点击 **Products** → **Add product**
2. 填写产品信息：
   - **Name**: AI Fortune - 50 Conversations (China)
   - **Description**: 解锁50次AI算命对话
   - **Price**: ¥4.99
   - **Currency**: CNY
   - **Billing**: One time（一次性支付）
3. 点击 **Save product**
4. **复制 Price ID**（格式：price_xxxxx）→ 记为 `PRICE_ID_CNY`

### 产品 2：海外用户（USD）

1. 点击 **Products** → **Add product**（或在刚才的产品中添加新价格）
2. 填写产品信息：
   - **Name**: AI Fortune - 50 Conversations (International)
   - **Description**: Unlock 50 AI fortune telling conversations
   - **Price**: $0.99
   - **Currency**: USD
   - **Billing**: One time
3. 点击 **Save product**
4. **复制 Price ID**（格式：price_xxxxx）→ 记为 `PRICE_ID_USD`

## 第三步：在 Supabase 设置环境变量

1. 访问 Supabase Dashboard：https://supabase.com/dashboard/project/mulrkyqqhaustbojzzes
2. 点击 **Settings** → **Edge Functions** → **Secrets**
3. 添加以下 Secrets（点击 **Add new secret**）：

   | Secret Name | Secret Value | 说明 |
   |------------|--------------|------|
   | `STRIPE_SECRET_KEY` | `sk_live_51SJTJ8...`（你的 Stripe Secret Key） | Stripe Secret Key |
   | `STRIPE_PRICE_ID_CNY` | `price_xxxxx`（你的CNY价格ID） | 中国用户价格ID ¥4.99 |
   | `STRIPE_PRICE_ID_USD` | `price_xxxxx`（你的USD价格ID） | 海外用户价格ID $0.99 |
   | `STRIPE_WEBHOOK_SECRET` | `whsec_xxxxx`（稍后获取） | Webhook签名密钥 |

⚠️ **重要**: 不要分享或提交这些密钥到代码仓库！

## 第四步：部署 Supabase Edge Functions

需要部署两个 Edge Functions：

### 1. stripe-checkout (处理支付请求)

1. 访问 Supabase Dashboard → **Edge Functions**
2. 点击 **Create a new function**
3. **Function name**: `stripe-checkout`
4. 复制代码：打开本地文件 `supabase/functions/stripe-checkout/index.ts`
5. 将全部代码粘贴到编辑器中
6. 点击 **Deploy**

### 2. stripe-webhook (处理 Stripe 回调)

1. 点击 **Create a new function**
2. **Function name**: `stripe-webhook`
3. 复制代码：打开本地文件 `supabase/functions/stripe-webhook/index.ts`
4. 将全部代码粘贴到编辑器中
5. 点击 **Deploy**

## 第五步：配置 Stripe Webhook

1. 在 Stripe Dashboard 点击 **Developers** → **Webhooks**
2. 点击 **Add endpoint**
3. 填写：
   - **Endpoint URL**: `https://mulrkyqqhaustbojzzes.supabase.co/functions/v1/stripe-webhook`
   - **Events to send**: 选择 `checkout.session.completed`
4. 创建后，复制 **Signing secret**（whsec_...）
5. 将这个 secret 添加到 Supabase Secrets（`STRIPE_WEBHOOK_SECRET`）

## 第六步：更新前端代码

在 `index.html` 中：
1. 引入 Stripe.js
2. 替换 `handlePayment()` 函数
3. 添加支付成功回调处理

## 测试支付

使用 Stripe 测试卡号：
- **成功支付**: 4242 4242 4242 4242
- **需要验证**: 4000 0025 0000 3155
- **支付失败**: 4000 0000 0000 9995
- 过期日期：任何未来日期（如 12/34）
- CVV：任意3位数字

## 安全注意事项

✅ Publishable Key 可以放在前端
✅ Secret Key 只能放在 Supabase Edge Function 环境变量中
✅ 使用 Webhook 验证支付（不要只依赖前端回调）
✅ 所有配额更新必须在 Webhook 中完成
