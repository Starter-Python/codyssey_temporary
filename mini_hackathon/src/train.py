"""
반도체 수율 예측 모델 (양품/불량 분류)
----------------------------------------
불균형 데이터에 맞춰 평가하고, 불량 핵심 인자를 도출한다.
- 전처리: 결측치 대치 + 표준화
- 모델: LogisticRegression, RandomForest 비교
- 평가: ROC-AUC, F1, PR-AUC, Confusion Matrix (recall 중시)
- 해석: 불량에 영향을 준 상위 센서 시각화
"""
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # 화면 없는 환경에서 파일로 저장
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, f1_score, classification_report,
    confusion_matrix, average_precision_score, precision_recall_curve,
)

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "secom_like.csv"
OUT = BASE / "outputs"


def load_data():
    df = pd.read_csv(DATA)
    X = df.drop(columns=["target"])
    y = df["target"]
    return X, y


def build_models():
    """전처리+모델을 하나로 묶은 파이프라인 2종."""
    pre = [
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]
    logreg = Pipeline(pre + [
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    rf = Pipeline(pre + [
        ("clf", RandomForestClassifier(
            n_estimators=300, class_weight="balanced",
            random_state=42, n_jobs=-1)),
    ])
    return {"LogisticRegression": logreg, "RandomForest": rf}


def evaluate(name, model, X_te, y_te):
    proba = model.predict_proba(X_te)[:, 1]
    pred = (proba >= 0.5).astype(int)
    metrics = {
        "ROC_AUC": roc_auc_score(y_te, proba),
        "PR_AUC": average_precision_score(y_te, proba),
        "F1": f1_score(y_te, pred),
    }
    print(f"\n[{name}]")
    for k, v in metrics.items():
        print(f"  {k:8s}: {v:.4f}")
    print("  --- classification report ---")
    print(classification_report(y_te, pred, target_names=["양품", "불량"],
                                digits=3))
    cm = confusion_matrix(y_te, pred)
    print(f"  Confusion Matrix (행=실제, 열=예측):\n{cm}")
    return metrics, proba


def plot_feature_importance(model, feature_names, out_path, top=15):
    rf = model.named_steps["clf"]
    imp = pd.Series(rf.feature_importances_, index=feature_names)
    top_imp = imp.sort_values(ascending=False).head(top)

    plt.figure(figsize=(8, 6))
    top_imp[::-1].plot(kind="barh", color="#1f77b4")
    plt.title("Top %d Key Sensors for Defect Prediction (RandomForest)" % top)
    plt.xlabel("Feature Importance")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()
    return top_imp


def plot_pr_curves(results, y_te, out_path):
    plt.figure(figsize=(7, 6))
    for name, proba in results.items():
        prec, rec, _ = precision_recall_curve(y_te, proba)
        ap = average_precision_score(y_te, proba)
        plt.plot(rec, prec, label=f"{name} (PR-AUC={ap:.3f})")
    plt.xlabel("Recall (how many defects are caught)")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    X, y = load_data()
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42)

    print("=" * 55)
    print("  반도체 수율 예측 - 모델 학습 & 평가")
    print("=" * 55)
    print(f"  학습셋: {len(X_tr)}  테스트셋: {len(X_te)}")
    print(f"  테스트 불량률: {y_te.mean()*100:.1f}%")

    models = build_models()
    proba_results = {}
    best_name, best_auc, best_model = None, -1, None
    for name, model in models.items():
        model.fit(X_tr, y_tr)
        metrics, proba = evaluate(name, model, X_te, y_te)
        proba_results[name] = proba
        if metrics["ROC_AUC"] > best_auc:
            best_name, best_auc, best_model = name, metrics["ROC_AUC"], model

    print("\n" + "=" * 55)
    print(f"  최고 모델: {best_name} (ROC-AUC={best_auc:.4f})")
    print("=" * 55)

    # PR 커브 저장
    pr_path = OUT / "pr_curve.png"
    plot_pr_curves(proba_results, y_te, pr_path)
    print(f"  [저장] PR 커브 -> {pr_path}")

    # RandomForest 핵심 인자
    if "RandomForest" in models:
        fi_path = OUT / "feature_importance.png"
        top_imp = plot_feature_importance(
            models["RandomForest"], X.columns, fi_path)
        print(f"  [저장] 핵심 인자 그래프 -> {fi_path}")
        print("\n  불량 예측 핵심 센서 Top 6:")
        for name, val in top_imp.head(6).items():
            print(f"    {name:15s}  {val:.4f}")


if __name__ == "__main__":
    main()
