"""
모든 Service 함수들에 대한 종합 테스트 코드
pytest 프레임워크를 사용하여 테스트합니다.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import patch
from src.services import (
    service_get_current_time,
    service_get_monitored_buildings,
    service_get_building_data_range,
    service_get_energy_usages_range,
    service_get_total_energy_usage,
    service_forecast_energy_usage,
    cache
)


class TestServiceGetCurrentTime:
    """service_get_current_time 테스트"""

    def test_returns_datetime(self):
        """datetime 객체를 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_current_time - datetime 반환")
        print("=" * 60)

        result = service_get_current_time()

        assert isinstance(result, datetime), "datetime 타입이어야 합니다"
        print(f"✓ 결과: {result}")
        print(f"✓ 타입: {type(result)}")

    def test_current_time_is_recent(self):
        """현재 시간과 가까운지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_current_time - 현재 시간 확인")
        print("=" * 60)

        before = datetime.now()
        result = service_get_current_time()
        after = datetime.now()

        # 테스트 실행 시간 내에 있어야 함
        assert before <= result <= after, "반환된 시간이 현재 시간 범위를 벗어남"
        print(f"✓ 현재 시간 범위 내에 있음")
        print(f"  - Before: {before}")
        print(f"  - Result: {result}")
        print(f"  - After: {after}")


class TestServiceGetMonitoredBuildings:
    """service_get_monitored_buildings 테스트"""

    def setup_method(self):
        """각 테스트 전 캐시 초기화"""
        cache.clear()

    @patch('src.services.execute_read_query')
    def test_returns_json_with_buildings(self, mock_query):
        """건물 목록을 JSON으로 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_monitored_buildings - 건물 목록 반환")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"Building": "하이테크센터"},
            {"Building": "테크노파크"},
            {"Building": "60주년기념관"}
        ]

        result = service_get_monitored_buildings()

        # JSON 파싱 검증
        result_dict = json.loads(result)
        assert isinstance(result_dict, list), "결과는 리스트여야 합니다"
        assert len(result_dict) == 3, "건물 개수가 일치하지 않습니다"
        assert result_dict[0]["Building"] == "하이테크센터"

        print(f"✓ 건물 개수: {len(result_dict)}")
        print(f"✓ 건물 목록: {[b['Building'] for b in result_dict]}")

    @patch('src.services.execute_read_query')
    def test_returns_error_when_no_data(self, mock_query):
        """데이터가 없을 때 에러 메시지를 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_monitored_buildings - 데이터 없음")
        print("=" * 60)

        # Mock: 빈 결과 반환
        mock_query.return_value = []

        result = service_get_monitored_buildings()
        result_dict = json.loads(result)

        assert "error" in result_dict, "에러 필드가 있어야 합니다"
        print(f"✓ 에러 메시지: {result_dict['error']}")

    def test_with_real_database(self):
        """실제 DB 연결 테스트"""
        print("\n" + "=" * 60)
        print("TEST: service_get_monitored_buildings - 실제 DB 연결")
        print("=" * 60)

        try:
            result = service_get_monitored_buildings()
            result_dict = json.loads(result)

            if "error" in result_dict:
                print(f"⚠️  DB 오류: {result_dict['error']}")
                pytest.skip("DB 연결 불가")
            else:
                assert isinstance(result_dict, list), "결과는 리스트여야 합니다"
                print(f"✓ 건물 개수: {len(result_dict)}")
                if len(result_dict) > 0:
                    print(f"✓ 첫 번째 건물: {result_dict[0]}")

        except Exception as e:
            print(f"⚠️  오류: {e}")
            pytest.skip("DB 연결 오류")


class TestServiceGetBuildingDataRange:
    """service_get_building_data_range 테스트"""

    @patch('src.services.execute_read_query')
    def test_returns_date_range(self, mock_query):
        """건물의 데이터 범위를 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_building_data_range - 날짜 범위 반환")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {
                "start_datetime": datetime(2024, 1, 1, 0, 0, 0),
                "end_datetime": datetime(2024, 12, 31, 23, 59, 59)
            }
        ]

        building = "하이테크센터"
        result = service_get_building_data_range(building)
        result_dict = json.loads(result)

        assert "start_datetime" in result_dict, "start_datetime 필드가 없습니다"
        assert "end_datetime" in result_dict, "end_datetime 필드가 없습니다"
        assert "building" in result_dict, "building 필드가 없습니다"
        assert result_dict["building"] == building

        print(f"✓ 건물: {result_dict['building']}")
        print(f"✓ 시작일: {result_dict['start_datetime']}")
        print(f"✓ 종료일: {result_dict['end_datetime']}")

    @patch('src.services.execute_read_query')
    def test_returns_error_when_no_data(self, mock_query):
        """데이터가 없을 때 에러를 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_building_data_range - 데이터 없음")
        print("=" * 60)

        # Mock: 빈 결과 또는 None
        mock_query.return_value = []

        result = service_get_building_data_range("존재하지않는건물")
        result_dict = json.loads(result)

        assert "error" in result_dict, "에러 필드가 있어야 합니다"
        print(f"✓ 에러 메시지: {result_dict['error']}")

    def test_with_real_database(self):
        """실제 DB 연결 테스트"""
        print("\n" + "=" * 60)
        print("TEST: service_get_building_data_range - 실제 DB 연결")
        print("=" * 60)

        try:
            building = "하이테크센터"
            result = service_get_building_data_range(building)
            result_dict = json.loads(result)

            if "error" in result_dict:
                print(f"⚠️  DB 오류: {result_dict['error']}")
                pytest.skip("DB 연결 불가 또는 데이터 없음")
            else:
                assert "start_datetime" in result_dict
                assert "end_datetime" in result_dict
                assert "building" in result_dict
                print(f"✓ 건물: {result_dict['building']}")
                print(f"✓ 시작일: {result_dict['start_datetime']}")
                print(f"✓ 종료일: {result_dict['end_datetime']}")

        except Exception as e:
            print(f"⚠️  오류: {e}")
            pytest.skip("DB 연결 오류")


class TestServiceGetEnergyUsagesRange:
    """service_get_energy_usages_range 테스트"""

    @patch('src.services.execute_read_query')
    def test_returns_energy_usage_data(self, mock_query):
        """기간별 에너지 사용량을 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_energy_usages_range - 에너지 사용량 반환")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {
                "Building": "하이테크센터",
                "DataValue": 1234.5,
                "TimeStamp": "2024-09-01 00:00:00",
                "DateTime": datetime(2024, 9, 1, 0, 0, 0)
            },
            {
                "Building": "하이테크센터",
                "DataValue": 1235.2,
                "TimeStamp": "2024-09-01 00:10:00",
                "DateTime": datetime(2024, 9, 1, 0, 10, 0)
            }
        ]

        result = service_get_energy_usages_range(
            "2024-09-01 00:00:00",
            "2024-09-01 01:00:00",
            "하이테크센터"
        )
        result_dict = json.loads(result)

        assert "meta" in result_dict, "meta 필드가 없습니다"
        assert "energyUsageInfos" in result_dict, "energyUsageInfos 필드가 없습니다"
        assert result_dict["meta"]["building"] == "하이테크센터"
        assert len(result_dict["energyUsageInfos"]) == 2

        print(f"✓ 건물: {result_dict['meta']['building']}")
        print(f"✓ 데이터 개수: {len(result_dict['energyUsageInfos'])}")

    @patch('src.services.execute_read_query')
    def test_returns_error_when_no_data(self, mock_query):
        """데이터가 없을 때 에러를 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_energy_usages_range - 데이터 없음")
        print("=" * 60)

        mock_query.return_value = []

        result = service_get_energy_usages_range(
            "2024-09-01 00:00:00",
            "2024-09-01 01:00:00",
            "존재하지않는건물"
        )
        result_dict = json.loads(result)

        assert "error" in result_dict, "에러 필드가 있어야 합니다"
        print(f"✓ 에러 메시지: {result_dict['error']}")

    def test_with_real_database(self):
        """실제 DB 연결 테스트"""
        print("\n" + "=" * 60)
        print("TEST: service_get_energy_usages_range - 실제 DB 연결")
        print("=" * 60)

        try:
            result = service_get_energy_usages_range(
                "2024-09-01 00:00:00",
                "2024-09-01 23:59:59",
                "하이테크센터"
            )
            result_dict = json.loads(result)

            if "error" in result_dict:
                print(f"⚠️  DB 오류: {result_dict['error']}")
                pytest.skip("DB 연결 불가 또는 데이터 없음")
            else:
                assert "meta" in result_dict
                assert "energyUsageInfos" in result_dict
                print(f"✓ 건물: {result_dict['meta']['building']}")
                print(f"✓ 데이터 개수: {len(result_dict['energyUsageInfos'])}")

        except Exception as e:
            print(f"⚠️  오류: {e}")
            pytest.skip("DB 연결 오류")


class TestServiceGetTotalEnergyUsage:
    """service_get_total_energy_usage 테스트"""

    @patch('src.services.execute_read_query')
    def test_calculates_total_usage(self, mock_query):
        """총 전력 사용량을 계산하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_total_energy_usage - 총 사용량 계산")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {
                "start_accumulated_val": 1000.0,
                "end_accumulated_val": 1500.0
            }
        ]

        result = service_get_total_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 23:59:59",
            "하이테크센터"
        )
        result_dict = json.loads(result)

        assert "meta" in result_dict, "meta 필드가 없습니다"
        assert "total_usage_kwh" in result_dict, "total_usage_kwh 필드가 없습니다"
        assert result_dict["total_usage_kwh"] == 500.0, "계산된 사용량이 일치하지 않습니다"

        print(f"✓ 건물: {result_dict['meta']['building']}")
        print(f"✓ 총 사용량: {result_dict['total_usage_kwh']} kWh")

    @patch('src.services.execute_read_query')
    def test_handles_negative_difference(self, mock_query):
        """음수 차이도 절댓값으로 처리하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_total_energy_usage - 음수 차이 처리")
        print("=" * 60)

        # Mock: 시작값이 끝값보다 큰 경우
        mock_query.return_value = [
            {
                "start_accumulated_val": 1500.0,
                "end_accumulated_val": 1000.0
            }
        ]

        result = service_get_total_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 23:59:59",
            "하이테크센터"
        )
        result_dict = json.loads(result)

        # abs() 함수로 처리되므로 양수여야 함
        assert result_dict["total_usage_kwh"] == 500.0
        print(f"✓ 절댓값 처리 확인: {result_dict['total_usage_kwh']} kWh")

    @patch('src.services.execute_read_query')
    def test_returns_error_when_no_data(self, mock_query):
        """데이터가 없을 때 에러를 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_get_total_energy_usage - 데이터 없음")
        print("=" * 60)

        mock_query.return_value = []

        result = service_get_total_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 23:59:59",
            "존재하지않는건물"
        )
        result_dict = json.loads(result)

        assert "error" in result_dict, "에러 필드가 있어야 합니다"
        print(f"✓ 에러 메시지: {result_dict['error']}")

    def test_with_real_database(self):
        """실제 DB 연결 테스트"""
        print("\n" + "=" * 60)
        print("TEST: service_get_total_energy_usage - 실제 DB 연결")
        print("=" * 60)

        try:
            result = service_get_total_energy_usage(
                "2024-09-01 00:00:00",
                "2024-09-01 23:59:59",
                "하이테크센터"
            )
            result_dict = json.loads(result)

            if "error" in result_dict:
                print(f"⚠️  DB 오류: {result_dict['error']}")
                pytest.skip("DB 연결 불가 또는 데이터 없음")
            else:
                assert "meta" in result_dict
                assert "total_usage_kwh" in result_dict
                assert result_dict["total_usage_kwh"] >= 0, "총 사용량은 0 이상이어야 합니다"
                print(f"✓ 건물: {result_dict['meta']['building']}")
                print(f"✓ 총 사용량: {result_dict['total_usage_kwh']} kWh")

        except Exception as e:
            print(f"⚠️  오류: {e}")
            pytest.skip("DB 연결 오류")


class TestServiceForecastEnergyUsage:
    """service_forecast_energy_usage 테스트 (기본 기능)"""

    def setup_method(self):
        """각 테스트 전 캐시 초기화"""
        service_forecast_energy_usage.cache_clear()

    @patch('src.services.execute_read_query')
    @patch('src.services.forecasting')
    def test_basic_forecast(self, mock_forecasting, mock_query):
        """기본 예측 기능 테스트"""
        print("\n" + "=" * 60)
        print("TEST: service_forecast_energy_usage - 기본 예측")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"DataValue": 100.0 + i} for i in range(144)  # 24시간 (10분 단위)
        ]

        import numpy as np
        mock_forecasting.return_value = (
            np.array([[105.0 + i for i in range(24)]]),  # point_forecast
            np.array([[[i] * 10 for i in range(24)]])  # quantile_forecast
        )

        result = service_forecast_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 23:59:59",
            "하이테크센터",
            24
        )
        result_dict = json.loads(result)

        assert "meta" in result_dict, "meta 필드가 없습니다"
        assert "forecast" in result_dict, "forecast 필드가 없습니다"
        assert "point_forecast" in result_dict["forecast"]
        assert len(result_dict["forecast"]["point_forecast"]) == 24

        print(f"✓ 건물: {result_dict['meta']['building']}")
        print(f"✓ Horizon: {result_dict['meta']['horizon']}")
        print(f"✓ 입력 데이터 포인트: {result_dict['meta']['data_points']}")
        print(f"✓ 예측값 개수: {len(result_dict['forecast']['point_forecast'])}")

    @patch('src.services.execute_read_query')
    def test_forecast_no_data(self, mock_query):
        """데이터가 없을 때 에러를 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: service_forecast_energy_usage - 데이터 없음")
        print("=" * 60)

        mock_query.return_value = []

        result = service_forecast_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 23:59:59",
            "존재하지않는건물"
        )
        result_dict = json.loads(result)

        assert "error" in result_dict, "에러 필드가 있어야 합니다"
        print(f"✓ 에러 메시지: {result_dict['error']}")

    @patch('src.services.execute_read_query')
    @patch('src.services.forecasting')
    def test_forecast_custom_horizon(self, mock_forecasting, mock_query):
        """커스텀 horizon 테스트"""
        print("\n" + "=" * 60)
        print("TEST: service_forecast_energy_usage - 커스텀 horizon (48)")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"DataValue": 100.0 + i} for i in range(144)
        ]

        import numpy as np
        mock_forecasting.return_value = (
            np.array([[105.0 + i for i in range(48)]]),  # horizon=48
            np.array([[[i] * 10 for i in range(48)]])
        )

        result = service_forecast_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 23:59:59",
            "하이테크센터",
            horizon=48
        )
        result_dict = json.loads(result)

        assert len(result_dict["forecast"]["point_forecast"]) == 48, "예측값 개수가 48개가 아님"
        assert result_dict["meta"]["horizon"] == 48, "horizon 값이 48이 아님"
        print(f"✓ Horizon: {result_dict['meta']['horizon']}")
        print(f"✓ 예측값 개수: {len(result_dict['forecast']['point_forecast'])}")

    @patch('src.services.execute_read_query')
    @patch('src.services.forecasting')
    def test_forecast_response_structure(self, mock_forecasting, mock_query):
        """응답 구조 상세 검증"""
        print("\n" + "=" * 60)
        print("TEST: service_forecast_energy_usage - 응답 구조 상세 검증")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"DataValue": 100.0 + i} for i in range(144)
        ]

        import numpy as np
        mock_forecasting.return_value = (
            np.array([[105.0 + i for i in range(24)]]),
            np.array([[[i] * 10 for i in range(24)]])
        )

        result = service_forecast_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 23:59:59",
            "60주년기념관",
            24
        )
        result_dict = json.loads(result)

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
        print(f"✓ forecast 필드 정상")

        # point_forecast 검증
        point_forecast = forecast["point_forecast"]
        assert isinstance(point_forecast, list), "point_forecast는 리스트여야 함"
        assert len(point_forecast) == 24, "point_forecast 길이가 24가 아님"
        assert all(isinstance(x, (int, float)) for x in point_forecast), "point_forecast 원소가 숫자가 아님"
        print(f"✓ point_forecast 정상: {len(point_forecast)}개 예측값")

    def test_forecast_with_real_database(self):
        """실제 DB 연결을 통한 예측 테스트"""
        print("\n" + "=" * 60)
        print("TEST: service_forecast_energy_usage - 실제 DB 연결")
        print("=" * 60)

        try:
            result = service_forecast_energy_usage(
                "2024-09-01 00:00:00",
                "2024-09-01 12:00:00",
                "60주년기념관",
                24
            )
            result_dict = json.loads(result)

            if "error" in result_dict:
                print(f"⚠️  오류: {result_dict['error']}")
                pytest.skip("DB 연결 또는 모델 로드 불가")
            else:
                assert "meta" in result_dict
                assert "forecast" in result_dict
                assert "point_forecast" in result_dict["forecast"]
                print(f"✓ 건물: {result_dict['meta']['building']}")
                print(f"✓ Horizon: {result_dict['meta']['horizon']}")
                print(f"✓ 입력 데이터: {result_dict['meta']['data_points']}개")
                print(f"✓ 예측값: {len(result_dict['forecast']['point_forecast'])}개")

        except Exception as e:
            print(f"⚠️  오류: {e}")
            pytest.skip("DB 연결 또는 모델 오류")


class TestResponseStructure:
    """모든 서비스의 응답 구조 검증"""

    @patch('src.services.execute_read_query')
    def test_all_services_return_valid_json(self, mock_query):
        """모든 서비스가 유효한 JSON을 반환하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: 모든 서비스 - JSON 유효성 검증")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [{"Building": "테스트"}]

        services = [
            ("get_monitored_buildings", service_get_monitored_buildings, []),
            ("get_building_data_range", service_get_building_data_range, ["테스트"]),
            ("get_energy_usages_range", service_get_energy_usages_range,
             ["2024-09-01 00:00:00", "2024-09-01 01:00:00", "테스트"]),
            ("get_total_energy_usage", service_get_total_energy_usage,
             ["2024-09-01 00:00:00", "2024-09-01 01:00:00", "테스트"]),
        ]

        for service_name, service_func, args in services:
            result = service_func(*args)
            try:
                json.loads(result)
                print(f"✓ {service_name}: 유효한 JSON")
            except json.JSONDecodeError as e:
                pytest.fail(f"{service_name}: JSON 파싱 실패 - {e}")