import unittest
from parser import Parser

class TestParser(unittest.TestCase):
    def test_extract_links(self):
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

        # 링크 추출
        links = parser.extract_links(base_url, sample_html)

        # 예상 결과
        expected_links = {
            "https://example.com/about",
            "https://www.python.org/",
            "https://example.com/articles/contact.html",
            "https://example.com/team"
        }

        # 테스트 어서션
        self.assertEqual(set(links), expected_links)