#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量导入知识库数据到 Supabase
将带有向量嵌入的知识库数据批量导入到 Supabase
"""

import json
import os
import sys
from typing import List, Dict, Any
from datetime import datetime
from tqdm import tqdm
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("/Users/martinlau/Desktop/horo/pdf-processing/.env")

# 配置
INPUT_FILE = "/Users/martinlau/Desktop/horo/pdf-processing/output/knowledge_base_with_embeddings.json"
BATCH_SIZE = 100  # 每批次导入的数量

def connect_to_supabase() -> Client:
    """连接到 Supabase"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ 错误: 请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY")
        sys.exit(1)

    supabase: Client = create_client(supabase_url, supabase_key)
    print(f"✓ 已连接到 Supabase")
    return supabase

def load_embeddings_data(file_path: str) -> tuple[List[Dict[str, Any]], Dict]:
    """加载嵌入数据"""
    print(f"正在加载数据文件: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    knowledge_base = data.get('knowledge_base', [])
    metadata = data.get('metadata', {})
    
    print(f"✓ 文件中共有 {len(knowledge_base)} 条数据")
    print(f"  - 向量维度: {metadata.get('embedding_dimension', 'N/A')}")
    print(f"  - 嵌入模型: {metadata.get('embedding_model', 'N/A')}")

    return knowledge_base, metadata

def check_table_status(supabase: Client) -> int:
    """检查表中当前的记录数"""
    try:
        result = supabase.table('knowledge_base').select('id', count='exact').limit(1).execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        print(f"✓ 数据库中当前有 {count} 条记录")
        return count
    except Exception as e:
        print(f"⚠️  无法获取记录数: {e}")
        return 0

def prepare_data_for_insert(data: List[Dict]) -> List[Dict[str, Any]]:
    """准备插入数据"""
    prepared_data = []

    print("\n准备数据...")
    for idx, item in enumerate(tqdm(data, desc="数据转换")):
        try:
            # 基本字段
            record = {
                'category': item.get('category'),
                'title': item.get('title'),
                'content': item.get('content')
            }

            # 向量数据 - 直接使用数组
            if 'embedding' in item and 'vector' in item['embedding']:
                vector = item['embedding']['vector']
                record['embedding'] = vector  # 直接传递数组
                record['dimension'] = len(vector)
            else:
                print(f"\n⚠️  第 {idx+1} 条数据缺少 embedding")
                continue

            # 扁平化的 metadata
            metadata = {}
            
            # 从原始数据提取
            if 'source' in item:
                metadata['source'] = item['source']
            if 'page' in item:
                metadata['page'] = item['page']
            if 'book' in item:
                metadata['book'] = item['book']
            if 'chunk_id' in item:
                metadata['chunk_id'] = item['chunk_id']
            
            # 从 embedding 信息提取
            if 'embedding' in item:
                embedding_info = item['embedding']
                if 'model' in embedding_info:
                    metadata['embedding_model'] = embedding_info['model']
                if 'created_at' in embedding_info:
                    metadata['embedding_created_at'] = embedding_info['created_at']

            if metadata:
                record['metadata'] = metadata

            prepared_data.append(record)

        except Exception as e:
            print(f"\n❌ 第 {idx+1} 条数据准备失败: {e}")
            continue

    print(f"✓ 成功准备 {len(prepared_data)} 条数据")
    return prepared_data

def batch_insert(supabase: Client, data: List[Dict], batch_size: int = 100) -> Dict[str, int]:
    """批量插入数据"""
    total = len(data)
    success_count = 0
    error_count = 0
    errors = []

    print(f"\n开始批量导入...")
    print(f"总数据量: {total} 条")
    print(f"批次大小: {batch_size} 条")
    print(f"预计批次: {(total + batch_size - 1) // batch_size} 批\n")

    # 分批处理
    for i in tqdm(range(0, total, batch_size), desc="导入进度"):
        batch = data[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        try:
            # 批量插入
            result = supabase.table('knowledge_base').insert(batch).execute()
            
            if result.data:
                batch_success = len(result.data)
                success_count += batch_success
                
                # 每10批打印一次详细信息
                if batch_num % 10 == 0:
                    print(f"\n  ✓ 批次 {batch_num}: 成功 {batch_success} 条")
            else:
                error_count += len(batch)
                errors.append(f"批次 {batch_num}: 未返回数据")

        except Exception as e:
            error_count += len(batch)
            error_msg = str(e)
            errors.append(f"批次 {batch_num}: {error_msg}")
            
            # 打印前3个错误
            if len(errors) <= 3:
                print(f"\n  ❌ 批次 {batch_num} 失败: {error_msg[:100]}")

    return {
        'success': success_count,
        'error': error_count,
        'errors': errors
    }

def verify_import(supabase: Client, expected_total: int):
    """验证导入结果"""
    try:
        result = supabase.table('knowledge_base').select('id', count='exact').limit(1).execute()
        actual_total = result.count if hasattr(result, 'count') else len(result.data)

        print("\n" + "="*60)
        print("验证结果")
        print("="*60)
        print(f"期望导入: {expected_total} 条")
        print(f"实际导入: {actual_total} 条")
        
        if actual_total == expected_total:
            print("✅ 所有数据已成功导入！")
        elif actual_total > 0:
            print(f"⚠️  导入不完整，缺少 {expected_total - actual_total} 条")
        else:
            print("❌ 导入失败，数据库为空")

        return actual_total

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return 0

def main():
    """主函数"""
    print("="*60)
    print("知识库全量导入工具 - Supabase")
    print("="*60)

    # 1. 检查输入文件
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 错误: 输入文件不存在: {INPUT_FILE}")
        sys.exit(1)

    # 2. 加载数据
    knowledge_base, file_metadata = load_embeddings_data(INPUT_FILE)

    if not knowledge_base:
        print("❌ 错误: 数据文件为空")
        sys.exit(1)

    # 3. 连接数据库
    supabase = connect_to_supabase()

    # 4. 检查表状态
    print("\n" + "-"*60)
    existing_count = check_table_status(supabase)

    if existing_count > 0:
        print(f"\n⚠️  警告: 数据库中已有 {existing_count} 条记录")
        confirm = input("是否继续导入？这可能会导致重复数据 (y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return

    # 5. 数据预览
    print("\n" + "-"*60)
    print("数据预览 (前3条):")
    print("-"*60)
    for i, item in enumerate(knowledge_base[:3]):
        title = item.get('title', 'N/A')[:50]
        content = item.get('content', '')[:80]
        has_embedding = 'embedding' in item and 'vector' in item['embedding']
        print(f"{i+1}. {title}")
        print(f"   内容: {content}...")
        print(f"   向量: {'✓' if has_embedding else '✗'}")

    # 6. 确认导入
    print("\n" + "-"*60)
    print(f"即将导入 {len(knowledge_base)} 条数据到 Supabase")
    print(f"批次大小: {BATCH_SIZE} 条")
    confirm = input("\n确认开始导入？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    # 7. 准备数据
    start_time = datetime.now()
    prepared_data = prepare_data_for_insert(knowledge_base)

    if not prepared_data:
        print("❌ 错误: 没有可导入的数据")
        return

    # 8. 批量导入
    result = batch_insert(supabase, prepared_data, BATCH_SIZE)

    # 9. 显示结果
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*60)
    print("导入完成")
    print("="*60)
    print(f"✓ 成功: {result['success']} 条")
    print(f"✗ 失败: {result['error']} 条")
    print(f"⏱  耗时: {duration:.2f} 秒")
    
    if result['errors'] and len(result['errors']) <= 10:
        print("\n错误详情:")
        for err in result['errors'][:10]:
            print(f"  - {err}")

    # 10. 验证
    verify_import(supabase, len(prepared_data))

if __name__ == "__main__":
    main()