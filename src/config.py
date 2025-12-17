import os
import logging
import sys
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# 로깅 설정 함수
def setup_logging():
    """표준 출력으로만 로그 출력"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 포맷 정의
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 표준 출력 핸들러
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def get_logger(name: str):
    """로거 인스턴스 반환"""
    return logging.getLogger(name)

def get_env(key: str, default: str = None) -> str:
    """환경 변수 값 반환"""
    return os.getenv(key, default)

# 모듈 임포트 시 로깅 자동 초기화
setup_logging()

# PostgreSQL 설정
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DATABASE', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
}