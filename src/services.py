import datetime
import json
import numpy as np
import asyncio
from .database import execute_read_query
from .config import get_logger
from .forecast_model import forecasting, model
from aiocache import cached


logger = get_logger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """datetime 객체를 JSON 직렬화 가능하게 변환하는 커스텀 인코더"""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

def service_get_current_time() -> str:
    """현재 로컬 시간 반환"""
    return datetime.datetime.now()

@cached(ttl=3600)
async def service_get_monitored_buildings() -> str:
    """10분마다 누적 유효전력량(KWH)이 수집되는 건물들의 목록을 반환"""
    query = """
    SELECT DISTINCT building
    FROM electricity
    ORDER BY building;
    """
    results = await execute_read_query(query)

    if results:
        return json.dumps(results, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": "데이터를 찾을 수 없습니다."}, ensure_ascii=False)

async def service_get_building_data_range(building: str) -> str:
    """electricity 테이블에서 지정된 건물의 datetime 최소(시작)/최대(종료) 값을 조회"""

    query = """
    SELECT
        MIN(datetime) as start_datetime,
        MAX(datetime) as end_datetime
    FROM electricity
    WHERE building = :building AND datavalue != 0
    """

    results = await execute_read_query(query, {"building": building})

    if results and results[0].get('start_datetime'):
        data = results[0]
        data['building'] = building
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    else:
        return json.dumps({"error": f"'{building}'에 대한 데이터를 찾을 수 없습니다."}, ensure_ascii=False)

async def service_get_energy_usages_range(start_date_time: datetime.datetime, end_date_time: datetime.datetime, building: str) -> str:
    """
    기간별 에너지 사용량 반환

    Args:
    - start_date_time: 시작 시간 (datetime 객체)
    - end_date_time: 종료 시간 (datetime 객체)
    - building: 건물명

    Returns:
    - JSON 형식의 조회 결과
    """
    query = """
    SELECT
        building,
        powerusage,
        datetime
    FROM electricity
    WHERE building = :building AND datetime >= :start_date_time AND datetime <= :end_date_time
    ORDER BY datetime DESC
    """
    results = await execute_read_query(query, {
        "building": building,
        "start_date_time": start_date_time,
        "end_date_time": end_date_time
    })

    if results:
        response = {
            "meta": {
                "building": building
            },
            "energyUsageInfos": results
        }
        return json.dumps(response, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
    else:
        return json.dumps({"error": "해당 기간의 에너지 사용량 데이터를 조회할 수 없습니다."}, ensure_ascii=False)


async def service_get_total_energy_usage(start_date_time: datetime.datetime, end_date_time: datetime.datetime, building: str) -> str:
    """
    특정 기간(start_date_time ~ end_date_time) 동안의 총 전력 사용량(kWh)을
    누적값(datavalue)의 차이로 계산하여 반환합니다.

    Args:
    - start_date_time: 시작 시간 (datetime 객체)
    - end_date_time:   종료 시간 (datetime 객체)
    - building:        건물명

    Returns:
    - JSON 형식의 조회 결과
    """

    query = """
    SELECT
        MIN(datavalue) as start_accumulated_val,
        MAX(datavalue) as end_accumulated_val
    FROM electricity
    WHERE building = :building
      AND datetime >= :start_date_time
      AND datetime <= :end_date_time
    """

    results = await execute_read_query(query, {
        "building": building,
        "start_date_time": start_date_time,
        "end_date_time": end_date_time
    })

    if results and results[0].get('start_accumulated_val') is not None:
        row = results[0]

        val_at_start = row['start_accumulated_val']
        val_at_end = row['end_accumulated_val']

        calculated_usage = abs(val_at_end - val_at_start)

        response = {
            "meta": {
                "building": building
            },
            "total_usage_kwh": calculated_usage
        }
        return json.dumps(response, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": "해당 기간에 데이터를 찾을 수 없습니다."}, ensure_ascii=False)

@cached(ttl=3600)
async def service_forecast_energy_usage(start_date_time: datetime.datetime, end_date_time: datetime.datetime, building: str, horizon: int = 24) -> str:
    """
    TimesFM 모델을 사용하여 전력량 예측

    Args:
    - start_date_time: 과거 데이터 시작 시간 (datetime 객체)
    - end_date_time: 과거 데이터 종료 시간 (datetime 객체)
    - building: 건물명
    - horizon: 예측할 타임스텝 수 (단위: 10분)

    Returns:
    - JSON 형식의 예측 결과
    """
    try:
        logger.info(f"forecast_energy_usage 시작 - building: {building}, horizon: {horizon}")

        # 1. DB에서 과거 데이터 조회
        query = """
        SELECT
            powerusage
        FROM electricity
        WHERE building = :building AND datetime >= :start_date_time AND datetime <= :end_date_time
        ORDER BY datetime ASC
        """

        results = await execute_read_query(query, {
            "building": building,
            "start_date_time": start_date_time,
            "end_date_time": end_date_time
        })

        if not results or len(results) == 0:
            logger.warning(f"forecast_energy_usage - {building}에 대한 데이터 없음")
            return json.dumps({"error": "해당 건물의 데이터가 없습니다."}, ensure_ascii=False)

        # 2. datavalue 추출
        energy_values = [float(r['powerusage']) for r in results]
        logger.info(f"forecast_energy_usage - 수집된 데이터 개수: {len(energy_values)}")

        # 3. numpy 배열로 변환
        input_data = np.array(energy_values)

        # 4. TimesFM 모델로 예측 (CPU-intensive 작업을 thread로 실행)
        point_forecast, quantile_forecast = await asyncio.to_thread(
            forecasting, model, horizon, input_data
        )

        logger.info(f"forecast_energy_usage - 예측 완료: {horizon}시간")

        # 5. 결과 포맷팅
        forecast_values = point_forecast[0].tolist()  # (1, horizon) -> list

        # 분위수 예측 (mean, q10, q20, ..., q90)
        # quantile_values = quantile_forecast[0].tolist()  # (1, horizon, 10) -> list

        response = {
            "meta": {
                "building": building,
                "horizon": horizon,
                "data_points": len(energy_values)
            },
            "forecast": {
                "point_forecast": forecast_values,  # 예측값
            }
        }

        logger.info(f"forecast_energy_usage - 응답 생성 완료")
        return json.dumps(response, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"forecast_energy_usage error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"전력량 예측 실패: {str(e)}"}, ensure_ascii=False)