#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import sys, re

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "짜까스"
    with sync_playwright() as p:
        # headful이 탐지 회피에 유리한 경우가 많음
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={"width": 1366, "height": 900},
            device_scale_factor=1.0,
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            },
        )
        page = context.new_page()

        # 기본적인 스텔스 패치 적용 (navigator.webdriver 등)
        stealth_sync(page)

        page.goto("https://www.naver.com", wait_until="domcontentloaded")
        sel = "input[name='query'], input#query"
        page.wait_for_selector(sel, state="visible", timeout=15000)
        page.click(sel)
        page.type(sel, query, delay=60)  # 사람처럼 천천히 타이핑
        page.keyboard.press("Enter")
        page.wait_for_url(re.compile(r"search\.naver\.com"), timeout=20000)
        print("title:", page.title())
        print("url:", page.url())
        browser.close()

if __name__ == "__main__":
    main()
