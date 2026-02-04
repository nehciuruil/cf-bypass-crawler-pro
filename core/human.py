# -*- coding: utf-8 -*-
import random
import asyncio
from playwright.async_api import Page
from config import HUMAN_EMULATE, MIN_DELAY, MAX_DELAY, MOUSE_MOVE_PROB, PAGE_SCROLL_PROB
import logging

logger = logging.getLogger("cf_crawler.human")

class HumanEmulator:
    @staticmethod
    async def emulate(page: Page):
        """动态行为仿真：基于页面生成真实操作，而非固定轨迹"""
        if not HUMAN_EMULATE:
            return
        try:
            # 基础随机延迟
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            await asyncio.sleep(delay)
            logger.debug(f"基础延迟：{delay:.2f}s")

            # 模拟鼠标移动（概率触发）
            if random.random() < MOUSE_MOVE_PROB:
                w = await page.evaluate("window.innerWidth")
                h = await page.evaluate("window.innerHeight")
                x = random.randint(int(w*0.1), int(w*0.9))
                y = random.randint(int(h*0.1), int(h*0.8))
                steps = random.randint(8, 20)
                await page.mouse.move(x, y, steps=steps)
                await asyncio.sleep(random.uniform(0.2, 0.6))
                logger.debug(f"模拟鼠标移动至 ({x}, {y})")

            # 模拟页面滚动（概率触发）
            if random.random() < PAGE_SCROLL_PROB:
                scroll_y = random.randint(200, 900)
                await page.evaluate(f"window.scrollTo({{top: {scroll_y}, behavior: 'smooth'}})")
                await asyncio.sleep(random.uniform(0.3, 0.8))
                logger.debug(f"模拟页面滚动至 {scroll_y}px")

        except Exception as e:
            logger.debug(f"行为仿真异常，不影响主流程：{str(e)}")
