import re
from browser_setup import BrowserSetup


def main():
    query = "온달좀"

    # BrowserSetup 클래스를 컨텍스트 매니저로 사용하여 자동으로 리소스 관리
    with BrowserSetup(headless=False) as browser_setup:
        # 새 페이지 생성
        page = browser_setup.new_page()

        # 네이버 메인 페이지로 이동
        page.goto("https://www.naver.com", wait_until="domcontentloaded")

        # 검색창에 검색어 입력
        sel = "input[name='query'], input#query"
        page.wait_for_selector(sel, state="visible", timeout=6000)
        page.click(sel)
        page.type(sel, query, delay=60)  # 사람처럼 천천히 타이핑
        page.keyboard.press("Enter")

        # 검색 결과 페이지 로딩 대기
        page.wait_for_url(re.compile(r"search\.naver\.com"), timeout=20000)
        print("title:", page.title())
        print("url:", page.url)

        # 검색 결과 페이지 내용 가져오기
        page_content = page.content()

        # 검색어가 검색 결과에 있는지 확인
        assert query in page_content, f"검색어 '{query}'가 검색 결과에 없습니다!"
        print(f"✓ 검색 결과에 '{query}'가 포함되어 있습니다.")


if __name__ == "__main__":
    main()
