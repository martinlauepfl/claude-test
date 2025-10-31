-- 检查知识库记录总数和状态

-- 1. 总记录数
SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as records_with_embedding,
    COUNT(CASE WHEN embedding IS NULL THEN 1 END) as records_without_embedding,
    ROUND(
        (COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)),
        2
    ) as embedding_percentage
FROM knowledge_base;

-- 2. 按分类统计
SELECT
    category,
    COUNT(*) as total,
    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embedding,
    COUNT(CASE WHEN embedding IS NULL THEN 1 END) as without_embedding
FROM knowledge_base
GROUP BY category
ORDER BY total DESC;

-- 3. 按书籍统计（显示前20本）
SELECT
    source,
    category,
    COUNT(*) as total_records,
    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embedding,
    ROUND(
        (COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)),
        2
    ) as embedding_percentage
FROM knowledge_base
GROUP BY source, category
ORDER BY total_records DESC
LIMIT 20;

-- 4. 检查最近添加的记录
SELECT
    source,
    category,
    LEFT(content, 80) as preview,
    CASE WHEN embedding IS NOT NULL THEN 'YES' ELSE 'NO' END as has_embedding
FROM knowledge_base
ORDER BY id DESC
LIMIT 10;