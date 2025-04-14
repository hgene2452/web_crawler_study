from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

class URLFilter:
    def __init__(self, user_agent="MySimpleCrawler"):
        self.user_agent = user_agent
        # 도메인 별 robots.txt 캐싱
        self.robot_parsers = {}

    def is_allowed(self, url):
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        if base_url not in self.robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            try:
                rp.read()
                self.robot_parsers[base_url] = rp
            except:
                print(f"robots.txt 읽기 실패: {base_url}")
                return False
        
        rp = self.robot_parsers[base_url]
        allowed = rp.can_fetch(self.user_agent, url)
        return allowed