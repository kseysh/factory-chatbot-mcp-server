from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from .config import POSTGRES_CONFIG, get_logger

logger = get_logger(__name__)

# PostgreSQL 연결 문자열 생성 (비동기 드라이버 사용)
db_url = (
    f"postgresql+asyncpg://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
    f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
)

# 비동기 엔진 생성 (싱글톤처럼 모듈 레벨에서 유지)
engine = create_async_engine(
    db_url,
    pool_size=30,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False
)

async def execute_read_query(query: str, params: dict = None) -> list:
    """
    SELECT 쿼리를 비동기로 실행하고 결과를 딕셔너리 리스트로 반환

    Parameters:
    - query: SELECT 쿼리 문자열 (named 파라미터 사용)
    - params: 쿼리 파라미터 딕셔너리. 날짜/시간은 PostgreSQL 형식 (YYYY-MM-DD HH:MM:SS) 사용

    Returns:
    - list: 쿼리 결과를 딕셔너리 리스트로 반환

    Raises:
    - ValueError: SELECT 쿼리가 아닌 경우
    - Exception: 데이터베이스 연결 또는 쿼리 실행 오류
    """
    if not query.strip().upper().startswith('SELECT'):
        raise ValueError("오직 SELECT 쿼리만 실행 가능합니다.")

    try:
        async with engine.connect() as conn:
            if params:
                result = await conn.execute(text(query), params)
            else:
                result = await conn.execute(text(query))

            columns = result.keys()
            rows = result.fetchall()
            results = []

            for row in rows:
                row_dict = {}
                for col, val in zip(columns, row):
                    row_dict[col] = val
                results.append(row_dict)
            return results

    except Exception as e:
        logger.error(f"DB Error: {str(e)}")
        raise Exception(f"데이터베이스 쿼리 실행 오류: {str(e)}")