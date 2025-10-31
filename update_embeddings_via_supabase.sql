-- 创建函数来更新向量（需要安装http扩展）
-- 注意：这个方案需要Supabase支持外部HTTP调用

-- 方案1：通过Supabase Edge Function更新
-- 你可以创建一个临时的Edge Function来批量更新向量

-- 方案2：通过Python脚本更新（需要正确的API密钥）
-- 请从Supabase控制台获取最新的service role key

-- 方案3：手动触发更新（小批量）
-- 你可以运行以下SQL来查看并手动更新少量记录

-- 1. 查看有多少记录需要更新
SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN embedding IS NULL THEN 1 END) as needs_embedding
FROM knowledge_base;

-- 2. 查看前10条没有向量的记录
SELECT
    id,
    source,
    category,
    LEFT(content, 100) as content_preview
FROM knowledge_base
WHERE embedding IS NULL
LIMIT 10;

-- 3. 单条更新示例（需要替换embedding值为实际的向量数组）
UPDATE knowledge_base
SET embedding = '{0.1, 0.2, 0.3, ...}'  -- 这里应该是1024个浮点数
WHERE id = 1;