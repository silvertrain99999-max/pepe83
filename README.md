# 현재 공통 운영 기준

**최신 진입점: [상품관리 공통 정책](management/README.md)**

`management/policy.py`로 공급사별 변경안과 사용자 인계 목록을 먼저 생성합니다.
판매중지 설정·해제, 삭제, 신규 상품 업로드는 사용자 담당입니다.
불명확한 매칭은 즉시 보류하며 기존 할인은 유지합니다.
아래 브랜드별 코드는 과거 참고 구현이며 최신 공통 정책을 우회하여 사용하지 않습니다.

---

# 공급사 6개 중심 상품관리

[공급사 → 브랜드 → 코드 구조](suppliers/README.md)를 관리 진입점으로 사용합니다.

| 공급사 | 관리 브랜드·범위 |
| --- | --- |
| TREK | TREK Bike / ACC |
| OD BIKE | MERIDA / TERN / 기타 ACC |
| GL&Co | SRAM |
| NNX SPORTS | SHIMANO |
| SPORTS55 | Park Tool / Finish Line |
| HLSC | TOPEAK |

공급사별 설정은 `suppliers/*.json`, 연결 확인은 `suppliers/router.py`입니다. 기존 코드는 아래 경로에 유지합니다. 미구현 공급사는 임의 규칙을 적용하지 않고 보류합니다.

---

# 토픽 상품관리 업무 기준

9월10~11일 사용자 점검의 과거 기록은 [operations/README.md](operations/README.md)입니다. 현재 규칙은 [공통 정책](management/README.md)이 우선합니다.

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

루트 src/plan.mjs, src/audit-today.mjs 및 examples/test는9월9일 이전 초안으로 보존합니다. 본사 품절시0·입고시5개 등의 이전 규칙은 현재 매장 재고 운영에 사용하지 않습니다. 현재 운영 기준은 management 폴더가 우선합니다.

실재고 표는 사용자 확인 당시의 역사적 목록이며 현재 수량으로 자동 사용하면 안 됩니다. 저장 이력과 실제 판매 화면 검증 완료도 구분합니다. 비밀번호·토큰·주문 및 고객 정보는 저장하지 않습니다.

## SPORTS55: 파크툴·피니쉬라인 (2026-09-16 추가)

[코드 사용 안내](sportson55/README.md) · [피니쉬라인 규칙](sportson55/finish_line.py) · [파크툴·공통 규칙](sportson55/rules.py)

가격·재고·옵션 변경안 생성 코드이며 온라인 저장은 별도입니다. 기존 할인 유지, 용량·제형·포장 단위 검증을 포함합니다. 토픽 규칙과 분리하여 사용합니다.
