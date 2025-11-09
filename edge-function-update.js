/**
 * AI聊天Edge Function (集成RAG) - 支持多语言
 * 修改说明：在第27行和第44-80行
 */

// 第27行修改：接收语言参数
const { messages, language = 'zh' } = await req.json();

// 第44-80行修改：根据语言生成不同的知识库提示
if (knowledgeResults.length > 0) {
  console.log(`[AI-Chat] 使用知识库生成回答，共 ${knowledgeResults.length} 条知识`);

  // 🔥 根据语言生成不同的知识库上下文
  let knowledgeContext = language === 'zh'
    ? '\n\n## 📚 相关古籍知识（请基于以下内容回答用户问题）\n\n'
    : '\n\n## 📚 Relevant Ancient Chinese Texts (Read and understand the following content, then answer in English)\n\n';

  knowledgeResults.forEach((result, index) => {
    const sourceLabel = language === 'zh' ? '来源' : 'Source';
    knowledgeContext += `【${sourceLabel}: ${result.source || (language === 'zh' ? '古籍' : 'Ancient Text')}】\n`;
    knowledgeContext += `${result.content}\n\n`;
    knowledgeContext += `---\n\n`;
  });

  knowledgeContext += language === 'zh'
    ? `
请根据上述古籍内容，结合你的毒舌算命先生风格，给出专业且接地气的回答。

回答格式要求：
1. 使用清晰的段落分隔，每段不要超过3句话
2. 适当使用换行和标点符号，让回答有呼吸感
3. 可以用数字序号或符号（-、•）来列举不同情况
4. 古籍原文用引号标注，解读部分正常叙述
5. 不要在结尾添加任何"基于古籍记载"的标注
`
    : `
📌 Important: The ancient texts above are in Chinese. Please read and understand them thoroughly, then provide your answer entirely in English.

Based on the ancient Chinese wisdom above, provide a professional and down-to-earth answer in your slightly sarcastic fortune teller style.

Answer format requirements:
1. Use clear paragraph separation, no more than 3 sentences per paragraph
2. Use line breaks and punctuation appropriately for better readability
3. Use numbers or symbols (-, •) to list different situations when needed
4. You may reference the ancient texts (e.g., "According to ancient wisdom..."), but respond in English
5. Do not add any notes like "based on ancient records" at the end

Remember: Answer completely in ENGLISH, even though the source material is in Chinese.
`;

  messages[0].content += knowledgeContext;
  console.log('[AI-Chat] 知识库已注入到 system prompt');
}
