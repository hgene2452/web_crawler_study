import unittest
from frontier import URLFrontier

class TestURLFrontier(unittest.TestCase):
    def test_frontier(self):
        # URLFrontier 인스턴스 생성
        frontier = URLFrontier()

        # 테스트용 URL을 추가 (세 번째는 중복)
        frontier.add_url("https://www.mk.co.kr/")
        frontier.add_url("https://www.chosun.com/")
        frontier.add_url("https://www.mk.co.kr/")  # 중복 URL, 큐에 추가되지 않아야 함

        # 큐가 비어있지 않은지 확인
        self.assertFalse(frontier.is_empty())

        urls = []

        # 큐가 빌 때까지 URL을 꺼내서 리스트에 저장
        while not frontier.is_empty():
            url = frontier.get_next_url()
            urls.append(url)

        # 중복 제거가 잘 되었는지 확인
        self.assertEqual(
            urls,
            ["https://www.mk.co.kr/", "https://www.chosun.com/"]
        )