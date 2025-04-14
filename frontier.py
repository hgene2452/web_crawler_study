from collections import deque

class URLFrontier:
    def __init__(self):
        self.queue = deque()            # 크롤링할 URL을 저장할 큐 (BFS 탐색에 적합)
        self.seen_urls = set()          # 중복된 URL 추가를 방지하기 위한 집합
    
    # 새 URL을 큐에 추가 (이미 본 URL은 제외)
    def add_url(self, url):
        if url not in self.seen_urls:
            self.queue.append(url)      # 큐에 추가
            self.seen_urls.add(url)     # 중복 방지를 위해 집합에 기록

    # 다음에 방문할 URL을 큐에서 꺼냄
    def get_next_url(self):
        if self.queue:
            return self.queue.popleft() # 큐의 앞에서 하나 꺼냄
        return None
    
    # 큐가 비었는지 여부 확인
    def is_empty(self):
        return len(self.queue) == 0