# -*- coding: utf-8 -*-
import os
from typing import Optional, List

# ==================== 基础配置 ====================
# 目标URL
TARGET_URL: str = ""
# 源码保存路径
SAVE_PATH: str = "cf_bypassed.html"
# Windows编码修复
WIN_ENCODING_FIX: bool = True

# ==================== Cloudflare 核心配置 ====================
# CF验证最大等待时间（秒）
CF_MAX_WAIT: int = 45
# CF状态检测间隔（秒）
CF_CHECK_INTERVAL: float = 0.8
# 总重试次数
MAX_RETRY: int = 4
# 页面加载完成等待（秒）
PAGE_LOAD_WAIT: int = 3

# ==================== 浏览器防检测配置 ====================
# 无头模式（高防护建议False）
HEADLESS: bool = False
# 视口
VIEWPORT: dict = {"width": 1920, "height": 1080}
# 随机UA池（Windows主流，无重复特征）
UA_POOL: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Edg/133.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/115.0.0.0"
]

# ==================== 代理池配置 ====================
# 启用代理
PROXY_ENABLE: bool = True
# 代理文件路径（每行一个，格式：http://ip:port 或 socks5://ip:port）
PROXY_FILE: str = "proxies.txt"
# 代理检测超时（秒）
PROXY_CHECK_TIMEOUT: int = 4
# 代理最大失败次数，超过则移除
PROXY_MAX_FAIL: int = 2
# 代理检测目标（用于快速验证连通性）
PROXY_TEST_URL: str = "http://httpbin.org/ip"

# ==================== Cookie配置 ====================
# 启用Cookie持久化
COOKIE_PERSIST: bool = True
# Cookie存储目录
COOKIE_DIR: str = "cookies"
# 仅保留CF关键Cookie
CF_COOKIE_KEYS: List[str] = ["cf_clearance", "__cf_bm", "cf_use_obf", "cf_session"]

# ==================== 行为仿真配置 ====================
# 启用行为仿真
HUMAN_EMULATE: bool = True
# 最小/最大操作延迟（秒）
MIN_DELAY: float = 1.2
MAX_DELAY: float = 3.5
# 模拟鼠标/滚动概率
MOUSE_MOVE_PROB: float = 0.9
PAGE_SCROLL_PROB: float = 0.85
