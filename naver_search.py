#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import sys, re

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "짜까스"
    # Wrap the Playwright context with stealth so launch/new_context/new_page
    # are automatically patched and init scripts are injected.
    with Stealth().use_sync(sync_playwright()) as p:
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

        # 스텔스 패치는 위의 Stealth().use_sync(...)로 이미 적용됨

        page.goto("https://www.naver.com", wait_until="domcontentloaded")
        sel = "input[name='query'], input#query"
        page.wait_for_selector(sel, state="visible", timeout=15000)
        page.click(sel)
        page.type(sel, query, delay=60)  # 사람처럼 천천히 타이핑
        page.keyboard.press("Enter")
        page.wait_for_url(re.compile(r"search\.naver\.com"), timeout=20000)
        print("title:", page.title())
        print("url:", page.url)

        # 검색 결과 페이지 내용 가져오기
        page_content = page.content()

        # "짜까스"가 검색 결과에 있는지 확인
        assert query in page_content, f"검색어 '{query}'가 검색 결과에 없습니다!"
        print(f"✓ 검색 결과에 '{query}'가 포함되어 있습니다.")

        browser.close()

if __name__ == "__main__":
    main()
