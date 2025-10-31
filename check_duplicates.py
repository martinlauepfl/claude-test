#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查knowledge_base_rag.json中的重复记录
"""

import json
from collections import defaultdict

def check_duplicates():
    # 读取JSON文件
    file_path = '/Users/martinlau/Desktop/claude test/pdf-processing/output/knowledge_base_rag.json'

    print("正在读取JSON文件...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 根据实际JSON结构调整
    if 'data' in data:
        records = data['data']
    elif 'knowledge_base' in data:
        records = data['knowledge_base']
    elif 'items' in data:
        records = data['items']
    else:
        # 假设是顶层列表
        if isinstance(data, list):
            records = data
        else:
            print("无法确定JSON文件结构")
            return
    print(f"总记录数: {len(records)}")

    # 1. 检查完全重复的记录
    print("\n1. 检查完全重复的记录...")
    seen = set()
    duplicates = []

    for i, record in enumerate(records):
        # 创建唯一标识（使用content的哈希）
        content_key = record.get('content', '')[:100]  # 前100个字符作为key
        record_hash = hash(content_key)

        if record_hash in seen:
            duplicates.append((i, record))
        else:
            seen.add(record_hash)

    print(f"发现 {len(duplicates)} 条完全重复的记录")

    if duplicates:
        print("\n重复记录示例:")
        for idx, record in duplicates[:5]:
            print(f"  索引 {idx}: {record.get('source', '未知')} - {record.get('content', '')[:50]}...")

    # 2. 按书籍统计
    print("\n2. 按书籍统计记录数:")
    book_counts = defaultdict(int)
    for record in records:
        source = record.get('source', '未知')
        book_counts[source] += 1

    # 排序并显示
    sorted_books = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"\n共有 {len(sorted_books)} 本书:")
    for book, count in sorted_books[:20]:  # 显示前20本
        print(f"  - {book}: {count} 条记录")

    # 3. 检查是否有同一本书的重复章节
    print("\n3. 检查可能的重复章节...")

    # 按书籍+章节前缀分组
    chapter_groups = defaultdict(list)

    for record in records:
        source = record.get('source', '未知')
        content = record.get('content', '')

        # 提取可能的章节标识
        chapter_marker = None
        if '第' in content and '章' in content:
            # 查找 "第X章" 模式
            import re
            match = re.search(r'第[一二三四五六七八九十百千万\d]+章', content[:50])
            if match:
                chapter_marker = match.group()
        elif '卦' in content:
            # 查找 "X卦" 模式
            import re
            match = re.search(r'[乾坤震巽坎离艮兑]+卦', content[:50])
            if match:
                chapter_marker = match.group()

        key = (source, chapter_marker) if chapter_marker else source
        chapter_groups[key].append(record)

    # 查找同一本书的重复章节
    duplicate_chapters = []
    for key, group in chapter_groups.items():
        if len(group) > 1:
            duplicate_chapters.append((key, len(group)))

    if duplicate_chapters:
        print(f"\n发现 {len(duplicate_chapters)} 个可能的重复章节:")
        for item in duplicate_chapters[:10]:
            if len(item) == 2:
                key, count = item
                if isinstance(key, tuple):
                    source, marker = key
                    print(f"  - {source} {marker if marker else ''}: {count} 条")
                else:
                    print(f"  - {key}: {count} 条")
            else:
                print(f"  - {item[0]}: {item[1]} 条")

    # 4. 内容相似度检查（简单版）
    print("\n4. 内容相似度检查（取前50个字符）...")

    prefix_counts = defaultdict(int)
    for record in records:
        prefix = record.get('content', '')[:50]  # 前50个字符
        if len(prefix) > 10:  # 只检查有意义的前缀
            prefix_counts[prefix] += 1

    # 找出重复的前缀
    repeated_prefixes = [(p, c) for p, c in prefix_counts.items() if c > 1]

    print(f"发现 {len(repeated_prefixes)} 个重复的内容前缀")

    if repeated_prefixes:
        print("\n重复内容示例（前5个）:")
        for prefix, count in sorted(repeated_prefixes, key=lambda x: x[1], reverse=True)[:5]:
            print(f"  重复 {count} 次: {prefix}...")

    print("\n=== 检查完成 ===")

    # 5. 总结
    print(f"\n总结:")
    print(f"- 总记录数: {len(records)}")
    print(f"- 完全重复: {len(duplicates)} 条")
    print(f"- 书籍数量: {len(sorted_books)} 本")
    print(f"- 可能的重复章节: {len(duplicate_chapters)} 个")
    print(f"- 内容前缀重复: {len(repeated_prefixes)} 个")

if __name__ == "__main__":
    check_duplicates()