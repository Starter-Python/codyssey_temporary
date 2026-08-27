# 8T SRAM 기반 PIM/IMC 공개 자료: 회로도·레이아웃 검증 목록

## 결론

요청하신 조건을 기준으로 공개 자료를 실제 파일 단위로 확인했습니다. **바로 재사용 가능한 8T PIM 회로도와 SPICE netlist**가 필요한 경우에는 `rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon`이 가장 직접적인 출발점입니다. 이는 8T SRAM 두 셀의 dedicated read bit-line을 이용하여 NOR/OR를 수행하는 **logic-PIM** 회로도와 netlist를 제공합니다.[1]

다만, **“8T PIM + xschem 원본(.sch) + Magic 원본(.mag) + transistor-level physical layout”** 네 조건을 동시에 만족하는 공개 저장소는 이번 검증 범위에서 찾지 못했습니다. `msvsdpim`은 README에 xschem·Magic·Sky130 환경을 명시하고 PIM 관련 GDS/DEF output도 제공하지만, 실제 8T PIM의 xschem schematic과 Magic `.mag` 원본은 포함하지 않았습니다.[5] 따라서 이 저장소를 완성된 cell-level 재사용 파일로 과장해서 추천하지 않았습니다.

| 우선순위 | 자료 | PIM/IMC 형태 | 회로도 | Physical layout | 사용 도구 | 추천 용도 |
|---:|---|---|---|---|---|---|
| **1** | Rahul Tiwari, `Mixed-Signal-Circuit-Design-and-SImulation-Marathon` | 8T SRAM **logic-PIM**: RBL discharge 기반 NOR/OR | **원본 `.sch` + `.cir`** | 없음 | eSim·ngspice | 회로를 직접 열고 8T read-compute 동작을 수정·시뮬레이션 |
| **2** | Abhash Kumar, `8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration` | 8T SRAM **in-memory DAC** | **원본 `.sch` + `.cir`**, schematic PDF | 없음 | eSim·Sky130 | 아날로그 PIM 입력 DAC/weighted-current 아이디어 참고 |
| **3** | Rajput et al., SDP8T-IMC TechRxiv preprint | 8T SRAM **IMBC**·BCAM, Virtual-VSS | 논문 figure | **논문 Figure 11 layout** | 65 nm UMC, EDA source 미공개 | cell topology와 layout figure를 함께 참조 |
| **4** | Shin & Jo, MDPI *Applied Sciences* 논문 | 8T SRAM **CIM** | bit-cell·write driver·body-bias schematic figure | figure 미제공 | source 미공개 | 8T CIM macro/periphery 회로 설명 참고 |
| **5** | `msvsdpim`의 IMC-gen | SRAM logic physical design | transistor-level schematic 없음 | **GDS·LEF·DEF** 있음 | OpenFASOC; README에 xschem·Magic 환경 설명 | PIM 주변 논리의 digital physical-design flow 참고 |

## 1. 최우선 GitHub 자료: 8T SRAM logic-PIM 회로도와 netlist

**[rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon][1]** 는 제목과 README가 모두 “In Memory Logic Operations with 8T SRAM cells”를 명시하는 공개 저장소입니다. 여기서는 두 8T SRAM cell에 operand를 기록하고, precharge한 RBL capacitor의 방전을 이용해 NOR를 만들며, CMOS inverter를 더해 OR 연산을 얻습니다. 즉, AI용 multi-bit analog MAC보다는 **in-memory Boolean computation(IMBC)** 을 공부하기에 맞는 PIM 설계입니다.[1]

| 확인 항목 | 검증 결과 | 바로 열 파일 |
|---|---|---|
| Top-level schematic | **있음**. eSim 형식의 `LOGICwithSRAM.sch` | [`LOGICwithSRAM.sch`][1a] |
| SPICE netlist | **있음**. 시뮬레이션용 `LOGICwithSRAM.cir` | [`LOGICwithSRAM.cir`][1b] |
| 결과 보고서 | **있음**. 8T PIM 회로 schematic과 동작을 1페이지로 요약 | [`FinalReport.pdf`][1c] |
| Layout source | **없음**. `.mag`, GDSII, LEF/DEF를 확인하지 못함 | 해당 없음 |
| 라이선스 | 저장소에 **GPL-3.0** 전문이 포함됨 | [`LICENSE`][1d] |

이 저장소는 **회로도 필수**라는 조건에는 가장 잘 맞습니다. 그러나 eSim `.sch`는 xschem `.sch`와 호환되는 파일 포맷이 아니므로, xschem에서 그대로 열기보다는 회로도 이미지/netlist를 보고 **xschem에서 다시 capture**하는 방식이 현실적입니다. 재배포하거나 수정본을 공개할 계획이라면 저장소의 GPL-3.0 조건을 별도로 검토해야 합니다.

## 2. 아날로그 PIM 서브블록에 적합한 GitHub 자료: 8T SRAM in-memory DAC

**[abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration][2]** 는 8T SRAM cell array의 read/current path와 transistor sizing을 활용해 4-bit DAC 동작을 구성한 자료입니다. 완전한 VMM/MAC macro는 아니지만, **아날로그 PIM의 입력 인가·가중치별 conductance·column current**를 이해하고 확장하기에 좋은 회로 수준 출발점입니다.[2]

| 확인 항목 | 검증 결과 | 바로 열 파일 |
|---|---|---|
| Top-level schematic | **있음**. 4개 SRAM 기반 DAC block이 보이는 회로도 | [`InMemDAC.sch`][2a] |
| SPICE netlist | **있음** | [`InMemDAC.cir`][2b] |
| 회로도 PDF | **있음**. top-level circuit을 PDF로 확인 가능 | [`InMemDAC_Schematic.pdf`][2c] |
| Layout source | **없음**. `.mag`, GDSII, LEF/DEF 미확인 | 해당 없음 |
| 사용 도구 | eSim, Makerchip, SkyWater PDK | [README][2] |

이 자료 역시 xschem·Magic 기반은 아니며, schematic을 xschem으로 옮겨 8T cell·precharge·sense/ADC·reference column을 붙이는 방식이 적합합니다. 특히 이 회로는 **PIM MAC 전체가 아니라 DAC-oriented compute primitive**라는 범위를 분명히 두고 사용해야 합니다.

## 3. schematic과 layout figure를 함께 참고할 수 있는 공개 논문

**[Rajput, Pattanaik, Kaushal의 SDP8T-IMC preprint][3]** 는 local bit-line sharing, read/write decoupling, virtual-VSS write assist를 갖는 Dual-Port 8T SRAM과 그 IMC 구조를 제안합니다. 논문은 전용 read path, word/bit-line, sense amplifier, reference generator를 포함한 SRAM/IMC architecture figure를 제공하고, **Figure 11에서 제안 SDP8T cell과 DP8T cell의 65 nm UMC layout**을 제시합니다.[3]

> 이 자료는 **회로도와 layout 그림을 모두 볼 수 있는 8T IMC 논문**이라는 점에서 가장 좋은 문헌 참고 자료입니다. 다만 Magic `.mag`, GDSII 또는 schematic source 같은 편집 가능한 EDA 파일은 공개하지 않습니다.[3]

이 논문은 MAC 중심이 아니라 NAND·AND·NOR·OR·XOR 등 Boolean IMC와 BCAM을 중심으로 합니다. TechRxiv의 해당 preprint는 CC BY 4.0로 공개되어 있으나, 공개 논문 figure를 자신의 tape-out layout으로 전용하기보다는 **topology 및 layout planning 참고** 용도로 쓰는 편이 적절합니다.[3]

## 4. 아날로그 MAC 구조까지 보는 공개 논문

**[Amogh K. M.와 Sunita M. S.의 8×8 8T SRAM IMC 논문][4]** 은 8×8 array에서 multiple RWL activation과 RBL charge-sharing을 이용해 MAC count를 전압으로 생성하고, comparator 8개를 포함하는 MAC decoder로 digital count를 얻는 구조를 공개합니다. 본문에는 **8T bit-cell architecture, 8×8 IMC array, MAC decoder, voltage comparator** figure가 포함되어 있어 아날로그 readout 중심 PIM macro의 회로적 구성을 파악하는 데 유용합니다.[4]

**[Shin과 Jo의 open-access 8T SRAM-CIM 논문][6]** 은 proposed 8T SRAM-CIM bit-cell schematic, 전체 CIM architecture, write-driver schematic, static body-biasing schematic을 제공하는 또 다른 공개 자료입니다. 이 논문의 figure 목록에는 physical layout figure가 없으므로, schematic/periphery 설계 참고 자료로 분류하는 것이 정확합니다.[6]

| 논문 | 8T cell schematic | Array/macro schematic | Comparator/driver schematic | Layout figure | 편집 가능한 EDA source |
|---|---:|---:|---:|---:|---:|
| 8×8 MAC-derived IMC [4] | 있음 | 있음 | 있음 | 미제공 | 미제공 |
| Low-Power 8T SRAM-CIM [6] | 있음 | 있음 | write driver·body bias 있음 | 미제공 | 미제공 |
| SDP8T-IMC [3] | 있음 | 있음 | SA/reference 관련 구조 있음 | **있음** | 미제공 |

## 5. xschem과 Magic을 꼭 써야 한다면: 가장 현실적인 조합

검증한 공개 자료 중 **xschem와 Magic으로 만든 완료형 8T PIM cell source**는 확인하지 못했습니다. 그러므로 아래처럼 “검증된 PIM topology”와 “open-source layout flow”를 분리해 결합하는 방식을 권합니다.

| 단계 | 추천 출발 자료 | xschem/Magic에서 수행할 작업 |
|---|---|---|
| 8T cell topology | GitHub logic-PIM [1] 또는 SDP8T 논문 [3] | 6T latch + 2T decoupled read port를 xschem에서 직접 재작성 |
| PIM read/compute operation | Logic-PIM [1] 또는 8×8 MAC IMC [4] | RBL precharge, 동시 RWL activation, inverter/SA 또는 comparator 연결 |
| 아날로그 DAC/weighted input | In-memory DAC [2] | DAC 또는 bit-serial input driver를 추가하고 ngspice로 transient 검증 |
| 물리 layout | Sky130/Open PDK + Magic | 8T cell의 regular array layout, RBL/WWL/BL routing, DRC/LVS, parasitic extraction |
| macro digital integration | `msvsdpim` IMC-gen [5] | 주변 control/decoder/logic의 GDS·LEF·DEF 및 OpenFASOC 흐름 참고 |

`msvsdpim`은 xschem 및 Magic 설치·Sky130 PDK 환경을 문서화하고 있으며, IMC-gen 하위에 `SRAMLOGIC.gds`, `SRAMLOGIC.lef`, final DEF 같은 physical output이 있습니다.[5] 하지만 저장소 전체에서 **8T PIM의 xschem `.sch`, Magic `.mag`, transistor-level SPICE source는 확인되지 않았으므로**, cell-level layout의 직접적인 출발점으로 사용하기보다 PIM 주변 logic의 digital backend 참고 자료로만 권합니다.

## 6. 보조 자료: 8T SRAM cell 자체의 eSim source

PIM 회로를 직접 확장하려면 8T cell source가 필요할 수 있습니다. **[PatelVatsalB21/8-T_SRAM_Cell][7]** 는 Sky130 및 eSim 기반 8T SRAM cell의 schematic, `.cir` netlist, `.net` 파일과 schematic PDF를 제공합니다. 이 자료는 PIM 구현은 아니지만, 위 PIM source의 cell 구조가 부족할 때 **8T cell 단위 회로를 참고하는 보조 자료**가 될 수 있습니다.[7]

## 참고문헌 및 직접 링크

[1] R. Tiwari, “[In Memory Logic Operations with 8T SRAM cells](https://github.com/rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon),” GitHub repository.

[1a] R. Tiwari, “[LOGICwithSRAM.sch](https://github.com/rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon/blob/main/LOGICwithSRAM.sch).”

[1b] R. Tiwari, “[LOGICwithSRAM.cir](https://github.com/rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon/blob/main/LOGICwithSRAM.cir).”

[1c] R. Tiwari, “[FinalReport.pdf](https://github.com/rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon/blob/main/FinalReport.pdf).”

[1d] R. Tiwari, “[GPL-3.0 License](https://github.com/rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon/blob/main/LICENSE).”

[2] A. Kumar, “[8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration](https://github.com/abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration),” GitHub repository.

[2a] A. Kumar, “[InMemDAC.sch](https://github.com/abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration/blob/main/eSim_ProjectFiles_InMemDAC/InMemDAC.sch).”

[2b] A. Kumar, “[InMemDAC.cir](https://github.com/abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration/blob/main/eSim_ProjectFiles_InMemDAC/InMemDAC.cir).”

[2c] A. Kumar, “[InMemDAC_Schematic.pdf](https://github.com/abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration/blob/main/eSim_ProjectFiles_InMemDAC/InMemDAC_Schematic.pdf).”

[3] A. Rajput, M. Pattanaik, and G. Kaushal, “[Local Bit-Line Sharing Robust Dual-Port 8T SRAM With Virtual VSS for Energy-Efficient In-Memory Computing Architecture](https://www.techrxiv.org/doi/full/10.36227/techrxiv.16704805.v1),” *TechRxiv*, 2021. [PDF](https://www.techrxiv.org/doi/pdf/10.36227/techrxiv.16704805)

[4] A. K. M. and S. M. S., “[A Novel 8T SRAM-Based In-Memory Computing Architecture for MAC-Derived Logical Functions](https://arxiv.org/html/2512.00441v1),” *arXiv*, 2025. [PDF](https://arxiv.org/pdf/2512.00441)

[5] R. Tiwari, “[msvsdpim](https://github.com/rahulearn2019/msvsdpim),” GitHub repository; [IMC-gen directory](https://github.com/rahulearn2019/msvsdpim/tree/main/week7/IMC-gen).

[6] H.-J. Shin and S.-H. Jo, “[Low-Power 8T SRAM Compute-in-Memory Macro for Edge AI Processors](https://www.mdpi.com/2076-3417/14/23/10924),” *Applied Sciences*, 2024.

[7] V. Patel, “[8-T SRAM Cell](https://github.com/PatelVatsalB21/8-T_SRAM_Cell),” GitHub repository.

---

*조사 기준: 공개 URL에서 PIM/IMC 구현 설명을 확인하고, GitHub 저장소는 실제 파일 트리에서 `.sch`, `.cir`, `.mag`, GDSII, LEF/DEF의 존재 여부를 점검했다. ‘layout 있음’은 편집 가능한 layout source가 아니라 논문 figure만 공개된 경우를 별도로 명시했다.*
