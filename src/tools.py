from fastmcp import FastMCP
from .config import get_logger
from .services import (
    service_get_current_time,
    service_get_energy_usages_range,
    service_get_energy_usage_single,
    service_forecast_energy_usage
)

logger = get_logger(__name__)

# MCP 서버 인스턴스 생성
mcp = FastMCP("MCP Energy Server")

@mcp.tool
def get_current_time():
    """현재 날짜와 시간을 반환합니다."""
    try:
        logger.info("get_current_time Tool called")
        result = service_get_current_time()
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
    - building: 건물 이름
    """
    try:
        logger.info(f"Range query called: {building}, {start_date_time} ~ {end_date_time}")
        result = service_get_energy_usages_range(start_date_time, end_date_time, building)
        logger.info(f"get_energy_usages_by_date_range result: {result}")
        return result
    except Exception as e:
        logger.error(f"Range query error: {str(e)}", exc_info=True)
        return str(e)

@mcp.tool
def get_energy_usage(measurement_date_time: str, building: str) -> str:
    """측정 시간과 건물 이름을 사용하여 단일 에너지 사용량을 조회합니다."""
    try:
        logger.info(f"Single query called: {building} at {measurement_date_time}")
        result = service_get_energy_usage_single(measurement_date_time, building)
        return result
    except Exception as e:
        logger.error(f"Single query error: {str(e)}", exc_info=True)
        return str(e)

@mcp.tool
def forecast_energy_usage(start_date_time: str, end_date_time: str, building: str, horizon: int = 24) -> str:
    """과거 에너지 사용량 데이터를 사용하여 미래 전력량을 예측합니다.

    Parameters:
    - start_date_time: 과거 데이터 시작 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
    - end_date_time: 과거 데이터 종료 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
    - building: 건물 이름
    - horizon: 예측할 시간 개수 (기본값: 24시간)

    Returns:
    - JSON 형식의 예측 결과 (point_forecast와 quantile_forecast 포함)
    """
    try:
        logger.info(f"Forecast called: {building}, {start_date_time} ~ {end_date_time}, horizon={horizon}")
        result = service_forecast_energy_usage(start_date_time, end_date_time, building, horizon)
        logger.info(f"forecast_energy_usage result: {result}")
        return result
    except Exception as e:
        logger.error(f"Forecast error: {str(e)}", exc_info=True)
        return str(e)