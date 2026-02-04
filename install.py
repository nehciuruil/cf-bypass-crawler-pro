#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
import sys

def run_command(cmd: list, desc: str):
    """执行命令并处理异常"""
    print(f"\n【{desc}】")
    try:
        subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
        print(f"✅ {desc}成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ {desc}失败：{e.output[:500]}")
        sys.exit(1)

def main():
    # 中文编码适配
    if sys.platform == "win32":
        os.system("chcp 65001 >nul")
    
    print("="*60)
    print("CF Bypass Crawler Pro - 一键安装脚本")
    print("适配国内镜像，自动安装所有依赖")
    print("="*60)

    # 1. 升级pip并设置国内镜像
    pip_mirror = "-i https://pypi.tuna.tsinghua.edu.cn/simple"
    run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", pip_mirror],
        "升级pip"
    )

    # 2. 安装Python依赖
    run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", pip_mirror],
        "安装Python依赖"
    )

    # 3. 设置Playwright国内镜像并安装浏览器驱动
    os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://npmmirror.com/mirrors/playwright/"
    run_command(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        "安装Playwright浏览器驱动"
    )

    # 4. 创建空的代理文件（规避警告）
    if not os.path.exists("proxies.txt"):
        with open("proxies.txt", "w", encoding="utf-8") as f:
            f.write("")
        print("✅ 创建空代理文件 proxies.txt")

    print("\n" + "="*60)
    print("✅ 所有依赖安装完成！")
    print("📌 运行程序：python main.py")
    print("📌 如需使用代理，请编辑 proxies.txt 文件")
    print("="*60)

if __name__ == "__main__":
    main()
