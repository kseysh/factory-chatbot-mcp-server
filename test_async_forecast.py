"""
비동기 forecasting 함수 테스트 스크립트
asyncio.to_thread()를 사용한 비동기 ML 추론이 제대로 동작하는지 확인합니다.
"""

import asyncio
import numpy as np
import sys
import time
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.forecast_model import forecasting, model


async def test_async_forecasting():
    """asyncio.to_thread를 사용한 forecasting 테스트"""
    print("=" * 60)
    print("비동기 Forecasting 테스트")
    print("=" * 60)

    # 테스트 데이터 생성 (sine wave)
    horizon = 24
    input_length = 144
    x = np.linspace(0, 4 * np.pi, input_length)
    input_data = 100 + 20 * np.sin(x) + np.random.normal(0, 1, input_length)

    print(f"\n📊 입력 데이터:")
    print(f"  - 길이: {input_length}개 포인트")
    print(f"  - 예측 horizon: {horizon}")
    print(f"  - 데이터 범위: [{input_data.min():.2f}, {input_data.max():.2f}]")
    print(f"  - 평균: {input_data.mean():.2f}")

    print(f"\n⏱️  비동기 예측 시작...")
    start_time = time.time()

    # asyncio.to_thread를 사용하여 비동기로 실행
    point_forecast, quantile_forecast = await asyncio.to_thread(
        forecasting, model, horizon, input_data
    )

    elapsed = time.time() - start_time
    print(f"✅ 예측 완료! (소요 시간: {elapsed:.2f}초)")

    # 결과 검증
    print(f"\n📈 예측 결과:")
    print(f"  - point_forecast shape: {point_forecast.shape}")
    print(f"  - quantile_forecast shape: {quantile_forecast.shape}")
    print(f"  - 예측값 범위: [{point_forecast.min():.2f}, {point_forecast.max():.2f}]")
    print(f"  - 예측값 평균: {point_forecast.mean():.2f}")

    # 기본 검증
    assert point_forecast.shape == (1, horizon), f"point_forecast shape 오류: {point_forecast.shape}"
    assert quantile_forecast.shape == (1, horizon, 10), f"quantile_forecast shape 오류: {quantile_forecast.shape}"

    print(f"\n✅ 모든 검증 통과!")

    return point_forecast, quantile_forecast


async def test_concurrent_forecasting():
    """여러 예측을 동시에 실행하여 비동기 성능 확인"""
    print("\n" + "=" * 60)
    print("동시 다중 예측 테스트 (비동기 성능 확인)")
    print("=" * 60)

    num_tasks = 3
    horizon = 24
    input_length = 144

    print(f"\n🔄 {num_tasks}개의 예측을 동시에 실행합니다...")
    start_time = time.time()

    tasks = []
    for i in range(num_tasks):
        # 각각 다른 시계열 데이터 생성
        x = np.linspace(0, 4 * np.pi, input_length)
        input_data = 100 + 20 * np.sin(x + i) + np.random.normal(0, 1, input_length)

        # 비동기 태스크 생성
        task = asyncio.to_thread(forecasting, model, horizon, input_data)
        tasks.append(task)

    # 모든 태스크를 동시에 실행
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time
    print(f"✅ {num_tasks}개 예측 모두 완료! (총 소요 시간: {elapsed:.2f}초)")
    print(f"   평균 예측 시간: {elapsed/num_tasks:.2f}초")

    # 결과 검증
    for i, (point_forecast, quantile_forecast) in enumerate(results):
        assert point_forecast.shape == (1, horizon), f"Task {i+1} - point_forecast shape 오류"
        assert quantile_forecast.shape == (1, horizon, 10), f"Task {i+1} - quantile_forecast shape 오류"
        print(f"   Task {i+1}: 예측값 평균 = {point_forecast.mean():.2f}")

    print(f"\n✅ 동시 실행 테스트 통과!")

    return results


async def test_asyncio_integration():
    """다른 비동기 작업과 함께 실행되는지 확인"""
    print("\n" + "=" * 60)
    print("비동기 통합 테스트 (다른 async 작업과 병행)")
    print("=" * 60)

    async def dummy_async_task(task_id, delay):
        """가짜 비동기 작업"""
        print(f"  Task {task_id}: 시작 (대기 시간: {delay}초)")
        await asyncio.sleep(delay)
        print(f"  Task {task_id}: 완료!")
        return f"Task {task_id} result"

    # 테스트 데이터
    horizon = 24
    input_length = 144
    x = np.linspace(0, 4 * np.pi, input_length)
    input_data = 100 + 20 * np.sin(x) + np.random.normal(0, 1, input_length)

    print(f"\n🔄 ML 예측과 다른 비동기 작업을 동시에 실행...")
    start_time = time.time()

    # ML 예측과 다른 비동기 작업을 동시에 실행
    results = await asyncio.gather(
        asyncio.to_thread(forecasting, model, horizon, input_data),
        dummy_async_task(1, 0.5),
        dummy_async_task(2, 1.0),
        dummy_async_task(3, 1.5),
    )

    elapsed = time.time() - start_time
    print(f"\n✅ 모든 작업 완료! (총 소요 시간: {elapsed:.2f}초)")

    # ML 예측 결과 검증
    point_forecast, quantile_forecast = results[0]
    assert point_forecast.shape == (1, horizon), "point_forecast shape 오류"
    assert quantile_forecast.shape == (1, horizon, 10), "quantile_forecast shape 오류"

    print(f"   ML 예측 평균값: {point_forecast.mean():.2f}")
    print(f"   다른 작업들: {results[1:]}")

    print(f"\n✅ 비동기 통합 테스트 통과!")
    print(f"   👉 ML 예측 중에도 다른 비동기 작업이 정상적으로 실행됨!")


async def main():
    """모든 테스트 실행"""
    print("\n" + "=" * 60)
    print("🚀 비동기 Forecasting 테스트 시작")
    print("=" * 60)

    try:
        # 테스트 1: 기본 비동기 예측
        await test_async_forecasting()

        # 테스트 2: 동시 다중 예측
        await test_concurrent_forecasting()

        # 테스트 3: 비동기 통합 테스트
        await test_asyncio_integration()

        print("\n" + "=" * 60)
        print("🎉 모든 테스트 통과!")
        print("=" * 60)
        print("\n✅ asyncio.to_thread()를 사용한 비동기 forecasting이 정상 동작합니다.")
        print("✅ ML 모델 추론 중에도 다른 비동기 작업이 블로킹되지 않습니다.")
        print("✅ 여러 예측을 동시에 실행할 수 있습니다.\n")

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
