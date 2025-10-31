#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除knowledge_base_rag.json中的重复记录
"""

import json
import hashlib
from datetime import datetime

def remove_duplicates():
    # 读取原始JSON文件
    input_path = '/Users/martinlau/Desktop/claude test/pdf-processing/output/knowledge_base_rag.json'
    output_path = '/Users/martinlau/Desktop/claude test/pdf-processing/output/knowledge_base_rag_clean.json'

    print("=" * 70)
    print("删除重复记录工具")
    print("=" * 70)

    print(f"\n正在读取文件: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
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
            print("❌ 无法确定JSON文件结构")
            return

    print(f"✅ 原始记录数: {len(records)}")

    # 使用字典来去重，基于内容的哈希值
    unique_records = {}
    duplicates_count = 0
    seen_hashes = set()

    print("\n正在去重...")
    for i, record in enumerate(records):
        # 创建内容的哈希值作为唯一标识
        content = record.get('content', '')
        # 使用前100个字符创建哈希
        content_key = content[:100]
        content_hash = hashlib.md5(content_key.encode('utf-8')).hexdigest()

        if content_hash in seen_hashes:
            duplicates_count += 1
            # 显示被删除的重复记录
            if duplicates_count <= 5:
                print(f"  删除重复: {record.get('source', '未知')} - {content[:50]}...")
            continue

        seen_hashes.add(content_hash)
        unique_records[content_hash] = record

    # 转换回列表
    clean_records = list(unique_records.values())

    print(f"\n✅ 去重完成!")
    print(f"  - 删除重复记录: {duplicates_count} 条")
    print(f"  - 保留记录: {len(clean_records)} 条")

    # 创建新的JSON结构
    if isinstance(data, dict):
        # 保持原有的结构
        for key in ['data', 'knowledge_base', 'items']:
            if key in data:
                clean_data = data.copy()
                clean_data[key] = clean_records
                break
        else:
            clean_data = {
                "data": clean_records,
                "total": len(clean_records),
                "cleaned_at": datetime.now().isoformat()
            }
    else:
        # 原来是列表，包装成对象
        clean_data = {
            "data": clean_records,
            "total": len(clean_records),
            "original_total": len(records),
            "duplicates_removed": duplicates_count,
            "cleaned_at": datetime.now().isoformat()
        }

    # 保存清理后的文件
    print(f"\n正在保存到: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    print("✅ 保存成功!")

    # 验证结果
    print("\n验证结果:")
    print(f"  原始文件大小: {len(json.dumps(data, ensure_ascii=False)):,} 字符")
    print(f"  清理后大小: {len(json.dumps(clean_data, ensure_ascii=False)):,} 字符")
    print(f"  节省空间: {len(json.dumps(data, ensure_ascii=False)) - len(json.dumps(clean_data, ensure_ascii=False)):,} 字符")

    # 显示书籍统计（清理后）
    print("\n清理后的书籍统计:")
    from collections import defaultdict
    book_counts = defaultdict(int)
    for record in clean_records:
        source = record.get('source', '未知')
        book_counts[source] += 1

    sorted_books = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)
    for book, count in sorted_books:
        print(f"  - {book}: {count} 条记录")

    print("\n" + "=" * 70)
    print("去重任务完成!")
    print(f"✅ 清理后的文件已保存到: {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    remove_duplicates()