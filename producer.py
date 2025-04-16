from kafka import KafkaProducer
import json

producer = KafkaProducer(
    # Kafka 클러스터의 브로커 목록 (분산 환경에서 하나 이상 지정하는 것이 안정적)
    bootstrap_servers=["localhost:10000","localhost:10001","localhost:10002"],
    # Kafka에 전송할 데이터(value)를 직렬화하는 방법
    # JSON 형식으로 직렬화하고 UTF-8로 인코딩하여 바이너리로 변환
    # - json.dumps: Python dict → JSON 문자열
    # - ensure_ascii=False: 한글 등 유니코드 문자가 그대로 저장되도록 함
    # - encode("utf-8"): Kafka는 바이트(binary) 형식만 전송 가능하므로 인코딩 필요
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
)
