# 웹 크롤러

## 1 웹 크롤러 아키텍처

![image (3)](https://github.com/user-attachments/assets/ecf18989-8f67-4554-b59e-0ee9968dac05)

### 1.1 그래프 탐색

- 웹 크롤러는 www에 대해 BFS or DFS를 수행하는 시스템.
- 하나의 출발 URL에서 시작해서 그안의 링크들을 추출하고, 또 그 링크들을 따라사면서 새로운 페이지를 탐색하는 방식.

---

### 1.2 크롤링 흐름

> Frontier → Fetcher → Parser → URL 필터링 → 중복 제거 → Frontier → …

**[1] URL Frontier (시작점)**

- 크롤러가 방문할 URL 목록을 가지고 있는 대기열.
- 여기사 BFS/DFS의 큐(Queue) 또는 스택(Stack) 역할을 함.
- 여기서 URL 하나를 꺼내서 Fetcher에게 전달함.

**[2] Fetcher (수집기)**

- 전달받은 URL을 실제로 웹에 요청해서 HTML을 가져옴.
- DNS를 통해 도메인 이름을 IP로 변환함 (이게 위 그림의 DNS 박스).
- 응답받은 HTML을 Parser에게 넘겨줌.

**[3] Parser (해석기)**

- HTML을 분석해서 새로운 URL들을 추출함.
  - 보통 `<a href=”…”>` 같은 하이퍼링크 태그.
- 이 URL 후보군들은 다시 탐색 대상이 됨.

**[4] Content Seen? ( 내용 중복 체크)**

- HTML 내용이 이전에 본 것과 완전히 똑같은지 확인.
- Doc FP (Fingerprint) : 해시처럼 문서 내용의 고유 ID를 만들어 비교함.
  - [문서 단위로 유사 중복을 판별하는 방법](https://github.com/aragorn/home/wiki/Near-Duplicate-Documents-Detection)

**[5] URL Filter**

- `robots.txt`에 따른 필터링을 수행 :
  - 크롤러가 요청을 해도 되거나 해선 안되는 경로를 적어둔 곳.
  - 페이지 루트 도메인에서 `/robots.txt`으로 들어가기.
  - https://www.mk.co.kr/robots.txt

**[6] Dup URL Elim (URL 중복 제거)**

- URL Set에 있는지 확인하여 이미 방문했거나 등록된 URL은 제거.
- 완전히 새로운 URL만 골라서 다시 Frontier로 보냄.

## 2 구현

### 2.1 URL Frontier 구현

- 대상 URL : https://www.mk.co.kr/
- Frontier : 방문할 URL 목록을 관리하는 큐 역할.
- Python의 `queue.Queue` 또는 `collections.deque` 사용 가능.
- URL을 추가하고 꺼내는 큐 구조 만들기.
- 중복 방지를 위해 set을 함께 사용.

---

### 2.2 Fetcher 구현

- `reuqests` 라이브러리 설치 후 Python에서 HTTP 요청 가능.
- URL을 받아서 HTTP GET 요청 전송.
  - `requests.get()`
  - header에 `User-Agent` :
    - 서버가 요청을 판단할 때 참고함 (크롤러 차단, 응답 변경 등).
    - 프로그램 이름과 버전.
    - (+URL) 형식은 optional인데, 보통 크롤러의 홈페이지나 연락처를 적기도 함 (검색엔진처럼 공개 크롤러일 경우).
- 응답 코드 확인 후, HTML 내용 (텍스트) 반환.
- 실패한 요청은 적절히 처리 (예외 처리).

---

### 2.3 Parser 구현

- `beautifulsoup4`, `lxml` 라이브러리 사용 가능.
- HTML을 분석해서 `<a href="...">` 링크를 찾아냄.
- 절대 URL로 변환 (`/about` → `https://example.com/about` 등).
- 유효한 HTTP/HTTPS 링크만 필터링.

---

### 2.4 중복 URL 제거 (Dup URL Elim)

- 같은 URL을 여러 번 크롤링하게 된다면?
  - 시간 낭비, 무한 루프의 위험성 존재.
- 따라서 두 가지 체크를 해야 함.
  - 이미 방문한 적 있는 URL인가?
  - Frontier에 이미 들어가 있는 URL인가?
- 앞서 URLFrontier 생성시 만들어두었던 `self.seen_urls = set()` 코드를 통해 중복체크 가능.

**[ 고도화 가능한 부분 ]**

- `seen_urls`를 메모리가 아닌 파일/데이터베이스/Redis에 저장해서 확장 가능.
- 중복 제거할 때 URL 정규화를 더 철저하게 함 (슬래시 유무, 쿼리 파라미터 등).
- 방문 여부를 해시로 빠르게 체스 (Bloom Filter 등).

---

### 2.5 URL Filter 구현

- 매일 경제 robots.txt : https://www.mk.co.kr/robots.txt
- 크롤링하고자하는 URL이 `robots.txt`에 의해 차단된 경로인지 확인.
  - 차단되었으면 Frontier에 추가하지 않음.
- Python의 `robotparser` 사용 가능.

**[ 고도화 가능한 부분 ]**

- 동일 사이트의 robots.txt는 한 번만 읽고 재사용하도록 `robots.txt` 캐싱.
- 요청 간 간격을 서버가 지정할 수 있도록 `Crawl-delay` 처리.
