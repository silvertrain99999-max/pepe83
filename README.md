# 토픽 상품관리 업무 기준

9월10~11일 사용자 점검을 반영한 최신 기준은 [operations/README.md](operations/README.md)입니다.

- [매장 실재고18종22개 표](operations/docs/inventory.md)
- [역할 분담과 업무 순서](operations/README.md)
- [미적용 및 인계 목록](operations/docs/handoff.md)
- [검토 계획 및 완료 판정 코드](operations/src/rules.mjs)

```sh
cd operations
node --test
node src/report.mjs
```

실제 쇼핑몰 접속이나 상품 변경은 하지 않습니다. 연동 확인·현재 실재고·모델 대응이 확인된 경우에만 검토 계획을 만들고 카페24 할인은 사용자에게 배정합니다.

## 이전 초안

루트 src/plan.mjs, src/audit-today.mjs 및 examples/test는9월9일 이전 초안으로 보존합니다. 본사 품절시0·입고시5개 등의 이전 규칙은 현재 매장 재고 운영에 사용하지 않습니다. 현재 운영 기준은 operations 폴더가 우선합니다.

실재고 표는 사용자 확인 당시의 역사적 목록이며 현재 수량으로 자동 사용하면 안 됩니다. 저장 이력과 실제 판매 화면 검증 완료도 구분합니다. 비밀번호·토큰·주문 및 고객 정보는 저장하지 않습니다.

## SPORTS55: 파크툴·피니쉬라인 (2026-09-16 추가)

[코드 사용 안내](sportson55/README.md) · [피니쉬라인 규칙](sportson55/finish_line.py) · [파크툴·공통 규칙](sportson55/rules.py)

가격·재고·옵션 변경안 생성 코드이며 온라인 저장은 별도입니다. 기존 할인 유지, 용량·제형·포장 단위 검증을 포함합니다. 토픽 규칙과 분리하여 사용합니다.
