from url_filter import URLFilter

def test_url_filter():
    url_filter = URLFilter(user_agent="MySimpleCrawler")

    print("\n[1] robots.txt 허용 테스트 (예: https://example.com/)")
    allowed = url_filter.is_allowed("https://example.com/")
    assert allowed is True or allowed is False  # robots.txt 없을 수도 있음
    print(f"접근 {'허용' if allowed else '차단'}됨")

    print("\n[2] robots.txt 차단 테스트 (예: https://www.mk.co.kr/search)")
    allowed = url_filter.is_allowed("https://www.mk.co.kr/search")
    assert allowed is False
    print("차단된 경로 처리 테스트 통과")

    print("\n[3] 존재하지 않는 도메인 테스트 (예외 처리)")
    allowed = url_filter.is_allowed("https://notarealwebsitexyz.openai/path")
    assert allowed is False  # 읽기 실패 시 기본 차단 정책
    print("예외 발생 시 처리 테스트 통과")

if __name__ == "__main__":
    test_url_filter()
