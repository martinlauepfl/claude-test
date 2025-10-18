# 更新新用户免费配额为10次

## 在 Supabase 执行以下操作

### 第一步：修改触发器函数

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
  VALUES (NEW.id, 10, 0);  -- 新用户获得10次免费对话
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

### 第三步：（可选）更新现有用户配额

如果需要将现有配额为2次的用户更新为10次，执行：

```sql
-- 仅更新配额为2的用户（原来的默认值）
UPDATE user_quotas
SET quota = 10
WHERE quota = 2 AND total_purchased = 0;
```

## 说明

- 新注册用户将自动获得 **10次** 免费对话次数
- 触发器在用户注册时自动执行
- 无需修改前端代码
