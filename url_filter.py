from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

class URLFilter:
    def __init__(self, user_agent="MySimpleCrawler"):
        # 크롤러의 User-Agent 지정
        self.user_agent = user_agent
        # 각 도메인 별로 robots.txt 정보를 저장할 캐시 딕셔너리
        self.robot_parsers = {}

    def is_allowed(self, url):
        # URL을 구성 요소별로 분해 (스킴, 호스트, 경로 등)
        parsed = urlparse(url)
        # robots.txt 요청을 위한 base_url 구성 (scheme + netloc)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        # 해당 도메인의 robots.txt 파서를 캐싱하지 않았다면 새로 가져옴
        if base_url not in self.robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt") # robots.txt 위치 지정
            try:
                rp.read() # robots.txt 파일 읽기 시도
                self.robot_parsers[base_url] = rp # 캐시에 저장
            except:
                print(f"robots.txt 읽기 실패: {base_url}")
                return False # robots.txt를 못 읽었으면 기본적으로 차단
        
        # 캐시된 파서를 통해 현재 URL이 접근 가능한지 확인
        rp = self.robot_parsers[base_url]
        allowed = rp.can_fetch(self.user_agent, url)

        # True: 접근 허용 / False: 접근 차단
        return allowed