from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Parser:
    def extract_links(self, base_url, html):
        links = set()
        soup = BeautifulSoup(html, "html.parser")

        # <a> 태그 중 href 속성이 있는 것만 찾음
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # 절대 경로로 변환
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            # http 또는 https로 시작하는 링크만 추가
            if parsed.scheme in ["http", "https"]:
                links.add(full_url)

        return links