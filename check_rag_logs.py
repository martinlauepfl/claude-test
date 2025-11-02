#!/usr/bin/env python3
"""
检查RAG函数执行日志
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv('/Users/martinlau/Desktop/horo/pdf-processing/.env')

# 测试RAG搜索，触发日志
def test_rag_and_check():
    print("=" * 60)
    print("测试RAG搜索并检查日志")
    print("=" * 60)

    # 发送测试请求
    print("\n1. 发送测试请求...")
    response = requests.post(
        "https://mulrkyqqhaustbojzzes.supabase.co/functions/v1/rag-search",
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11bHJreXFxaGF1c3Rib2p6emVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NTAzNDYsImV4cCI6MjA3NjMyNjM0Nn0.IP0h8Ps8CSloKNvsE8yItTOE4zdVLf36zLnsgm18uhc",
            "Content-Type": "application/json"
        },
        json={
            "query": "梦见蛇",
            "limit": 3
        }
    )

    if response.ok:
        data = response.json()
        print(f"✅ 请求成功")
        print(f"   结果数量: {data.get('count', 0)}")
        print(f"   性能: embed={data.get('performance', {}).get('embed_time')}ms, "
              f"search={data.get('performance', {}).get('search_time')}ms")

        # 检查具体问题
        if data.get('count', 0) == 0:
            print("\n❌ 没有返回结果，可能的原因：")
            print("   1. 向量搜索失败（维度不匹配）")
            print("   2. 阈值太高（当前是0.5）")
            print("   3. 数据库中没有向量数据")
            print("   4. match_knowledge函数有问题")

            print("\n🔧 建议操作：")
            print("   1. 在Supabase Dashboard查看rag-search函数的详细日志")
            print("   2. 检查数据库中knowledge_base表的向量数据")
            print("   3. 尝试将阈值降到0.3测试")
            print("   4. 检查match_knowledge RPC函数是否正确创建")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"   错误信息: {response.text}")

if __name__ == "__main__":
    test_rag_and_check()