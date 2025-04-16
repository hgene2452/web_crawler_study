from fetcher import Fetcher
from parser import Parser
from url_filter import URLFilter
from frontier import URLFrontier
from bs4 import BeautifulSoup
from datetime import datetime
from producer import producer
import json

START_URL = "https://www.mk.co.kr/news/economy/"
TOPIC_URL = "test-crawling-topic"

# 기사 URL 확인 조건
def is_article_url(url):
    return "/news/economy/" in url and url.split("/")[-1].isdigit()

# 제목 + 본문 추출
def extract_article_content(html):
    soup = BeautifulSoup(html, "html.parser")

    # 제목 추출
    title_tag = soup.select_one("h2.news_ttl")
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    # 본문 추출
    body_wrapper = soup.select_one("div.news_cnt_detail_wrap")
    paragraphs = body_wrapper.find_all("p") if body_wrapper else []
    body_text = "\n".join(p.get_text(strip=True) for p in paragraphs) if paragraphs else "본문 없음"

    return {
        "title": title,
        "body": body_text
    }

def run():
    fetcher = Fetcher()
    parser = Parser()
    url_filter = URLFilter()
    frontier = URLFrontier()

    print(f"\n시작 URL: {START_URL}")

    # 시작 페이지에서 기사 URL 추출
    status, html = fetcher.fetch(START_URL)
    if status != 200 or html is None:
        print("시작 페이지 요청 실패")
        return

    links = parser.extract_links(START_URL, html)
    print(f"추출된 링크 수: {len(links)}")

    for link in links:
        if is_article_url(link):
            frontier.add_url(link)

    print(f"탐색 대상 기사 수: {len(frontier.queue)}")

    # 기사 페이지 크롤링
    while not frontier.is_empty():
        url = frontier.get_next_url()
        print(f"\n기사 방문: {url}")

        if not url_filter.is_allowed(url):
            print("robots.txt 차단됨")
            continue

        status, article_html = fetcher.fetch(url)
        if status != 200 or article_html is None:
            print("기사 요청 실패")
            continue

        article = extract_article_content(article_html)

        # Kafka에 전송할 데이터 형식
        article_data = {
            "title": article['title'],
            "content": article['body'],
            "url": url,
            "crawled_at": datetime.utcnow().isoformat()
        }
        
        # Kafka로 전송
        print(f"Kafka로 전송 중: {article_data['title']}")
        future = producer.send(TOPIC_URL, value=article_data)

        # 결과 확인 (타임아웃 예외처리)
        try:
            result = future.get(timeout=10)
            print("Kafka로 전송 완료: ", result)
        except Exception as e:
            print("Kafka로 전송 실패: ", e)

    producer.flush() # 보내기 완료 기다림
    producer.close() # 연결 종료

if __name__ == "__main__":
    run()
