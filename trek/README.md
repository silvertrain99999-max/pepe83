# TREK 상품관리 코드

## Top-down 카테고리 운영

`categories.json`이 TREK 메뉴 전체를 자전거·장비부터 세부 카테고리까지 보존합니다.
각 잎 카테고리는 아래 두 축을 가집니다.

- `scope`: `sell_now`(현재 취급), `explore`(신규 판매 도전), `exclude`(가지치기), `undecided`(판단 전)
- `status`: `not_started`, `in_progress`, `blocked`, `complete`, `excluded`

`complete`에는 결과 보고서인 `evidence`가 반드시 필요합니다. `next` 명령은 원래
카테고리 순서에서 첫 미완료 항목을 반환하므로 한 카테고리를 끝내기 전에 다음
단계로 넘어가는 일을 막습니다.

```powershell
python trek/category_cli.py trek/categories.json summary
python trek/category_cli.py trek/categories.json next
python trek/category_cli.py trek/categories.json queue --root gear
python trek/category_cli.py trek/categories.json set gear.components.tubeless --scope exclude
python trek/category_cli.py trek/categories.json set gear.components.tubeless --status complete --evidence management/reports/...
```

TREK 상품은 이름이 아니라 **옵션별 SKU**로 관리합니다. `catalog.json`이 확인된
상품 원장이며, `catalog.py`는 SKU 누락·중복·가격 오류·통합상품 혼합을 검사하고
채널별 입력값을 계산합니다. 쇼핑몰을 직접 수정하는 자동 실행기는 아닙니다.

## 핵심 규칙

- 신규 상품과 신규 옵션은 TREK SKU가 없으면 원장에 등록하지 않습니다.
- 액세서리 재고는 본사 재고만 사용합니다.
- 타이어처럼 별도 합의된 상품만 `supplier_plus_store`로 매장 재고를 합산합니다.
- 본사 `50+`는 원장에 `50`으로 기록합니다.
- 스마트스토어 할인: 정상 판매가를 유지하고 즉시할인 금액을 입력합니다.
- 카페24 할인: 소비자가에 정상가, 판매가에 할인가를 입력하고 별도 할인은 끕니다.
- 재고관리표의 할인가는 본사 할인 정보가 아니라 YB샵의 기존 판매가를 기록합니다.
- 카페24와 스마트스토어의 기존 할인가가 다를 수 있으므로 채널별 열에 따로 기록합니다.
- 정상가·할인 정책이 다른 SKU를 한 온라인 상품에 섞으면 검증 오류가 발생합니다.
- 저장 완료와 재조회 확인 전에는 작업 완료로 기록하지 않습니다.
- 재고관리표는 TREK 전용입니다. 다른 공급처는 별도 지시 전까지 생성하지 않습니다.
- 작업 순서는 본사 확인 → 판매 채널 대조 → 상품 수정 → 재조회 검증 → 재고관리표 갱신 → 코드 기록입니다.

## 실행

```powershell
python trek/cli.py trek/catalog.json
python trek/cli.py trek/catalog.json --channel smartstore --output trek/smartstore-plan.json
python trek/cli.py trek/catalog.json --channel cafe24 --output trek/cafe24-plan.json
python -m unittest discover -s trek -p "test_*.py" -v
node trek/inventory_report.mjs
```

`catalog.json`에는 오늘 확인한 대표 상품부터 넣었습니다. 앞으로 카테고리별로
본사 제품번호, 공식명, 옵션명, SKU, 정상가, 행사 가격, 본사 재고와 채널 상품번호를
추가하면 됩니다.
