# 🔄 更新 Stripe 价格配置

## 📋 价格变更说明

| 版本 | 中国用户 | 海外用户 |
|------|---------|---------|
| **旧价格** | ¥4.99 | $0.99 |
| **新价格** | ¥9.99 | $2.99 |

**购买内容**: 50次对话

---

## 第一步：在 Stripe 创建新价格

### 1. 登录 Stripe Dashboard

访问: https://dashboard.stripe.com/products

### 2. 更新中国用户价格 (CNY)

**方式A: 创建新产品** (推荐)

1. 点击 **Create product**
2. 填写信息:
   ```
   Name: AI算命 - 50次对话 (中国)
   Description: 解锁50次AI算命对话
   ```
3. 添加价格:
   ```
   Price: 9.99
   Currency: CNY (Chinese Yuan)
   Billing period: One time
   ```
4. 点击 **Save product**
5. **复制 Price ID** (格式: `price_xxxxxxxxxxxxx`)
6. 记下这个ID,稍后需要用到 → **PRICE_ID_CNY_NEW**

**方式B: 在现有产品中添加新价格**

1. 找到现有的产品
2. 点击 **Add another price**
3. 设置:
   ```
   Price: 9.99
   Currency: CNY
   Billing period: One time
   ```
4. 保存并复制 **Price ID**

### 3. 更新海外用户价格 (USD)

1. 点击 **Create product** 或在现有产品中添加
2. 填写信息:
   ```
   Name: AI Fortune - 50 Conversations (International)
   Description: Unlock 50 AI fortune telling conversations
   ```
3. 添加价格:
   ```
   Price: 2.99
   Currency: USD (US Dollar)
   Billing period: One time
   ```
4. 点击 **Save product**
5. **复制 Price ID** → **PRICE_ID_USD_NEW**

---

## 第二步：更新 Supabase Edge Function 环境变量

### 1. 访问 Supabase Dashboard

https://supabase.com/dashboard/project/mulrkyqqhaustbojzzes

### 2. 更新 Secrets

1. 点击 **Settings** → **Edge Functions**
2. 找到 **Secrets** 部分
3. 更新以下 Secrets:

| Secret Name | 旧值 | 新值 | 操作 |
|------------|------|------|------|
| `STRIPE_PRICE_ID_CNY` | `price_xxx...` (¥4.99) | `price_xxx...` (¥9.99) | 点击编辑,替换为新的Price ID |
| `STRIPE_PRICE_ID_USD` | `price_xxx...` ($0.99) | `price_xxx...` ($2.99) | 点击编辑,替换为新的Price ID |

**具体操作**:
1. 找到 `STRIPE_PRICE_ID_CNY`
2. 点击右侧的 **Edit** (铅笔图标)
3. 粘贴新的 Price ID (从Stripe复制的)
4. 点击 **Save**
5. 对 `STRIPE_PRICE_ID_USD` 重复相同操作

### 3. 验证配置

在 Secrets 列表中,应该看到:

```
STRIPE_SECRET_KEY: sk_live_51SJTJ8... ✅
STRIPE_PRICE_ID_CNY: price_xxxxxxxxx (新的¥9.99) ✅
STRIPE_PRICE_ID_USD: price_xxxxxxxxx (新的$2.99) ✅
STRIPE_WEBHOOK_SECRET: whsec_xxxxxx ✅
```

---

## 第三步：重新部署 Edge Functions (可选)

通常更新环境变量后会自动生效,但如果遇到问题,可以重新部署:

1. 访问 **Edge Functions** → `stripe-checkout`
2. 点击 **Deploy**
3. 对 `stripe-webhook` 重复操作

---

## 第四步：测试支付流程

### 1. 使用测试模式

如果你还在用测试密钥 (`pk_test_...`):

1. 访问你的网站
2. 登录账号,用完免费配额
3. 点击 **立即支付**
4. 检查 Stripe Checkout 页面显示的价格:
   - 中文用户: 应该显示 **¥9.99**
   - 英文用户: 应该显示 **$2.99**
5. 使用测试卡号完成支付:
   ```
   卡号: 4242 4242 4242 4242
   过期日期: 12/34 (任何未来日期)
   CVV: 123
   ```

### 2. 验证配额更新

1. 支付成功后,应该跳转回你的网站
2. 检查右上角配额是否增加了 **50次**
3. 在 Supabase Dashboard 查看 `user_quotas` 表确认

### 3. 检查 Stripe Dashboard

1. 访问 https://dashboard.stripe.com/payments
2. 应该看到新的支付记录,金额为 ¥9.99 或 $2.99

---

## 第五步：切换到生产模式 (上线时)

当测试完成,准备上线时:

### 1. 在 Stripe 获取生产密钥

1. Stripe Dashboard → **Developers** → **API keys**
2. 切换到 **Live mode** (右上角开关)
3. 复制:
   - **Publishable key**: `pk_live_...`
   - **Secret key**: `sk_live_...`

### 2. 在生产环境创建产品和价格

重复"第一步",在 **Live mode** 下创建:
- 中国用户: ¥9.99
- 海外用户: $2.99

### 3. 更新前端和后端密钥

**前端** (`index.html`, `index-avatar.html`, `index-avatar-jobs.html`):
```javascript
const STRIPE_PUBLISHABLE_KEY = 'pk_live_51SJTJ8...'; // 替换为生产密钥
```

**Supabase Secrets**:
- `STRIPE_SECRET_KEY`: 替换为 `sk_live_...`
- `STRIPE_PRICE_ID_CNY`: 生产环境的CNY价格ID
- `STRIPE_PRICE_ID_USD`: 生产环境的USD价格ID

### 4. 更新 Webhook

在生产模式下重新配置 Webhook,获取新的 `STRIPE_WEBHOOK_SECRET`

---

## 📝 总结清单

完成以下步骤:

- [ ] 在 Stripe 创建 ¥9.99 CNY 价格,复制 Price ID
- [ ] 在 Stripe 创建 $2.99 USD 价格,复制 Price ID
- [ ] 在 Supabase 更新 `STRIPE_PRICE_ID_CNY` 环境变量
- [ ] 在 Supabase 更新 `STRIPE_PRICE_ID_USD` 环境变量
- [ ] 测试中文版支付流程
- [ ] 测试英文版支付流程
- [ ] 验证配额正确增加50次

---

## ⚠️ 常见问题

**Q: 我需要删除旧的价格吗?**
A: 不需要。可以保留旧价格,但将新价格设为默认。已有的旧价格支付记录仍然有效。

**Q: 更新后旧用户已购买的配额会受影响吗?**
A: 不会。已购买的配额不会改变,只有新的支付会使用新价格。

**Q: 如何确认环境变量更新成功?**
A: 在 Supabase → Settings → Edge Functions → Secrets 中查看,或进行一次测试支付。

**Q: 测试支付会扣费吗?**
A: 使用测试密钥 (`pk_test_...`) 不会产生真实扣费。

---

## 🆘 需要帮助?

如果遇到问题:
1. 检查浏览器控制台是否有错误
2. 查看 Supabase Edge Function 日志
3. 检查 Stripe Dashboard 的 Events 和 Logs
