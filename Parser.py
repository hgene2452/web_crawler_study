from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Parser:
    def extract_links(self, base_url, html):
        # 추출한 링크들을 저장할 집합 (중복 제거)
        links = set()
        # HTML 문자열을 BeautifulSoup 객체로 파싱
        soup = BeautifulSoup(html, "html.parser")

        # <a> 태그 중 href 속성이 있는 것만 반복
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"] # 링크 주소 추출 (상대 또는 절대일 수 있음)

            # 상대 경로인 경우, base_url 기준으로 절대 경로로 변환
            full_url = urljoin(base_url, href)

            # URL을 구성 요소별로 분해 (scheme, netloc, path 등)
            parsed = urlparse(full_url)
            
            # http 또는 https 링크만 허용 (mailto:, ftp:, javascript: 등 제외)
            if parsed.scheme in ["http", "https"]:
                links.add(full_url) # 중복 없이 추가됨

        # 최종적으로 추출된 유효한 링크 집합 반환
        return links