# 8T SRAM PIM 공개 자료 조사 노트

## 1. rahulearn2019/msvsdpim

- URL: https://github.com/rahulearn2019/msvsdpim
- 저장소 소개: “In Memory logic using 8TSRAM cells”를 수행하는 mixed-signal physical design 프로젝트.
- README에서 확인한 도구: Open PDK/Sky130, **xschem**, **Magic**, ngspice.
- 저장소 최상위 구조: `debugs`, `week1`~`week7`, README.
- 2026-08-27 브라우저 확인 결과: README에는 xschem schematic 작성 및 Magic layout 절차와 다수의 이미지가 있으나, 최상위 파일 목록만으로 8T PIM 최종 schematic source 및 Magic `.mag` layout source의 정확한 경로는 아직 미검증.
- 검증 필요: raw GitHub tree/API로 `.sch`, `.sym`, `.mag`, `.spice`, `.gds` 및 8T/PIM 파일을 특정할 것.

## 2. silicon-vlsi/PS-2025-RAM

- URL: https://github.com/silicon-vlsi/PS-2025-RAM
- 저장소 소개: 8T SRAM 기반 IMC architecture라고 검색 결과에는 나타났으나, README 본문에서는 130 nm CMOS 기반 16-byte SRAM을 설명하며 Cadence tools 사용을 명시.
- 최상위 파일: `8T_SRAM.png`, `precharge ckt.png`, `Rowdec.png`, `PC.png`, `DOCS`.
- README 목차에는 `8T_SRAM`, precharge, row decoder, `RAM/ICM logic block`, sense amplifier, write driver, simulation, layout이 있음.
- 주의: README Architecture 세부 본문은 6T SRAM array를 설명하는 등 8T/IMC 구현 서술과 불일치가 있음. xschem/Magic 사용 조건도 충족하지 않음.
- 잠정 판단: schematic/레이아웃 이미지 참고 자료 후보일 수 있으나, xschem·Magic 기반 8T PIM의 재사용 가능한 source 파일 후보로는 낮은 우선순위.

## 다음 확인 대상

- `rahulearn2019/msvsdpim`의 GitHub tree에서 8T SRAM PIM 관련 xschem/Magic 원본을 파일 단위로 특정.
- `abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration`의 schematic·layout 공개 범위 검증.
- raw GitHub API로 후보 저장소의 source 확장자 및 README 도구 서술을 교차 검증.

*조사일: 2026-08-27 (GMT+9)*

## 3. abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration

이 공개 저장소는 8T SRAM 기반 in-memory DAC를 AI 가속 관점에서 제안한다. README는 eSim, Makerchip, SkyWater PDK를 사용했다고 명시하며, 저장소에는 `eSim_ProjectFiles_InMemDAC/InMemDAC.sch`, `InMemDAC.cir`, 그리고 `InMemDAC_Schematic.pdf`가 실제로 포함되어 있다. PDF의 단일 페이지 회로도는 네 개의 SRAM 기반 DAC 소자 블록, 입력 제어, 출력 노드, 전원과 GND를 포함한 top-level in-memory DAC schematic임을 시각적으로 확인했다.

다만 조사한 파일 트리에는 Magic `.mag`, GDSII, LEF/DEF, KiCad PCB layout과 같은 physical layout 원본·산출물이 없다. 따라서 이 저장소는 **8T SRAM 기반 메모리 내 아날로그 변환 회로도와 SPICE netlist의 출발점**으로는 매우 적합하나, layout 재사용 자료로는 적합하지 않다. 또한 구현 도구는 xschem·Magic이 아니라 eSim 계열이다.

- URL: https://github.com/abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration
- 직접 열 수 있는 schematic PDF: https://github.com/abhash2205/8T-SRAM-Based-In-Memory-DAC-for-AI-acceleration/blob/main/eSim_ProjectFiles_InMemDAC/InMemDAC_Schematic.pdf
- 회로 원본 파일: `eSim_ProjectFiles_InMemDAC/InMemDAC.sch`, `eSim_ProjectFiles_InMemDAC/InMemDAC.cir`
- 잠정 등급: **A- (회로도·netlist 공개, layout 없음, 8T PIM의 DAC 서브블록 중심)**

## 보안/신뢰성 유의 사항

`rahulearn2019/msvsdpim` 복제본의 `week7/IMC-gen/readme.md`에서 저장소 내용과 무관한 실행 지시문이 발견되었다. 해당 텍스트는 신뢰하지 않았으며 실행하지 않았다. 이 저장소는 회로 파일 검증 결과에서도 `.sch`, `.mag`, SPICE netlist가 확인되지 않아 최종 추천에서는 ‘도구·플로우 참고’로만 다룬다.

## 4. rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon

이 저장소는 제목·README 기준으로 **“In Memory Logic Operations with 8T SRAM cells”** 를 구현한 공개 PIM 자료이다. 8T SRAM 두 셀의 저장값을 read bit-line capacitor에서 NOR로 만들고, 인버터로 OR를 생성하는 구조를 설명한다. top-level eSim 회로 원본 `LOGICwithSRAM.sch`, SPICE 성격의 netlist `LOGICwithSRAM.cir`, 회로도 화면 이미지, 1쪽 분량의 `FinalReport.pdf`를 제공한다. 보고서의 텍스트에서도 8T SRAM 기반 PIM과 circuit schematic이 직접 확인된다.

파일 트리 검증 결과 Magic `.mag`, GDSII, LEF/DEF 등 physical layout 산출물은 없다. 즉, **가장 직접적인 8T logic-PIM schematic 및 circuit/netlist 공개 후보**이지만, layout이 필수라면 추가 물리 구현이 필요하다. 회로도 형식·README의 공개 도구 문맥은 eSim이며 xschem이 아니다.

- URL: https://github.com/rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon
- 회로도 원본: https://github.com/rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon/blob/main/LOGICwithSRAM.sch
- 회로 netlist: https://github.com/rahulearn2019/Mixed-Signal-Circuit-Design-and-SImulation-Marathon/blob/main/LOGICwithSRAM.cir
- 회로도·PIM 작동 설명: 저장소 README 및 `FinalReport.pdf`
- 잠정 등급: **A (8T logic-PIM schematic·netlist 확인, layout 없음, eSim 기반)**

## 5. rahulearn2019/msvsdpim의 IMC-gen 하위 프로젝트

`week7/IMC-gen`은 `SRAMLOGIC.v`, `imc.v` 같은 논리 소스와 `SRAMLOGIC.gds`, `SRAMLOGIC.lef`, final DEF 등 OpenFASOC 기반 physical-design 산출물을 포함한다. 즉, PIM 주변 논리의 GDS/LEF/DEF 참고 및 full digital physical-design 흐름 학습에는 유용하다. 그러나 저장소 전체 검사에서 xschem `.sch`, Magic `.mag`, SPICE netlist는 0개였고, 8T SRAM cell의 transistor-level schematic과 Magic layout을 재사용 가능한 원본 형태로 제공하지 않는다.

- IMC 하위 프로젝트: https://github.com/rahulearn2019/msvsdpim/tree/main/week7/IMC-gen
- 관련 산출물: `week7/IMC-gen/blocks/sky130hd/gds/SRAMLOGIC.gds`, `week7/IMC-gen/blocks/sky130hd/lef/SRAMLOGIC.lef`, `week7/IMC-gen/flow/results/sky130hd/imc/6_final.def`
- 잠정 등급: **B- (IMC logic physical output 및 xschem/Magic 환경 학습, 8T transistor-level schematic/Magic layout 원본은 없음)**

## 6. 공개 논문 후보: Low-Power 8T SRAM Compute-in-Memory Macro for Edge AI Processors

- URL: https://www.mdpi.com/2076-3417/14/23/10924
- 공개성: MDPI의 open-access 논문으로 전체 본문과 회로 figure를 웹에서 열람할 수 있다.
- 확인한 내용: 본문 도입부 및 검색 결과는 proposed 8T SRAM-CIM bit-cell schematic을 Figure 1로 제시한다. 따라서 **회로도 그림을 참조하는 논문 자료**로는 유효하다.
- 현재 범위: 논문은 설계 figure·시뮬레이션 결과를 제공하는 문헌이지, xschem `.sch`, Magic `.mag`, GDSII 같은 재사용 가능한 EDA source 파일을 제공하는 공개 저장소는 아니다. layout figure의 포함 여부는 문서 텍스트를 별도 추출하여 최종 확인할 예정.
- 잠정 등급: **A- (공개 논문 schematic figure, editable circuit/layout source는 미확인)**

브라우저 내 keyword 검색은 일시적인 실행 오류로 완료되지 않았으므로, 본문 텍스트 저장본 및 공개 PDF 경로를 이용해 대체 검증한다.

## 7. 확장 검색: OpenACM과 6T IMC 공개 사례

**OpenACM**(https://github.com/ShenShan123/OpenACM)은 SRAM 기반 approximate digital CIM(DCiM)을 위한 공개 컴파일러/회로 생성 프런트엔드다. 저장소에는 DCIM, DCIM_OPT, SRAM-OPT, examples 및 OpenROAD flow 관련 디렉터리가 있고 Apache-2.0 라이선스로 공개된다. 다만 이는 8T cell의 transistor-level schematic이나 custom layout source가 아니라 multiplier/SRAM/PE generator, RTL template 및 digital physical-design flow 중심이다. 즉, “PIM 코드는 공개된다”는 사례이지만, 8T analog-SRAM macro를 직접 복제할 수 있는 자료는 아니다.

**Shubham-G04/In-Memory-Computing-Applied-on-an-8x8-6T-SRAM-Array**(https://github.com/Shubham-G04/In-Memory-Computing-Applied-on-an-8x8-6T-SRAM-Array)는 180 nm/90 nm/45 nm Cadence Virtuoso 기반 8×8 6T SRAM IMC의 layout·simulation·SPICE library·HDL을 공개하고 MIT 라이선스를 사용한다. 8T는 아니지만, 이 저장소는 custom SRAM IMC의 공개물 수준을 보여 주는 유의미한 반례이다. 현재 공개 파일/README에 나타난 도구는 Cadence이며 xschem/Magic은 아니다.

이 두 사례를 통해 공개 생태계가 ‘완전히 부재’한 것이 아니라, 공개되는 층위가 **RTL/compiler/architecture** 또는 **6T 학생 프로젝트**에 집중되고, 8T custom analog CIM의 cell schematic·layout source 공개는 상대적으로 희소함을 확인했다.
