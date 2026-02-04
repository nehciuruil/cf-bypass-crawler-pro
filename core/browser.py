# -*- coding: utf-8 -*-
import random
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
# 适配playwright_stealth 2.x版本（直接导入异步stealth）
from playwright_stealth import stealth
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
        # 读取指纹伪装脚本（兼容路径不存在的异常）
        try:
            self.fp_script = Path("assets/fingerprint.js").read_text(encoding="utf-8")
        except FileNotFoundError:
            self.fp_script = ""
            logger.warning("⚠️ 指纹伪装脚本 assets/fingerprint.js 不存在，跳过注入")

    def _get_random_ua(self) -> str:
        """获取随机UA（兼容UA池为空）"""
        if not UA_POOL:
            default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            logger.warning("⚠️ UA池为空，使用默认UA")
            return default_ua
        return random.choice(UA_POOL)

    async def init(self) -> bool:
        """初始化零特征浏览器（自动检测系统Chrome/Edge，无硬编码路径）"""
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

            # 获取有效代理（兼容代理池为空）
            proxy = None
            try:
                proxy = await self.proxy_pool.get_valid_proxy()
            except Exception as e:
                logger.warning(f"⚠️ 获取代理失败，禁用代理：{str(e)[:50]}")
            proxy_config = {"server": proxy} if proxy else None

            # 自动检测系统浏览器（优先Chrome，降级Edge）
            browser_launched = False
            # 1. 优先启动系统Chrome
            try:
                self.browser = await self.playwright.chromium.launch(
                    headless=HEADLESS,
                    args=launch_args,
                    proxy=proxy_config,
                    ignore_default_args=["--enable-automation"],
                    channel="chrome"
                )
                logger.info("✅ 成功启动系统Chrome浏览器")
                browser_launched = True
            except Exception as e:
                logger.warning(f"⚠️ 系统Chrome未检测到（{str(e)[:60]}），尝试启动Edge")
                # 2. 降级启动系统Edge
                try:
                    self.browser = await self.playwright.chromium.launch(
                        headless=HEADLESS,
                        args=launch_args,
                        proxy=proxy_config,
                        ignore_default_args=["--enable-automation"],
                        channel="msedge"
                    )
                    logger.info("✅ 成功启动系统Edge浏览器")
                    browser_launched = True
                except Exception as e2:
                    logger.error(f"❌ 系统Chrome/Edge均未检测到：{str(e2)}")
            
            if not browser_launched:
                logger.error("❌ 浏览器启动失败：未安装Chrome/Edge，且无备用浏览器")
                return False

            # 创建上下文，设置基础指纹
            self.context = await self.browser.new_context(
                viewport=VIEWPORT,
                user_agent=self._get_random_ua(),
                ignore_https_errors=True,
                locale="zh-CN"
            )

            # 注入深度指纹伪装脚本（兼容脚本为空）
            if self.fp_script:
                await self.context.add_init_script(self.fp_script)
                logger.info("✅ 深度指纹伪装脚本已注入")
            logger.info("✅ 浏览器初始化完成，全维度指纹已伪装")
            return True

        except Exception as e:
            logger.error(f"❌ 浏览器初始化失败：{str(e)}")
            await self.close()
            return False

    async def new_page(self) -> Page:
        """创建新页面并应用Stealth防检测"""
        try:
            page = await self.context.new_page()
            # 应用stealth防检测（适配2.x版本）
            await stealth(page)
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
            logger.info("✅ 新页面创建完成，Stealth防检测已应用")
            return page
        except Exception as e:
            logger.error(f"❌ 创建新页面失败：{str(e)}")
            raise e  # 抛出异常让上层处理

    async def close(self):
        """安全释放浏览器资源"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("✅ 浏览器资源已安全释放")
        except Exception as e:
            logger.warning(f"⚠️ 释放浏览器资源时出现异常：{str(e)}")
