## 环境要求
- Windows 10/11
- Python 3.10+
- 网络通畅（Playwright自动下载Chromium）

## 快速部署
### 1. 克隆/下载项目
```bash
git clone https://github.com/nehciuruil/cf-bypass-crawler-pro.git
cd cf-bypass-crawler-pro
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装Playwright驱动（必须）
```bash
playwright install Chromium
```

### 4. 配置代理（可选，强烈推荐）
编辑 `proxies.txt`，每行一个代理：
```
http://ip:port
http://user:pass@ip:port
socks5://ip:port
```

### 5. 运行程序
```bash
python main.py
```

## 高级调优（config.py）
1. **CF_MAX_WAIT**：面对慢响应CF站点，调至60秒
2. **HEADLESS**：高防护站点设为False（非无头），调试完成后改True
3. **PROXY_ENABLE**：IP频繁封禁时，务必启用住宅代理池
4. **HUMAN_EMULATE**：行为检测严格时，增大MIN_DELAY/MAX_DELAY
5. **CF_CHECK_INTERVAL**：状态检测间隔，越小响应越快，越小资源占用越高

## 高防护CF绕过策略
| 防护类型 | 解决方案 |
|----------|----------|
| 深度指纹检测 | 全维度指纹伪装+Stealth，无自动化特征 |
| 5秒盾 | 智能等待，自动通过 |
| Turnstile | 浏览器手动完成验证，程序复用Cookie |
| IP封禁 | 启用住宅代理池，自动切换失效代理 |
| 行为检测 | 开启动态行为仿真，增大操作延迟 |
| IP信誉风控 | 高匿住宅代理+有效Cookie绑定 |

## 常见问题
1. **Playwright安装失败**：以管理员身份运行PowerShell，重新执行`playwright install chrome`
2. **CF验证超时**：启用代理池，延长CF_MAX_WAIT，改为非无头模式
3. **IP频繁封禁**：使用住宅代理，避免数据中心代理
4. **中文乱码**：程序已内置Windows编码修复，使用PowerShell运行

## 法律声明
本工具仅用于合法的网络测试、学术研究，爬取行为需遵守目标网站robots.txt协议及相关法律法规，严禁用于非法数据窃取、商业爬虫等违法行为。
