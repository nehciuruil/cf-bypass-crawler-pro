# -*- coding: utf-8 -*-
import random
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import stealth_async
from config import HEADLESS, VIEWPORT, UA_POOL
from core.proxy import ProxyPool
import logging

logger = logging.getLogger("cf_crawler.browser")

class BrowserCore:
    def __init__(self, proxy_pool: ProxyPool):
        self.proxy_pool = proxy_pool
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.fp_script = Path("assets/fingerprint.js").read_text(encoding="utf-8")

    def _get_random_ua(self) -> str:
        return random.choice(UA_POOL)

    async def init(self) -> bool:
        """初始化零特征浏览器，所有自动化特征全部消除"""
        try:
            self.playwright = await async_playwright().start()
            # 启动参数：禁用所有自动化标记，最小化特征
            launch_args = [
                f"--window-size={VIEWPORT['width']},{VIEWPORT['height']}",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-web-security",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--lang=zh-CN",
                "--start-maximized",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding"
            ]

            # 获取有效代理
            proxy = await self.proxy_pool.get_valid_proxy()
            proxy_config = {"server": proxy} if proxy else None

            # 启动浏览器（忽略自动化参数）
            self.browser = await self.playwright.chromium.launch(
                headless=HEADLESS,
                args=launch_args,
                proxy=proxy_config,
                ignore_default_args=["--enable-automation"]
            )

            # 创建上下文，设置基础指纹
            self.context = await self.browser.new_context(
                viewport=VIEWPORT,
                user_agent=self._get_random_ua(),
                ignore_https_errors=True,
                locale="zh-CN"
            )

            # 注入深度指纹伪装脚本（核心）
            await self.context.add_init_script(self.fp_script)
            logger.info("浏览器初始化完成，全维度指纹已伪装")
            return True

        except Exception as e:
            logger.error(f"浏览器初始化失败：{str(e)}")
            return False

    async def new_page(self) -> Page:
        """创建新页面并应用Stealth，双重防检测"""
        page = await self.context.new_page()
        await stealth_async(page)
        # 设置标准请求头，模拟真实浏览器
        await page.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        })
        logger.info("新页面创建完成，Stealth已应用")
        return page

    async def close(self):
        """安全释放资源"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("浏览器资源已安全释放")
