#!/usr/bin/env python3
"""
Capture screenshots of Qwen 3.5 related websites
"""

import asyncio
from playwright.async_api import async_playwright

async def capture_screenshot(url, output_path, full_page=False):
    """Capture screenshot of a URL"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})

            # Navigate to the page
            await page.goto(url, wait_until="networkidle")

            # Wait a bit for any dynamic content
            await asyncio.sleep(2)

            # Capture screenshot
            await page.screenshot(path=output_path, full_page=full_page)

            await browser.close()
            print(f"✓ Screenshot saved: {output_path}")
            return True
    except Exception as e:
        print(f"✗ Failed to capture {url}: {e}")
        return False

async def main():
    """Main function"""
    images_dir = "/Users/damon/myWork/myBlog/qwen35-research/images"

    # URLs to capture
    urls = [
        ("https://chat.qwen.ai/", f"{images_dir}/screenshot_qwen_chat_home.png"),
        ("https://huggingface.co/collections/Qwen/qwen3-67dd247413f0e2e4f653967f", f"{images_dir}/screenshot_qwen3_hf.png"),
        ("https://modelscope.cn/collections/Qwen3-9743180bdc6b48", f"{images_dir}/screenshot_qwen3_modelscope.png"),
    ]

    # Capture screenshots
    for url, output_path in urls:
        await capture_screenshot(url, output_path, full_page=False)

    print("\n✓ Screenshot capture complete!")

if __name__ == "__main__":
    asyncio.run(main())
