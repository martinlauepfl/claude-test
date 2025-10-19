# 更新新用户免费配额为3次

## 在 Supabase 执行以下操作

### 第一步：修改触发器函数（新用户获得3次免费）

1. 访问 https://supabase.com/dashboard/project/mulrkyqqhaustbojzzes
2. 点击左侧 **"SQL Editor"**
3. 点击 **"New query"**
4. 粘贴以下 SQL 代码并点击 **"Run"**：

```sql
-- 创建或替换触发器函数：新用户注册时自动创建配额记录
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_quotas (user_id, quota, total_purchased)
  VALUES (NEW.id, 3, 0);  -- 新用户获得3次免费对话
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 如果触发器不存在，创建触发器
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'on_auth_user_created'
  ) THEN
    CREATE TRIGGER on_auth_user_created
      AFTER INSERT ON auth.users
      FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
  END IF;
END $$;
```

### 第二步：验证配置

执行以下查询检查触发器是否正确设置：

```sql
SELECT * FROM pg_trigger WHERE tgname = 'on_auth_user_created';
```

### 第三步：（可选）测试新用户注册

注册一个新测试账号，然后检查配额：

```sql
-- 查看最新注册用户的配额
SELECT u.email, q.quota, q.total_purchased, q.created_at
FROM auth.users u
JOIN user_quotas q ON u.id = q.user_id
ORDER BY u.created_at DESC
LIMIT 5;
```

应该看到新用户的 `quota` 为 3。

## 价格配置说明

前端已更新价格显示：
- **中文版**: ¥9.99 购买50次对话
- **英文版**: $2.99 购买50次对话

## 说明

- ✅ 新注册用户将自动获得 **3次** 免费对话次数
- ✅ 触发器在用户注册时自动执行
- ✅ 无需修改前端代码
- ⚠️ 此更改只影响**新注册**的用户
- ⚠️ 已有用户的配额**不会改变**
