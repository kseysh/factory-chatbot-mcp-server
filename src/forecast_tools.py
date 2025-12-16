from .config import get_logger
from .services import service_forecast_energy_usage

logger = get_logger(__name__)

def register_forecast_tools(mcp_server):
    """시계열 예측 관련 도구들을 MCP서버에 등록"""

    @mcp_server.tool(
        name="forecast_energy_usage",
        description="과거 누적 유효전력량(KWH) 데이터를 활용해 미래 전력량을 예측합니다."
    )
    async def forecast_energy_usage(start_date_time: str, end_date_time: str, building: str, horizon: int = 144) -> str:
        """
        과거 누적 유효전력량(KWH) 데이터를 활용해 미래 전력량을 예측합니다.

        Args:
        - start_date_time: 과거 데이터 시작 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
        - end_date_time: 과거 데이터 종료 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
        - building: 건물 이름
        - horizon: 예측할 타임스텝 수 (단위: 10분)

        Returns:
        - JSON 형식의 예측 결과:
        {
            "meta": {
                "building": "<건물명>",
                "horizon": <예측 타임스텝 수>,
                "data_points": <예측에 사용된 과거 관측치의 수>
            },
            "forecast": {
                "point_forecast": [
                    <예측값 1>,
                    <예측값 2>,
                    ...
                ]
            }
        }
        """
        try:
            logger.info(f"Forecast called: {building}, {start_date_time} ~ {end_date_time}, horizon={horizon}")
            result = await service_forecast_energy_usage(start_date_time, end_date_time, building, horizon)
            logger.info(f"forecast_energy_usage result: {result}")
            return result
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}", exc_info=True)
            return str(e)