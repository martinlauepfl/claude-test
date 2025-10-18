# 部署指南

## 第一步：部署 Cloudflare Worker

1. **注册 Cloudflare 账号**
   - 访问 https://dash.cloudflare.com/sign-up
   - 免费注册一个账号

2. **创建 Worker**
   - 登录后，点击左侧菜单 "Workers & Pages"
   - 点击 "Create application"
   - 选择 "Create Worker"
   - 给 Worker 起个名字，比如 `ai-fortune-api`
   - 点击 "Deploy"

3. **配置 Worker 代码**
   - 部署后，点击 "Edit code"
   - 删除默认代码，复制 `worker.js` 的全部内容粘贴进去
   - 点击右上角 "Save and Deploy"

4. **设置环境变量（重要！）**
   - 返回 Worker 详情页
   - 点击 "Settings" 标签
   - 找到 "Environment Variables" 部分
   - 点击 "Add variable"
   - 变量名：`API_KEY`
   - 变量值：`sk-dd0415392eba4dd1856f2b29560b0035`
   - 勾选 "Encrypt"（加密）
   - 点击 "Save"

5. **获取 Worker URL**
   - 在 Worker 详情页，你会看到一个 URL，类似：
   - `https://ai-fortune-api.你的用户名.workers.dev`
   - **复制这个 URL**，下一步需要用到

## 第二步：更新前端代码

1. 打开 `index.html`
2. 找到 `callAPI()` 函数
3. 修改其中的 API 调用地址为你的 Worker URL
4. 删除 `config.js` 的引用

## 第三步：提交到 GitHub

```bash
git add .
git commit -m "使用 Cloudflare Worker 保护 API keys"
git push
```

等待几分钟，GitHub Pages 会自动更新。

## 验证

访问你的网站 www.ai-fortune.top，测试对话功能是否正常。

---

## 费用说明

Cloudflare Workers 免费套餐：
- 每天 100,000 次请求
- 完全够用，无需付费

## 安全性

✅ API Key 存储在 Cloudflare 环境变量中，加密保存
✅ 用户浏览器无法看到 API Key
✅ GitHub 代码中不包含任何密钥
