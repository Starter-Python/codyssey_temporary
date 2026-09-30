"""
반도체 공정 가상 데이터 생성기
----------------------------------
실제 SECOM(반도체 공정) 데이터셋의 특성을 모사한 합성 데이터를 만든다.
- 다수의 센서 피처 (온도/압력/유량/전력 등)
- 심한 클래스 불균형 (불량률 낮음) -> 실제 반도체 공정과 유사
- 일부 피처만 불량과 실제로 연관 (나머지는 노이즈)
- 결측치 포함
"""
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)

N_SAMPLES = 2000       # 웨이퍼 로트 수
N_FEATURES = 40        # 센서 개수
N_INFORMATIVE = 6      # 실제로 불량과 연관된 센서 수
FAIL_RATE = 0.10       # 불량률 (불균형)

FEATURE_GROUPS = {
    "temp": "온도 센서",
    "pressure": "압력 센서",
    "gasflow": "가스 유량",
    "power": "전력",
    "vibration": "진동",
}


def generate():
    # 1) 기본 센서값: 정규분포 (각 센서마다 다른 평균/표준편차)
    means = RNG.uniform(50, 500, size=N_FEATURES)
    stds = RNG.uniform(1, 20, size=N_FEATURES)
    X = RNG.normal(means, stds, size=(N_SAMPLES, N_FEATURES))

    # 2) 불량에 영향을 주는 informative 피처 선택
    informative_idx = RNG.choice(N_FEATURES, size=N_INFORMATIVE, replace=False)
    weights = RNG.uniform(0.8, 1.6, size=N_INFORMATIVE) * RNG.choice([-1, 1], N_INFORMATIVE)

    # 표준화된 informative 피처의 선형결합 -> 불량 확률(logit)
    Xi = (X[:, informative_idx] - X[:, informative_idx].mean(0)) / X[:, informative_idx].std(0)
    logit = Xi @ weights
    # 불균형 맞추기 위해 절편 조정
    logit += np.log(FAIL_RATE / (1 - FAIL_RATE)) - logit.mean()
    prob_fail = 1 / (1 + np.exp(-logit))
    y = (RNG.uniform(size=N_SAMPLES) < prob_fail).astype(int)

    # 3) 컬럼 이름 만들기 (센서 그룹별)
    group_names = list(FEATURE_GROUPS.keys())
    cols = []
    for i in range(N_FEATURES):
        g = group_names[i % len(group_names)]
        cols.append(f"{g}_{i:02d}")
    df = pd.DataFrame(X, columns=cols)

    # 4) 결측치 주입 (센서 고장 모사) - 전체의 약 2%
    n_missing = int(0.02 * df.size)
    ri = RNG.integers(0, df.shape[0], n_missing)
    ci = RNG.integers(0, df.shape[1], n_missing)
    for r, c in zip(ri, ci):
        df.iat[r, c] = np.nan

    df["target"] = y  # 1 = 불량(fail), 0 = 양품(pass)

    # 정답 피처가 무엇이었는지 기록 (검증용)
    informative_cols = [cols[i] for i in informative_idx]
    return df, informative_cols


def main():
    base = Path(__file__).resolve().parent.parent
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    df, informative_cols = generate()
    out = data_dir / "secom_like.csv"
    df.to_csv(out, index=False)

    print("=" * 55)
    print("  반도체 공정 데이터 생성 완료")
    print("=" * 55)
    print(f"  저장 위치 : {out}")
    print(f"  샘플 수   : {len(df):,} 개 웨이퍼 로트")
    print(f"  센서 수   : {df.shape[1] - 1} 개")
    print(f"  불량 수   : {int(df['target'].sum()):,} 개 "
          f"({df['target'].mean() * 100:.1f}%)  <- 불균형")
    print(f"  결측치    : {int(df.isna().sum().sum()):,} 개")
    print(f"  실제 불량 연관 센서(정답): {informative_cols}")
    print("=" * 55)


if __name__ == "__main__":
    main()
