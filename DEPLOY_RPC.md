# 部署配额扣除RPC函数

## 为什么需要这个RPC函数？

当前前端代码的配额扣除有一个小问题：如果用户同时打开2个标签页，可能会导致配额计算不准确。

**举例：**
- 用户有5次配额
- 同时在2个标签页发送消息
- 两个标签页都读取到"5次"
- 两个都计算：5 - 1 = 4
- 结果：配额变成4，但用户实际使用了2次（应该是3次）

**RPC函数解决方案：**
让数据库自己完成"读取-计算-更新"，并加锁防止并发问题。

---

## 部署步骤

### 1. 登录 Supabase Dashboard

访问：https://supabase.com/dashboard/project/mulrkyqqhaustbojzzes

### 2. 打开 SQL Editor

在左侧菜单找到：**SQL Editor**

### 3. 复制并执行 SQL

1. 点击 **New Query** 创建新查询
2. 打开文件 `supabase/functions/deduct-quota.sql`
3. 复制全部内容
4. 粘贴到 SQL Editor
5. 点击右下角 **Run** 按钮执行

### 4. 验证函数已创建

执行以下SQL查看函数：

```sql
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name = 'deduct_user_quota';
```

应该看到：
```
routine_name        | routine_type
--------------------|-------------
deduct_user_quota   | FUNCTION
```

---

## 测试 RPC 函数

### 方法1: 在 SQL Editor 中测试

```sql
-- 1. 查看你的用户ID和当前配额
SELECT user_id, quota FROM user_quotas LIMIT 1;

-- 2. 扣除配额（替换为你的user_id）
SELECT * FROM deduct_user_quota('your-user-id-here');

-- 3. 再次查看配额（应该减少1）
SELECT user_id, quota FROM user_quotas WHERE user_id = 'your-user-id-here';
```

### 方法2: 在前端测试

1. 打开网站并登录
2. 打开浏览器控制台（F12）
3. 发送一条消息
4. 查看控制台应该显示：`✅ 配额扣除成功，剩余: X`

### 方法3: 多标签页压力测试

1. 打开2个标签页，登录同一账号
2. 查看当前配额（比如5次）
3. 同时在2个标签页快速发送消息
4. 检查配额是否正确减少（应该是3次，而不是4次）

---

## 如果出现问题

### 错误："function deduct_user_quota does not exist"

**原因：** SQL未成功执行

**解决：**
1. 重新执行 `deduct-quota.sql` 中的SQL
2. 检查是否有错误提示
3. 确保你有足够权限（项目Owner）

### 错误："Quota record not found"

**原因：** 用户在 `user_quotas` 表中没有记录

**解决：**
```sql
-- 为用户创建配额记录
INSERT INTO user_quotas (user_id, quota)
VALUES ('your-user-id', 3)
ON CONFLICT (user_id) DO NOTHING;
```

### 错误："Insufficient quota"

**原因：** 配额已用完（quota = 0）

**解决：**
```sql
-- 手动增加配额用于测试
UPDATE user_quotas
SET quota = 5
WHERE user_id = 'your-user-id';
```

---

## 前端已自动适配

`index.html` 中的 `deductQuota()` 函数已经修改为调用这个RPC函数，无需额外配置。

部署SQL后，前端会自动使用新的安全方式扣除配额！

---

## 如果需要回滚

如果RPC函数有问题，可以删除函数：

```sql
DROP FUNCTION IF EXISTS deduct_user_quota(UUID);
```

然后将 `index.html` 的 `deductQuota()` 函数改回原来的版本（使用 `git log` 查看历史）。
