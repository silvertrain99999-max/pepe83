# 공급사 중심 상품관리

관리 진입점은 공급사 → 브랜드 → 해당 규칙 코드입니다. 공급사 설정파일 6개를 중심으로 브랜드가 나뉘며, `router.py`가 연결을 확인합니다. 구현 코드는 기존 경로에 유지해 기존 사용법을 보존했습니다.

```text
suppliers/
├─ trek.json       TREK
│  ├─ trek_bike    자전거 (미구현)
│  └─ trek_acc     용품·부품 (미구현)
├─ odbike.json     OD BIKE
│  ├─ merida       MERIDA (미구현)
│  ├─ tern         TERN (미구현)
│  └─ other_acc    기타 ACC (브랜드 확인 필요)
├─ glnco.json      GL&Co
│  └─ sram         SRAM (미구현)
├─ nnxsports.json  NNX SPORTS
│  └─ shimano      SHIMANO (미구현)
├─ sports55.json   SPORTS55
│  ├─ park_tool    → sportson55/rules.py
│  └─ finish_line  → sportson55/finish_line.py
└─ hlsc.json       HLSC
   └─ topeak       → operations/src/rules.mjs
```

브랜드 항목은 JSON 안의 하위 설정입니다. 새 브랜드는 해당 공급사 파일에 추가하고, 공급사 선택 없이 브랜드만으로 임의 실행하지 않습니다. 미구현·잘못된 연결은 `hold`로 반환합니다. 코드가 있는 브랜드도 `planner_ready`는 오프라인 변경안 생성 가능 상태이며, 실제 사이트 수정 완료를 뜻하지 않습니다.

## 사용

저장소 루트에서:

```sh
python suppliers/router.py sports55 park_tool
python suppliers/router.py sports55 finish_line
python suppliers/router.py hlsc topeak
python -m unittest discover -s suppliers -p "test_*.py" -v
```

출력의 `entry`와 `function`이 해당 브랜드 코드입니다. 라우터는 파일을 실행하거나 쇼핑몰을 수정하지 않습니다.

## 규칙 분리

- SPORTS55: 본사 재고 있으면20, 본사 품절이면 확인된 매장 수량, 둘 다 없으면0. 기존 할인 유지.
- HLSC/토픽: 기존 코드의 범위는 확인된 매장재고 작업. 당시20% 할인·배송3000원 합의는 재개 시 최신 지시와 대조. SPORTS5520개 규칙을 상속하지 않음.
- 다른4개 공급사: 공급사·브랜드 구조만 등록. 가격·재고·할인 규칙은 확인 후 구현.
- 스마트스토어·카페24는 판매채널이며 공급사가 아님. 각 브랜드 변경안에 채널을 지정.
- 최신 실재고·본사 가격·판매상태·상품/옵션 대응을 확인한 뒤 내장 브라우저로 저장하고 재조회.

공급사 목록과 브랜드 범위는 사용자가 지정한6곳 기준입니다. 영업상 최신 취급 브랜드 전체 목록이라고 단정하지 않습니다.

