import re  # 정규표현식을 쓰기 위한 표준 라이브러리입니다. (주소 검사에 활용)
from browser_setup import BrowserSetup  # Playwright 브라우저를 쉽게 열고 닫도록 만든 도우미 클래스


def main():
    # 검색창에 넣을 텍스트입니다.
    # 다른 단어를 검색하고 싶다면 아래 문자열을 바꾸면 됩니다.
    query = "온달좀"

    # with 문: "자동으로 열고 자동으로 닫기" 도구
    # BrowserSetup(...) 이 브라우저를 켜고,
    # with 블록이 끝나면 브라우저가 자동으로 닫히니 초보자도 기억해 둘 필요가 없습니다.
    # headless=False : 실제 브라우저 창이 화면에 나타나도록 설정합니다. (True 로 바꾸면 창이 뜨지 않습니다.)
    with BrowserSetup(headless=False) as browser_setup:
        # new_page() 는 새 탭을 여는 것과 같습니다.
        page = browser_setup.new_page()

        # 네이버 첫 화면으로 이동합니다.
        # wait_until="domcontentloaded" : 화면의 기본 뼈대가 만들어질 때까지 기다립니다.
        page.goto("https://www.naver.com", wait_until="domcontentloaded")

        # 네이버 검색창을 선택하기 위한 CSS 선택자입니다.
        # 두 가지 선택자를 함께 적어서 어떤 경우에도 검색창을 찾도록 했습니다.
        sel = "input[name='query'], input#query"

        # 검색창이 실제로 화면에 보일 때까지 최대 6초 기다립니다.
        page.wait_for_selector(sel, state="visible", timeout=6000)

        # 검색창을 클릭해서 커서를 옮깁니다.
        page.click(sel)

        # 검색어 입력: delay=60 으로 0.06초마다 한 글자씩 넣어 사람이 쳐주는 것처럼 보이게 합니다.
        page.type(sel, query, delay=60)

        # 키보드의 Enter 키를 눌러 검색을 시작합니다.
        page.keyboard.press("Enter")

        # 검색 결과 주소에 "search.naver.com" 이 나타날 때까지 최대 20초 기다립니다.
        # re.compile(...) 은 정규표현식 도구로, 주소 문자열을 검사할 때 사용합니다.
        page.wait_for_url(re.compile(r"search\.naver\.com"), timeout=20000)

        # ✅ 새로 추가한 기능: 검색 결과 화면을 스크린샷으로 저장합니다.
        # full_page=True 로 설정하면 페이지 전체를 한 장에 담아 줍니다.
        # 저장 파일 이름은 요청하신 대로 "naver_screen_capture.png" 입니다.
        page.screenshot(path="naver_screen_capture.png", full_page=True)

        # 현재 페이지 제목과 주소를 확인해 콘솔에 출력합니다.
        print("title:", page.title())
        print("url:", page.url)

        # 페이지의 전체 HTML 내용을 문자열로 가져옵니다.
        page_content = page.content()

        # 우리가 검색한 단어가 결과 페이지 안에도 포함되어 있는지 간단히 확인합니다.
        # assert 가 실패하면 프로그램이 멈추고 아래 메시지를 보여 줍니다.
        assert query in page_content, f"검색어 '{query}'가 검색 결과에 없습니다!"
        print(f"✓ 검색 결과에 '{query}'가 포함되어 있습니다.")


# Python 스크립트가 직접 실행될 때만 main() 함수를 호출하도록 하는 표준 구조입니다.
if __name__ == "__main__":
    main()
