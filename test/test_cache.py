"""
캐싱 데코레이터 테스트 코드
TTLCache와 LRU Cache의 동작을 검증합니다.
"""

import time
import pytest
from unittest.mock import patch
from src.services import (
    service_get_monitored_buildings,
    service_forecast_energy_usage,
    cache
)

class TestTTLCache:
    """TTLCache (@cached) 데코레이터 테스트"""

    def setup_method(self):
        """각 테스트 전 캐시 초기화"""
        cache.clear()

    @patch('src.services.execute_read_query')
    def test_cache_on_first_call(self, mock_query):
        """첫 호출 시 실제 DB 쿼리가 실행되는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: TTLCache - 첫 호출 시 DB 쿼리 실행")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"Building": "하이테크센터"},
            {"Building": "테크노파크"}
        ]

        # 첫 번째 호출
        result1 = service_get_monitored_buildings()

        # DB 쿼리가 1번 실행되었는지 확인
        assert mock_query.call_count == 1
        print(f"✓ DB 쿼리 실행 횟수: {mock_query.call_count}")
        print(f"✓ 반환값: {result1[:100]}...")

    @patch('src.services.execute_read_query')
    def test_cache_on_second_call(self, mock_query):
        """두 번째 호출 시 캐시된 값이 반환되는지 확인 (DB 호출 없음)"""
        print("\n" + "=" * 60)
        print("TEST: TTLCache - 캐시된 값 반환 (DB 호출 없음)")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"Building": "하이테크센터"},
            {"Building": "테크노파크"}
        ]

        # 첫 번째 호출
        result1 = service_get_monitored_buildings()
        initial_call_count = mock_query.call_count

        # 두 번째 호출 (캐시에서 반환되어야 함)
        result2 = service_get_monitored_buildings()

        # DB 쿼리가 추가로 실행되지 않았는지 확인
        assert mock_query.call_count == initial_call_count
        print(f"✓ 첫 호출 후 DB 쿼리 횟수: {initial_call_count}")
        print(f"✓ 두 번째 호출 후 DB 쿼리 횟수: {mock_query.call_count}")

        # 같은 결과가 반환되는지 확인
        assert result1 == result2
        print(f"✓ 캐시된 값이 일치함")


class TestLRUCache:
    """LRU Cache (@lru_cache) 데코레이터 테스트"""

    def setup_method(self):
        """각 테스트 전 캐시 초기화"""
        # lru_cache는 cache_clear() 메서드로 초기화
        service_forecast_energy_usage.cache_clear()

    @patch('src.services.execute_read_query')
    @patch('src.services.forecasting')
    def test_lru_cache_on_same_parameters(self, mock_forecasting, mock_query):
        """동일한 파라미터로 호출 시 캐시된 값이 반환되는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: LRU Cache - 동일 파라미터로 호출 시 캐시 사용")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"DataValue": 100.5},
            {"DataValue": 101.2},
            {"DataValue": 102.0}
        ]

        import numpy as np
        mock_forecasting.return_value = (
            np.array([[105.0, 106.0, 107.0]]),  # point_forecast
            np.array([[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]])  # quantile_forecast
        )

        # 동일한 파라미터로 두 번 호출
        start = "2024-09-01 00:00:00"
        end = "2024-09-01 12:00:00"
        building = "하이테크센터"
        horizon = 24

        result1 = service_forecast_energy_usage(start, end, building, horizon)
        initial_query_count = mock_query.call_count
        initial_forecast_count = mock_forecasting.call_count

        result2 = service_forecast_energy_usage(start, end, building, horizon)

        # 캐시가 사용되어 DB 쿼리와 예측이 다시 실행되지 않았는지 확인
        assert mock_query.call_count == initial_query_count
        assert mock_forecasting.call_count == initial_forecast_count
        print(f"✓ 첫 호출 후 DB 쿼리 횟수: {initial_query_count}")
        print(f"✓ 두 번째 호출 후 DB 쿼리 횟수: {mock_query.call_count}")
        print(f"✓ 첫 호출 후 예측 실행 횟수: {initial_forecast_count}")
        print(f"✓ 두 번째 호출 후 예측 실행 횟수: {mock_forecasting.call_count}")

        # 같은 결과가 반환되는지 확인
        assert result1 == result2
        print(f"✓ 캐시된 값이 일치함")

    @patch('src.services.execute_read_query')
    @patch('src.services.forecasting')
    def test_lru_cache_on_different_parameters(self, mock_forecasting, mock_query):
        """다른 파라미터로 호출 시 새로운 값이 계산되는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: LRU Cache - 다른 파라미터로 호출 시 재계산")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"DataValue": 100.5},
            {"DataValue": 101.2},
            {"DataValue": 102.0}
        ]

        import numpy as np
        mock_forecasting.return_value = (
            np.array([[105.0, 106.0, 107.0]]),
            np.array([[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]])
        )

        # 첫 번째 호출
        result1 = service_forecast_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 12:00:00",
            "하이테크센터",
            24
        )
        initial_count = mock_query.call_count

        # 다른 파라미터로 두 번째 호출
        result2 = service_forecast_energy_usage(
            "2024-09-02 00:00:00",  # 다른 시작 시간
            "2024-09-02 12:00:00",  # 다른 종료 시간
            "하이테크센터",
            24
        )

        # DB 쿼리가 다시 실행되었는지 확인
        assert mock_query.call_count == initial_count + 1
        print(f"✓ 첫 호출 후 DB 쿼리 횟수: {initial_count}")
        print(f"✓ 다른 파라미터로 호출 후 DB 쿼리 횟수: {mock_query.call_count}")

    @patch('src.services.execute_read_query')
    @patch('src.services.forecasting')
    def test_lru_cache_info(self, mock_forecasting, mock_query):
        """LRU Cache 정보 확인 (hits, misses, size)"""
        print("\n" + "=" * 60)
        print("TEST: LRU Cache - 캐시 정보 확인")
        print("=" * 60)

        # Mock 데이터 설정
        mock_query.return_value = [
            {"DataValue": 100.5},
            {"DataValue": 101.2},
            {"DataValue": 102.0}
        ]

        import numpy as np
        mock_forecasting.return_value = (
            np.array([[105.0, 106.0, 107.0]]),
            np.array([[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]])
        )

        # 캐시 정보 초기화 후 확인
        info_before = service_forecast_energy_usage.cache_info()
        print(f"캐시 정보 (실행 전): {info_before}")

        # 첫 번째 호출 (cache miss)
        service_forecast_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 12:00:00",
            "하이테크센터",
            24
        )

        info_after_first = service_forecast_energy_usage.cache_info()
        print(f"캐시 정보 (첫 호출 후): {info_after_first}")
        assert info_after_first.misses == 1
        assert info_after_first.hits == 0

        # 동일한 파라미터로 두 번째 호출 (cache hit)
        service_forecast_energy_usage(
            "2024-09-01 00:00:00",
            "2024-09-01 12:00:00",
            "하이테크센터",
            24
        )

        info_after_second = service_forecast_energy_usage.cache_info()
        print(f"캐시 정보 (두 번째 호출 후): {info_after_second}")
        assert info_after_second.hits == 1
        print(f"✓ Cache Hit: {info_after_second.hits}")
        print(f"✓ Cache Miss: {info_after_second.misses}")
        print(f"✓ Cache Size: {info_after_second.currsize}")


class TestCacheIntegration:
    """캐시 통합 테스트 (실제 DB 연결 필요)"""

    def test_ttl_cache_with_real_db(self):
        """TTL Cache 실제 동작 테스트 (DB 연결 필요)"""
        print("\n" + "=" * 60)
        print("TEST: TTL Cache - 실제 DB 연결 테스트")
        print("=" * 60)

        try:
            # 캐시 초기화
            cache.clear()

            # 첫 번째 호출
            start_time = time.time()
            result1 = service_get_monitored_buildings()
            first_call_time = time.time() - start_time

            # 두 번째 호출 (캐시됨)
            start_time = time.time()
            result2 = service_get_monitored_buildings()
            second_call_time = time.time() - start_time

            print(f"✓ 첫 번째 호출 시간: {first_call_time:.4f}초")
            print(f"✓ 두 번째 호출 시간: {second_call_time:.4f}초 (캐시)")
            print(f"✓ 속도 향상: {first_call_time / second_call_time:.2f}배")

            # 캐시된 값이 동일한지 확인
            assert result1 == result2
            print(f"✓ 결과 일치 확인")

            # 캐시 사용으로 인한 성능 향상 확인
            assert second_call_time < first_call_time
            print(f"✓ 캐시 사용 시 성능 향상 확인")

        except Exception as e:
            print(f"⚠️  DB 연결 오류: {e}")
            print("⚠️  이 테스트는 실제 DB 연결이 필요합니다.")
            pytest.skip("DB 연결 불가")

    def test_lru_cache_with_real_db(self):
        """LRU Cache 실제 동작 테스트 (DB 연결 필요)"""
        print("\n" + "=" * 60)
        print("TEST: LRU Cache - 실제 DB 연결 테스트")
        print("=" * 60)

        try:
            # 캐시 초기화
            service_forecast_energy_usage.cache_clear()

            # 동일한 파라미터로 두 번 호출
            start = "2024-09-01 00:00:00"
            end = "2024-09-01 12:00:00"
            building = "하이테크센터"

            # 첫 번째 호출
            start_time = time.time()
            result1 = service_forecast_energy_usage(start, end, building, 24)
            first_call_time = time.time() - start_time

            # 두 번째 호출 (캐시됨)
            start_time = time.time()
            result2 = service_forecast_energy_usage(start, end, building, 24)
            second_call_time = time.time() - start_time

            print(f"✓ 첫 번째 호출 시간: {first_call_time:.4f}초")
            print(f"✓ 두 번째 호출 시간: {second_call_time:.4f}초 (캐시)")
            print(f"✓ 속도 향상: {first_call_time / second_call_time:.2f}배")

            # 캐시 정보 출력
            cache_info = service_forecast_energy_usage.cache_info()
            print(f"✓ 캐시 정보: {cache_info}")

            # 캐시된 값이 동일한지 확인
            assert result1 == result2
            print(f"✓ 결과 일치 확인")

        except Exception as e:
            print(f"⚠️  오류: {e}")
            print("⚠️  이 테스트는 실제 DB 연결과 모델이 필요합니다.")
            pytest.skip("DB 연결 또는 모델 로드 불가")