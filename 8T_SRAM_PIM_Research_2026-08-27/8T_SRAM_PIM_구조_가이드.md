# 8T SRAM으로 만드는 PIM 구조: 개념, 회로 블록, 데이터 경로

> **핵심 요약:** PIM(Processing-in-Memory)은 데이터를 메모리에서 꺼내 멀리 있는 CPU/ALU로 옮긴 뒤 계산하는 대신, **메모리 어레이 내부 또는 바로 옆에서 연산**하는 구조입니다. 8T SRAM PIM에서는 보통 SRAM 셀에 **가중치(weight)** 를 저장하고, 입력을 read word-line에 인가하여 발생한 bit-line 변화들을 열(column)에서 합산해 벡터-행렬 곱(VMM) 또는 MAC의 일부를 수행합니다.

## 1. PIM 구조란 무엇인가?

일반적인 컴퓨팅에서는 SRAM/DRAM에서 데이터를 읽어 CPU·GPU의 연산기로 보내고, 결과를 다시 메모리에 저장합니다. 신경망의 행렬-벡터 곱처럼 데이터 이동량이 매우 큰 연산에서는 이 **데이터 이동 자체가 지연과 에너지의 큰 원인**이 됩니다. PIM은 메모리 셀 또는 메모리 주변 회로(periphery)를 연산 경로로 활용하여 이 이동을 줄이는 접근입니다.[1]

**CIM(Compute-in-Memory)** 은 통상 메모리 매크로 안에서 연산을 하는 PIM의 한 형태입니다. 따라서 논문에서는 PIM과 CIM을 거의 같은 맥락으로 쓰기도 하지만, 실무적으로는 아래처럼 이해하면 편합니다.

| 용어 | 의미 | 8T SRAM 예시 |
|---|---|---|
| **PIM** | 메모리 가까이 또는 메모리 내부에서 처리하는 넓은 개념 | SRAM 뱅크 옆에 popcount/ALU를 둠 |
| **CIM / IMC** | 메모리 **어레이와 bit-line/word-line 자체**를 연산에 이용 | 여러 셀의 RBL 방전량을 합산하여 dot product 생성 |
| **Near-memory** | 어레이 안은 아니지만 메모리 주변에 연산기를 둠 | SRAM bank별 작은 MAC/adder 배치 |

목표 연산은 보통 다음과 같습니다.

\[
y_j = \sum_{i=0}^{N-1} x_i w_{i,j}
\]

여기서 \(x_i\)는 입력 activation, \(w_{i,j}\)는 SRAM 셀에 저장한 weight, \(y_j\)는 한 열이 만드는 출력입니다. 이진 입력·이진 가중치라면 각 셀은 AND/XNOR 같은 1-bit 곱을 만들고, 같은 열의 bit-line에서 그 결과를 더해 **popcount 또는 dot product** 를 얻습니다.

---

## 2. 왜 8T SRAM을 쓰나?

### 2.1 기본 6T 셀과 8T 셀의 차이

일반적인 6T SRAM은 다음으로 구성됩니다.

- 교차결합 인버터 두 개: 저장 노드 \(Q, \overline{Q}\)를 유지하는 **4개 트랜지스터**
- write/read access transistor 두 개: word-line(WWL)에 의해 제어되는 **2개 트랜지스터**

6T에서는 저장, 읽기, 쓰기가 동일한 내부 노드와 bit-line을 공유합니다. 반면 가장 널리 쓰이는 **표준 8T 셀**은 6T 저장·쓰기 부분에 읽기 전용 포트 2개 트랜지스터를 더합니다. 즉, read word-line(RWL)과 read bit-line(RBL)을 사용해 저장 노드에 직접 접속하지 않고 읽습니다.

| 구분 | 6T SRAM | 8T SRAM(대표적 6T+2T) | PIM에서의 의미 |
|---|---|---|---|
| 저장 래치 | 4T | 4T | \(Q/\overline{Q}\)에 weight 저장 |
| 쓰기 포트 | 2T, WWL·WBL/WBLB | 2T, WWL·WBL/WBLB | weight programming |
| 읽기 포트 | write 포트 공유 | 별도 2T, RWL·RBL | read/compute와 write 분리 |
| 읽기 안정성 | read disturb에 민감할 수 있음 | 저장 노드와 RBL 경로가 분리되어 유리 | 다중 행 활성화·저전압 PIM에 유리 |

> **주의:** “8T SRAM PIM”은 하나의 고정된 회로도가 아닙니다. 가장 흔한 것은 6T 저장 셀 + 2T 분리 read port이지만, 논문에 따라 read transistor의 극성, RBL의 단일/차동 구성, 계산용 capacitor·switch의 추가 여부가 달라집니다. 따라서 **8T는 출발점이고, PIM 기능은 셀 구동법과 주변 회로까지 포함해 정의**됩니다.

8T는 read path가 write/storage path로부터 분리될 수 있으므로 read disturb를 줄이고 read 안정성을 높이기 쉽습니다. 이 특성 때문에 CIM 설계에서 분리된 RBL에 전하 또는 전류를 누적하는 방식이 많이 쓰입니다.[1] 표준 two-port 8T SRAM 매크로를 기반으로 multi-bit CIM을 구현한 실증 사례도 있습니다.[2]

### 2.2 대표적인 8T read 동작

아래는 흔한 **single-ended 8T read port**를 단순화한 설명입니다. RBL을 먼저 \(V_{DD}\)로 precharge하고, 저장값 \(Q=1\) 및 RWL=1이면 read stack이 RBL을 GND 쪽으로 방전합니다.

```text
                 write / storage section (6T)
              WBL ── access ── Q ── cross-coupled latch ── Qbar ── access ── WBLB
                              ↑
                         저장된 weight

                 decoupled read section (2T, 대표 예)
              RBL ── read device(Q가 gate 제어) ── read device(RWL 제어) ── GND

              Q=1 이고 RWL=1  → RBL 방전
              그 외             → RBL은 precharge 전압을 유지
```

이 read stack은 논리적으로 **stored weight AND input**을 만들 수 있습니다. 즉 \(Q=w\), RWL pulse=\(x\)라 보면 RBL의 방전 여부가 \(x\land w\)를 반영합니다. 여러 행의 RWL을 동시에 켜면 한 column RBL에 여러 셀의 방전 효과가 모여 합산 신호가 됩니다.

---

## 3. 전체 8T SRAM PIM 매크로 구조

가장 전형적인 구조는 **행에는 입력, 셀에는 가중치, 열에는 출력**을 대응시키는 것입니다. 예를 들어 \(N\)-원소 입력 벡터와 \(N\times M\) weight matrix를 계산하려면, 각 행은 입력 \(x_i\), 각 열은 출력 \(y_j\)에 대응합니다.

```text
                         ┌──────────── PIM macro ────────────┐
Host / DMA ── config ───▶│ controller / sequencer             │
                         │    │              │                │
weight load ────────────▶│ WWL decoder    WBL/WBLB drivers   │
input vector x[i] ──────▶│ RWL drivers / input encoder       │
                         │    │                               │
                         │    ▼                               │
                         │  ┌─────────────────────────────┐  │
                         │  │         8T SRAM array       │  │
                         │  │ row i: x[i] → RWL_i         │  │
                         │  │ cell(i,j): weight w[i,j]    │  │
                         │  └─────────────────────────────┘  │
                         │       │RBL_0 ... RBL_(M-1)         │
                         │       ▼                             │
                         │ precharge / clamp / column isolate │
                         │       ▼                             │
                         │ sense amp 또는 comparator/ADC      │
                         │       ▼                             │
                         │ popcount/accumulator/shift-add     │
                         │       ▼                             │
                         │ output register · requant · ReLU   │
                         └─────────────────────────────────────┘
```

실제 어레이 방향은 레이아웃에 따라 행과 열을 바꾸어 놓을 수 있습니다. 중요한 것은 **공유되는 bit-line 한 개가 하나의 출력 dot product를 누적한다**는 논리적 대응입니다.

---

## 4. 반드시 필요한 회로들

### 4.1 공통 필수 블록

아래 회로는 디지털형·아날로그/혼성신호형 8T SRAM PIM 모두에 사실상 필요합니다.

| 블록 | 주요 신호 | 역할 | 설계 핵심 |
|---|---|---|---|
| **8T SRAM cell array** | \(Q,\overline{Q}\), RWL, RBL, WWL, WBL/WBLB | weight 저장과 cell-level AND/read 생성 | row/column 수, read stack sizing, leakage |
| **write word-line decoder/driver** | WWL | weight를 쓸 행 선택 | 일반 SRAM write margin 확보 |
| **write bit-line driver** | WBL/WBLB | 0/1 weight를 셀에 기록 | 충분한 write current, column mux |
| **RWL decoder/driver 또는 input driver** | RWL | 입력을 행으로 broadcast, 필요 시 여러 행 동시 활성화 | pulse width, slew, simultaneous-row 수 |
| **RBL precharge 회로** | RBL, PCH | 매 연산 전 모든 RBL을 알려진 전압으로 초기화 | precharge 시간·에너지·균일성 |
| **column isolation / local bit-line** | RBL, GBL | 긴 bit-line의 RC 및 누설을 완화하고 bank를 분할 | large array에서는 매우 중요 |
| **readout 회로** | RBL, reference | bit-line의 작은 전압/전류 변화를 유효한 결과로 판정 | sense margin, offset, PVT 보정 |
| **controller / timing sequencer** | CLK, PRE, RWL, SAMPLE, CONV, RESET | write·precharge·compute·convert 순서를 제어 | non-overlap timing, mode 전환 |
| **output register 및 인터페이스** | result, valid | 결과를 저장·전송하고 다음 블록에 전달 | latency hiding, data formatting |

### 4.2 연산 방식에 따라 추가되는 회로

8T SRAM 어레이 아래에는 어떤 방식으로 RBL을 읽어 결과를 만들지에 따라 두 가지 큰 계열이 있습니다.

| 계열 | RBL에서 일어나는 일 | 필요한 후단 회로 | 장점 | 주된 부담 |
|---|---|---|---|---|
| **디지털 PIM** | 한 번에 1행 또는 제한된 행을 읽고 0/1을 판단 | sense amplifier, XOR/XNOR/AND, popcount counter 또는 adder tree | PVT 변화에 상대적으로 견고, ADC 불필요 | 병렬성 또는 cycle 수가 제한될 수 있음 |
| **아날로그/전하영역 CIM** | 여러 셀이 RBL을 충·방전하거나 전류를 합산 | sample/hold, comparator, reference generator, ADC, digital accumulator | 많은 행의 MAC을 한 번에 병렬 처리 | ADC 면적·전력, offset·nonlinearity·PVT 보정 |

#### (A) 디지털 PIM의 최소 구현

가장 구현 위험이 낮은 첫 버전은 **한 행씩 읽는 방식**입니다. RWL에 입력 \(x_i\)를 인가하고 RBL sense amplifier가 \(x_i\land w_{i,j}\)를 읽은 뒤, 각 열에 counter를 두어 누적합니다. 이는 다중 행 RBL voltage를 정밀 ADC로 해석하지 않아도 되므로 검증하기 쉽습니다.

```text
Precharge → RWL_i = x_i → RBL sense → bit result → column counter += bit result
                                                └→ i = 0...N-1 반복
```

이 경우 열마다 필요한 핵심 후단 회로는 **precharge + sense amplifier + 1-bit result register + popcount counter/adder**입니다. XNOR 기반 BNN을 만들려면 입력의 보수와 \(Q/\overline Q\)를 선택하거나, 두 번의 AND 결과를 합성하는 방식으로 구현할 수 있습니다.

#### (B) 아날로그/혼성신호 CIM의 고병렬 구현

더 빠른 구조는 여러 RWL을 동시에 활성화합니다. 각 셀의 read current 또는 RBL 충·방전이 합쳐져 아래처럼 column 결과가 됩니다.

\[
\Delta V_{\mathrm{RBL},j} \approx \frac{T_{\mathrm{eval}}}{C_{\mathrm{RBL}}}
\sum_i I_{\mathrm{cell}}(x_i,w_{i,j})
\]

이 \(\Delta V\)를 ADC가 digital code로 바꾸면 한 번의 evaluate 단계에서 여러 row의 결과를 얻습니다. 실제 8T CIM 문헌에서도 RBL의 충·방전 누적 결과를 comparator와 reference cell 기반 ADC로 양자화하거나,[1] bit-line charge sharing과 reference column을 이용해 ADC 비용을 줄이는 구성을 사용합니다.[3]

이 방식에 더해지는 회로는 다음과 같습니다.

| 추가 회로 | 역할 | 대표 선택지 |
|---|---|---|
| **sample-and-hold / evaluation capacitor** | RBL 결과를 샘플하고 누적 조건을 일정하게 유지 | intrinsic BL cap, explicit MOM/MIM cap |
| **reference generator / replica column** | ‘count=0, 1, …’에 대응하는 판정 기준 생성 | reference cell row, capacitor DAC, current DAC |
| **comparator 또는 sense-amplifier 기반 quantizer** | RBL과 reference 비교 | dynamic comparator, latch SA |
| **ADC** | 합산 아날로그 값을 다중 bit로 변환 | flash, SAR, ramp/counter, coarse-fine |
| **calibration 회로** | comparator offset, BL variation, 온도·전압 변화를 보정 | replica array, trim code, background calibration |
| **shift-and-add / digital accumulator** | bit-serial 입력·bit-sliced weight의 부분합을 결합 | carry-save adder, accumulator register |

---

## 5. 한 번의 PIM 연산은 어떻게 진행되나?

### 5.1 이진 AND-popcount 예

가중치 \(w_{i,j}\in\{0,1\}\)가 8T 셀의 \(Q\)에 저장되어 있고 입력 \(x_i\in\{0,1\}\)라고 가정합니다.

| 단계 | 동작 | 회로 상태 |
|---|---|---|
| 1. Weight write | 행/열을 선택해 \(w_{i,j}\) 저장 | WWL, WBL/WBLB driver 동작 |
| 2. Precharge | RBL을 \(V_{DD}\)로 초기화 | precharge PMOS on |
| 3. Input apply | \(x_i=1\)인 행의 RWL을 pulse | RWL driver 동작 |
| 4. Evaluate | \(x_i=1\)이고 \(w_{i,j}=1\)인 셀이 RBL을 방전 | read stack on, 열별 방전량 누적 |
| 5. Readout | RBL 변화에서 합산 결과 판정 | SA 또는 comparator/ADC |
| 6. Post-process | popcount, bit-slice partial sum, activation 수행 | counter/adder/activation unit |
| 7. Reset | 다음 vector를 위해 RBL과 state 초기화 | precharge, accumulator control |

다중 행을 동시에 켜는 아날로그형에서는 방전이 클수록 ‘1×1’ 항의 개수가 많다는 뜻이 됩니다. 단, **RBL 전압이 작아지는 비선형성, cell current 편차, 배선 RC** 때문에 활성화 행 수와 ADC resolution을 함께 정해야 합니다.

### 5.2 부호 있는 BNN(XNOR-popcount) 예

BNN의 weight와 activation이 \(\{-1,+1\}\)일 때는 곱을 XNOR-popcount로 바꿔 계산할 수 있습니다.

\[
\sum_i x_iw_i=2\cdot\mathrm{popcount}(\mathrm{XNOR}(x_i,w_i))-N
\]

8T 셀 하나가 자동으로 XNOR을 만드는 것은 아닙니다. 보통 \(Q\)와 \(\overline Q\) 중 어느 읽기 경로를 선택할지 입력에 따라 제어하거나, 두 개의 AND term을 읽어 XNOR을 구성합니다. 따라서 설계 명세에는 **‘셀 하나가 AND만 제공하는가, XNOR까지 직접 제공하는가’** 를 명확히 적어야 합니다.

---

## 6. 실제 설계에서 흔히 놓치는 핵심 회로와 이슈

| 이슈 | 왜 문제인가 | 필요한 대응 회로/방법 |
|---|---|---|
| **다중 행 활성화(MRA)** | 동시에 켜는 행 수가 늘면 RBL swing은 커지지만 비선형성·IR drop·누설도 커짐 | RWL pulse shaping, row grouping, local array 분할 |
| **ADC 비용** | 고분해능 ADC는 area/energy/latency를 크게 차지 | 저비트 ADC + quantization-aware training, reference column, coarse-fine ADC |
| **PVT 및 mismatch** | 셀 read current·comparator offset이 합산 code를 바꿈 | replica/reference column, offset calibration, ECC/guardband |
| **긴 RBL의 RC** | 대형 array에서 settling과 linearity가 나빠짐 | hierarchical BL, local sense, column mux/segmentation |
| **write와 compute mode 충돌** | weight update 중 compute를 하면 잘못된 RBL 상태 가능 | WWL/RWL non-overlap timing, mode FSM, isolation switch |
| **입력·가중치 다중 bit화** | 1-bit cell만으로 4–8 bit MAC이 바로 되지 않음 | bit-slicing, time-serial RWL pulse/PWM, shift-and-add |
| **정확도 관리** | 아날로그 readout의 잡음과 양자화가 모델 정확도에 반영됨 | hardware-aware training, clipping, calibration, redundancy |

특히 8T로 바꾼다고 해서 곧바로 정확한 multi-bit MAC이 보장되지는 않습니다. 논문 구현들은 RWL pulse 수, binary-weighted computation capacitor, charge-sharing, reference column 같은 추가 기법을 조합해 multi-bit input/weight/output을 지원합니다.[2] [3]

---

## 7. 권장 출발 구조

처음 회로 설계 또는 졸업 연구용 prototype이라면, 아래 순서가 현실적입니다.

| 단계 | 권장 구성 | 검증 목표 |
|---|---|---|
| **1단계: 8T SRAM 자체** | 6T latch + 2T decoupled read, 1R1W | SNM, write margin, read delay, leakage |
| **2단계: 1-bit compute** | RBL precharge + RWL=input + SA | 저장 bit AND 입력 bit가 정확히 read되는지 |
| **3단계: digital popcount** | 한 행씩 read + per-column counter | 정확한 binary dot product |
| **4단계: MRA** | 여러 RWL 동시 활성화 + RBL voltage 측정 | 방전량과 popcount의 선형성 |
| **5단계: mixed-signal readout** | comparator/ADC + reference column | multi-row dot product의 latency·energy 개선 |
| **6단계: multi-bit MAC** | bit-sliced weights, bit-serial inputs, shift-add | 실제 NN layer의 precision/accuracy |

### 최소 회로 체크리스트

**가장 단순한 8T SRAM PIM prototype**에 필요한 회로는 다음과 같이 정리할 수 있습니다.

1. 8T SRAM array와 전원/ground mesh.
2. WWL decoder, WBL/WBLB driver, write enable.
3. RWL decoder/driver 또는 입력 broadcast driver.
4. RBL precharge 회로와 (대형 array이면) column isolation.
5. RBL sense amplifier 또는 comparator.
6. 결과용 popcount counter/accumulator와 output register.
7. precharge–evaluate–sense–reset 순서를 만드는 clocked controller/FSM.
8. test mode, scan/DFT, replica/reference column 및 calibration 회로.

여기서 **ADC는 필수는 아닙니다.** 한 행씩 읽어서 digital counter로 합산하는 PIM이면 ADC 없이도 됩니다. 반대로 여러 row의 아날로그 bit-line 누적을 한 cycle에 digitize해 속도를 높이려면 ADC와 reference/calibration 블록이 사실상 핵심이 됩니다.

---

## 8. 결론

8T SRAM 기반 PIM의 본질은 단순히 “8T 셀을 넣는다”가 아니라, **분리된 read port를 계산 포트로 이용하고, 같은 column의 RBL에서 다수 셀의 결과를 읽어 합산**하는 데 있습니다. 셀은 weight를 저장하고 1-bit 곱/조건부 방전을 제공하며, 실제 PIM 매크로는 그 주변의 **RWL 입력 구동기, RBL precharge, sense/ADC, reference·calibration, accumulator, timing controller**가 완성합니다.

처음에는 `8T cell + precharge + RWL input + sense amp + digital counter` 형태의 디지털 PIM으로 기능을 검증한 뒤, 속도와 에너지 효율이 목표라면 `multi-row activation + RBL charge/current accumulation + ADC`의 혼성신호 CIM으로 확장하는 것이 가장 안전한 접근입니다.

## References

[1] Y. Kim et al., “[A Novel Ultra-Low Power 8T SRAM-Based Compute-in-Memory Design for Binary Neural Networks](https://www.mdpi.com/2079-9292/10/17/2181),” *Electronics*, 2021.

[2] M. E. Sinangil et al., “[A 7-nm Compute-in-Memory SRAM Macro Supporting Multi-Bit Input, Weight and Output](https://ieeexplore.ieee.org/abstract/document/9250531/),” *IEEE Journal of Solid-State Circuits*, 2021.

[3] J. Kim, K. Lee, and J. Park, “[A Charge Domain P-8T SRAM Compute-In-Memory with Low-Cost DAC/ADC Operation for 4-bit Input Processing](https://dl.acm.org/doi/10.1145/3531437.3539718),” *ISLPED*, 2022.

---

*작성: Manus AI · 회로도, SPICE netlist, 또는 Verilog-A 수준으로 확장할 때에는 목표 연산(AND/XNOR/MAC), input/weight/output bit precision, 공정 node, target array size를 먼저 고정해야 합니다.*
