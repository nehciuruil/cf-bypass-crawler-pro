# -*- coding: utf-8 -*-
import asyncio
from enum import Enum
from playwright.async_api import Page
from config import CF_MAX_WAIT, CF_CHECK_INTERVAL
import logging

logger = logging.getLogger("cf_crawler.cf_handler")

class CFStatus(Enum):
    NORMAL = "normal"          # 无CF防护/已通过
    FIVE_SECOND = "five_second"# 5秒盾
    TURNSTILE = "turnstile"    # CF人机验证(Turnstile)
    IP_BLOCK = "ip_block"      # IP封禁
    UNKNOWN = "unknown"        # 未知CF状态

class CFHandler:
    def __init__(self):
        self.max_wait = CF_MAX_WAIT
        self.check_interval = CF_CHECK_INTERVAL

    async def _detect_status(self, page: Page) -> CFStatus:
        """精准CF状态检测，低误判"""
        try:
            content = await page.content()
            title = await page.title()
            url = page.url.lower()

            # 特征匹配（优先级：IP封禁 > Turnstile > 5秒盾 > 正常）
            if any(kw in content for kw in ["Access denied", "IP blocked", "Your IP has been", "cloudflare ray id"]):
                return CFStatus.IP_BLOCK
            if any(kw in content or kw in title for kw in ["Cloudflare Challenge", "Turnstile", "Verify you are human", "cf-captcha"]):
                return CFStatus.TURNSTILE
            if any(kw in content or kw in title for kw in ["Just a moment", "Checking your browser", "cf-browser-verification"]):
                return CFStatus.FIVE_SECOND
            if "cloudflare" in content.lower() and "cf-ray" in content.lower():
                return CFStatus.UNKNOWN
            return CFStatus.NORMAL
        except Exception as e:
            logger.error(f"CF状态检测异常：{str(e)}")
            return CFStatus.UNKNOWN

    async def handle(self, page: Page) -> CFStatus:
        """分级处理CF防护，智能等待/引导，无冗余操作"""
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < self.max_wait:
            status = await self._detect_status(page)
            logger.info(f"当前CF状态：{status.value}")

            if status == CFStatus.NORMAL:
                return CFStatus.NORMAL
            elif status == CFStatus.IP_BLOCK:
                logger.critical("IP被Cloudflare封禁，需更换代理")
                return CFStatus.IP_BLOCK
            elif status == CFStatus.TURNSTILE:
                logger.warning("检测到CF Turnstile人机验证，请在浏览器中完成验证后按Enter")
                # 非阻塞等待用户操作
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, input, "完成验证后按Enter继续...")
                await asyncio.sleep(1)
            elif status in [CFStatus.FIVE_SECOND, CFStatus.UNKNOWN]:
                await asyncio.sleep(self.check_interval)

        logger.error(f"CF验证超时，超过{self.max_wait}秒")
        return CFStatus.UNKNOWN
