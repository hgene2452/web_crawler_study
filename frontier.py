from collections import deque

class URLFrontier:
    def __init__(self):
        self.queue = deque()
        self.seen_urls = set()
    
    def add_url(self, url):
        if url not in self.seen_urls:
            self.queue.append(url)
            self.seen_urls.add(url)

    def get_next_url(self):
        if self.queue:
            return self.queue.popleft()
        return None
    
    def is_empty(self):
        return len(self.queue) == 0