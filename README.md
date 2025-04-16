# 뉴스 기사 크롤링 & Kafka 프로듀서 연동

> 크롤러를 통해 수집한 뉴스 기사 데이터를 Kafka 클러스터로 전송하는 프로젝트입니다.

<br>

## 📌 주요 목적

- 웹 크롤러를 구현하여 실시간 뉴스 데이터를 수집
- 수집된 데이터를 Kafka Producer를 통해 Kafka 클러스터로 전송

<br>

## 📖 사전 학습 개념

### ✅ Web Crawler 아키텍처

[crawler 정리](https://github.com/hgene2452/web_crawler_study/blob/main/docs/crawler.md)
- **Fetcher**: URL 요청 및 HTML 응답 수신
- **Parser**: HTML 문서에서 제목, 본문 등 데이터 추출
- **Frontier**: 수집할 URL을 관리하는 큐 역할
- **Filter**: 중복 및 불필요한 URL 제거

### ✅ Kafka 클러스터 & Producer 이해

[kafka 정리](https://github.com/hgene2452/web_crawler_study/blob/main/docs/kafka.md)
- Kafka 클러스터 구성 (다중 브로커 포함)
- Kafka Python 라이브러리 사용 (`kafka-python`)
- `KafkaProducer` 객체로 메시지 직렬화 후 전송

<br>

## 🔧 프로젝트 구성

```bash
web_crawler_study/
├── docker/
│   └── docker-compose.yml.py  # Kafka 브로커, Kafka UI 컨테이너 생성
├── producer.py                # KafkaProducer 인스턴스 정의
├── crawler.py                 # 크롤러 실행 및 Kafka 전송 로직
├── fetcher.py                 # HTML fetch 기능
├── parser.py                  # 뉴스 파싱 로직
├── frontier.py                # URL 큐 관리
├── test/                      # 테스트 코드
└── .gitignore
```

<br>

## 🧪 실습 결과 요약

✅ 수집 대상
MK 뉴스 경제 페이지

✅ 수집 데이터

- 제목 (title)
- 본문 내용 (body)
- 기사 링크 (url)
- 수집 일시 (crawled_at)

✅ 처리 결과

- 위 정보를 포함한 Python 객체 리스트 생성
- KafkaProducer.send() 메서드를 통해 Kafka로 전송

<br>

## 🚀 실행 방법

Kafka 클러스터 실행 (docker-compose 등)

```bash
docker-compose up --build
```

.venv 가상 환경 생성 및 활성화

```bash
python -m venv .venv
source .venv/bin/activate
```

필수 라이브러리 설치

```bash
pip install requests beautifulsoup4 kafka-python
```

kafka 토픽 생성

```bash
kafka-topics.sh \
  --create \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

crawler.py 실행

```bash
python -m crawler
```

.venv 가상 비활성화

```bash
deactivate
```

docker 컨테이너 제거 및 로컬 볼륨 삭제

```bash
docker-compose down -v
```

<br>

<img width="1469" alt="image (5)" src="https://github.com/user-attachments/assets/80d7410a-6423-4d63-b61d-b52233d688b8" />

<br>

전송된 메시지는 지정된 Kafka Topic(e.g. localhost:8080)에서 확인할 수 있습니다.

<br>

## 🛠 사용 기술 스택

<img src="https://img.shields.io/badge/Python 3.12-3776AB?style=for-the-badge&logo=python&logoColor=white"><img src="https://img.shields.io/badge/Requests-506365?style=for-the-badge&logo=Requests&logoColor=white"><img src="https://img.shields.io/badge/BeautifulSoup4-EF3F56?style=for-the-badge&logo=BeautifulSoup4&logoColor=white"><img src="https://img.shields.io/badge/Apache Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white"><img src="https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
