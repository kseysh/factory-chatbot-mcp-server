from sqlalchemy import create_engine
from urllib.parse import quote_plus
import datetime
from .config import MSSQL_CONFIG, get_logger

logger = get_logger(__name__)

# 연결 문자열 생성
params = quote_plus(
    f"DRIVER={MSSQL_CONFIG['driver']};"
    f"SERVER={MSSQL_CONFIG['server']};"
    f"DATABASE={MSSQL_CONFIG['database']};"
    f"UID={MSSQL_CONFIG['uid']};"
    f"PWD={MSSQL_CONFIG['pwd']};"
    "TrustServerCertificate=yes;"
)
db_url = f"mssql+pyodbc:///?odbc_connect={params}"

# 엔진 생성 (싱글톤처럼 모듈 레벨에서 유지)
engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

def execute_read_query(query: str, params: list = None) -> list:
    """
    SELECT 쿼리를 실행하고 결과를 딕셔너리 리스트로 반환

    Parameters:
    - query: SELECT 쿼리 문자열 (? 파라미터 사용)
    - params: 쿼리 파라미터 리스트. 날짜/시간은 SQL Server 형식 (YYYY-MM-DD HH:MM:SS) 사용

    Returns:
    - list: 쿼리 결과를 딕셔너리 리스트로 반환 (SQL Server에서 제공한 형식 그대로)

    Raises:
    - ValueError: SELECT 쿼리가 아닌 경우
    - Exception: 데이터베이스 연결 또는 쿼리 실행 오류
    """
    if not query.strip().upper().startswith('SELECT'):
        raise ValueError("오직 SELECT 쿼리만 실행 가능합니다.")

    try:
        # raw_connection을 사용하여 ? 파라미터 문법 지원
        conn = engine.raw_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if cursor.description:
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                results = []

                for row in rows:
                    row_dict = {}
                    for col, val in zip(columns, row):
                        row_dict[col] = val
                    results.append(row_dict)
                return results
            return []
            
        finally:
            cursor.close()
            conn.close() # 풀로 반환
            
    except Exception as e:
        logger.error(f"DB Error: {str(e)}")
        raise Exception(f"데이터베이스 쿼리 실행 오류: {str(e)}")