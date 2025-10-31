-- 检查知识库中的所有书籍和分类

-- 1. 查看所有书籍（source）和记录数
SELECT
    source,
    COUNT(*) as record_count,
    STRING_AGG(DISTINCT category, ', ') as categories
FROM knowledge_base
GROUP BY source
ORDER BY record_count DESC;

-- 2. 查看所有分类
SELECT
    category,
    COUNT(*) as record_count,
    COUNT(DISTINCT source) as book_count
FROM knowledge_base
GROUP BY category
ORDER BY record_count DESC;

-- 3. 搜索包含"梅花"的记录
SELECT
    source,
    category,
    LEFT(content, 100) as content_preview,
    embedding IS NOT NULL as has_embedding
FROM knowledge_base
WHERE content ILIKE '%梅花%'
LIMIT 10;

-- 4. 搜索包含"易数"的记录
SELECT
    source,
    category,
    LEFT(content, 100) as content_preview,
    embedding IS NOT NULL as has_embedding
FROM knowledge_base
WHERE content ILIKE '%易数%'
LIMIT 10;

-- 5. 检查哪些记录没有向量
SELECT
    source,
    category,
    COUNT(*) as count_without_embedding
FROM knowledge_base
WHERE embedding IS NULL
GROUP BY source, category
ORDER BY count_without_embedding DESC;