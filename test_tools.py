"""
MCP Tools 테스트 코드
Tool 함수들을 직접 테스트합니다.
"""

import json
import sys
from datetime import datetime
from src.services import (
    service_get_current_time,
    service_get_energy_usage_single,
    service_get_energy_usages_range
)

PYODBC_AVAILABLE = True


def test_get_current_time():
    """get_current_time Tool 테스트"""
    print("=" * 50)
    print("TEST 1: get_current_time")
    print("=" * 50)
    try:
        result = service_get_current_time()
        print(f"✓ 결과: {result}")
        print(f"✓ 타입: {type(result)}")
        assert isinstance(result, datetime), "datetime 타입이어야 합니다"
        print("✓ 테스트 통과!\n")
        return True
    except Exception as e:
        print(f"✗ 오류: {e}\n")
        return False


def test_get_energy_usage():
    """service_get_energy_usage_single 테스트"""
    print("=" * 50)
    print("TEST 2: service_get_energy_usage_single")
    print("=" * 50)

    if not PYODBC_AVAILABLE:
        print("⚠️  pyodbc 라이브러리가 없어서 DB 연결 테스트를 할 수 없습니다.\n")
        return False

    try:
        # 테스트 파라미터
        measurement_date_time = "2024-09-01 12:00:00"
        building = "하이테크센터"

        print(f"입력 파라미터:")
        print(f"  - measurement_date_time: {measurement_date_time}")
        print(f"  - building: {building}")

        result = service_get_energy_usage_single(measurement_date_time, building)

        print(f"\n✓ 결과 (JSON):")
        # JSON 파싱 테스트
        result_dict = json.loads(result)
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))

        print("✓ 테스트 통과!\n")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON 파싱 오류: {e}")
        print(f"원본 결과: {result}\n")
        return False
    except Exception as e:
        print(f"✗ 오류: {e}\n")
        return False


def test_get_energy_usages_by_date_range():
    """service_get_energy_usages_range Tool 테스트"""
    print("=" * 50)
    print("TEST 3: service_get_energy_usages_range")
    print("=" * 50)

    if not PYODBC_AVAILABLE:
        print("⚠️  pyodbc 라이브러리가 없어서 DB 연결 테스트를 할 수 없습니다.\n")
        return False

    try:
        # 테스트 파라미터
        start_date_time = "2024-09-01 00:00:00"
        end_date_time = "2024-09-01 23:59:59"
        building = "하이테크센터"

        print(f"입력 파라미터:")
        print(f"  - start_date_time: {start_date_time}")
        print(f"  - end_date_time: {end_date_time}")
        print(f"  - building: {building}")

        result = service_get_energy_usages_range(start_date_time, end_date_time, building)

        print(f"\n✓ 결과 (JSON):")
        # JSON 파싱 테스트
        result_dict = json.loads(result)
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))

        # 결과 구조 검증
        assert "meta" in result_dict, "meta 필드가 없습니다"
        assert "energyUsageInfos" in result_dict, "energyUsageInfos 필드가 없습니다"
        assert result_dict["meta"]["building"] == building, "building 정보가 일치하지 않습니다"

        print(f"\n✓ 데이터 개수: {len(result_dict['energyUsageInfos'])}개")
        print("✓ 테스트 통과!\n")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON 파싱 오류: {e}")
        print(f"원본 결과: {result}\n")
        return False
    except AssertionError as e:
        print(f"✗ 검증 오류: {e}\n")
        return False
    except Exception as e:
        print(f"✗ 오류: {e}\n")
        return False


def main():
    """테스트 실행"""
    print("\n" + "=" * 50)
    print("MCP Energy Server Tool 테스트")
    print("=" * 50 + "\n")

    results = []

    # TEST 1: get_current_time
    results.append(("get_current_time", test_get_current_time()))

    # TEST 2: get_energy_usage
    results.append(("get_energy_usage", test_get_energy_usage()))

    # TEST 3: get_energy_usages_by_date_range
    results.append(("get_energy_usages_by_date_range", test_get_energy_usages_by_date_range()))

    # 결과 요약
    print("=" * 50)
    print("테스트 요약")
    print("=" * 50)

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