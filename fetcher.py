import requests

class Fetcher:
    def __init__(self, timeout=5):
        self.timeout = timeout # 요청 타임아웃(초) 설정 (기본값 5초)

    def fetch(self, url):
        try:
            # GET 요청을 보내고 응답을 받음
            response = requests.get(
                url, 
                timeout=self.timeout, # 타임아웃 지정
                headers={
                    # 서버에 전달할 User-Agent (크롤러 정체성)
                    "User-Agent": "MySimpleCrawler/1.0 (https://github.com/hgene2452/web_crawler_study)"
                }
            )

            # 응답 코드가 200 (정상)인 경우 HTML 반환
            if response.status_code == 200:
                print(f"Fetched {url}")
            else:
                # 정상 응답이 아닐 경우 상태코드 출력
                print(f"Fatiled to fetch {url} (status: {response.status_code})")
            return response.status_code, response.text # HTML 문자열 반환 - status 관계없이 내용은 반환 (로그는 남김)

        except requests.RequestException as e:
            # 네트워크 오류, 연결 실패 등 예외 처리
            print(f"Error fetching {url}: {e}")

            return None, None # 실패했을 경우 None 반환