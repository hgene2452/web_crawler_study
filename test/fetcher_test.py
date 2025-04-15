import unittest
from fetcher import Fetcher

class TestFetcher(unittest.TestCase):
    def test(self):
        fetcher = Fetcher()

        # [1] 정상 페이지 요청 테스트
        status, html = fetcher.fetch("https://www.mk.co.kr/")
        self.assertEqual(status, 200)
        self.assertIsNotNone(html)
        self.assertIn("<html", html.lower())

        # [2] 존재하지 않는 페이지 테스트 (404 등)
        status, html = fetcher.fetch("https://www.mk.co.kr/thispagedoesnotexist123")
        self.assertEqual(status, 404)
        self.assertIsNotNone(html)

        # [3] 잘못된 도메인 테스트 (예외 처리)
        status, html = fetcher.fetch("https://notarealwebsitexyz.openai")
        self.assertIsNone(status)
        self.assertIsNone(html)