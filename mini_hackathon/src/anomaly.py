"""
비지도 이상탐지 (라벨 없이 비정상 로트 찾기)
------------------------------------------------
실제 현장에서는 불량 라벨이 없거나 적은 경우가 많다.
IsolationForest로 라벨 없이 이상 로트를 탐지하고,
실제 불량 라벨과 비교해 탐지 성능을 확인한다.
"""
import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, classification_report

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "secom_like.csv"


def main():
    df = pd.read_csv(DATA)
    X = df.drop(columns=["target"])
    y = df["target"]

    contamination = float(y.mean())  # 대략적인 불량 비율 가정

    model = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("iso", IsolationForest(
            n_estimators=300, contamination=contamination,
            random_state=42, n_jobs=-1)),
    ])
    model.fit(X)

    # score: 낮을수록 이상. 부호 뒤집어 '이상 점수'로 사용
    anomaly_score = -model.named_steps["iso"].score_samples(
        model.named_steps["scale"].transform(
            model.named_steps["impute"].transform(X)))
    pred = (model.predict(X) == -1).astype(int)  # -1 = 이상

    print("=" * 55)
    print("  비지도 이상탐지 (IsolationForest)")
    print("=" * 55)
    print(f"  가정한 이상 비율(contamination): {contamination*100:.1f}%")
    auc = roc_auc_score(y, anomaly_score)
    print(f"  이상점수 기준 ROC-AUC (실제 불량 대비): {auc:.4f}")
    print("  --- 이상=불량으로 간주한 분류 리포트 ---")
    print(classification_report(y, pred, target_names=["양품", "불량"],
                                digits=3))
    print("  * 라벨 없이도 불량 로트를 어느 정도 걸러낼 수 있는지 확인용")
    print("=" * 55)


if __name__ == "__main__":
    main()
