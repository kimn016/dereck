from playwright.sync_api import sync_playwright


class BrowserSetup:
    def __init__(self, headless=False):
        """
        브라우저 설정 초기화

        Args:
            headless: headless 모드 사용 여부 (기본값: False - headful이 탐지 회피에 유리)
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def setup(self):
        """브라우저 및 컨텍스트 설정"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
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
        return self

    def new_page(self):
        """새 페이지 생성"""
        if self.context is None:
            raise RuntimeError("먼저 setup()을 호출해야 합니다.")
        self.page = self.context.new_page()
        return self.page

    def close(self):
        """브라우저 및 관련 리소스 정리"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()