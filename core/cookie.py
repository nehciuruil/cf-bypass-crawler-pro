# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from urllib.parse import urlparse
from typing import List
from playwright.async_api import BrowserContext
from config import COOKIE_PERSIST, COOKIE_DIR, CF_COOKIE_KEYS
import logging

logger = logging.getLogger("cf_crawler.cookie")

class CookieManager:
    def __init__(self):
        self.enable = COOKIE_PERSIST
        self.cookie_dir = Path(COOKIE_DIR)
        self.cookie_dir.mkdir(exist_ok=True)

    def _get_domain(self, url: str) -> str:
        """从URL提取根域名，作为Cookie存储标识"""
        parsed = urlparse(url)
        return parsed.netloc.replace(":", "_")

    def _get_cookie_path(self, domain: str) -> Path:
        return self.cookie_dir / f"{domain}.json"

    async def load_cookies(self, context: BrowserContext, url: str) -> bool:
        """加载对应域名的有效CF Cookie"""
        if not self.enable:
            return False
        domain = self._get_domain(url)
        path = self._get_cookie_path(domain)
        if not path.exists():
            logger.info(f"域名 {domain} 无已保存Cookie")
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            # 仅加载CF关键Cookie
            cf_cookies = [c for c in cookies if c.get("name") in CF_COOKIE_KEYS]
            await context.add_cookies(cf_cookies)
            logger.info(f"成功加载 {len(cf_cookies)} 个CF Cookie，域名：{domain}")
            return True
        except Exception as e:
            logger.error(f"加载Cookie失败：{str(e)}")
            return False

    async def save_cookies(self, context: BrowserContext, url: str):
        """保存有效CF Cookie，自动过滤无效项"""
        if not self.enable:
            return
        domain = self._get_domain(url)
        path = self._get_cookie_path(domain)
        try:
            all_cookies = await context.cookies()
            # 只保留CF有效Cookie，剔除无用项
            valid_cookies = [c for c in all_cookies if c.get("name") in CF_COOKIE_KEYS and c.get("value")]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(valid_cookies, f, ensure_ascii=False, indent=2)
            logger.info(f"成功保存 {len(valid_cookies)} 个有效CF Cookie，域名：{domain}")
        except Exception as e:
            logger.error(f"保存Cookie失败：{str(e)}")
