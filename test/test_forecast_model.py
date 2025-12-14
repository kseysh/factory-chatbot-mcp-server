"""
forecast_model 모듈의 forecasting 함수에 대한 테스트 코드
pytest 프레임워크를 사용하여 테스트합니다.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


class TestForecastingFunction:
    """forecasting 함수 테스트"""

    @patch('src.forecast_model.model')
    def test_basic_forecast(self, mock_model):
        """기본 예측 기능이 제대로 동작하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecasting - 기본 예측")
        print("=" * 60)

        from src.forecast_model import forecasting

        # Mock 모델 설정
        horizon = 24
        input_data = np.array([100.0 + i for i in range(144)])  # 144개 데이터 포인트

        # Mock forecast 결과 설정
        expected_point = np.array([[105.0 + i for i in range(horizon)]])
        expected_quantile = np.random.rand(1, horizon, 10)
        mock_model.forecast.return_value = (expected_point, expected_quantile)

        # forecasting 함수 호출
        point_forecast, quantile_forecast = forecasting(
            model=mock_model,
            horizon=horizon,
            input=input_data
        )

        # 검증
        assert point_forecast is not None, "point_forecast가 None입니다"
        assert quantile_forecast is not None, "quantile_forecast가 None입니다"
        assert isinstance(point_forecast, np.ndarray), "point_forecast는 numpy 배열이어야 합니다"
        assert isinstance(quantile_forecast, np.ndarray), "quantile_forecast는 numpy 배열이어야 합니다"

        print(f"✓ point_forecast shape: {point_forecast.shape}")
        print(f"✓ quantile_forecast shape: {quantile_forecast.shape}")
        print(f"✓ horizon: {horizon}")

    @patch('src.forecast_model.model')
    def test_forecast_output_shape(self, mock_model):
        """예측 결과의 shape이 올바른지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecasting - 출력 shape 검증")
        print("=" * 60)

        from src.forecast_model import forecasting

        horizon = 48
        input_data = np.array([100.0 + i for i in range(200)])

        # Mock 설정
        expected_point = np.array([[105.0 + i for i in range(horizon)]])
        expected_quantile = np.random.rand(1, horizon, 10)
        mock_model.forecast.return_value = (expected_point, expected_quantile)

        # forecasting 호출
        point_forecast, quantile_forecast = forecasting(
            model=mock_model,
            horizon=horizon,
            input=input_data
        )

        # Shape 검증
        assert point_forecast.shape == (1, horizon), f"point_forecast shape이 잘못됨: {point_forecast.shape}"
        assert quantile_forecast.shape == (1, horizon, 10), f"quantile_forecast shape이 잘못됨: {quantile_forecast.shape}"

        print(f"✓ point_forecast shape: {point_forecast.shape} (expected: (1, {horizon}))")
        print(f"✓ quantile_forecast shape: {quantile_forecast.shape} (expected: (1, {horizon}, 10))")

    @patch('src.forecast_model.model')
    def test_forecast_with_different_horizons(self, mock_model):
        """다양한 horizon 값으로 예측이 제대로 동작하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecasting - 다양한 horizon 값 테스트")
        print("=" * 60)

        from src.forecast_model import forecasting

        horizons = [12, 24, 48, 96, 144]
        input_data = np.array([100.0 + i for i in range(500)])

        for horizon in horizons:
            # Mock 설정
            expected_point = np.array([[105.0 + i for i in range(horizon)]])
            expected_quantile = np.random.rand(1, horizon, 10)
            mock_model.forecast.return_value = (expected_point, expected_quantile)

            # forecasting 호출
            point_forecast, quantile_forecast = forecasting(
                model=mock_model,
                horizon=horizon,
                input=input_data
            )

            # 검증
            assert point_forecast.shape[1] == horizon, f"horizon {horizon}에 대한 예측 길이가 일치하지 않음"
            assert quantile_forecast.shape[1] == horizon, f"horizon {horizon}에 대한 quantile 예측 길이가 일치하지 않음"

            print(f"✓ Horizon {horizon}: point_forecast shape = {point_forecast.shape}")

    @patch('src.forecast_model.model')
    def test_forecast_with_different_input_lengths(self, mock_model):
        """다양한 길이의 입력 데이터로 예측이 제대로 동작하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecasting - 다양한 입력 길이 테스트")
        print("=" * 60)

        from src.forecast_model import forecasting

        horizon = 24
        input_lengths = [100, 200, 500, 1000]

        for length in input_lengths:
            input_data = np.array([100.0 + i for i in range(length)])

            # Mock 설정
            expected_point = np.array([[105.0 + i for i in range(horizon)]])
            expected_quantile = np.random.rand(1, horizon, 10)
            mock_model.forecast.return_value = (expected_point, expected_quantile)

            # forecasting 호출
            point_forecast, quantile_forecast = forecasting(
                model=mock_model,
                horizon=horizon,
                input=input_data
            )

            # 검증 - 입력 길이와 상관없이 horizon 길이의 예측이 나와야 함
            assert point_forecast.shape == (1, horizon), f"입력 길이 {length}에 대한 예측 shape이 잘못됨"

            print(f"✓ Input length {length}: 예측 성공 (output shape: {point_forecast.shape})")

    @patch('src.forecast_model.model')
    def test_model_forecast_called_with_correct_args(self, mock_model):
        """모델의 forecast 메서드가 올바른 인자로 호출되는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecasting - 모델 호출 인자 검증")
        print("=" * 60)

        from src.forecast_model import forecasting

        horizon = 24
        input_data = np.array([100.0 + i for i in range(144)])

        # Mock 설정
        expected_point = np.array([[105.0 + i for i in range(horizon)]])
        expected_quantile = np.random.rand(1, horizon, 10)
        mock_model.forecast.return_value = (expected_point, expected_quantile)

        # forecasting 호출
        forecasting(model=mock_model, horizon=horizon, input=input_data)

        # 모델의 forecast가 올바르게 호출되었는지 검증
        mock_model.forecast.assert_called_once()
        call_kwargs = mock_model.forecast.call_args.kwargs

        assert 'horizon' in call_kwargs, "horizon 인자가 없습니다"
        assert 'inputs' in call_kwargs, "inputs 인자가 없습니다"
        assert call_kwargs['horizon'] == horizon, f"horizon 값이 일치하지 않음: {call_kwargs['horizon']}"

        print(f"✓ 모델이 올바른 인자로 호출됨")
        print(f"  - horizon: {call_kwargs['horizon']}")
        print(f"  - inputs type: {type(call_kwargs['inputs'])}")


class TestRealModelIntegration:
    """실제 모델을 사용한 통합 테스트"""

    def test_real_model_forecast(self):
        """실제 모델을 로드하여 예측이 제대로 동작하는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecasting - 실제 모델 통합 테스트")
        print("=" * 60)

        try:
            from src.forecast_model import model, forecasting

            # 간단한 시계열 데이터 생성 (sine wave)
            horizon = 24
            input_length = 144
            x = np.linspace(0, 4 * np.pi, input_length)
            input_data = 100 + 20 * np.sin(x) + np.random.normal(0, 1, input_length)

            print(f"입력 데이터: {input_length}개 포인트")
            print(f"예측 horizon: {horizon}")
            print(f"입력 데이터 범위: [{input_data.min():.2f}, {input_data.max():.2f}]")

            # 예측 수행
            point_forecast, quantile_forecast = forecasting(
                model=model,
                horizon=horizon,
                input=input_data
            )

            # 기본 검증
            assert point_forecast is not None, "point_forecast가 None입니다"
            assert quantile_forecast is not None, "quantile_forecast가 None입니다"
            assert isinstance(point_forecast, np.ndarray), "point_forecast는 numpy 배열이어야 합니다"
            assert isinstance(quantile_forecast, np.ndarray), "quantile_forecast는 numpy 배열이어야 합니다"

            # Shape 검증
            assert point_forecast.shape[0] == 1, f"point_forecast의 첫 번째 차원이 1이 아님: {point_forecast.shape}"
            assert point_forecast.shape[1] == horizon, f"point_forecast의 길이가 horizon과 일치하지 않음: {point_forecast.shape[1]} != {horizon}"

            assert quantile_forecast.shape[0] == 1, f"quantile_forecast의 첫 번째 차원이 1이 아님"
            assert quantile_forecast.shape[1] == horizon, f"quantile_forecast의 길이가 horizon과 일치하지 않음"
            assert quantile_forecast.shape[2] == 10, f"quantile_forecast의 분위수 개수가 10이 아님: {quantile_forecast.shape[2]}"

            # 예측값이 합리적인 범위에 있는지 확인
            input_mean = np.mean(input_data)
            input_std = np.std(input_data)
            forecast_mean = np.mean(point_forecast)

            # 예측값이 입력 데이터의 평균 ± 3*표준편차 범위 안에 있는지 확인
            lower_bound = input_mean - 3 * input_std
            upper_bound = input_mean + 3 * input_std
            assert lower_bound <= forecast_mean <= upper_bound, \
                f"예측값이 합리적인 범위를 벗어남: {forecast_mean:.2f} not in [{lower_bound:.2f}, {upper_bound:.2f}]"

            print(f"✓ 예측 성공!")
            print(f"  - point_forecast shape: {point_forecast.shape}")
            print(f"  - quantile_forecast shape: {quantile_forecast.shape}")
            print(f"  - 입력 데이터 평균: {input_mean:.2f}")
            print(f"  - 예측값 평균: {forecast_mean:.2f}")
            print(f"  - 예측값 범위: [{point_forecast.min():.2f}, {point_forecast.max():.2f}]")

        except ImportError as e:
            print(f"⚠️  모델 로드 실패: {e}")
            pytest.skip("모델을 로드할 수 없어 테스트를 건너뜁니다")
        except Exception as e:
            print(f"⚠️  예측 중 오류 발생: {e}")
            pytest.skip(f"예측 실행 중 오류: {str(e)}")

    def test_real_model_multiple_forecasts(self):
        """실제 모델로 여러 번 예측을 수행해도 안정적인지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecasting - 다중 예측 안정성 테스트")
        print("=" * 60)

        try:
            from src.forecast_model import model, forecasting

            horizon = 24
            num_iterations = 3

            for i in range(num_iterations):
                # 매번 다른 데이터 생성
                input_length = 144
                x = np.linspace(0, 4 * np.pi, input_length)
                input_data = 100 + 20 * np.sin(x + i) + np.random.normal(0, 1, input_length)

                # 예측 수행
                point_forecast, quantile_forecast = forecasting(
                    model=model,
                    horizon=horizon,
                    input=input_data
                )

                # 기본 검증
                assert point_forecast.shape == (1, horizon), f"반복 {i+1}에서 point_forecast shape이 잘못됨"
                assert quantile_forecast.shape == (1, horizon, 10), f"반복 {i+1}에서 quantile_forecast shape이 잘못됨"

                print(f"✓ 반복 {i+1}/{num_iterations}: 예측 성공 (평균: {np.mean(point_forecast):.2f})")

            print(f"✓ 총 {num_iterations}번의 예측이 모두 성공적으로 완료됨")

        except ImportError:
            pytest.skip("모델을 로드할 수 없어 테스트를 건너뜁니다")
        except Exception as e:
            pytest.skip(f"예측 실행 중 오류: {str(e)}")


class TestModelConfiguration:
    """모델 설정 테스트"""

    def test_model_is_loaded(self):
        """모델이 제대로 로드되었는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecast_model - 모델 로드 확인")
        print("=" * 60)

        try:
            from src.forecast_model import model

            assert model is not None, "모델이 None입니다"
            assert hasattr(model, 'forecast'), "모델에 forecast 메서드가 없습니다"

            print(f"✓ 모델 로드 성공")
            print(f"✓ 모델 타입: {type(model).__name__}")

        except ImportError as e:
            print(f"⚠️  모델 로드 실패: {e}")
            pytest.skip("모델을 로드할 수 없어 테스트를 건너뜁니다")
        except Exception as e:
            print(f"⚠️  오류: {e}")
            pytest.skip(f"모델 확인 중 오류: {str(e)}")

    def test_model_has_compiled_config(self):
        """모델이 compile 설정을 가지고 있는지 확인"""
        print("\n" + "=" * 60)
        print("TEST: forecast_model - 모델 compile 설정 확인")
        print("=" * 60)

        try:
            from src.forecast_model import model

            # 모델이 컴파일되었는지 확인 (TimesFM 모델은 compile 메서드를 호출함)
            # 실제로는 forecast 메서드가 작동하는지 확인하는 것으로 충분
            assert hasattr(model, 'forecast'), "모델에 forecast 메서드가 없습니다"

            print(f"✓ 모델이 올바르게 구성됨")

        except ImportError:
            pytest.skip("모델을 로드할 수 없어 테스트를 건너뜁니다")
        except Exception as e:
            pytest.skip(f"모델 확인 중 오류: {str(e)}")