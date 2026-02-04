# -*- coding: utf-8 -*-
import random
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
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
        self.fp_script = Path("assets/fingerprint.js").read_text(encoding="utf-8")

    def _get_random_ua(self) -> str:
        return random.choice(UA_POOL)

    async def init(self) -> bool:
        """初始化零特征浏览器，所有自动化特征全部消除"""
        try:
            self.playwright = await async_playwright().start()
            # 启动参数：禁用所有自动化标记，最小化特征（保留原有所有参数）
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

            # 获取有效代理（保留原有代理逻辑）
            proxy = await self.proxy_pool.get_valid_proxy()
            proxy_config = {"server": proxy} if proxy else None

            # ========== 核心修改：自动检测系统Chrome/Edge，无硬编码路径 ==========
            browser_launched = False
            # 1. 优先启动系统Chrome（自动查找路径，跨平台通用）
            try:
                self.browser = await self.playwright.chromium.launch(
                    headless=HEADLESS,
                    args=launch_args,
                    proxy=proxy_config,
                    ignore_default_args=["--enable-automation"],
                    channel="chrome"  # 自动检测系统Chrome
                )
                logger.info("✅ 成功启动系统Chrome浏览器")
                browser_launched = True
            except Exception as e:
                logger.warning(f"⚠️ 系统Chrome未检测到（{str(e)[:60]}），尝试启动Edge")
                # 2. 降级启动系统Edge（Windows预装，兼容性最高）
                try:
                    self.browser = await self.playwright.chromium.launch(
                        headless=HEADLESS,
                        args=launch_args,
                        proxy=proxy_config,
                        ignore_default_args=["--enable-automation"],
                        channel="msedge"  # 自动检测系统Edge
                    )
                    logger.info("✅ 成功启动系统Edge浏览器")
                    browser_launched = True
                except Exception as e2:
                    logger.error(f"❌ 系统Chrome/Edge均未检测到：{str(e2)}")
            
            if not browser_launched:
                logger.error("❌ 浏览器启动失败：未安装Chrome/Edge，且无备用浏览器")
                return False
            # ========== 核心修改结束 ==========

            # 创建上下文，设置基础指纹（保留原有逻辑）
            self.context = await self.browser.new_context(
                viewport=VIEWPORT,
                user_agent=self._get_random_ua(),
                ignore_https_errors=True,
                locale="zh-CN"
            )

            # 注入深度指纹伪装脚本（核心，保留原有逻辑）
            await self.context.add_init_script(self.fp_script)
            logger.info("浏览器初始化完成，全维度指纹已伪装")
            return True

        except Exception as e:
            logger.error(f"浏览器初始化失败：{str(e)}")
            # 确保资源释放
            await self.close()
            return False

    async def new_page(self) -> Page:
        """创建新页面并应用Stealth，双重防检测（保留原有逻辑）"""
        page = await self.context.new_page()
        await stealth(page)
        # 设置标准请求头，模拟真实浏览器（保留原有请求头）
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
        """安全释放资源（保留原有逻辑，补充异常捕获）"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("浏览器资源已安全释放")
        except Exception as e:
            logger.warning(f"释放浏览器资源时出现异常：{str(e)}")
