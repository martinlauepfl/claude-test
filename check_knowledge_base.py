#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查知识库中的书籍
"""

import requests

def check_books():
    url = 'https://mulrkyqqhaustbojzzes.supabase.co/rest/v1/knowledge_base'

    # 使用service role key
    headers = {
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11bHJreXFxaHVzdGJvanplcyIsInJvbGUiOiJzZXJ2aWNlX3JvbGUiLCJpYXQiOjE3NjA3NTAzNDYsImV4cCI6MjA3NjMyNjM0Nn0.Tq-69aOZrxCU2IvhqzSFyIn_dCAIN9iRR3PwYZHDvVA',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11bHJreXFxaHVzdGJvanplcyIsInJvbGUiOiJzZXJ2aWNlX3JvbGUiLCJpYXQiOjE3NjA3NTAzNDYsImV4cCI6MjA3NjMyNjM0Nn0.Tq-69aOZrxCU2IvhqzSFyIn_dCAIN9iRR3PwYZHDvVA'
    }

    print("检查知识库中的书籍...")
    print("="*60)

    # 1. 获取所有不同的source（书名）
    print("\n1. 查询所有书籍:")
    response = requests.get(f"{url}?select=source", headers=headers)

    if response.status_code == 200:
        sources = {}
        for item in response.json():
            source = item.get('source', '未知')
            sources[source] = sources.get(source, 0) + 1

        print(f"共有 {len(sources)} 本书:")
        for source, count in sorted(sources.items()):
            print(f"  - {source}: {count} 条记录")
    else:
        print(f"查询失败: {response.status_code}")

    # 2. 搜索包含"梅花"的记录
    print("\n2. 搜索包含'梅花'的记录:")
    search_response = requests.get(f"{url}?select=source,category&ilike=content,*%E6%A2%85%E8%8A%B1*&limit=10", headers=headers)

    if search_response.status_code == 200:
        results = search_response.json()
        print(f"找到 {len(results)} 条包含'梅花'的记录:")
        for item in results:
            print(f"  - 书籍: {item.get('source', 'N/A')}, 分类: {item.get('category', 'N/A')}")
    else:
        print(f"搜索失败: {search_response.status_code}")

    # 3. 检查分类
    print("\n3. 查询所有分类:")
    cat_response = requests.get(f"{url}?select=category", headers=headers)

    if cat_response.status_code == 200:
        categories = {}
        for item in cat_response.json():
            cat = item.get('category', '未分类')
            categories[cat] = categories.get(cat, 0) + 1

        print(f"共有 {len(categories)} 个分类:")
        for cat, count in sorted(categories.items()):
            print(f"  - {cat}: {count} 条记录")

    # 4. 测试查询"梅花易数"
    print("\n4. 测试RAG搜索'梅花易数':")
    rag_response = requests.post(
        'https://mulrkyqqhaustbojzzes.supabase.co/functions/v1/rag-search',
        headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11bHJreXFxaWF1c3Rib2p6emVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NTAzNDYsImV4cCI6MjA3NjMyNjM0Nn0.IP0h8Ps8CSloKNvsE8yItTOE4zdVLf36zLnsgm18uhc',
            'Content-Type': 'application/json'
        },
        json={
            'query': '梅花易数',
            'limit': 5,
            'threshold': 0.3  # 使用低阈值测试
        }
    )

    if rag_response.status_code == 200:
        result = rag_response.json()
        print(f"RAG搜索结果: {result.get('count', 0)} 条")
        if result.get('results'):
            for r in result['results'][:3]:
                print(f"  - {r.get('source', 'N/A')}: {r.get('content', '')[:50]}...")
    else:
        print(f"RAG搜索失败: {rag_response.status_code}")

if __name__ == "__main__":
    check_books()