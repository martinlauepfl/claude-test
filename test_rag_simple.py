#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试RAG搜索功能
"""

import requests
import json

def test_rag():
    # RAG搜索端点
    url = 'https://mulrkyqqhaustbojzzes.supabase.co/functions/v1/rag-search'

    # 使用anon key（从index.html中获取）
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11bHJreXFxaGF1c3Rib2p6emVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NTAzNDYsImV4cCI6MjA3NjMyNjM0Nn0.IP0h8Ps8CSloKNvsE8yItTOE4zdVLf36zLnsgm18uhc',
        'Content-Type': 'application/json'
    }

    # 测试数据
    data = {
        'query': '乾卦',
        'limit': 5,
        'threshold': 0.3
    }

    print("测试RAG搜索...")
    print(f"URL: {url}")
    print(f"查询: {data['query']}")
    print("-" * 50)

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ 成功!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ 失败!")
            print(f"响应: {response.text}")

    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    test_rag()