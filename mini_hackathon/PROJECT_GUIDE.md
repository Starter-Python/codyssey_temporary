# 📂 mini_hackathon 프로젝트 상세 설명

> SK하이닉스 AI 해커톤 2026 대비용 미니 시뮬레이션 프로젝트
> "반도체 공정 센서 데이터로 웨이퍼 불량을 예측하고 원인을 찾는다"

---

## 1. 프로젝트 개요

반도체 제조 공정에서 발생하는 **웨이퍼 불량(수율 하락)** 문제를,
공정 센서 데이터를 이용해 머신러닝으로 예측·분석하는 전 과정을 담았다.
실제 해커톤 본선("반도체 현장의 고민을 AI로 해결")을 가정한 연습 프로젝트다.

**핵심 질문 3가지**
1. 센서 값으로 불량 웨이퍼를 예측할 수 있는가? (분류)
2. 어떤 공정 변수가 불량을 유발하는가? (설명력)
3. 라벨이 없어도 이상 로트를 찾을 수 있는가? (이상탐지)

---

## 2. 파일별 상세 설명

### 📄 `README.md`
프로젝트의 문제 정의, 접근 전략, 폴더 구조, 해커톤 관점 포인트를 담은 개요 문서.

### 📄 `src/generate_data.py` — 데이터 생성기
실제 SECOM(반도체 공정) 데이터셋의 특성을 모사한 **합성 데이터**를 생성한다.
- **2,000개 웨이퍼 로트 × 40개 센서** 생성
- 센서는 5개 그룹(온도/압력/가스유량/전력/진동)으로 명명
- **40개 중 6개 센서만** 실제로 불량과 연관 (나머지는 노이즈) → 모델이 진짜 원인을 찾아내는지 검증 가능
- **클래스 불균형**(불량률 약 25%)과 **결측치**(약 2%)를 의도적으로 주입 → 실제 현장과 유사
- 실행 시 `data/secom_like.csv` 저장, 정답 센서 목록도 출력

```bash
python src/generate_data.py
```

### 📄 `src/train.py` — 수율 예측 모델 학습·평가
- **전처리 파이프라인**: 결측치 중앙값 대치(SimpleImputer) → 표준화(StandardScaler)
- **모델 2종 비교**: LogisticRegression, RandomForest (둘 다 `class_weight="balanced"`로 불균형 대응)
- **평가지표**: ROC-AUC, PR-AUC, F1, Confusion Matrix, classification report
  - 불균형 데이터라 accuracy가 아닌 **ROC-AUC / Recall** 중심 평가
- **결과물 저장**:
  - `outputs/pr_curve.png` — Precision-Recall 곡선 (두 모델 비교)
  - `outputs/feature_importance.png` — 불량 예측 핵심 센서 Top 15
- 콘솔에 불량 핵심 센서 Top 6 출력 → 데이터에 심은 정답 센서와 일치 확인

```bash
python src/train.py
```

### 📄 `src/anomaly.py` — 비지도 이상탐지
- **IsolationForest**로 라벨 없이 이상(비정상) 로트를 탐지
- 실제 불량 라벨과 비교해 탐지 성능(ROC-AUC) 확인
- 목적: "라벨이 없거나 적을 때"의 대안 접근을 실험하고, 지도학습과 성능을 비교

```bash
python src/anomaly.py
```

### 📁 `data/secom_like.csv`
생성된 데이터셋. 40개 센서 컬럼 + `target`(1=불량, 0=양품).

### 📁 `outputs/`
- `feature_importance.png` — 어떤 센서가 불량에 중요한지 시각화
- `pr_curve.png` — 두 모델의 Precision-Recall 성능 비교

---

## 3. 실행 결과 요약

| 모델 | ROC-AUC | 불량 Recall | 불량 Precision |
|------|---------|-------------|----------------|
| LogisticRegression | 0.893 | 0.780 | 0.596 |
| RandomForest | 0.875 | 0.559 | 0.717 |

**핵심 성과**: 모델이 뽑은 불량 핵심 센서 Top 6가
데이터 생성 시 심어둔 실제 정답 센서 6개와 **정확히 일치** →
모델이 "불량의 진짜 원인"을 제대로 찾아냈음을 검증.

---

## 4. 실행 환경

- Python 3.12
- 필요 패키지: `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `seaborn`

```bash
pip install numpy pandas scikit-learn matplotlib seaborn

# 순서대로 실행
python src/generate_data.py   # 1) 데이터 생성
python src/train.py           # 2) 모델 학습·평가·시각화
python src/anomaly.py         # 3) 이상탐지 실험
```

---

## 5. 이 프로젝트에서 배우는 해커톤 실전 감각

1. **불균형 데이터**에선 accuracy가 아니라 ROC-AUC / Recall / PR-AUC로 평가
2. **비즈니스 트레이드오프**: 불량 놓치지 않기(Recall) vs 오탐 줄이기(Precision)
3. **설명 가능성**: 성능뿐 아니라 "왜 불량인가"를 센서 중요도로 설명
4. **baseline → 고도화** 순서로 접근하는 방법론
5. **지도 vs 비지도**: 라벨 유무에 따른 접근법과 성능 차이
