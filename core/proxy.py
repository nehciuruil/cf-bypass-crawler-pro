# -*- coding: utf-8 -*-
import aiohttp
import random
from typing import Optional, List
from config import PROXY_ENABLE, PROXY_FILE, PROXY_CHECK_TIMEOUT, PROXY_MAX_FAIL, PROXY_TEST_URL
import logging

logger = logging.getLogger("cf_crawler.proxy")

class ProxyPool:
    def __init__(self):
        self.enable = PROXY_ENABLE
        self.proxies: List[str] = []
        self.proxy_failures: dict = {}
        self._load_proxies()

    def _load_proxies(self):
        """从文件加载代理，自动去重"""
        if not self.enable:
            logger.info("代理池已禁用")
            return
        try:
            with open(PROXY_FILE, "r", encoding="utf-8") as f:
                raw = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            self.proxies = list(set(raw))
            logger.info(f"代理池加载完成，有效代理数：{len(self.proxies)}")
        except FileNotFoundError:
            logger.error(f"代理文件 {PROXY_FILE} 不存在，已禁用代理")
            self.enable = False

    async def _check_proxy(self, proxy: str) -> bool:
        """高速代理连通性检测"""
        try:
            timeout = aiohttp.ClientTimeout(total=PROXY_CHECK_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(PROXY_TEST_URL, proxy=proxy) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def get_valid_proxy(self) -> Optional[str]:
        """获取可用代理，失败自动移除，秒级切换"""
        if not self.enable or not self.proxies:
            return None

        random.shuffle(self.proxies)
        for proxy in self.proxies:
            if await self._check_proxy(proxy):
                self.proxy_failures[proxy] = 0
                logger.info(f"选中有效代理：{proxy}")
                return proxy
            # 累计失败次数，超阈值移除
            self.proxy_failures[proxy] = self.proxy_failures.get(proxy, 0) + 1
            if self.proxy_failures[proxy] >= PROXY_MAX_FAIL:
                self.proxies.remove(proxy)
                logger.warning(f"代理 {proxy} 失败次数超限，已移除，剩余代理：{len(self.proxies)}")

        logger.error("代理池已无可用代理")
        return None
