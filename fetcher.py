import requests

class Fetcher:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def fetch(self, url):
        try:
            response = requests.get(
                url, 
                timeout=self.timeout,
                headers={
                    "User-Agent": "MySimpleCrawler/1.0 (https://github.com/hgene2452/web_crawler_study)"
                }
            )
            if response.status_code == 200:
                print(f"Fetched {url}")
                return response.text
            else:
                print(f"Fatiled to fetch {url} (status: {response.status_code})")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
        return None