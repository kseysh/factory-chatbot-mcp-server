from .config import get_logger
from .services import (
    service_get_monitored_buildings,
    service_get_building_data_range,
    service_get_energy_usages_range,
    service_get_total_energy_usage,
)

logger = get_logger(__name__)

def register_electricity_tools(mcp_server):
    """인하대학교 전력 데이터 정보 조회 및 집계와 관련된 도구들을 MCP 서버에 등록"""

    @mcp_server.tool(
        name="get_monitored_buildings",
        description="현재 데이터 수집 및 모니터링 중인 건물 목록을 반환합니다."
    )
    async def get_monitored_buildings() -> str:
        """10분마다 누적 유효전력량(KWH)이 수집되는 건물들의 목록을 반환"""
        try:
            logger.info("get_monitored_buildings Tool called")
            result = await service_get_monitored_buildings()
            logger.info(f"get_monitored_buildings result: {result}")
            return result
        except Exception as e:
            logger.error(f"get_monitored_buildings error: {str(e)}", exc_info=True)
            raise

    @mcp_server.tool(
        name="get_building_data_range",
        description="건물의 전력 사용량 데이터 수집 기간(시작 시점 및 종료 시점)을 조회합니다."
    )
    async def get_building_data_range(building: str) -> str:
        """
        지정된 건물의 전력 사용량 데이터가 수집된 전체 기간(시작 일시부터 종료 일시)을 조회합니다.

        Args:
            building: get_monitored_buildings 도구를 통해 확인된 정확한 건물명
        """
        try:
            logger.info(f"get_building_data_range called: {building}")
            result = await service_get_building_data_range(building)
            logger.info(f"get_building_data_range result: {result}")
            return result
        except Exception as e:
            logger.error(f"get_building_data_range error: {str(e)}", exc_info=True)
            return str(e)

    @mcp_server.tool(
        name="get_energy_usages",
        description="건물의 전력 사용량(KWH) 시계열 데이터를 조회합니다. 시작(start_date_time)과 종료(end_date_time)는 필수이며, 두 시간이 같으면 단일 시점 데이터를, 다르면 해당 구간의 10분 단위 데이터를 반환합니다."
    )
    async def get_energy_usages(start_date_time: str, end_date_time: str, building: str) -> str:
        """
        지정된 건물에서 10분 간격으로 기록되는 누적 유효전력량(KWH) 시계열 데이터를 조회합니다.

        Args:
        - start_date_time: 시작 시간 (Format: 'YYYY-MM-DD HH:MM:SS')
        - end_date_time: 종료 시간 (Format: 'YYYY-MM-DD HH:MM:SS')
        - building: get_monitored_buildings 도구를 통해 확인된 정확한 건물명
        """
        try:
            logger.info(f"Range query called: {building}, {start_date_time} ~ {end_date_time}")
            result = await service_get_energy_usages_range(start_date_time, end_date_time, building)
            logger.info(f"get_energy_usages_by_date_range result: {result}")
            return result
        except Exception as e:
            logger.error(f"Range query error: {str(e)}", exc_info=True)
            return str(e)

    @mcp_server.tool(
        name="get_total_energy_usage",
        description="특정 건물의 지정된 기간(YYYY-MM-DD HH:MM:SS) 동안의 총 전력 사용량(kWh)을 계산하여 반환합니다."
    )
    async def get_total_energy_usage(start_date_time: str, end_date_time: str, building: str) -> str:
        """
        건물의 누적 전력량 데이터를 기반으로 특정 기간(Start ~ End) 동안의 총 사용량을 계산하여 반환합니다.

        Args:
            start_date_time: 조회 시작 일시 (Format: 'YYYY-MM-DD HH:MM:SS')
            end_date_time: 조회 종료 일시 (Format: 'YYYY-MM-DD HH:MM:SS')
            building: get_monitored_buildings 도구를 통해 확인된 정확한 건물명
        """
        try:
            logger.info(f"get_total_energy_usage called: {building}, {start_date_time} ~ {end_date_time}")
            result = await service_get_total_energy_usage(start_date_time, end_date_time, building)
            logger.info(f"get_total_energy_usage result: {result}")
            return result
        except Exception as e:
            logger.error(f"get_total_energy_usage error: {str(e)}", exc_info=True)
            return str(e)

    