#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多个RAG查询
"""

import requests
import json

def test_query(query, expected_category=None):
    url = 'https://mulrkyqqhaustbojzzes.supabase.co/functions/v1/rag-search'
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11bHJreXFxaGF1c3Rib2p6emVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NTAzNDYsImV4cCI6MjA3NjMyNjM0Nn0.IP0h8Ps8CSloKNvsE8yItTOE4zdVLf36zLnsgm18uhc',
        'Content-Type': 'application/json'
    }

    data = {
        'query': query,
        'limit': 3,
        'threshold': 0.3
    }

    print(f"\n测试查询: {query}")
    print("-" * 50)

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功! 找到 {result.get('count', 0)} 条结果")
            print(f"检测到的分类: {result.get('detected_category', '未分类')}")

            if expected_category:
                if result.get('detected_category') == expected_category:
                    print(f"✅ 分类正确 ({expected_category})")
                else:
                    print(f"⚠️ 分类不匹配，期望: {expected_category}, 实际: {result.get('detected_category')}")

            for i, item in enumerate(result.get('results', []), 1):
                print(f"\n{i}. 相似度: {item.get('similarity', 0):.2f}")
                print(f"   来源: {item.get('source', 'N/A')}")
                print(f"   内容预览: {item.get('content', 'N/A')[:100]}...")
        else:
            print(f"❌ 失败! 状态码: {response.status_code}")

    except Exception as e:
        print(f"❌ 异常: {e}")

def main():
    print("="*60)
    print("RAG搜索多查询测试")
    print("="*60)

    test_cases = [
        ("乾卦", "易经"),
        ("梦见蛇", "周公解梦"),
        ("手相事业线", "面相手相"),
        ("风水布局", "风水"),
        ("星座运势", "星座"),
        ("梅花易数", "梅花易数"),
        ("算命方法", None),  # 通用查询
        ("财运", None),      # 通用查询
    ]

    for query, expected_category in test_cases:
        test_query(query, expected_category)

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()