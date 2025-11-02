#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成知识库向量 - 使用text-embedding-v3模型
用于解决模型不一致导致的相似度计算问题
"""

import os
import requests
import time
import psycopg2
from psycopg2.extras import execute_values
import json

# 配置
DATABASE_URL = os.getenv('DATABASE_URL', 'your_database_url')
ALIBABA_API_KEY = os.getenv('ALIBABA_API_KEY', 'your_api_key')
API_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings'

def generate_embedding(text: str, retry_count=3):
    """生成单个文本的embedding向量"""
    headers = {
        'Authorization': f'Bearer {ALIBABA_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'text-embedding-v3',
        'input': text,
        'encoding_format': 'float'
    }

    for attempt in range(retry_count):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['data'][0]['embedding']
            else:
                print(f"API错误 (尝试 {attempt + 1}): {response.status_code}, {response.text}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # 指数退避

        except Exception as e:
            print(f"请求异常 (尝试 {attempt + 1}): {e}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)

    raise Exception(f"生成embedding失败: {text[:50]}...")

def regenerate_all_embeddings():
    """重新生成所有知识库向量"""

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 获取所有记录
        cursor.execute("SELECT id, content FROM knowledge_base ORDER BY id")
        records = cursor.fetchall()

        print(f"开始重新生成 {len(records)} 条记录的向量...")
        print("使用模型: text-embedding-v3")

        success_count = 0
        failed_count = 0

        for i, (record_id, content) in enumerate(records, 1):
            try:
                print(f"处理记录 {i}/{len(records)} (ID: {record_id})")

                if not content:
                    print(f"  跳过空内容记录")
                    continue

                # 生成新的embedding
                embedding = generate_embedding(content)

                # 验证维度
                if len(embedding) != 1024:
                    print(f"  错误: 向量维度错误 ({len(embedding)})")
                    failed_count += 1
                    continue

                # 更新数据库
                cursor.execute(
                    "UPDATE knowledge_base SET embedding = %s WHERE id = %s",
                    (json.dumps(embedding), record_id)
                )
                conn.commit()

                success_count += 1
                print(f"  ✅ 成功")

                # 控制频率
                time.sleep(0.2)

            except Exception as e:
                print(f"  ❌ 失败: {e}")
                failed_count += 1
                conn.rollback()

        print(f"\n完成!")
        print(f"成功: {success_count} 条")
        print(f"失败: {failed_count} 条")

        # 统计当前状态
        cursor.execute("SELECT COUNT(*) FROM knowledge_base WHERE embedding IS NOT NULL")
        with_embedding = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        total = cursor.fetchone()[0]

        print(f"\n数据库状态:")
        print(f"总记录数: {total}")
        print(f"有向量记录数: {with_embedding}")
        print(f"覆盖率: {with_embedding/total*100:.1f}%")

    except Exception as e:
        print(f"数据库操作错误: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("⚠️  注意: 此操作将重新生成所有知识库向量")
    print("    这将消耗大量API调用额度")
    print("    建议先备份数据库")
    print()

    confirm = input("确定要继续吗? (yes/no): ")
    if confirm.lower() == 'yes':
        regenerate_all_embeddings()
    else:
        print("操作已取消")