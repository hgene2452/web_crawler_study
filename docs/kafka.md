# 카프카 파이프라인 구축

## 1 Kafka vs Logstash

| 항목                               | Kafka                                                     | Logstash                                |
| ---------------------------------- | --------------------------------------------------------- | --------------------------------------- |
| **주요 목적**                      | 메시지 브로커 (데이터 전달 중계소)                        | 데이터 수집, 전처리, 전송               |
| **역할**                           | 고속/내결함성 있는 메시지 큐                              | 다양한 Input → Filter → Output 처리     |
| **데이터 저장**                    | 디스크 기반으로 메시지를 지정된 시간 동안 저장 (기본 7일) | 저장하지 않고 실시간 처리 (stateless)   |
| **확장성**                         | 분산처리, 수평 확장 우수                                  | 단일 인스턴스 또는 파이프라인 중심      |
| **입출력 대상**                    | Producer/Consumer 구조                                    |
| (Logstash도 Consumer가 될 수 있음) | 파일, Kafka, DB, API, Elasticsearch 등 다양하게 연결 가능 |
| **주 사용처**                      | 대규모 데이터 스트림 처리, 비동기 통신                    | 다양한 소스로부터 수집 → 가공 → 저장    |
| **실시간 전송**                    | 가능하지만 자체 전처리는 없음                             | 실시간 전송 + 필터링, 변환 가능         |
| **예시**                           | 데이터를 중간에 안전하게 넘겨주는 택배회사                | 택배 물품을 분류하고 포장하는 택배 센터 |

### 1.1 Logstash가 필요한 이유는?

1. 전처리 (필터링, 정제)가 필요하기 때문

- Kafka에서 받는 데이터는 보통 raw JSON / 로그 / 텍스트 형태이기 때문에 이걸 바로 Elasticsearch에 넣으면 아래의 문제 발생 가능.
  - 쓸데없는 필드 증가.
  - 날짜 포맷 안맞음.
  - 키가 중첩되거나 불필요하게 복잡함.
- Logstask를 사용하면 아래의 효과 가능.
  - `grok`, `mutate`, `date`, `json` 같은 필터로 데이터를 정리해줌.
    - 예를 들어 `"2024-04-01T01:00:00Z"` → `"@timestamp"` 로 파싱.
  - 불필요한 필드 삭제, 필요한 필드 추가 가능.
  ```json
  filter {
    json { source => "message" }
    mutate { remove_field => ["host", "offset"] }
    date { match => ["event_time", "ISO8601"] }
  }
  ```

2. 포맷 변환 / 구조화가 필요하기 때문

- Elasticsearch는 정형화된 JSON 구조를 선호하는데, Kafka는 다양한 형식으로 메시지를 받을 수 있기 때문에 중간에서 누군가 구조를 표준화해줘야 함.

```json
Kafka 원본 → {"msg": "CPU usage: 89%", "timestamp": "2025/04/14"}
Logstash 필터 →
{
  "cpu_usage": 89,
  "@timestamp": "2025-04-14T00:00:00Z"
}
```

3. 구성 유연성 & 유지보수 측면에서 유리하기 때문

- Logstash는 다양한 input/output/filter 조합이 가능해서 파이프라인 확장에 용이.
- 설정파일 하나만 수정해서 흐름 변경 가능.

## 2 Kafka Cluster

### 2.1 **분산 저장 (Distributed Storage)** 구조

- `Topic` : 메시지의 논리적인 묶음.
- `Partition` : Topic 안에서의 병렬 처리 단위.
- `Broker` : Kafka 서버 한 대. 각 Partition은 Broker 중 한 대에 저장됨 (Partition → Broker 매핑).

---

### 2.2 Replication 구조

```json
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Broker 1      │    │ Broker 2      │    │ Broker 3      │
│ - P0 (Leader) │    │ - P1 (Leader) │    │ - P2 (Leader) │
│ - P1 (Replica)│    │ - P2 (Replica)│    │ - P0 (Replica)│
└───────────────┘    └───────────────┘    └───────────────┘

Producer → Kafka Topic: news-headlines
          → Partition 0 → Leader: Broker 1
          → Partition 1 → Leader: Broker 2
          → Partition 2 → Leader: Broker 3

Consumer → 각 Partition에서 메시지 읽음

※ Broker 하나가 죽으면 Replica가 Leader가 됨 → 장애 대응 완료
```

- Kafka는 고가용성(HA)을 보장하기 위해 복제(replication) 기능을 사용.
- 각 Partition은 여러 개의 복제본(Replica)을 가질 수 있음.
- e.g. replication.factor = 3 이라면?
  | Partition | Leader Broker | Replica 1 | Replica 2 |
  | --------- | ------------- | --------- | --------- |
  | 0 | Broker 1 | Broker 2 | Broker 3 |
  | 1 | Broker 2 | Broker 1 | Broker 3 |
  | 2 | Broker 3 | Broker 1 | Broker 2 |
  - Leader : Producer/Consumer가 직접 통신하는 대상.
  - Follower : Leader의 데이터를 복제 받음 (read-only).
  - Producer는 항상 Leader Partition에 메시지를 씀.
  - Consumer도 Leader에서 메시지를 읽음.
- 장애가 발생할 경우 (브로커 하나가 죽으면) ? e.g. Broker 1이 죽음
  → Partition 0의 Leader였던 Broker 1이 사라짐.
  → Kafka는 자동으로 Broker 2 or 3을 Leader로 승격함.
  - Leader Election : Follower가 Leader가 되어 서비스는 계속 정상 작동.
  - 이 덕분에 Kafka는 무중단 운영이 가능해짐.

## 3 docker-compose 활용 Kafka 환경 구축

```bash
[BROKER 0]──┐
[BROKER 1]──┼─ KRaft 클러스터 (Controller + Broker) ←→ Kafka UI (8080)
[BROKER 2]──┘

↳ 공유 네트워크: data_network
↳ 각 브로커는 독립된 볼륨: DataVolume00~02
↳ Client 접근용 외부 포트: 10000 ~ 10002
```

### 3.1 네트워크 구성

```yaml
networks:
  data_network:
```

- Kafka 브로커 간 내부 통신 (Controller 선출, 데이터 복제 등)에 필요한 네트워크.
- 도커에서 서로 다른 컨테이너가 서비스명으로 통신하려면 동일한 네트워크에 있어야 함.
- Kafka UI 또한 이 네트워크를 통해 브로커들과 통신함.

---

### 3.2 볼륨 구성

```yaml
volumes:
  DataVolume00:
    driver: local
  DataVolume01:
    driver: local
  DataVolume02:
    driver: local
```

- Kafka는 데이터를 디스크에 저장함 (파티션 로그 등).
- Docker 컨테이너가 재시작되어도 데이터가 사라지지 않도록 `local volume` 설정.
- 각각의 브로커는 독립된 볼륨 사용 → 브로커 간 데이터 충돌 방지.
- `driver: local`
  - Docker의 기본 저장 방식, 컨테이너 내부 디렉토리를 호스트 머신의 로컬 디렉토리에 매핑.
  - 컨테이너 재시작/삭제에도 데이터 유지됨.
  - `/var/lib/docker/volumes/DataVolume00/_data/`에 실제 파일 저장됨.
- 다른 volume driver 예시 :
  | 드라이버 이름 | 설명 |
  | ------------- | ------------------------------------------------- |
  | `local` | 가장 일반적인 로컬 디스크 (기본값) |
  | `nfs` | NFS 네트워크 파일 시스템과 연결 |
  | `azurefile` | Azure Blob Storage 사용 시 |
  | `efs` | AWS EFS 연동 |
  | `csi` | Kubernetes CSI (Container Storage Interface) 연동 |

---

### 3.3 Kafka 브로커 설정 (KRaft 기반)

```yaml
services:
  # 카프카 브로커 00 설정
  Broker00:
    image: bitnami/kafka:3.5.1-debian-11-r44 # 카프카 이미지 버전 선택
    restart: unless-stopped # 재시작 정책
    container_name: BrokerContainer00 # 컨테이너 명명
    ports:
      # 포트 바인딩: 내 컴퓨터에서 localhost:10000 으로 접속하면 → 컨테이너의 9094로 연결됨
      - "10000:9094"
    environment: # 환경변수 설정
      - KAFKA_CFG_BROKER_ID=0
      - KAFKA_CFG_NODE_ID=0
      - KAFKA_KRAFT_CLUSTER_ID=c3dpbGlnaHQtNGZjMy05MTk5LTllMGY
      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@Broker00:9093,1@Broker01:9093,2@Broker02:9093
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://:9094
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://Broker00:9092,EXTERNAL://127.0.0.1:10000
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CFG_OFFSETS_TOPIC_REPLICATION_FACTOR=3
      - KAFKA_CFG_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=3
      - KAFKA_CFG_TRANSACTION_STATE_LOG_MIN_ISR=2
      - KAFKA_CFG_PROCESS_ROLES=controller,broker
      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
    networks:
      - data_network
    volumes:
      - "DataVolume00:/bitnami/kafka"
```

| 환경변수                                      | 의미                                                    |
| --------------------------------------------- | ------------------------------------------------------- |
| `KAFKA_CFG_BROKER_ID` / `KAFKA_CFG_NODE_ID`   | 브로커 식별자 (KRaft에선 둘 다 사용됨)                  |
| `KAFKA_KRAFT_CLUSTER_ID`                      | 클러스터 고유 ID (Base64 인코딩된 UUID, 22자 이상 추천) |
| `KAFKA_CFG_CONTROLLER_QUORUM_VOTERS`          | 리더 선출을 위한 컨트롤러 투표자 목록                   |
| `KAFKA_CFG_PROCESS_ROLES=controller,broker`   | 이 노드는 컨트롤러+브로커 역할 모두 수행                |
| `KAFKA_CFG_LISTENERS`, `ADVERTISED_LISTENERS` | 내부/외부 접근을 위한 포트 구성                         |
| `REPLICATION_FACTOR=3`, `MIN_ISR=2`           | 고가용성을 위한 복제 및 최소 인-싱크 복제본 설정        |
| `ALLOW_PLAINTEXT_LISTENER=yes`                | 인증 없이 평문 통신 허용 (테스트 환경에서만 추천)       |
| - `KAFKA_KRAFT_CLUSTER_ID`는 `uuidgen         | base64` 명령으로 생성 가능.                             |

- 모든 브로커에 동일한 값이 들어가야 클러스터로 묶임.

**[ Kafka Broker Image - `bitnami/kafka:3.5.1-debian-11-r44` ]**

| 구성 요소         | 설명                                            |
| ----------------- | ----------------------------------------------- |
| **bitnami/kafka** | Bitnami에서 만든 Kafka 도커 이미지              |
| **3.5.1**         | Kafka 버전 (Zookeeper 없는 **KRaft** 지원 포함) |
| **debian-11**     | 이미지에 포함된 OS (Debian 11 기반)             |
| **r44**           | 리비전 버전 (Bitnami 내부 빌드 넘버)            |
| 주요 특징         | - KRaft 모드 지원                               |

- Kafka 설정을 **환경변수 기반**으로 쉽게 할 수 있도록 래핑됨
- 생산환경에서도 사용 가능할 만큼 안정적 |

**[ Kafka UI Image - `provectuslabs/kafka-ui:latest` ]**

| 항목         | 내용                                                                |
| ------------ | ------------------------------------------------------------------- |
| **이미지명** | `provectuslabs/kafka-ui`                                            |
| **버전**     | `latest` (가장 최신 태그를 사용)                                    |
| **제작자**   | [Provectus](https://github.com/provectus)                           |
| **목적**     | Kafka 클러스터를 시각적으로 관리할 수 있는 **오픈소스 Web UI** 제공 |
| 기능         | - 토픽 목록, 파티션 정보, 메시지 확인                               |

- 메시지 Produce/Consume 테스트
- Consumer Group 오프셋 확인
- 토픽 생성/삭제
- Kafka Connect, Schema Registry 연동도 가능 |

**[ 정상적인 Base64 UUID 값 생성해서 넣기 - `KAFKA_KRAFT_CLUSTER_ID` ]**

```bash
# 1. UUID 생성 → Base64로 인코딩
# **리눅스/macOS 환경이라면 아래 명령어 그대로 사용**
uuidgen | tr -d '-' | xxd -r -p | base64
```

```bash
# e.g.
(.venv) hyeonjinlee@Hyeonjinui-MacBookAir docker % uuidgen | tr -d '-' | xxd -r -p | base64
eAJw2DkAQsSlgxm92vgA6Q==
```

- Kafka KRaft 모드는 Zookeeper가 없기 때문에 클러스터를 식별할 Cluster ID가 반드시 필요함.
- 이 ID는 내부 메타데이터 로그에 기록되며, Base64 UUID가 표준으로 요구됨.
- 잘못된 형식이면 `exited with code 1` 오류로 중단됨.

---

### 3.4 Kafka Web UI 구성

```yaml
WebUI:
  image: provectuslabs/kafka-ui:latest
  restart: always
  container_name: KafkaWebUI
  ports:
    - "8080:8080"
  environment:
    - KAFKA_CLUSTERS_0_NAME=MyLocalKafkaCluster
    - KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=Broker00:9092,Broker01:9092,Broker02:9092
    - DYNAMIC_CONFIG_ENABLED=true
    - KAFKA_CLUSTERS_0_AUDIT_TOPICAUDITENABLED=true
    - KAFKA_CLUSTERS_0_AUDIT_CONSOLEAUDITENABLED=true
  depends_on:
    - Broker00
    - Broker01
    - Broker02
  networks:
    - data_network
```

| 설정 항목                                              | 설명                                      |
| ------------------------------------------------------ | ----------------------------------------- |
| `KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS`                    | UI가 접근할 브로커들의 PLAINTEXT 주소     |
| `DYNAMIC_CONFIG_ENABLED=true`                          | 클러스터 정보를 UI에서 동적으로 추가 가능 |
| `AUDIT_TOPICAUDITENABLED`, `AUDIT_CONSOLEAUDITENABLED` | 토픽 생성/메시지 전송 등 이벤트 로깅 기능 |

- Kafka UI는 포트 `8080`으로 접속

---

### 3.5 Docker Compose 전체 실행

```bash
docker-compose up --build
```

- 모든 서비스가 `data_network`로 묶이고,
- `Broker00`, `Broker01`, `Broker02`가 올라간 뒤,
- `KafkaWebUI`가 마지막으로 실행됨 (depends_on).
- **Kafka UI 접속 확인**
  - `localhost:8080` 접속.
  - 브로커 정상 연결 여부 확인.
  - "Add Topic" 버튼을 통해 토픽 생성 및 메시지 테스트 가능.

```bash
docker-compose down -v
```

- docker 컨테이너 정지 + 삭제 + 로컬에 연결된 볼륨까지 삭제.

## 4 Python Kafka Producer 구현

### 4.1 토픽 생성

- Kafka UI 접속 → `http://localhost:8080`.
- Add a Topic → 이름: test-crawling-topic.

---

### 4.2 Python Kafka Producer 구현

- `kafka-python` 라이브러리 사용 가능.

```bash
pip install kafka-python
```

- data가 이후에는 크롤링한 데이터로 대체되어야 함.
- 크롤링 데이터 뿐만 아니라, `실시간 주가 정보 수집`, `검색 키워드 트렌드 수집`도 WebSocket을 통해 가져와서 Kafka Producer를 통해 전송해줘야 함.

---

### 4.3 전송 확인

- Kafka UI에서 확인 : http://localhost:8080 → `테스트용 토픽` 클릭.
- 상단 탭 → `Messages`.
- 메시지가 보이면 성공.
