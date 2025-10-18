# 聊天历史功能设置指南

## 第一步：在 Supabase 创建数据表

1. 访问 https://supabase.com/dashboard/project/mulrkyqqhaustbojzzes
2. 点击左侧 **"SQL Editor"**
3. 点击 **"New query"**
4. 粘贴以下 SQL 代码并点击 **"Run"**：

```sql
-- 创建聊天消息表
CREATE TABLE chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_user_created (user_id, created_at DESC)
);

-- 启用 Row Level Security
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- 创建策略：用户只能查看自己的聊天记录
CREATE POLICY "用户只能查看自己的聊天记录"
    ON chat_messages
    FOR SELECT
    USING (auth.uid() = user_id);

-- 创建策略：用户只能插入自己的聊天记录
CREATE POLICY "用户只能插入自己的聊天记录"
    ON chat_messages
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- 创建策略：用户只能删除自己的聊天记录
CREATE POLICY "用户只能删除自己的聊天记录"
    ON chat_messages
    FOR DELETE
    USING (auth.uid() = user_id);
```

5. 确认看到 "Success. No rows returned" 提示

## 第二步：验证表创建成功

1. 点击左侧 **"Table Editor"**
2. 应该能看到 `chat_messages` 表
3. 检查表结构是否正确

## 完成！

数据表创建完成后，前端代码会自动保存和加载聊天历史。
