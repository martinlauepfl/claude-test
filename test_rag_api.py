#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAG API
"""

import json
import requests

# 配置
SUPABASE_URL = 'https://mulrkyqqhaustbojzzes.supabase.co'
SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11bHJreXFxaGF1c3Rib2p6emVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDc1MDM0NiwiZXhwIjoyMDc2MzI2MzQ2fQ.Tq-69aOZrxCU2IvhqzSFyIn_dCAIN9iRR3PwYZHDvVA'

def test_rag_search():
    """测试RAG搜索"""
    print("=" * 60)
    print("测试RAG搜索功能")
    print("=" * 60)

    url = f"{SUPABASE_URL}/functions/v1/rag-search"

    # 测试查询
    queries = [
        "梦见蛇代表什么",
        "手相事业线很长是什么意思",
        "风水布局要注意什么",
        "易经第一卦是什么"
    ]

    for query in queries:
        print(f"\n查询: {query}")
        print("-" * 40)

        payload = {
            "query": query,
            "limit": 3,
            "threshold": 0.7
        }

        try:
            response = requests.post(
                url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}'
                },
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 搜索成功")
                print(f"检测到的分类: {data.get('detected_category', '未分类')}")
                print(f"找到 {len(data.get('results', []))} 个相关结果")

                for i, result in enumerate(data.get('results', []), 1):
                    print(f"\n结果 {i}:")
                    print(f"  来源: {result.get('source', '未知')}")
                    print(f"  分类: {result.get('category', '未知')}")
                    print(f"  相似度: {result.get('similarity', 0):.3f}")
                    print(f"  内容: {result.get('content', '')[:100]}...")

            else:
                print(f"❌ 搜索失败: HTTP {response.status_code}")
                print(f"错误信息: {response.text[:200]}")

        except Exception as e:
            print(f"❌ 请求异常: {e}")

def test_knowledge_base_stats():
    """测试知识库统计"""
    print("\n\n" + "=" * 60)
    print("知识库统计")
    print("=" * 60)

    url = f"{SUPABASE_URL}/rest/v1/knowledge_base"

    try:
        response = requests.get(
            url,
            headers={
                'apikey': SUPABASE_SERVICE_KEY,
                'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}'
            },
            params={
                'select': 'category,source'
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # 统计
            categories = {}
            sources = {}

            for item in data:
                cat = item.get('category', '未知')
                src = item.get('source', '未知')
                categories[cat] = categories.get(cat, 0) + 1
                sources[src] = sources.get(src, 0) + 1

            print(f"\n总记录数: {len(data)}")
            print(f"\n分类统计:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count} 条")

            print(f"\n书籍统计:")
            for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                print(f"  {src}: {count} 条")

        else:
            print(f"❌ 获取统计失败: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")

def main():
    test_rag_search()
    test_knowledge_base_stats()

    print("\n\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()