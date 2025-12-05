"""
service_forecast_energy_usage 테스트 코드
"""

import json
import sys
from datetime import datetime, timedelta
from src.services import service_forecast_energy_usage
from src.config import get_logger

logger = get_logger(__name__)


def test_forecast_energy_usage_basic():
    """기본 예측 테스트"""
    print("=" * 60)
    print("TEST 1: 기본 전력량 예측 (기본 horizon=24)")
    print("=" * 60)

    try:
        # SQL Server 형식 (YYYY-MM-DD HH:MM:SS)
        start_date_str = "2024-09-01 00:00:00"
        end_date_str = "2024-09-01 23:59:59"
        building = "60주년기념관"

        print(f"입력 파라미터:")
        print(f"  - start_date_time: {start_date_str}")
        print(f"  - end_date_time: {end_date_str}")
        print(f"  - building: {building}")
        print(f"  - horizon: 24 (기본값)")

        result = service_forecast_energy_usage(
            start_date_time=start_date_str,
            end_date_time=end_date_str,
            building=building
        )

        print(f"\n✓ 결과 (JSON):")
        result_dict = json.loads(result)
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))

        # 검증
        assert "meta" in result_dict, "meta 필드 없음"
        assert "forecast" in result_dict, "forecast 필드 없음"
        assert "point_forecast" in result_dict["forecast"], "point_forecast 필드 없음"
        assert len(result_dict["forecast"]["point_forecast"]) == 24, "예측값 개수가 24개가 아님"

        print(f"\n✓ 테스트 통과!")
        return True

    except Exception as e:
        print(f"✗ 오류: {str(e)}")
        logger.error(f"test_forecast_energy_usage_basic error: {e}", exc_info=True)
        return False


def test_forecast_energy_usage_custom_horizon():
    """커스텀 horizon 테스트"""
    print("\n" + "=" * 60)
    print("TEST 2: 커스텀 horizon 예측 (horizon=48)")
    print("=" * 60)

    try:
        start_date_str = "2024-09-01 00:00:00"
        end_date_str = "2024-09-01 23:59:59"
        building = "60주년기념관"

        print(f"입력 파라미터:")
        print(f"  - start_date_time: {start_date_str}")
        print(f"  - end_date_time: {end_date_str}")
        print(f"  - building: {building}")
        print(f"  - horizon: 48")

        result = service_forecast_energy_usage(
            start_date_time=start_date_str,
            end_date_time=end_date_str,
            building=building,
            horizon=48
        )

        print(f"\n✓ 결과 (JSON):")
        result_dict = json.loads(result)
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))

        # 검증
        assert len(result_dict["forecast"]["point_forecast"]) == 48, "예측값 개수가 48개가 아님"
        assert result_dict["meta"]["horizon"] == 48, "horizon 값이 48이 아님"

        print(f"\n✓ 테스트 통과!")
        return True

    except Exception as e:
        print(f"✗ 오류: {str(e)}")
        logger.error(f"test_forecast_energy_usage_custom_horizon error: {e}", exc_info=True)
        return False


def test_forecast_energy_usage_no_data():
    """데이터 없는 경우 테스트"""
    print("\n" + "=" * 60)
    print("TEST 3: 데이터 없는 건물 예측")
    print("=" * 60)

    try:
        start_date_str = "2024-09-01 00:00:00"
        end_date_str = "2024-09-01 23:59:59"

        print(f"입력 파라미터:")
        print(f"  - start_date_time: {start_date_str}")
        print(f"  - end_date_time: {end_date_str}")
        print(f"  - building: 존재하지않는건물")
        print(f"  - horizon: 24")

        result = service_forecast_energy_usage(
            start_date_time=start_date_str,
            end_date_time=end_date_str,
            building="존재하지않는건물"
        )

        print(f"\n결과 (JSON):")
        result_dict = json.loads(result)
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))

        # 검증
        if "error" in result_dict:
            print(f"\n✓ 예상된 오류 반환됨")
            print(f"✓ 테스트 통과!")
            return True
        else:
            print(f"\n✗ 오류: 데이터 없음 에러가 반환되지 않음")
            return False

    except Exception as e:
        print(f"✗ 오류: {str(e)}")
        logger.error(f"test_forecast_energy_usage_no_data error: {e}", exc_info=True)
        return False

def test_forecast_response_structure():
    """응답 구조 상세 검증"""
    print("\n" + "=" * 60)
    print("TEST 4: 응답 구조 상세 검증")
    print("=" * 60)

    try:
        start_date_str = "2024-09-01 00:00:00"
        end_date_str = "2024-09-01 23:59:59"
        building = "60주년기념관"
        result = service_forecast_energy_usage(
            start_date_time=start_date_str,
            end_date_time=end_date_str,
            building=building,
            horizon=24
        )

        result_dict = json.loads(result)

        print("응답 구조 검증:")

        # meta 필드 검증
        assert "meta" in result_dict, "meta 필드 없음"
        meta = result_dict["meta"]
        assert "building" in meta, "meta.building 필드 없음"
        assert "horizon" in meta, "meta.horizon 필드 없음"
        assert "data_points" in meta, "meta.data_points 필드 없음"
        print(f"✓ meta 필드 정상")
        print(f"  - building: {meta['building']}")
        print(f"  - horizon: {meta['horizon']}")
        print(f"  - data_points: {meta['data_points']}")

        # forecast 필드 검증
        assert "forecast" in result_dict, "forecast 필드 없음"
        forecast = result_dict["forecast"]
        assert "point_forecast" in forecast, "forecast.point_forecast 필드 없음"
        assert "quantile_forecast" in forecast, "forecast.quantile_forecast 필드 없음"
        print(f"✓ forecast 필드 정상")

        # point_forecast 검증
        point_forecast = forecast["point_forecast"]
        assert isinstance(point_forecast, list), "point_forecast는 리스트여야 함"
        assert len(point_forecast) == 24, "point_forecast 길이가 24가 아님"
        assert all(isinstance(x, (int, float)) for x in point_forecast), "point_forecast 원소가 숫자가 아님"
        print(f"✓ point_forecast 정상: {len(point_forecast)}개 예측값")

        # quantile_forecast 검증
        quantile_forecast = forecast["quantile_forecast"]
        assert isinstance(quantile_forecast, list), "quantile_forecast는 리스트여야 함"
        assert len(quantile_forecast) == 24, "quantile_forecast 길이가 24가 아님"
        print(f"✓ quantile_forecast 정상: {len(quantile_forecast)}개 시점")
        print(f"  각 시점마다 분위수 개수: {len(quantile_forecast[0]) if quantile_forecast else 0}개")

        print(f"\n✓ 테스트 통과!")
        return True

    except Exception as e:
        print(f"✗ 오류: {str(e)}")
        logger.error(f"test_forecast_response_structure error: {e}", exc_info=True)
        return False


def main():
    """테스트 실행"""
    print("\n" + "=" * 60)
    print("service_forecast_energy_usage 테스트")
    print("=" * 60 + "\n")

    results = []

    # TEST 1
    results.append(("기본 예측 (horizon=24)", test_forecast_energy_usage_basic()))

    # TEST 2
    results.append(("커스텀 horizon (horizon=48)", test_forecast_energy_usage_custom_horizon()))

    # TEST 3
    results.append(("데이터 없는 건물", test_forecast_energy_usage_no_data()))

    # TEST 4
    results.append(("응답 구조 검증", test_forecast_response_structure()))

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 요약")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\n총 {passed}/{total} 테스트 통과")

    if passed == total:
        print("🎉 모든 테스트 성공!\n")
        sys.exit(0)
    else:
        print(f"⚠️  {total - passed}개 테스트 실패\n")
        sys.exit(1)


if __name__ == "__main__":
    main()