#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理 Supabase 数据库中的重复数据
保留每条内容的第一条记录，删除重复项
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm

# 加载环境变量
load_dotenv("/Users/martinlau/Desktop/horo/pdf-processing/.env")

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

def get_all_records(supabase: Client):
    """获取所有记录"""
    print("\n获取所有记录...")
    
    try:
        # 分页获取所有数据
        all_records = []
        page_size = 1000
        offset = 0
        
        while True:
            result = supabase.table('knowledge_base')\
                .select('id, content, created_at')\
                .order('created_at')\
                .range(offset, offset + page_size - 1)\
                .execute()
            
            if not result.data:
                break
            
            all_records.extend(result.data)
            offset += page_size
            
            print(f"  已获取 {len(all_records)} 条...")
            
            if len(result.data) < page_size:
                break
        
        print(f"✓ 总共获取 {len(all_records)} 条记录")
        return all_records
    
    except Exception as e:
        print(f"❌ 获取记录失败: {e}")
        return []

def find_duplicates(records):
    """找出重复的记录"""
    print("\n分析重复数据...")
    
    # 使用 content 前 200 字符作为唯一标识
    content_map = {}
    duplicates = []
    
    for record in tqdm(records, desc="扫描"):
        content_key = record['content'][:200] if record['content'] else ''
        
        if content_key in content_map:
            # 这是重复项，保留最早的那条
            duplicates.append(record['id'])
        else:
            # 第一次出现，记录下来
            content_map[content_key] = record['id']
    
    print(f"✓ 找到 {len(duplicates)} 条重复记录")
    print(f"✓ 唯一记录数: {len(content_map)}")
    
    return duplicates, len(content_map)

def delete_duplicates(supabase: Client, duplicate_ids):
    """删除重复记录"""
    if not duplicate_ids:
        print("\n✅ 没有重复数据需要删除")
        return
    
    print(f"\n准备删除 {len(duplicate_ids)} 条重复记录...")
    
    # 确认
    confirm = input(f"⚠️  即将删除 {len(duplicate_ids)} 条记录，确认？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return
    
    deleted_count = 0
    error_count = 0
    
    # 批量删除（每次最多 100 条）
    batch_size = 100
    
    for i in tqdm(range(0, len(duplicate_ids), batch_size), desc="删除进度"):
        batch = duplicate_ids[i:i + batch_size]
        
        try:
            # Supabase 删除语法
            for record_id in batch:
                result = supabase.table('knowledge_base').delete().eq('id', record_id).execute()
                if result.data:
                    deleted_count += 1
                else:
                    error_count += 1
        
        except Exception as e:
            print(f"\n❌ 删除批次失败: {e}")
            error_count += len(batch)
    
    print(f"\n✓ 成功删除: {deleted_count} 条")
    print(f"✗ 删除失败: {error_count} 条")

def verify_final_count(supabase: Client):
    """验证最终记录数"""
    try:
        result = supabase.table('knowledge_base').select('id', count='exact').limit(1).execute()
        total = result.count if hasattr(result, 'count') else len(result.data)
        
        print("\n" + "="*60)
        print("最终验证结果")
        print("="*60)
        print(f"数据库总记录数: {total} 条")
        
        if total == 1402:
            print("✅ 数据库记录数正确！")
        elif total < 1402:
            print(f"⚠️  还缺少 {1402 - total} 条数据")
        else:
            print(f"⚠️  仍有 {total - 1402} 条多余数据")
        
        return total
    
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return 0

def main():
    """主函数"""
    print("="*60)
    print("Supabase 数据库去重工具")
    print("="*60)
    
    # 1. 连接数据库
    supabase = connect_to_supabase()
    
    # 2. 获取所有记录
    all_records = get_all_records(supabase)
    
    if not all_records:
        print("❌ 无法获取数据")
        return
    
    print(f"\n当前记录数: {len(all_records)}")
    print(f"预期记录数: 1402")
    print(f"多余记录: {len(all_records) - 1402}")
    
    # 3. 找出重复项
    duplicates, unique_count = find_duplicates(all_records)
    
    # 4. 删除重复项
    if duplicates:
        delete_duplicates(supabase, duplicates)
    
    # 5. 验证最终结果
    verify_final_count(supabase)

if __name__ == "__main__":
    main()