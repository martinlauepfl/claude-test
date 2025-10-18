# Stripe 数据库配置

## 更新 payment_records 表

需要在 Supabase SQL Editor 中执行以下 SQL，更新支付记录表以支持 Stripe：

```sql
-- 更新 payment_records 表结构
ALTER TABLE payment_records
ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'usd',
ADD COLUMN IF NOT EXISTS stripe_session_id TEXT;

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_payment_stripe_session
ON payment_records(stripe_session_id);

-- 查看表结构
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'payment_records';
```

## 完整表结构

payment_records 表应包含以下字段：

- `id`: UUID (主键)
- `user_id`: UUID (外键到 auth.users)
- `amount`: NUMERIC (支付金额)
- `currency`: TEXT (货币，如 'usd', 'cny')
- `quota_added`: INTEGER (增加的配额数量)
- `payment_method`: TEXT (支付方式，'stripe')
- `stripe_session_id`: TEXT (Stripe Session ID)
- `status`: TEXT (状态，'completed', 'pending', 'failed')
- `created_at`: TIMESTAMP (创建时间)
