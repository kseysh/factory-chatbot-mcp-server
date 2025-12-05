import os
import logging
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# 로깅 설정 함수
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def get_logger(name: str):
    return logging.getLogger(name)

# MSSQL 설정
MSSQL_CONFIG = {
    'driver': os.getenv('MSSQL_DRIVER', '{ODBC Driver 18 for SQL Server}'),
    'server': os.getenv('MSSQL_SERVER', 'localhost'),
    'database': os.getenv('MSSQL_DATABASE', 'master'),
    'uid': os.getenv('MSSQL_UID', 'sa'),
    'pwd': os.getenv('MSSQL_PWD', ''),
}