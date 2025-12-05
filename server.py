from fastmcp import FastMCP

import json
import pyodbc
import os
import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),  # 파일에 기록
        logging.StreamHandler()  # 콘솔에도 출력
    ]
)

logger = logging.getLogger(__name__)

# MSSQL 연결 설정
MSSQL_CONFIG = {
    'driver': os.getenv('MSSQL_DRIVER', '{ODBC Driver 18 for SQL Server}'),
    'server': os.getenv('MSSQL_SERVER', 'localhost'),
    'database': os.getenv('MSSQL_DATABASE', 'master'),
    'uid': os.getenv('MSSQL_UID', 'sa'),
    'pwd': os.getenv('MSSQL_PWD', ''),
}

def get_mssql_connection():
    """MSSQL 연결 생성"""
    connection_string = (
        f"DRIVER={MSSQL_CONFIG['driver']};"
        f"SERVER={MSSQL_CONFIG['server']};"
        f"DATABASE={MSSQL_CONFIG['database']};"
        f"UID={MSSQL_CONFIG['uid']};"
        f"PWD={MSSQL_CONFIG['pwd']};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)

def execute_read_query(query: str, params: list = None) -> list:
    """읽기 전용 쿼리 실행 (SELECT만 허용)"""
    # 쿼리 검증: SELECT 쿼리만 허용
    if not query.strip().upper().startswith('SELECT'):
        raise ValueError("오직 SELECT 쿼리만 실행 가능합니다.")

    try:
        conn = get_mssql_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # 결과를 딕셔너리 리스트로 변환
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        results = []

        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                # datetime 객체를 ISO 8601 문자열로 변환
                if isinstance(val, datetime.datetime):
                    row_dict[col] = val.isoformat()
                else:
                    row_dict[col] = val
            results.append(row_dict)

        cursor.close()
        conn.close()

        return results
    except Exception as e:
        raise Exception(f"데이터베이스 쿼리 실행 오류: {str(e)}")

mcp = FastMCP("MCP Energy Server")

@mcp.tool
def get_current_time():
    """현재 날짜와 시간을 반환합니다."""
    try:
        logger.info("get_current_time Tool called")
        result = datetime.datetime.now()
        logger.info(f"get_current_time result: {result}")
        return result
    except Exception as e:
        logger.error(f"get_current_time error: {str(e)}", exc_info=True)
        raise

@mcp.tool
def get_energy_usages_by_date_range(start_date_time: str, end_date_time: str, building: str) -> str:
    """날짜 범위와 건물 이름을 사용하여 에너지 사용량 목록을 조회합니다.

    Parameters:
    - start_date_time: ISO-8601 형식의 시작 시간 (예: 2024-01-01T00:00:00)
    - end_date_time: ISO-8601 형식의 종료 시간 (예: 2024-01-31T23:59:59)
    - building: 건물 이름 (건물 이름에는 공백이 존재하지 않습니다.)
    """
    try:
        logger.info(f"get_energy_usages_by_date_range Tool called - start: {start_date_time}, end: {end_date_time}, building: {building}")

        query = """
        SELECT
            Building,
            DataValue,
            TimeStamp,
            DateTime
        FROM dbo.Tech_All_KWH
        WHERE Building = ? AND DateTime >= ? AND DateTime <= ?
        ORDER BY DateTime DESC
        """

        results = execute_read_query(query, [building, start_date_time, end_date_time])
        logger.info(f"get_energy_usages_by_date_range - results count: {len(results)}")

        response = {
            "meta": {
                "building": building
            },
            "energyUsageInfos": results
        }
        return json.dumps(response, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"get_energy_usages_by_date_range error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"쿼리 실행 실패: {str(e)}"}, ensure_ascii=False)

@mcp.tool
def get_energy_usage(measurement_date_time: str, building: str) -> str:
    """측정 시간과 건물 이름을 사용하여 단일 에너지 사용량을 조회합니다.

    Parameters:
    - measurement_date_time: ISO-8601 형식의 측정 시간 (예: 2024-01-01T12:00:00)
    - building: 건물 이름 (건물 이름에는 공백이 존재하지 않습니다.)
    """
    try:
        logger.info(f"get_energy_usage Tool called - datetime: {measurement_date_time}, building: {building}")

        query = """
        SELECT TOP 1
            Building,
            DataValue,
            TimeStamp,
            DateTime
        FROM dbo.Tech_All_KWH
        WHERE DateTime = ? AND Building = ?
        """

        results = execute_read_query(query, [measurement_date_time, building])
        logger.info(f"get_energy_usage - results found: {len(results) > 0}")

        if results:
            logger.info(f"get_energy_usage - returning data for {building}")
            return json.dumps(results[0], ensure_ascii=False, indent=2)
        else:
            logger.warning(f"get_energy_usage - no data found for {building} at {measurement_date_time}")
            return json.dumps({"error": "데이터를 찾을 수 없습니다."}, ensure_ascii=False)
    except Exception as e:
        logger.error(f"get_energy_usage error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"쿼리 실행 실패: {str(e)}"}, ensure_ascii=False)


if __name__ == "__main__": # 파일이 직접 실행될 때만 실행됩니다. 다른 모듈에서 임포트될 때는 실행되지 않습니다.
    mcp.run(
        transport="streamable-http", # FastMCP 서버를 HTTP 프로토콜을 통해 실행합니다. 이 설정은 클라이언트가 HTTP를 통해 서버와 통신할 수 있도록 합니다.
        host="0.0.0.0",
        port=8000,
        path="/mcp", # 클라이언트 요청을 수신할 HTTP 경로를 지정합니다. /는 루트 경로를 의미합니다.
        log_level="debug",
    ) # MCP 서버를 시작합니다.

