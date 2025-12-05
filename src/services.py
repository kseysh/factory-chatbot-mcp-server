import datetime
import json
import numpy as np
from .database import execute_read_query
from .config import get_logger
from .forecast_model import forecasting, model

logger = get_logger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """datetime 객체를 JSON 직렬화 가능하게 변환하는 커스텀 인코더"""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

def service_get_current_time():
    """현재 시간 로직"""
    return datetime.datetime.now()

def service_get_energy_usages_range(start_date_time: str, end_date_time: str, building: str) -> str:
    """
    기간별 에너지 사용량 조회 로직

    Parameters:
    - start_date_time: 시작 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
    - end_date_time: 종료 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
    - building: 건물명

    Returns:
    - JSON 형식의 조회 결과
    """
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
    return json.dumps(response, ensure_ascii=False, indent=2, cls=DateTimeEncoder)

def service_get_energy_usage_single(measurement_date_time: str, building: str) -> str:
    """
    단건 에너지 사용량 조회 로직

    Parameters:
    - measurement_date_time: 측정 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
    - building: 건물명

    Returns:
    - JSON 형식의 조회 결과
    """
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
        return json.dumps(results[0], ensure_ascii=False, indent=2, cls=DateTimeEncoder)
    else:
        return json.dumps({"error": "데이터를 찾을 수 없습니다."}, ensure_ascii=False)

def service_forecast_energy_usage(start_date_time: str, end_date_time: str, building: str, horizon: int = 24) -> str:
    """
    TimesFM 모델을 사용하여 전력량 예측

    Parameters:
    - start_date_time: 과거 데이터 시작 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
    - end_date_time: 과거 데이터 종료 시간 (SQL Server 형식: YYYY-MM-DD HH:MM:SS)
    - building: 건물명
    - horizon: 예측할 시간 단위 (기본값: 24시간)

    Returns:
    - JSON 형식의 예측 결과
    """
    try:
        logger.info(f"forecast_energy_usage 시작 - building: {building}, horizon: {horizon}")

        # 1. DB에서 과거 데이터 조회
        query = """
        SELECT
            DataValue
        FROM dbo.Tech_All_KWH
        WHERE Building = ? AND DateTime >= ? AND DateTime <= ?
        ORDER BY DateTime ASC
        """

        results = execute_read_query(query, [building, start_date_time, end_date_time])

        if not results or len(results) == 0:
            logger.warning(f"forecast_energy_usage - {building}에 대한 데이터 없음")
            return json.dumps({"error": "해당 건물의 데이터가 없습니다."}, ensure_ascii=False)

        # 2. DataValue 추출
        energy_values = [float(r['DataValue']) for r in results]
        logger.info(f"forecast_energy_usage - 수집된 데이터 개수: {len(energy_values)}")

        # 3. numpy 배열로 변환
        input_data = np.array(energy_values)

        # 4. TimesFM 모델로 예측
        point_forecast, quantile_forecast = forecasting(model, horizon, input_data)

        logger.info(f"forecast_energy_usage - 예측 완료: {horizon}시간")

        # 5. 결과 포맷팅
        forecast_values = point_forecast[0].tolist()  # (1, horizon) -> list

        # 분위수 예측 (mean, q10, q20, ..., q90)
        quantile_values = quantile_forecast[0].tolist()  # (1, horizon, 10) -> list

        response = {
            "meta": {
                "building": building,
                "horizon": horizon,
                "data_points": len(energy_values)
            },
            "forecast": {
                "point_forecast": forecast_values,  # 평균 예측값
                "quantile_forecast": quantile_values  # 분위수 예측값 (mean + 9개 분위수)
            }
        }

        logger.info(f"forecast_energy_usage - 응답 생성 완료")
        return json.dumps(response, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"forecast_energy_usage error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"전력량 예측 실패: {str(e)}"}, ensure_ascii=False)