from .models.timesfm.src.timesfm.configs import ForecastConfig
from .models.timesfm.src.timesfm.timesfm_2p5.timesfm_2p5_torch import TimesFM_2p5_200M_torch
import torch

model = TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch", torch_compile=False)

model.model.to(dtype=torch.float32)

model.compile(
    ForecastConfig(
        max_context=1024*4,
        max_horizon=1024,
        normalize_inputs=True,
        use_continuous_quantile_head=True,
        force_flip_invariance=True,
        infer_is_positive=True,
        fix_quantile_crossing=True,
        window_size=144*7,
    )
) 

def forecasting(model, horizon, input):
    """
    Arguments
    ---------
    model : timesfm.TimesFM_2p5_200M_torch
        사전학습된 TimesFM 모델 객체.

    input_data : np.ndarray | list[np.ndarray]
        원하는 시계열 데이터 구간.
        각 시퀀스의 shape: (길이,)

    horizon : int
        예측할 구간 수.
        시계열의 마지막 시점으로부터 horizon 길이만큼 미래를 예측합니다.

    Returns
    -------
    point_forecast : np.ndarray
        Shape: (입력 개수, horizon)
        평균(또는 대표값) 예측 결과.

    quantile_forecast : np.ndarray
        Shape: (입력 개수, horizon, 10)
        첫 번째 값은 mean, 이후 q10 ~ q90 분위수 예측값을 포함합니다.
    """
    point_forecast, quantile_forecast = model.forecast(
        horizon=horizon,
        inputs=[
            input
        ]
    )
    return (point_forecast, quantile_forecast)