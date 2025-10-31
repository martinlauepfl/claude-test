# Cloudflare 配置指南

## 项目概述
为 ai-fortune.top 配置 Cloudflare CDN 加速和安全防护,并设置 www 到裸域的 301 重定向。

## 第一步: 添加域名到 Cloudflare

### 1. 注册/登录 Cloudflare
- 访问 https://dash.cloudflare.com/
- 使用你的账号登录(或免费注册)

### 2. 添加站点
1. 点击右上角 "Add a Site" (添加站点)
2. 输入你的域名: `ai-fortune.top`
3. 选择套餐: **Free** (免费版足够使用)
4. 点击 "Continue" 继续

### 3. 等待 DNS 扫描
Cloudflare 会自动扫描你现有的 DNS 记录,需要 1-2 分钟。

---

## 第二步: 配置 DNS 记录

扫描完成后,你需要配置以下 DNS 记录指向 GitHub Pages:

### 必需的 DNS 记录

#### 1. A 记录(裸域 ai-fortune.top)
添加 4 条 A 记录指向 GitHub Pages 的 IP:
```
Type: A
Name: @
IPv4 address: 185.199.108.153
Proxy status: Proxied (橙色云图标)
```

重复添加以下 3 个 IP:
- `185.199.109.153`
- `185.199.110.153`
- `185.199.111.153`

#### 2. CNAME 记录(www 子域名)
```
Type: CNAME
Name: www
Target: (你的 GitHub Pages 地址)
Proxy status: Proxied (橙色云图标)
```

#### 3. CNAME 记录(GitHub Pages 验证)
如果你有自定义域名验证记录,保留它:
```
Type: CNAME
Name: _github-pages-challenge-martinlauepfl
Target: (GitHub 提供的验证值)
Proxy status: DNS only (灰色云图标)
```

### DNS 配置完成标志
- 所有主要记录的 Proxy status 应该是 "Proxied" (橙色云)
- DNS 状态显示 "Active"

---

## 第三步: 更换域名服务器(Nameservers)

### 1. 获取 Cloudflare Nameservers
Cloudflare 会显示两个名称服务器,类似:
```
eamon.ns.cloudflare.com
raquel.ns.cloudflare.com
```

### 2. 前往域名注册商
- 登录你购买 ai-fortune.top 的域名注册商(如 Namecheap, GoDaddy, 阿里云等)
- 找到 "域名管理" → "DNS 设置" 或 "Nameservers"

### 3. 修改 Nameservers
将默认 Nameservers 替换为 Cloudflare 提供的两个:
```
eamon.ns.cloudflare.com
raquel.ns.cloudflare.com
```

### 4. 等待生效
- Nameserver 更改可能需要 **2-48 小时**生效(通常 2-4 小时)
- Cloudflare 会发送邮件通知激活成功

---

## 第四步: 设置 301 重定向(www → 裸域)

等 Nameservers 生效后,配置重定向规则:

### 方法 1: 使用 Page Rules(免费版)

1. 在 Cloudflare 控制面板,点击你的域名 `ai-fortune.top`
2. 左侧菜单选择 **Rules** → **Page Rules**
3. 点击 "Create Page Rule"

#### 配置如下:
```
URL: www.ai-fortune.top/*
Setting: Forwarding URL
Status Code: 301 - Permanent Redirect
Destination URL: https://ai-fortune.top/$1
```

4. 点击 "Save and Deploy"

**注意**: 免费版有 3 条 Page Rules 限额,足够使用。

### 方法 2: 使用 Redirect Rules(推荐,新版功能)

如果你的账户支持新版 Rules:

1. 左侧菜单选择 **Rules** → **Redirect Rules**
2. 点击 "Create rule"

#### 配置如下:
```
Rule name: WWW to Apex Redirect

When incoming requests match:
  Field: Hostname
  Operator: equals
  Value: www.ai-fortune.top

Then:
  Type: Dynamic
  Expression: concat("https://ai-fortune.top", http.request.uri.path)
  Status code: 301
```

3. 点击 "Deploy"

---

## 第五步: SSL/TLS 配置

### 1. 设置 SSL 模式
1. 左侧菜单选择 **SSL/TLS** → **Overview**
2. 选择加密模式: **Full** (推荐)
   - **Full**: Cloudflare 和 GitHub Pages 之间使用加密连接
   - 不要选 "Flexible",会导致重定向循环

### 2. 启用 Always Use HTTPS
1. 在 **SSL/TLS** → **Edge Certificates**
2. 打开 **Always Use HTTPS** 开关
3. 这会自动将所有 HTTP 请求重定向到 HTTPS

### 3. 启用 HSTS(可选,安全增强)
在同一页面:
```
Enable HSTS: ON
Max Age: 6 months (推荐)
Include subdomains: ON
Preload: OFF (除非你确定要永久启用)
```

---

## 第六步: GitHub Pages 配置

### 1. 更新仓库 CNAME 文件
确保你的仓库根目录有 CNAME 文件,内容为:
```
ai-fortune.top
```

### 2. 启用 HTTPS
1. 前往 GitHub 仓库 Settings → Pages
2. 在 "Custom domain" 输入: `ai-fortune.top`
3. 勾选 **Enforce HTTPS**
4. 等待 DNS 检查通过(可能需要几分钟)

---

## 第七步: 性能优化(可选)

### 1. 启用自动压缩
- 在 **Speed** → **Optimization**
- 启用 **Auto Minify**: HTML, CSS, JavaScript
- 启用 **Brotli** 压缩

### 2. 缓存配置
- 在 **Caching** → **Configuration**
- Caching Level: **Standard** (免费版默认)
- Browser Cache TTL: **4 hours** (推荐)

### 3. 启用 HTTP/3
- 在 **Network** → **HTTP/3 (with QUIC)**
- 开启 HTTP/3 支持

---

## 验证配置是否成功

### 1. 检查 DNS 传播
访问 https://dnschecker.org/ ,输入 `ai-fortune.top`,确认全球 DNS 已传播。

### 2. 测试重定向
在浏览器输入:
- `http://www.ai-fortune.top` → 应该 301 重定向到 `https://ai-fortune.top`
- `http://ai-fortune.top` → 应该 301 重定向到 `https://ai-fortune.top`

### 3. 检查 SSL 证书
- 访问 https://ai-fortune.top
- 点击浏览器地址栏的锁图标,确认证书由 Cloudflare 颁发

### 4. 测试页面加载
- 打开网站,检查所有功能正常(登录、聊天、支付)
- 打开浏览器开发者工具(F12),检查是否有 Mixed Content 错误

---

## 常见问题排查

### 问题 1: 重定向循环(Too many redirects)
**原因**: SSL 模式设置错误
**解决**: 在 SSL/TLS → Overview 改为 **Full** 模式

### 问题 2: www 无法访问或重定向失败
**原因**: DNS 记录配置错误或未生效
**解决**:
- 检查 www CNAME 记录是否指向 `martinlauepfl.github.io`
- 确保 Proxy status 是 "Proxied" (橙色云)

### 问题 3: GitHub Pages 显示 "Domain's DNS record could not be retrieved"
**原因**: Nameservers 未生效或 DNS 配置错误
**解决**:
- 等待 24-48 小时 Nameservers 完全生效
- 检查 A 记录是否正确配置 4 个 GitHub Pages IP

### 问题 4: 部分资源加载失败(Mixed Content)
**原因**: HTTP 和 HTTPS 混用
**解决**:
- 检查 `index.html` 中所有外部资源(CDN)使用 `https://`
- 启用 "Always Use HTTPS"

---

## 配置检查清单

- [ ] 域名已添加到 Cloudflare
- [ ] DNS 记录配置完成(A 记录 + www CNAME)
- [ ] Nameservers 已更换并生效
- [ ] 301 重定向规则已创建(www → 裸域)
- [ ] SSL/TLS 模式设置为 **Full**
- [ ] Always Use HTTPS 已启用
- [ ] GitHub Pages Custom Domain 设置为 `ai-fortune.top`
- [ ] GitHub Pages HTTPS 已启用
- [ ] 测试 www 重定向正常
- [ ] 测试 HTTPS 访问正常
- [ ] 网站所有功能测试通过

---

## 预计时间线

1. **DNS 配置**: 5-10 分钟
2. **Nameservers 更换**: 立即完成(在注册商)
3. **Nameservers 生效**: 2-48 小时(通常 2-4 小时)
4. **Cloudflare 激活**: Nameservers 生效后立即
5. **SSL 证书颁发**: Cloudflare 激活后 5-15 分钟
6. **重定向规则生效**: 配置后立即生效
7. **全球 DNS 传播**: 24-48 小时完全传播

**建议**: 先完成 DNS 配置和 Nameservers 更换,然后等待 2-4 小时后再配置其他高级功能。

---

## 下一步行动

当前需要你手动操作:
1. 登录 Cloudflare 添加域名
2. 配置 DNS 记录
3. 在域名注册商更换 Nameservers
4. 等待生效后设置重定向规则

如果遇到任何问题,可以参考本文档的故障排查部分。
