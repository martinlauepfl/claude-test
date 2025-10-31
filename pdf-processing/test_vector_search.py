#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 AI Chat with RAG Function
"""

import requests
import json

# 配置
SUPABASE_URL = "https://mulrkyqqhaustbojzzes.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11bHJreXFxaGF1c3Rib2p6emVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NTAzNDYsImV4cCI6MjA3NjMyNjM0Nn0.IP0h8Ps8CSloKNvsE8yItTOE4zdVLf36zLnsgm18uhc"

def test_ai_chat(user_message: str):
    """测试 AI Chat Function"""
    
    url = f"{SUPABASE_URL}/functions/v1/ai-chat-with-rag"
    
    headers = {
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "你是一个精通中国古代文化的AI助手，擅长解读易经、周易等古籍。"
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    
    print("="*60)
    print(f"用户问题: {user_message}")
    print("="*60)
    print("\nAI 回答:")
    print("-"*60)
    
    # 发送请求（流式响应）
    response = requests.post(
        url, 
        headers=headers, 
        json=payload,
        stream=True  # 重要：启用流式接收
    )
    
    if response.status_code != 200:
        print(f"❌ 错误: {response.status_code}")
        print(response.text)
        return
    
    # 处理流式响应
    full_response = ""
    
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            
            # 跳过空行和注释
            if not line_text.strip() or line_text.startswith(':'):
                continue
            
            # 解析 SSE 格式
            if line_text.startswith('data: '):
                data_str = line_text[6:]  # 去掉 "data: " 前缀
                
                # 跳过 [DONE] 标记
                if data_str.strip() == '[DONE]':
                    break
                
                try:
                    data = json.loads(data_str)
                    
                    # 提取内容
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        
                        if content:
                            print(content, end='', flush=True)
                            full_response += content
                
                except json.JSONDecodeError:
                    continue
    
    print("\n" + "-"*60)
    print(f"\n✅ 回答完成 (共 {len(full_response)} 字)")
    print("="*60)
    
    return full_response

if __name__ == "__main__":
    # 测试 1: 简单问题
    print("\n【测试 1】简单问题")
    test_ai_chat("什么是乾卦？")
    
    print("\n\n")
    
    # 测试 2: 复杂问题
    print("\n【测试 2】复杂问题")
    test_ai_chat("乾卦在易经中的地位如何？它有什么深层含义？")
    
    print("\n\n")
    
    # 测试 3: 多轮对话
    print("\n【测试 3】多轮对话")
    
    url = f"{SUPABASE_URL}/functions/v1/ai-chat-with-rag"
    headers = {
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    # 第一轮
    messages = [
        {
            "role": "system",
            "content": "你是一个精通中国古代文化的AI助手。"
        },
        {
            "role": "user",
            "content": "乾卦是什么？"
        }
    ]
    
    print("用户: 乾卦是什么？")
    print("AI: ", end='')
    
    response = requests.post(url, headers=headers, json={"messages": messages}, stream=True)
    ai_response = ""
    
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            if line_text.startswith('data: ') and line_text[6:].strip() != '[DONE]':
                try:
                    data = json.loads(line_text[6:])
                    content = data['choices'][0]['delta'].get('content', '')
                    if content:
                        print(content, end='', flush=True)
                        ai_response += content
                except:
                    pass
    
    print("\n")
    
    # 第二轮（带上下文）
    messages.append({
        "role": "assistant",
        "content": ai_response
    })
    messages.append({
        "role": "user",
        "content": "那坤卦呢？"
    })
    
    print("用户: 那坤卦呢？")
    print("AI: ", end='')
    
    response = requests.post(url, headers=headers, json={"messages": messages}, stream=True)
    
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            if line_text.startswith('data: ') and line_text[6:].strip() != '[DONE]':
                try:
                    data = json.loads(line_text[6:])
                    content = data['choices'][0]['delta'].get('content', '')
                    if content:
                        print(content, end='', flush=True)
                except:
                    pass
    
    print("\n")