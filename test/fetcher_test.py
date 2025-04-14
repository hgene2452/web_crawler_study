from fetcher import Fetcher

def test_fetcher():
    fetcher = Fetcher()

    print("\n[1] 정상 페이지 요청 테스트")
    status, html = fetcher.fetch("https://www.mk.co.kr/")
    assert status == 200
    assert html is not None and "<html" in html.lower()
    print("정상 페이지 fetch 테스트 통과")

    print("\n[2] 존재하지 않는 페이지 테스트 (404 등)")
    status, html = fetcher.fetch("https://www.mk.co.kr/thispagedoesnotexist123")
    assert status == 404
    assert html is not None  # 404라도 HTML 본문은 반환되는 경우 많음
    print("404 페이지 처리 테스트 통과")

    print("\n[3] 잘못된 도메인 테스트 (예외 처리)")
    status, html = fetcher.fetch("https://notarealwebsitexyz.openai")
    assert status is None and html is None  # 예외 발생 시 (None, None) 반환됨
    print("예외 발생 처리 테스트 통과")

if __name__ == "__main__":
    test_fetcher()
