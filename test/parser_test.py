from parser import Parser

def test_parser():
    parser = Parser()
    base_url = "https://example.com/articles/"

    sample_html = """
    <html>
      <body>
        <a href="/about">About</a>                             <!-- 절대 경로 -->
        <a href="https://www.python.org/">Python</a>           <!-- 완전한 절대 URL -->
        <a href="contact.html">Contact</a>                     <!-- 상대 경로 -->
        <a href="../team">Team</a>                             <!-- 상대 상위 경로 -->
        <a href="mailto:test@example.com">Email</a>            <!-- 제외 대상 -->
        <a href="ftp://example.com/file.txt">FTP</a>           <!-- 제외 대상 -->
        <a href="javascript:void(0)">Click</a>                 <!-- 제외 대상 -->
      </body>
    </html>
    """

    links = parser.extract_links(base_url, sample_html)

    print("\n추출된 링크 목록:")
    for link in links:
        print("-", link)

    expected_links = {
        "https://example.com/about",
        "https://www.python.org/",
        "https://example.com/articles/contact.html",
        "https://example.com/team"
    }

    assert links == expected_links
    print("parser 테스트 통과")

if __name__ == "__main__":
    test_parser()
