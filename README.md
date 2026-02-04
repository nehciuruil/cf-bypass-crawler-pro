# CF Bypass Crawler Pro
工业级Cloudflare绕过爬虫，支持CF 5秒盾/Turnstile验证/深度指纹检测/IP封禁规避，开箱即用。

## 🌟 特性
- 🚀 自动检测系统Chrome/Edge浏览器，无硬编码路径
- 🛡️ 全维度指纹伪装，消除所有自动化特征
- 🔄 多轮重试机制，提升绕过成功率
- 🇨🇳 适配国内镜像，下载依赖不卡顿
- 📝 详细日志输出，便于调试和问题定位

## 📋 环境要求
- Python 3.10 ~ 3.12（推荐3.11，避免3.14+兼容性问题）
- Windows/Mac/Linux（Windows需预装Chrome/Edge）
- 网络环境：可访问目标网站（如需翻墙请配置代理）

## ⚡ 快速开始
### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/cf-bypass-crawler-pro.git
cd cf-bypass-crawler-pro
```

### 2. 一键安装依赖
#### 方法1：跨平台（推荐）
```bash
python install.py
```

#### 方法2：Windows快捷方式
双击运行 `install.bat`

### 3. 运行程序
```bash
python main.py
```

### 4. 使用说明
- 运行后输入目标URL（必须包含https://）
- 程序会自动尝试绕过CF验证并爬取页面源码
- 爬取成功后，源码会保存到 `crawl_result.html`

## 📄 配置说明
### 代理配置
- 编辑 `proxies.txt` 文件，按以下格式填写代理：
  ```
  http://账号:密码@代理IP:端口
  socks5://代理IP:端口
  ```
- 空文件表示禁用代理

### 自定义配置
- 修改 `config.py` 文件可调整：
  - `HEADLESS`：是否无头模式运行（True/False）
  - `VIEWPORT`：浏览器窗口大小
  - `UA_POOL`：用户代理池
  - `MAX_RETRY`：最大重试次数
