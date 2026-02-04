# -*- coding: utf-8 -*-
import sys
import os
import asyncio
import logging
from colorlog import ColoredFormatter
from config import (
    WIN_ENCODING_FIX, MAX_RETRY, PAGE_LOAD_WAIT,
    SAVE_PATH, TARGET_URL
)
from core.proxy import ProxyPool
from core.cookie import CookieManager
from core.human import HumanEmulator
from core.cf_handler import CFHandler, CFStatus
from core.browser import BrowserCore

# ==================== Windows 环境修复 ====================
if os.name == "nt" and WIN_ENCODING_FIX:
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
    # 兼容Python 3.14+的异步事件循环配置（消除弃用警告，纯空格缩进）
    if sys.platform == 'win32':
        try:
            # 优先使用新版策略，无则降级（统一4个空格缩进）
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except (AttributeError, DeprecationWarning):
            # 兼容旧版本（同样4个空格缩进）
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# ==================== 日志配置 ====================
def setup_logger():
    logger = logging.getLogger("cf_crawler")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    console_fmt = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={"INFO": "green", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold_red"}
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()

# ==================== 核心爬取流程 ====================
async def crawl_once(browser_core: BrowserCore, cookie_mgr: CookieManager, cf_handler: CFHandler, url: str) -> str:
    page = None
    try:
        page = await browser_core.new_page()
        # 预加载有效Cookie
        await cookie_mgr.load_cookies(browser_core.context, url)
        # 访问目标页面
        logger.info(f"开始访问：{url}")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        # 处理CF防护
        status = await cf_handler.handle(page)
        if status != CFStatus.NORMAL:
            return ""
        # 行为仿真
        await HumanEmulator.emulate(page)
        # 等待页面完全加载
        await asyncio.sleep(PAGE_LOAD_WAIT)
        # 获取渲染后源码
        source = await page.content()
        # 保存有效Cookie
        await cookie_mgr.save_cookies(browser_core.context, url)
        logger.info(f"爬取成功，源码长度：{len(source)} 字符")
        return source
    finally:
        if page:
            await page.close()

def save_source(content: str):
    """保存源码，Windows UTF-8编码"""
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"源码已保存至：{os.path.abspath(SAVE_PATH)}")
    except Exception as e:
        logger.error(f"保存失败：{str(e)}")

async def main():
    print("="*80)
    print("      Cloudflare Bypass Crawler Pro - 工业级绕过版      ")
    print("      支持CF 5秒盾/Turnstile/深度指纹/IP封禁检测      ")
    print("="*80)

    # 获取目标URL
    url = input("\n请输入目标URL（含https://）：").strip() or TARGET_URL
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        logger.error("URL格式错误，必须以http://或https://开头")
        return

    # 初始化核心组件
    logger.info("初始化核心组件...")
    proxy_pool = ProxyPool()
    cookie_mgr = CookieManager()
    cf_handler = CFHandler()
    browser_core = BrowserCore(proxy_pool)

    if not await browser_core.init():
        logger.critical("浏览器初始化失败，程序退出")
        return

    # 带重试的爬取流程
    source = ""
    for attempt in range(1, MAX_RETRY + 1):
        logger.info(f"第 {attempt}/{MAX_RETRY} 次尝试")
        source = await crawl_once(browser_core, cookie_mgr, cf_handler, url)
        if source:
            break
        logger.warning(f"第 {attempt} 次尝试失败，准备重试")
        await asyncio.sleep(2)

    # 结果处理
    if source:
        print(f"\n✅ 爬取成功！源码预览（前1000字符）：")
        print("-"*80)
        print(source[:1000] + ("..." if len(source) > 1000 else ""))
        print("-"*80)
        save = input("\n是否保存源码？(y/n，默认y)：").strip().lower()
        if save in ["", "y", "yes"]:
            save_source(source)
    else:
        logger.critical(f"经 {MAX_RETRY} 次重试，爬取最终失败")

    # 资源释放
    await browser_core.close()
    input("\n按回车键退出程序...")

if __name__ == "__main__":
    asyncio.run(main())
