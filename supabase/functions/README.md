# Supabase Edge Functions 说明

本目录包含所有部署的 Supabase Edge Functions。

## 函数列表

### 1. ai-chat-with-rag
**用途**: 集成RAG功能的AI聊天服务
- 功能：先检索知识库，再调用AI生成回答
- 特点：AI会直接引用古籍原文
- 依赖：阿里云API、Supabase数据库

### 2. ai-chat
**用途**: 基础AI聊天服务
- 功能：不使用知识库的纯AI对话
- 用途：备用服务或简单咨询

### 3. rag-search
**用途**: RAG向量搜索服务
- 功能：根据用户查询检索相关知识
- 输出：返回相关古籍文本片段
- 向量维度：1024

### 4. generate-embeddings
**用途**: 批量生成向量嵌入
- 功能：为知识库文本生成向量
- 用途：知识库维护和更新

### 5. alibaba-tts
**用途**: 阿里云文本转语音
- 功能：将文字转换为语音
- 用途：语音播报功能（可选）

### 6. stripe-checkout
**用途**: Stripe支付处理
- 功能：创建支付会话
- 集成：与Stripe支付系统

### 7. stripe-webhook
**用途**: Stripe Webhook处理
- 功能：处理支付回调
- 功能：确认支付状态

## 部署说明

每个函数都需要：
1. 复制对应目录下的 `index.ts` 文件内容
2. 在 Supabase Dashboard 中创建/更新函数
3. 设置环境变量
4. 部署并测试

## 环境变量

所有函数需要的环境变量：
- `ALIBABA_API_KEY`: 阿里云DashScope API密钥
- `SUPABASE_URL`: Supabase项目URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase服务角色密钥

## 重要提示

- 这些是生产环境正在使用的函数
- 修改前请备份
- 确保环境变量正确配置
- 测试后再部署到生产环境