# 아날로그 8T SRAM CIM의 Variation 문제와 보정 회로 기법

> **핵심 답변:** 아날로그 CIM의 정확도는 ‘SRAM 셀이 저장한 0/1’보다, 그 셀이 만들어 내는 **아날로그 전류·전하·전압을 얼마나 일정하게 합산하고 판독하느냐**에 의해 좌우됩니다. 따라서 변동 대응은 하나의 회로로 끝나지 않습니다. **(1) 8T의 분리 read port로 compute path를 안정화하고, (2) current-domain 대신 charge-domain 또는 differential path로 민감도를 낮추며, (3) replica/reference column과 offset·gain calibration으로 잔여 오차를 code-domain에서 보정하는 계층적 접근**이 일반적입니다.

## 1. 먼저 구분할 것: Process variation, PVT, noise

엄밀히 말해 **process variation**은 제조 공정에서 생기는 트랜지스터 \(V_{TH}\), 이동도 \(\mu\), 채널 길이/폭, 저항, capacitor 값 등의 편차입니다. 회로 설계에서는 이것을 공급전압과 온도 변화까지 합친 **PVT(Process–Voltage–Temperature)** 로 평가하는 경우가 많습니다. 잡음, 전하 주입, clock jitter, aging은 공정 변동 그 자체는 아니지만 최종 MAC 오차에 같은 방식으로 더해지므로 함께 관리해야 합니다.

| 구분 | 시간·공간 특성 | 대표적인 원인 | CIM 출력에 나타나는 형태 |
|---|---|---|---|
| **Global process corner** | die/wafer 전체에서 비교적 공통 | FF/SS/TT, \(V_{TH}\)·\(\mu\)의 전역 변화 | 모든 column의 gain, delay, common-mode 변화 |
| **Local mismatch** | cell·column마다 랜덤 | random \(V_{TH}\), \(\beta\) mismatch, capacitor mismatch | column마다 다른 offset/gain, code spread |
| **Voltage variation** | 시간에 따라 변함 | IR drop, supply ripple, reference droop | input/DAC/bit-line/ADC의 동시 gain error |
| **Temperature variation** | 공간·시간에 따라 변함 | self-heating, ambient temperature | mobility·leakage·comparator delay 변화 |
| **Dynamic noise / parasitic** | 연산마다 달라짐 | thermal/flicker noise, charge injection, coupling, clock jitter | 랜덤 code jitter, nonlinearity, settling failure |

아날로그 CIM은 다수의 SRAM 행을 동시에 활성화하여 bit-line에서 MAC을 만들기 때문에, 각 cell의 아주 작은 편차도 합산 결과의 offset·gain·비선형성으로 전파됩니다. 특히 current-domain CIM은 MOSFET의 비선형 I–V 특성과 PVT에 민감한 read current 때문에 변동 문제가 두드러집니다.[1] 반면 charge-domain은 capacitor의 전하 재분배를 활용해 선형성과 PVT 견고성을 개선할 수 있으나, capacitor 비율 오차와 switch non-ideality는 여전히 남습니다.[1] [2]

---

## 2. Variation은 MAC 결과에 어떻게 들어오나?

current-domain 8T CIM을 간단히 쓰면, \(j\)번째 column의 bit-line 전압 변화는 다음과 같이 근사할 수 있습니다.

\[
\Delta V_{\mathrm{RBL},j}
\approx \frac{T_{\mathrm{eval}}}{C_{\mathrm{RBL},j}}
\sum_{i\in\mathrm{active}} I_{\mathrm{cell},i,j}(x_i,w_{i,j})
\]

이상적으로는 활성화된 cell 수(popcount)에 따라 \(\Delta V\)가 일정한 간격으로 증가해야 합니다. 실제로는 \(I_{\mathrm{cell}}\), \(C_{\mathrm{RBL}}\), evaluate time, supply, 온도, comparator threshold가 모두 달라져서 출력 code가 흔들립니다.

\[
D_{j}=\mathrm{ADC}\{G_j\cdot S_j+O_j+\varepsilon_{\mathrm{NL},j}+n_j\}
\]

여기서 \(S_j\)는 이상적인 dot product, \(G_j\)는 column gain, \(O_j\)는 offset, \(\varepsilon_{\mathrm{NL},j}\)는 입력 code에 따라 달라지는 비선형 오차, \(n_j\)는 noise입니다. 회로 보정의 목적은 **오차가 생기지 않게 하는 것**과 **생긴 오차를 측정해 제거하는 것**으로 나뉩니다.

```text
x[i], w[i,j]
     │
     ▼
[8T read cell] ── cell current/charge mismatch ──┐
[8T read cell] ── cell current/charge mismatch ──┼─► RBL/V_MAC
[8T read cell] ── cell current/charge mismatch ──┘       │
                                             BL RC, parasitic C,
                                             IR drop, leakage
                                                         ▼
                              reference / comparator offset / ADC INL
                                                         ▼
                                                    digital code
```

---

## 3. 블록별로 발생하는 대표 오차

### 3.1 8T cell 및 read path

8T SRAM은 일반적으로 6T 저장·write 부분에 2T read port를 추가합니다. read path가 저장 노드·write path와 분리되므로 multi-row activation에서 read disturb를 줄이고 compute port의 동작을 분리하기에 유리합니다.[3] 그러나 read stack의 \(V_{TH}\), \(W/L\), body effect, mobility가 cell마다 다르면 같은 ‘1’ weight라도 방전 전류가 달라집니다.

| 오차 원인 | MAC에 미치는 영향 | 8T에서 특히 보는 항목 |
|---|---|---|
| Read NMOS \(V_{TH}\), \(\beta\) mismatch | cell current의 랜덤 분산 → popcount level overlap | 두 read transistor stack의 mismatch와 source degeneration |
| RWL amplitude/pulse-width 편차 | \(T_{\mathrm{eval}}\) 또는 on-current 변동 | row driver slew, far-end WL droop |
| Leakage | 작은 MAC 결과에서 baseline drift | off-cell read leakage, 고온 leakage |
| Read-path data dependence | ‘1’ cell 수가 많을수록 BL slope가 비선형 | RBL의 voltage-dependent discharge current |
| Multi-row activation | 큰 throughput 대신 읽기 조건 악화 | shared RBL의 IR drop, simultaneous switching |

### 3.2 Bit-line·배선·누산 노드

긴 RBL은 distributed RC network이며, cell을 많이 연결할수록 \(C_{\mathrm{RBL}}\)과 저항성 전압 강하가 커집니다. 동쪽과 서쪽 cell이 같은 값을 저장해도 readout endpoint까지의 거리 차이로 기여도가 달라질 수 있습니다. RBL precharge 전압의 column-to-column 불일치, precharge device mismatch, sense 시점의 settling 부족도 offset을 만듭니다.

특히 current-domain에서는 RBL 전압이 방전될수록 transistor의 \(V_{DS}\) 조건이 바뀌어 cell current가 일정하지 않으므로, 이상적인 ‘셀 수에 비례하는 방전량’이 무너집니다. 큰 multi-row activation(MRA)은 dynamic range를 키우지만 이 비선형성·IR drop·supply droop도 확대합니다.[1]

### 3.3 Charge-domain의 고유 오차

charge-domain CIM은 전류를 긴 시간 흘려 누적하기보다, capacitor에 저장한 전하를 switch로 연결해 전압을 형성합니다. capacitor 비율이 잘 맞으면 transistor의 절대 \(V_{TH}\)·\(\mu\)에 대한 민감도를 줄일 수 있어 current-domain보다 variation tolerance와 선형성에서 유리한 경우가 많습니다.[1] [2]

하지만 ‘charge-domain이면 variation-free’는 아닙니다.

| charge-domain 오차 | 원인 | 결과 |
|---|---|---|
| **Capacitor ratio mismatch** | MOM/MIM capacitor 면적·fringe·metal density 차이 | DAC gain/INL, weighted sum 오차 |
| **Parasitic capacitance** | switch gate, routing, comparator input, coupling | 기대한 charge division ratio 변화 |
| **Charge injection / clock feedthrough** | MOS switch off 시 channel charge와 clock coupling | code-dependent offset, small-signal 오류 |
| **Finite switch resistance** | input voltage에 따른 \(R_{on}\), settling time 부족 | incomplete charge transfer, nonlinearity |
| **Capacitor leakage** | 고온·긴 hold time | sampled MAC value droop |

가중 capacitor \(C,2C,4C,\ldots\)를 작은 면적에 만들면 matching이 어려워져 shift-and-add의 비선형성이 커질 수 있습니다. 동일한 local capacitor를 DAC·MAC·shift-and-add·ADC에서 재사용하고, 균일한 capacitor 다수를 charge-sharing하는 방식은 이러한 matching 및 parasitic 영향을 줄이려는 대표적 접근입니다.[4]

### 3.4 DAC, comparator, ADC

입력 DAC와 readout ADC는 어레이가 잘 계산한 값을 왜곡할 수 있는 ‘양 끝단’입니다. current-steering DAC는 current source mismatch와 \(V_{DD}\), temperature 변화에 민감하며 보통 calibration 부담을 수반합니다.[4] Comparator는 input-referred offset, kickback, metastability, noise를 만들고, ADC reference ladder/C-DAC mismatch와 timing 오차는 DNL/INL로 나타납니다.

| 주변 회로 | 대표 variation 문제 | 관측 지표 |
|---|---|---|
| Input DAC | resistor/current/cap ratio error, buffer gain error | DAC INL/DNL, input gain error |
| Comparator / SA | transistor mismatch, offset, kickback | decision threshold shift, random code error |
| Flash ADC | comparator offset, reference mismatch | bubble error, DNL/INL, 큰 면적 |
| SAR ADC | C-DAC mismatch, comparator offset, settling | DNL/INL, conversion latency |
| Time-domain ADC/TDC | delay-cell PVT, clock jitter | time-to-code gain drift |

---

## 4. 해결 기법: ‘민감도 저감’과 ‘측정 후 보정’을 함께 쓴다

### 4.1 1차 방어: cell과 compute-domain 선택

| 회로 기법 | 해결하려는 문제 | 장점 | 비용·주의점 |
|---|---|---|---|
| **8T의 decoupled read port** | 6T 공유 port의 read disturb·storage coupling | compute path 격리, MRA 안정성 향상 | 6T보다 cell area 증가; read current mismatch 자체는 남음 |
| **Differential RBL/RBLB** | 공통 전원·온도·precharge 변화 | common-mode noise와 offset 일부 상쇄 | 2배에 가까운 routing/SA 비용, path matching 필요 |
| **Charge-domain MAC** | current-domain의 \(I\)–\(V\) 비선형·\(V_{TH}\) 민감성 | capacitor ratio 기반의 선형성, PVT 견고성 개선 | capacitor·switch parasitic 및 charge injection 관리 필요 |
| **Local array / hierarchical BL** | 긴 bit-line RC, position-dependent error | BL capacitance·IR drop·settling 완화 | global partial-sum 결합 회로 필요 |
| **제한된 MRA와 row grouping** | 과도한 BL swing, saturation, supply droop | linear operating region 유지 | cycle 수 증가 가능 |
| **Dummy/replica BL** | precharge·sense의 불균형 | 실제 BL과 유사한 common-mode 조건 확보 | 면적·전력 오버헤드 |

**current-domain 구조**를 반드시 쓴다면, RBL swing을 작게 제한하고 evaluate time을 짧고 일정하게 하여 transistor가 크게 포화·비선형 영역으로 이동하지 않게 하는 것이 우선입니다. 반대로 높은 정확도가 중요한 multi-bit MAC이면, capacitor 비율과 규칙적 레이아웃을 확보할 수 있는 **charge-domain**이 일반적으로 더 유리한 출발점입니다.[1] [2]

### 4.2 Reference / replica column: 가장 실용적인 보정 기준

**reference column**은 알고 있는 MAC 값에 해당하는 기준 전압·전하를 실제 array와 거의 같은 회로 경로에서 생성하는 column입니다. ideal voltage source로 만든 reference보다 실제 cell, BL, precharge, 온도의 공통 변화를 함께 겪으므로 tracking이 더 좋습니다.

```text
                       같은 precharge / RWL timing / BL 환경
 Compute column:   SRAM cells ──────► V_MAC,j ───┐
                                                 ├─► comparator / ADC
 Reference column: replica cells ─► V_REF[k] ────┘
                               (k = 0,1,2,... count level)
```

| reference 방식 | 원리 | 적합한 용도 |
|---|---|---|
| **Replica cell/column** | 실제 compute cell과 같은 read path를 복제 | cell current·temperature·supply tracking |
| **Reference row with known weights** | 0, midscale, full-scale 등 known pattern 저장 | offset/gain anchor 생성 |
| **ADC reference cell array** | 별도 SRAM cell 수를 달리 activate하여 reference level sweep | low-cost column ADC, count-to-code 변환 |
| **Dummy column / dummy BL** | data에는 쓰지 않는 매칭 BL 유지 | precharge/charge injection/common-mode 보상 |
| **Replica bias loop** | replica에서 bias를 만들고 main path에 feedback | global PVT tracking |

실제 65 nm 8T SRAM CIM 매크로 사례는 각 column neuron에 dot-product cell 64개 외에 **ADC reference용 replica bitcell 32개와 offset calibration용 bitcell 32개**를 두고, reference level을 sweep하여 differential RBL 전압을 digitize했습니다. 이 설계는 offset calibration 후 DNL 및 INL을 각각 약 ±0.3 LSB 이내로 보고했습니다.[3] 따라서 reference/calibration cell을 단순한 부가 기능이 아니라 **아날로그 CIM의 핵심 주변 회로**로 보는 것이 맞습니다.

### 4.3 Offset calibration: ‘0 입력’ 또는 ‘zero MAC’에서 기준점을 측정

가장 먼저 필요한 보정은 offset입니다. weight=0 또는 input=0처럼 이상적 출력이 알려진 조건에서 raw code를 읽으면, 그 값은 precharge mismatch, comparator offset, BL leakage 등을 포함한 \(O_j\)의 측정치가 됩니다.

\[
D_{\mathrm{corr},j}=D_{\mathrm{raw},j}-D_{\mathrm{off},j}
\]

| 구현 방식 | 회로 동작 | 장점 | 한계 |
|---|---|---|---|
| **Foreground offset calibration** | 시작 시 zero-MAC을 읽어 SRAM/register에 \(D_{off}\) 저장 | 단순하고 정확 | calibration 동안 compute 중단 |
| **Comparator auto-zero** | sampling phase에 comparator 자체 offset을 저장·상쇄 | ADC 입력단에서 offset 저감 | switch noise·추가 capacitor 필요 |
| **Correlated double sampling (CDS)** | baseline과 signal을 연속 샘플해 차분 | slow offset·flicker noise 완화 | 2회 sampling 및 hold accuracy 필요 |
| **Offset replica cell** | offset만 만들도록 구성한 replica cell/column 사용 | main path tracking 우수 | replica의 mismatch는 완전히 0이 아님 |

foreground 방식은 전원 인가 시, layer 변경 시, 또는 온도가 크게 바뀔 때 실행합니다. 온도 변화가 빠르거나 장시간 연속 동작한다면 idle cycle에 reference를 측정하는 **background calibration**을 추가할 수 있습니다.

### 4.4 Gain 및 비선형 보정: two-point, multi-point, LUT

offset만 빼도 ‘1 count당 voltage step’이 column마다 다르면 출력은 계속 틀립니다. 따라서 0과 full-scale 혹은 두 개 이상의 known pattern을 측정해 gain을 구합니다.

\[
\alpha_j=\frac{D_{\mathrm{ideal,H}}-D_{\mathrm{ideal,L}}}
{D_{\mathrm{raw,H},j}-D_{\mathrm{raw,L},j}},\qquad
D_{\mathrm{corr},j}=\alpha_j\left(D_{\mathrm{raw},j}-D_{\mathrm{off},j}\right)
\]

| 보정 수준 | 저장할 calibration data | 잡을 수 있는 오차 | 권장 상황 |
|---|---|---|---|
| **1-point** | offset 1개/column | 일정한 baseline shift | low-resolution BNN, 면적 최소화 |
| **2-point** | offset + gain 1개/column | affine error | 가장 실용적인 기본값 |
| **Multi-point** | code별 LUT 또는 piecewise slope | BL saturation, capacitor/DAC INL | 5 bit 이상 정밀 MAC, 심한 비선형 |
| **Adaptive LUT** | 온도·VDD bin별 LUT | 환경 의존 비선형 | wide PVT range, 고정밀 목표 |

중요한 점은 **local mismatch는 per-column 보정**이 필요하고, die 전체의 temperature/VDD 변화는 shared reference 또는 global scale 보정으로도 상당 부분 추적할 수 있다는 점입니다. 모든 cell을 개별 보정하는 것은 면적과 test time이 과도하므로 보통 column 또는 local-array 단위가 비용·효과 균형점이 됩니다.

### 4.5 ADC 중심 보정

아날로그 CIM에서 ADC는 단순한 후단 변환기가 아니라 전체 MAC 정밀도의 일부입니다. 좋은 ADC라도 reference가 compute path를 추적하지 못하면 효과가 제한됩니다.

| 기법 | 적용 위치 | 효과 |
|---|---|---|
| **Comparator offset trim/auto-zero** | flash/SAR comparator | decision threshold mismatch 감소 |
| **Coarse–fine ADC** | flash 또는 hybrid ADC | comparator 수·input loading을 줄이면서 speed 유지 |
| **Reference-column-based ADC** | SRAM array + ADC | PVT를 겪은 in-array 기준으로 conversion |
| **ADC input sampling capacitor 공유** | charge-domain array | sampling mismatch와 buffer overhead 저감 |
| **Redundant comparison / digital error correction** | SAR/flash encoder | comparator metastability·bubble error 완화 |
| **Power-gated dynamic comparator** | ADC front end | static bias variation·전력 저감, 단 timing 재검증 필요 |

reference column을 이용한 coarse-fine flash ADC와 charge-sharing은 8T CIM에서 ADC reference 생성·DAC/ADC 비용을 줄이면서 variation-tolerant, linear MAC을 목표로 사용된 사례가 있습니다.[2]

### 4.6 Layout, 배선, 전원은 ‘보정 이전’에 해결해야 한다

보정 회로가 있다고 해서 layout mismatch를 방치하면 안 됩니다. calibration range를 벗어난 오차나 랜덤 noise는 나중에 되돌릴 수 없습니다.

| 물리 설계 기법 | 대상 | 이유 |
|---|---|---|
| **Common-centroid / interdigitation** | capacitor array, differential pair, reference/compute cell | gradient 및 systematic mismatch 완화 |
| **같은 방향·대칭 routing** | RBL/RBLB, compute/reference BL | RC·coupling의 차이를 축소 |
| **Dummy device/capacitor** | array edge | edge effect와 metal-density 차이 완화 |
| **Shielding 및 충분한 spacing** | sensitive BL, comparator input, reference | digital clock/control coupling 저감 |
| **Local decap + clean reference** | DAC, comparator, ADC, precharge | supply droop가 code error로 바뀌는 것을 방지 |
| **Local array partition** | 대규모 SRAM CIM | BL RC·IR drop 감소, calibration granularity 향상 |

---

## 5. 8T SRAM 아날로그 CIM에 권장하는 실전 조합

아래는 ‘정확도도 보고 싶은 8T SRAM CIM prototype’에 대한 현실적인 우선순위입니다. 목표 정밀도·공정·array 크기에 따라 구체 회로는 달라지지만, 순서는 대체로 유지됩니다.

| 우선순위 | 권장 선택 | 해결하는 핵심 문제 |
|---|---|---|
| 1 | **8T decoupled read port + separate RWL/RBL** | read disturb와 storage/compute coupling |
| 2 | **작은 local sub-array + hierarchical BL** | BL RC, position error, MRA scale 한계 |
| 3 | **differential readout 또는 matched reference path** | common-mode PVT, precharge mismatch |
| 4 | **charge-domain accumulation** 또는 small-swing current-domain | transistor I–V 비선형성, gain variation |
| 5 | **replica/reference column** | 실제 array PVT를 ADC reference까지 tracking |
| 6 | **column-wise offset calibration** | comparator/BL의 static offset |
| 7 | **two-point gain calibration** | column별 read current/capacitance 차이 |
| 8 | **ADC auto-zero 또는 comparator trim** | ADC threshold mismatch |
| 9 | **hardware-aware quantization/training** | 남은 random/nonlinear error의 모델 정확도 영향 |

특히 1–5 bit 정도의 low-resolution neural inference에서는 ‘매우 높은 해상도의 ADC’보다 **잘 맞는 reference, offset/gain calibration, 그리고 모델이 인지한 quantization**이 더 효율적인 경우가 많습니다. 문헌의 8T column-ADC 사례도 reference cell 및 offset calibration을 array 내부에 포함시키는 방향을 취합니다.[3]

---

## 6. 검증 방법: SPICE에서 반드시 분리해 볼 항목

회로가 정확해 보이는 TT, 27 °C, nominal \(V_{DD}\) 결과만으로는 아날로그 CIM을 평가할 수 없습니다. 다음 순서로 검증해야 원인을 분리할 수 있습니다.

| 단계 | 시뮬레이션/측정 | 확인할 지표 |
|---|---|---|
| 1 | **단일 8T cell Monte Carlo** | read current mean/σ, leakage, RWL pulse sensitivity |
| 2 | **소형 column Monte Carlo** | count별 \(\Delta V_{RBL}\) 분포, level overlap, monotonicity |
| 3 | **PVT corner sweep** | SS/TT/FF × \(V_{DD}\) × temperature에서 gain/offset |
| 4 | **Post-layout extracted simulation** | RBL RC, parasitic C, coupling, settling time |
| 5 | **ADC 포함 end-to-end** | DNL, INL, SNDR/SQNR, offset calibration 전후 비교 |
| 6 | **Array-level random mapping** | data pattern·cell 위치에 따른 code error |
| 7 | **DNN inference co-simulation** | accuracy drop, layer별 sensitivity, calibration 주기 |

### 권장 Monte Carlo 변수

```text
Cell/read path:     VTH mismatch, W/L variation, mobility, RBL leakage
Interconnect:       RBL/WWL resistance, coupling C, precharge device mismatch
Charge domain:      unit-C mismatch, parasitic C, switch R_on, charge injection
ADC:                comparator offset, reference/C-DAC mismatch, clock jitter
Environment:        global corner, VDD droop/ripple, temperature gradient
```

결과는 평균값만 보지 말고 **code histogram의 겹침**, worst-case INL, 3σ/6σ yield, calibration 전후의 SQNR 및 inference accuracy까지 비교해야 합니다. 두 가지 error가 평균적으로 상쇄되더라도 특정 column·특정 input pattern에서 decision boundary를 넘으면 DNN 정확도가 떨어질 수 있습니다.

---

## 7. 결론

아날로그 8T SRAM CIM에서 variation은 크게 **cell read current/charge의 mismatch**, **bit-line·capacitor·switch의 비이상성**, **DAC·comparator·ADC의 offset 및 reference error**, **전압·온도·배선 RC**로 구성됩니다. 8T는 read path를 분리해 read disturb와 compute/storage coupling을 낮추는 좋은 기반이지만, 아날로그 MAC 정확도를 자동으로 보장하지는 않습니다.

가장 효과적인 해법은 다음 세 층을 함께 적용하는 것입니다.

1. **구조적 저감:** 8T decoupled read, differential/matched path, local array, small-swing 또는 charge-domain MAC.
2. **추적 기준:** 실제 compute path와 유사한 **replica/reference column**과 안정적인 precharge/reference 설계.
3. **디지털 보정:** per-column **offset calibration**, two-point gain correction, 필요 시 LUT 기반 nonlinearity 보정과 hardware-aware training.

즉, 설계 관점에서 가장 중요한 질문은 “variation을 없앨 수 있는가?”가 아니라 **“어떤 오차는 공통 경로로 상쇄하고, 어떤 오차는 reference로 추적하며, 남는 오차를 어느 단위(column/local array)에서 몇 bit의 calibration으로 보정할 것인가?”** 입니다.

## References

[1] Z. Chen et al., “[PICO-RAM: A PVT-Insensitive Analog Compute-In-Memory SRAM Macro with In-Situ Multi-Bit Charge Computing and 6T Thin-Cell-Compatible Layout](https://arxiv.org/html/2407.12829v1),” 2024.

[2] J. Kim, K. Lee, and J. Park, “[A Charge Domain P-8T SRAM Compute-In-Memory with Low-Cost DAC/ADC Operation for 4-bit Input Processing](https://arxiv.org/abs/2211.16008),” *ISLPED*, 2022.

[3] C. Yu et al., “[A 65-nm 8T SRAM Compute-in-Memory Macro with Column ADCs for Processing Neural Networks](https://dr.ntu.edu.sg/entities/publication/090b9d7a-a64e-4699-b5ed-f900faf52db2),” *IEEE Journal of Solid-State Circuits*, 2022.

[4] S. Lee and Y. Kim, “[Charge-Domain Static Random Access Memory-Based In-Memory Computing with Low-Cost Multiply-and-Accumulate Operation and Energy-Efficient 7-Bit Hybrid Analog-to-Digital Converter](https://www.mdpi.com/2079-9292/13/3/666),” *Electronics*, 2024.

---

*작성: Manus AI · 이 문서는 8T SRAM 기반 아날로그 CIM을 중심으로 설명했지만, reference/replica·offset/gain calibration·layout matching의 원칙은 다른 SRAM CIM에도 동일하게 적용됩니다.*
