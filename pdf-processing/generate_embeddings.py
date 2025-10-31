#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成知识库向量嵌入 - 使用阿里云千问API
为RAG系统准备向量化的知识库数据
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Any
import sys
from tqdm import tqdm

# 配置
API_KEY = os.getenv("ALIBABA_API_KEY")  # 从环境变量获取
BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"

# 输入输出文件
INPUT_FILE = "/Users/martinlau/Desktop/horo/pdf-processing/output/knowledge_base_rag_clean.json"
OUTPUT_FILE = "/Users/martinlau/Desktop/horo/pdf-processing/output/knowledge_base_with_embeddings.json"

def load_knowledge_base(file_path: str) -> List[Dict[str, Any]]:
    """加载知识库数据"""
    print(f"正在加载知识库数据: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    knowledge_base = data.get('knowledge_base', [])
    print(f"加载了 {len(knowledge_base)} 条知识库数据")

    return knowledge_base, data

def generate_embedding(text: str, retry_count: int = 3) -> List[float]:
    """调用千问API生成向量嵌入"""
    if not API_KEY:
        print("警告: 未设置 ALIBABA_API_KEY 环境变量")
        return None

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'text-embedding-v4',
        'input': {
            'texts': [text]
        },
        'parameters': {
            'text_type': 'document'
        }
    }

    for attempt in range(retry_count):
        try:
            response = requests.post(BASE_URL, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            if 'output' in result and 'embeddings' in result['output']:
                embedding = result['output']['embeddings'][0]['embedding']
                return embedding
            else:
                print(f"API响应格式错误: {result}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"API调用失败 (尝试 {attempt + 1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                return None
        except Exception as e:
            print(f"生成嵌入时出错: {e}")
            return None

def process_batch(knowledge_base: List[Dict], batch_size: int = 10) -> List[Dict]:
    """批量处理知识库数据，生成向量嵌入"""
    processed_data = []

    print(f"开始处理 {len(knowledge_base)} 条数据，批量大小: {batch_size}")
    print("注意: 千问text-embedding-v4模型生成1024维向量")

    for i in tqdm(range(0, len(knowledge_base), batch_size), desc="处理进度"):
        batch = knowledge_base[i:i + batch_size]

        for item in batch:
            # 准备文本内容
            text_content = ""

            # 从知识库项中提取文本
            if isinstance(item, dict):
                # 尝试不同的字段名
                for field in ['content', 'text', 'title', 'description']:
                    if field in item and item[field]:
                        text_content += str(item[field]) + "\n"

                # 如果没有找到内容字段，尝试遍历所有字段
                if not text_content:
                    for key, value in item.items():
                        if key not in ['id', 'embedding', 'vector'] and value:
                            text_content += str(value) + " "
            else:
                text_content = str(item)

            # 限制文本长度（千问API有token限制）
            if len(text_content) > 8000:
                text_content = text_content[:8000] + "..."

            # 生成向量嵌入
            embedding = generate_embedding(text_content.strip())

            if embedding:
                # 添加嵌入到数据项
                item_with_embedding = item.copy()
                item_with_embedding['embedding'] = {
                    'vector': embedding,
                    'dimension': len(embedding),
                    'model': 'text-embedding-v4',
                    'created_at': datetime.now().isoformat()
                }
                processed_data.append(item_with_embedding)
            else:
                print(f"警告: 无法为项 {i} 生成嵌入")
                processed_data.append(item)  # 保留原始数据

        # 批次间暂停，避免API限制
        if i + batch_size < len(knowledge_base):
            time.sleep(1)

    return processed_data

def save_with_embeddings(original_data: Dict, processed_knowledge_base: List[Dict], output_file: str):
    """保存带有向量嵌入的知识库"""
    # 更新元数据
    metadata = original_data.get('metadata', {}).copy()
    metadata['updated_at'] = datetime.now().isoformat()
    metadata['embedding_model'] = 'text-embedding-v4'
    metadata['embedding_dimension'] = 1024
    metadata['total_processed'] = len(processed_knowledge_base)

    # 统计成功生成嵌入的数量
    embedded_count = sum(1 for item in processed_knowledge_base if 'embedding' in item)
    metadata['embedded_count'] = embedded_count
    metadata['embedding_rate'] = f"{embedded_count / len(processed_knowledge_base) * 100:.2f}%"

    # 准备输出数据
    output_data = {
        'metadata': metadata,
        'statistics': original_data.get('statistics', {}),
        'knowledge_base': processed_knowledge_base
    }

    # 保存到文件
    print(f"\n正在保存到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"保存完成!")
    print(f"- 总数据条数: {len(processed_knowledge_base)}")
    print(f"- 成功嵌入: {embedded_count}")
    print(f"- 嵌入率: {metadata['embedding_rate']}")

def main():
    """主函数"""
    print("=" * 50)
    print("知识库向量化工具 - 阿里云千问")
    print("=" * 50)

    # 检查API密钥
    if not API_KEY:
        print("错误: 请设置 ALIBABA_API_KEY 环境变量")
        print("export ALIBABA_API_KEY='your-api-key-here'")
        sys.exit(1)

    # 加载知识库
    if not os.path.exists(INPUT_FILE):
        print(f"错误: 输入文件不存在: {INPUT_FILE}")
        sys.exit(1)

    knowledge_base, original_data = load_knowledge_base(INPUT_FILE)

    if not knowledge_base:
        print("错误: 知识库数据为空")
        sys.exit(1)

    # 处理数据
    start_time = time.time()
    processed_data = process_batch(knowledge_base)
    end_time = time.time()

    # 保存结果
    save_with_embeddings(original_data, processed_data, OUTPUT_FILE)

    print(f"\n处理完成! 总耗时: {end_time - start_time:.2f} 秒")
    print(f"输出文件: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()