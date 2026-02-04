# -*- coding: utf-8 -*-
import sys
import asyncio
import logging
from core.browser import BrowserCore
from core.proxy import ProxyPool
from core.cookie import CookieManager
from core.cf_handler import CFHandler
from config import MAX_RETRY, LOG_LEVEL

# 配置日志（开源友好，输出到控制台）
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("cf_crawler")

# ===================== 修复：兼容Python 3.11+的事件循环 =====================
# 解决Windows子进程NotImplementedError，适配开源场景
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except (AttributeError, DeprecationWarning):
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

async def crawl_once(browser_core: BrowserCore, cookie_mgr: CookieManager, cf_handler: CFHandler, url: str) -> str:
    """单次爬取逻辑（保留原有核心逻辑，补充异常捕获）"""
    try:
        page = await browser_core.new_page()
        # 应用CF绕过处理
        await cf_handler.bypass(page, url)
        # 获取页面源码
        source = await page.content()
        # 保存Cookie
        await cookie_mgr.save_cookies(page.context.cookies())
        await page.close()
        return source
    except Exception as e:
        logger.error(f"❌ 单次爬取失败：{str(e)}")
        raise e

async def main():
    """主函数（开源友好，交互清晰）"""
    print("="*80)
    print("      Cloudflare Bypass Crawler Pro - 工业级绕过版")
    print("      支持CF 5秒盾/Turnstile/深度指纹/IP封禁检测")
    print("="*80 + "\n")

    # 获取目标URL
    url = input("请输入目标URL（含https://）：").strip()
    if not url.startswith(("http://", "https://")):
        logger.error("❌ URL格式错误，必须以http://或https://开头")
        return

    # 初始化核心组件
    logger.info("初始化核心组件...")
    proxy_pool = ProxyPool()
    browser_core = BrowserCore(proxy_pool)
    cookie_mgr = CookieManager()
    cf_handler = CFHandler()

    # 初始化浏览器
    if not await browser_core.init():
        logger.critical("❌ 浏览器初始化失败，程序退出")
        return

    # 多轮重试爬取
    source = None
    for retry in range(1, MAX_RETRY + 1):
        logger.info(f"第 {retry}/{MAX_RETRY} 次尝试")
        try:
            source = await crawl_once(browser_core, cookie_mgr, cf_handler, url)
            if source:
                logger.info("✅ 爬取成功！")
                break
        except Exception as e:
            logger.error(f"❌ 第{retry}次尝试失败：{str(e)}")
            if retry == MAX_RETRY:
                logger.critical("❌ 所有重试均失败，程序退出")

    # 输出结果（可选：保存到文件）
    if source:
        print("\n" + "="*80)
        print("✅ 爬取成功，页面源码前500字符预览：")
        print(source[:500] + "..." if len(source) > 500 else source)
        # 可选：保存源码到文件
        with open("crawl_result.html", "w", encoding="utf-8") as f:
            f.write(source)
        logger.info("✅ 爬取结果已保存到 crawl_result.html")

    # 释放资源
    await browser_core.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ 用户手动终止程序")
    except Exception as e:
        logger.critical(f"❌ 程序异常退出：{str(e)}")
        sys.exit(1)
