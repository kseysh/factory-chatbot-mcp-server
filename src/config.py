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
    logger.setLevel(logging.DEBUG)

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
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def get_logger(name: str):
    """로거 인스턴스 반환"""
    return logging.getLogger(name)

# 모듈 임포트 시 로깅 자동 초기화
setup_logging()

# MSSQL 설정
MSSQL_CONFIG = {
    'driver': os.getenv('MSSQL_DRIVER', '{ODBC Driver 18 for SQL Server}'),
    'server': os.getenv('MSSQL_SERVER', 'localhost'),
    'database': os.getenv('MSSQL_DATABASE', 'master'),
    'uid': os.getenv('MSSQL_UID', 'sa'),
    'pwd': os.getenv('MSSQL_PWD', ''),
}