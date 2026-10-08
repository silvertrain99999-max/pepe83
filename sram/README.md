# SRAM 공통 분류 기준

기준일: 2026-10-08. 카페24와 스마트스토어 공통. 시마노 설정과 분리.

사용자가 제조사 구조를 기준으로 만든 매장 분류표이며, 제품 호환성을 보증하는 표가 아닙니다. 기존 Eagle 12단을 S-Series로 묶는 것은 사용자 운영 예외입니다.

## 사용

`python sram/catalog.py` — 전체 19개 경로 조회

`python sram/catalog.py --code sram.brakes.hydraulic` — 한 분류 조회

코드와 운영 규칙은 [categories.json](categories.json)을 기준으로 합니다. 쇼핑몰에 접속하거나 상품을 변경하지 않습니다.

## 분류표

| 코드 | 경로 |
|---|---|
| sram.mtb.transmission_12 | SRAM → MTB → 12단 트랜스미션 |
| sram.mtb.s_series_12 | SRAM → MTB → 12단 S-Series |
| sram.mtb.speed_7_11 | SRAM → MTB → 11~7단 |
| sram.mtb.chainrings | SRAM → MTB → 체인링 |
| sram.mtb.accessories | SRAM → MTB → 악세서리 |
| sram.road.etap_axs | SRAM → 로드 → eTap AXS |
| sram.road.aero_brakes | SRAM → 로드 → 에어로 브레이크 |
| sram.road.fixed | SRAM → 로드 → 픽시드(싱글기어) |
| sram.road.speed_11 | SRAM → 로드 → 11단 |
| sram.road.apex | SRAM → 로드 → APEX |
| sram.road.speed_10 | SRAM → 로드 → 10단 |
| sram.road.chainrings | SRAM → 로드 → 체인링 |
| sram.road.bottom_brackets | SRAM → 로드 → 버텀브라켓(BB) |
| sram.road.accessories | SRAM → 로드 → 악세서리 |
| sram.brakes.hydraulic | SRAM → 브레이크 → 유압식 브레이크 |
| sram.brakes.mechanical | SRAM → 브레이크 → 기계식 브레이크 |
| sram.brakes.rotors | SRAM → 브레이크 → 로터 |
| sram.brakes.pads | SRAM → 브레이크 → 패드 |
| sram.brakes.accessories | SRAM → 브레이크 → 악세서리 |

## 지속 적용 규칙

- 기존 XX1/X01/GX/NX/SX Eagle 12단은 MTB/12단 S-Series에 포함
- 트랜스미션/T-Type 구동부품과 POD 컨트롤러 본체는 MTB/12단 트랜스미션
- 체인링, BB, 보수부품은 해당 전용 분류 우선
- 로드 AXS 변속·브레이크 통합 세트는 로드/eTap AXS
- 타사 호환품은 SRAM 정품과 구분하고 포함 여부 별도 결정
- 단종은 카테고리와 별도 기록. 정확한 모델·세대·옵션 및 공급 재고 확인. 단종만으로 삭제하지 않음
- 양 채널 분류 기준은 같지만 수정·판매상태·재고는 각각 확인
- 한글·영문 표기 모두 검색. 검색 0건은 단종/미등록 확정 근거가 아님. 전수 검증 전 완전 목록으로 단정하지 않음

## 운영 상태

- 사용자가 SRAM 카페24–스마트스토어 연동을 모두 해제했다고 보고함. 양 채널 수정은 독립적으로 처리.
- 상품 삭제·판매중지 설정/해제는 기존 공통 정책에 따라 사용자 담당.
- 분류 권고와 실제 저장 완료를 구분. 이 기준표 생성은 사이트 변경을 뜻하지 않음.
- 과거 상품 목록은 검색 누락이 있었으므로 완전한 전수 목록으로 사용하지 않음.
- 카페24에 확인됐던 MTB 버텀 브라켓은 공통 19개 경로 밖의 차이점. 양 채널 구조 재확인 전 임의 통합 금지.
- 상품별 관리표 필드: model, category_code, cafe24_product_code, smartstore_product_id, discontinuation_evidence, stock_supply_status, cafe24_status, smartstore_status.

[공통 관리 정책](../management/README.md)

