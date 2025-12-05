import datetime
import json
from .database import execute_read_query
from .config import get_logger

logger = get_logger(__name__)

def service_get_current_time():
    """현재 시간 로직"""
    return datetime.datetime.now()

def service_get_energy_usages_range(start_date_time: str, end_date_time: str, building: str) -> str:
    """기간별 에너지 사용량 조회 로직"""
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
    
    response = {
        "meta": {"building": building},
        "energyUsageInfos": results
    }
    return json.dumps(response, ensure_ascii=False, indent=2)

def service_get_energy_usage_single(measurement_date_time: str, building: str) -> str:
    """단건 에너지 사용량 조회 로직"""
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
    
    if results:
        return json.dumps(results[0], ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": "데이터를 찾을 수 없습니다."}, ensure_ascii=False)