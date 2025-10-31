#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理并导入剩余的数据
移除 \u0000 空字符后重新导入失败的批次
"""

import json
import os
import sys
import re
from typing import List, Dict, Any
from datetime import datetime
from tqdm import tqdm
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("/Users/martinlau/Desktop/horo/pdf-processing/.env")

# 配置
INPUT_FILE = "/Users/martinlau/Desktop/horo/pdf-processing/output/knowledge_base_with_embeddings.json"
BATCH_SIZE = 100

def clean_text(text: str) -> str:
    """清理文本中的非法字符"""
    if not text:
        return text
    
    # 移除 \u0000 空字符
    text = text.replace('\u0000', '')
    text = text.replace('\x00', '')
    
    # 移除其他控制字符（可选）
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    
    return text

def connect_to_supabase() -> Client:
    """连接到 Supabase"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ 错误: 请设置环境变量")
        sys.exit(1)

    supabase: Client = create_client(supabase_url, supabase_key)
    print(f"✓ 已连接到 Supabase")
    return supabase

def load_embeddings_data(file_path: str) -> List[Dict[str, Any]]:
    """加载嵌入数据"""
    print(f"正在加载数据文件: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    knowledge_base = data.get('knowledge_base', [])
    print(f"✓ 文件中共有 {len(knowledge_base)} 条数据")

    return knowledge_base

def get_existing_content_hashes(supabase: Client) -> set:
    """获取已存在的数据指纹（使用 content 前100字符）"""
    print("\n获取已导入的数据...")
    try:
        result = supabase.table('knowledge_base').select('content').execute()
        
        existing_hashes = set()
        for item in result.data:
            content = item.get('content', '')[:100]
            existing_hashes.add(content)
        
        print(f"✓ 数据库中已有 {len(existing_hashes)} 条记录")
        return existing_hashes
    
    except Exception as e:
        print(f"❌ 获取已有数据失败: {e}")
        return set()

def find_missing_data(all_data: List[Dict], existing_hashes: set) -> List[Dict]:
    """找出缺失的数据"""
    missing = []
    
    print("\n查找缺失的数据...")
    for item in tqdm(all_data, desc="扫描"):
        content = item.get('content', '')[:100]
        if content not in existing_hashes:
            missing.append(item)
    
    print(f"✓ 找到 {len(missing)} 条缺失数据")
    return missing

def prepare_and_clean_data(data: List[Dict]) -> List[Dict[str, Any]]:
    """准备并清理数据"""
    prepared_data = []
    cleaned_count = 0

    print("\n准备并清理数据...")
    for idx, item in enumerate(tqdm(data, desc="数据清理")):
        try:
            # 清理文本字段
            category = clean_text(item.get('category', '')) if item.get('category') else None
            title = clean_text(item.get('title', '')) if item.get('title') else None
            content = clean_text(item.get('content', ''))
            
            # 检查是否清理了数据
            if '\u0000' in str(item.get('content', '')) or '\x00' in str(item.get('content', '')):
                cleaned_count += 1
            
            # 基本字段
            record = {
                'category': category,
                'title': title,
                'content': content
            }

            # 向量数据
            if 'embedding' in item and 'vector' in item['embedding']:
                vector = item['embedding']['vector']
                record['embedding'] = vector
                record['dimension'] = len(vector)
            else:
                print(f"\n⚠️  第 {idx+1} 条数据缺少 embedding")
                continue

            # 清理 metadata
            metadata = {}
            
            if 'source' in item:
                metadata['source'] = clean_text(str(item['source']))
            if 'page' in item:
                metadata['page'] = item['page']
            if 'book' in item:
                metadata['book'] = clean_text(str(item['book']))
            if 'chunk_id' in item:
                metadata['chunk_id'] = clean_text(str(item['chunk_id']))
            
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
    print(f"✓ 清理了 {cleaned_count} 条包含空字符的数据")
    return prepared_data

def batch_insert(supabase: Client, data: List[Dict], batch_size: int = 100) -> Dict[str, int]:
    """批量插入数据"""
    total = len(data)
    success_count = 0
    error_count = 0
    errors = []

    print(f"\n开始批量导入...")
    print(f"总数据量: {total} 条")
    print(f"批次大小: {batch_size} 条\n")

    for i in tqdm(range(0, total, batch_size), desc="导入进度"):
        batch = data[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        try:
            result = supabase.table('knowledge_base').insert(batch).execute()
            
            if result.data:
                batch_success = len(result.data)
                success_count += batch_success
            else:
                error_count += len(batch)
                errors.append(f"批次 {batch_num}: 未返回数据")

        except Exception as e:
            error_count += len(batch)
            error_msg = str(e)
            errors.append(f"批次 {batch_num}: {error_msg}")
            
            if len(errors) <= 3:
                print(f"\n  ❌ 批次 {batch_num} 失败: {error_msg[:100]}")

    return {
        'success': success_count,
        'error': error_count,
        'errors': errors
    }

def verify_import(supabase: Client):
    """验证最终结果"""
    try:
        result = supabase.table('knowledge_base').select('id', count='exact').limit(1).execute()
        total = result.count if hasattr(result, 'count') else len(result.data)

        print("\n" + "="*60)
        print("最终验证结果")
        print("="*60)
        print(f"数据库总记录数: {total} 条")
        
        if total >= 1402:
            print("✅ 所有数据已成功导入！")
        else:
            print(f"⚠️  还缺少 {1402 - total} 条数据")

    except Exception as e:
        print(f"❌ 验证失败: {e}")

def main():
    """主函数"""
    print("="*60)
    print("清理并导入剩余数据工具")
    print("="*60)

    # 1. 连接数据库
    supabase = connect_to_supabase()

    # 2. 加载所有数据
    all_data = load_embeddings_data(INPUT_FILE)

    # 3. 获取已存在的数据
    existing_hashes = get_existing_content_hashes(supabase)

    # 4. 找出缺失的数据
    missing_data = find_missing_data(all_data, existing_hashes)

    if not missing_data:
        print("\n✅ 没有缺失数据，所有数据已导入！")
        verify_import(supabase)
        return

    # 5. 显示缺失数据预览
    print("\n" + "-"*60)
    print("缺失数据预览 (前3条):")
    print("-"*60)
    for i, item in enumerate(missing_data[:3]):
        title = item.get('title', 'N/A')[:50]
        content = item.get('content', '')[:80]
        has_null = '\u0000' in str(item.get('content', ''))
        print(f"{i+1}. {title}")
        print(f"   内容: {content}...")
        print(f"   包含空字符: {'是' if has_null else '否'}")

    # 6. 确认导入
    print(f"\n即将清理并导入 {len(missing_data)} 条缺失数据")
    confirm = input("确认开始导入？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    # 7. 准备并清理数据
    start_time = datetime.now()
    prepared_data = prepare_and_clean_data(missing_data)

    if not prepared_data:
        print("❌ 没有可导入的数据")
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
    
    if result['errors']:
        print(f"\n错误详情 (前10条):")
        for err in result['errors'][:10]:
            print(f"  - {err}")

    # 10. 最终验证
    verify_import(supabase)

if __name__ == "__main__":
    main()