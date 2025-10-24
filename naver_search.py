import math  # 이미지 간 차이를 숫자로 계산할 때 필요 (RMS 계산)
import re  # 검색 결과 주소 검사에 사용하는 정규표현식 도구
from pathlib import Path  # 파일 경로를 안전하게 다루는 표준 라이브러리

from PIL import Image, ImageChops, ImageStat  # Pillow: 이미지 열기, 비교, 통계 계산용

from browser_setup import BrowserSetup  # Playwright 브라우저를 켜고 닫아 주는 도우미 클래스

# 결과 스크린샷과 기준 이미지를 저장할 파일 경로를 한곳에서 정의해 둡니다.
# 프로그램을 실행하는 위치(현재 폴더)에 PNG 파일이 만들어집니다.
CAPTURE_PATH = Path("naver_screen_capture.png")
REFERENCE_PATH = Path("naver_screen_reference.png")


def compare_with_reference(captured_path, reference_path, diff_threshold=0.0):
    """
    방금 저장한 스크린샷과 기준 이미지를 비교해 차이가 있는지 알려줍니다.

    Args:
        captured_path: 새로 저장된 스크린샷 경로
        reference_path: 비교 대상이 되는 기준 이미지 경로
        diff_threshold: 허용할 평균 픽셀 차이 (0이면 완전 일치만 통과)

    Returns:
        일치하면 True, 다르면 False, 기준 이미지가 없으면 None
    """
    # 기준 이미지가 없다면 비교 자체를 할 수 없으므로 안내 메시지 후
    # 이번에 찍은 이미지를 기준본으로 삼아 복사해 둡니다.
    if not reference_path.exists():
        print(f"⚠️ 기준 이미지가 없어 새로 생성했습니다: {reference_path}")
        reference_path.write_bytes(captured_path.read_bytes())
        print("   → 다음 실행부터는 지금 저장된 이미지를 기준으로 비교합니다.")
        return True

    # Pillow로 두 이미지를 모두 RGB 모드로 열어 비교 준비를 합니다.
    with Image.open(captured_path).convert("RGB") as captured, Image.open(
        reference_path
    ).convert("RGB") as reference:
        # 크기가 다르면 비교 자체가 의미가 없으므로 바로 실패를 반환합니다.
        if captured.size != reference.size:
            print(
                f"✗ 이미지 크기가 다릅니다. 캡처={captured.size}, 기준={reference.size}"
            )
            return False

        # ImageChops.difference 로 픽셀 간의 차이를 나타내는 이미지(diff_image)를 만듭니다.
        diff_image = ImageChops.difference(captured, reference)
        # 통계값을 구해 각 색상 채널의 평균 밝기 차이를 얻습니다.
        stat = ImageStat.Stat(diff_image)
        # 평균 밝기 차이를 제곱해서 평균을 내고 다시 제곱근을 씌우면 RMS 값이 됩니다.
        # 값이 0이면 완전히 동일한 이미지입니다.
        rms = math.sqrt(sum(channel_mean**2 for channel_mean in stat.mean) / len(stat.mean))

        if rms <= diff_threshold:
            print(f"✓ 스크린샷이 기준 이미지와 일치합니다. (RMS {rms:.2f} ≤ {diff_threshold})")
            return True

        # 차이가 나면 diff 이미지를 따로 저장해 어떤 부분이 다른지 육안으로 확인할 수 있게 합니다.
        diff_output = captured_path.with_name(f"{captured_path.stem}_diff.png")
        diff_image.save(diff_output)
        print(
            f"✗ 스크린샷이 기준 이미지와 다릅니다. (RMS {rms:.2f} > {diff_threshold})"
        )
        print(f"   → 차이 이미지를 저장했습니다: {diff_output}")
        return False


def main():
    # 네이버 검색창에 입력할 기본 검색어입니다.
    # 다른 검색어를 쓰고 싶다면 아래 문자열을 원하는 텍스트로 바꾸면 됩니다.
    query = "온달좀"

    # with 문을 사용하면 BrowserSetup 이 알아서 브라우저를 열고,
    # 블록이 끝날 때 깔끔하게 닫아 주기 때문에 자원 관리가 쉽습니다.
    # headless=False 로 두면 실제 브라우저 창이 눈에 보이며,
    # True 로 바꾸면 화면 없이 백그라운드에서 실행됩니다.
    with BrowserSetup(headless=False) as browser_setup:
        page = browser_setup.new_page()

        # 네이버 메인 페이지로 이동합니다.
        # wait_until="domcontentloaded" 는 기본 HTML 구조가 준비될 때까지 기다리라는 의미입니다.
        page.goto("https://www.naver.com", wait_until="domcontentloaded")

        # 검색창은 상황에 따라 name 속성이나 id 속성을 쓸 수 있어서 두 가지 선택자를 모두 적었습니다.
        sel = "input[name='query'], input#query"
        # 검색창이 화면에 나타날 때까지 최대 6초 기다립니다.
        page.wait_for_selector(sel, state="visible", timeout=6000)
        # 검색창을 클릭해서 입력할 준비를 합니다.
        page.click(sel)
        # delay=60 으로 지정하면 0.06초 간격으로 글자를 입력해 사람이 타이핑하는 것처럼 보이게 됩니다.
        page.type(sel, query, delay=60)
        # Enter 키를 눌러 검색을 실행합니다.
        page.keyboard.press("Enter")

        # 검색 결과 페이지로 이동했는지 URL 로 확인합니다.
        # re.compile(...) 을 사용해 "search.naver.com" 이 포함될 때까지 기다립니다.
        page.wait_for_url(re.compile(r"search\.naver\.com"), timeout=20000)
        print("title:", page.title())
        print("url:", page.url)

        # 전체 검색 결과 화면을 스크린샷으로 저장합니다.
        # full_page=True 옵션은 페이지 길이가 길어도 한 장의 긴 이미지로 저장해 줍니다.
        page.screenshot(path=str(CAPTURE_PATH), full_page=True)
        print(f"✔ 검색 결과 화면을 저장했습니다: {CAPTURE_PATH}")

        # 검색 결과 페이지의 HTML 전체를 문자열로 가져옵니다.
        page_content = page.content()
        # HTML 안에 검색어가 있는지 확인해 결과가 제대로 나왔는지 검증합니다.
        assert query in page_content, f"검색어 '{query}'가 검색 결과에 없습니다!"
        print(f"✓ 검색 결과에 '{query}'가 포함되어 있습니다.")

        # 저장된 스크린샷과 기준 이미지를 비교해 화면이 변했는지 확인합니다.
        compare_with_reference(CAPTURE_PATH, REFERENCE_PATH)


if __name__ == "__main__":
    main()
