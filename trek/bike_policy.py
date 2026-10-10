"""Offline TREK Bike review gates. Never connects to or modifies a shop."""
import argparse
import json
from pathlib import Path

CHANNELS = {"cafe24", "smartstore"}
IDENTITY = ("sku", "model", "year", "generation", "color", "size")
SEO_FIELDS = {
    "cafe24": {"name", "search_terms", "meta_title", "meta_author", "meta_description", "meta_keywords", "alttag"},
    "smartstore": {"name", "page_title", "meta_description", "tags"},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evidence(value):
    """Presence gate only: an operator must actually inspect the cited source."""
    return isinstance(value, dict) and all(value.get(k) for k in ("reference", "checked_at", "revision")) and value.get("confirmed") is True


def quantity(value):
    require(type(value) is int and value >= 0, "수량은 확인된 0 이상의 정수여야 합니다")
    return value


def stock_target(row, basis):
    require(evidence(basis), "재고 산정 방식의 합의 근거 필요")
    mode = basis.get("mode")
    require(mode in {"supplier_only", "store_only", "supplier_plus_store"}, "재고 산정 방식 미확인")
    total = 0
    for name in ("supplier", "store"):
        if mode != "supplier_plus_store" and mode != name + "_only":
            continue
        source = row.get(name, {})
        require(evidence(source), name + " 최신 재고 확인 근거 필요")
        require(source.get("state") == "known", name + " 미확인/보관 제품을 0으로 바꿀 수 없습니다")
        total += quantity(source.get("quantity"))
    return total


def inventory_plan(item):
    """All options or none. Product-level sale suspension is never resumed here."""
    require(evidence(item.get("match")), "정확한 상품·전체 옵션 매칭 근거 필요")
    require(item.get("product_state") in {"selling", "soldout"}, "판매중지 상품은 별도 사용자 지시 필요")
    rows = item.get("rows", [])
    require(bool(rows), "옵션 목록 필요")
    expected = item.get("expected_option_ids", {})
    require(set(expected) == CHANNELS, "두 채널 전체 옵션 목록 필요")
    result, seen_skus = [], set()
    seen_ids = {c: set() for c in CHANNELS}
    for row in rows:
        require(all(row.get(k) for k in IDENTITY), "SKU·모델·연식·세대·색상·사이즈 필요 (세대 미적용은 n/a)")
        require(row["sku"] not in seen_skus, "중복 SKU")
        seen_skus.add(row["sku"])
        mappings = row.get("channels", {})
        require(set(mappings) == CHANNELS, "두 채널 상품번호·옵션번호 필요")
        for channel, mapping in mappings.items():
            require(mapping.get("product_id") == item.get("product_ids", {}).get(channel) and mapping.get("product_id"), "상품번호 불일치")
            oid = mapping.get("option_id")
            require(oid and oid not in seen_ids[channel], "옵션번호 누락/중복")
            seen_ids[channel].add(oid)
        stock = stock_target(row, item.get("stock_basis", {}))
        resume = any(m.get("option_selling") is not True for m in mappings.values()) and stock > 0
        require(not resume or evidence(item.get("option_resume_authorization")), "옵션 판매함 변경 지시 근거 필요")
        result.append({"sku": row["sku"], "channels": mappings, "quantity": stock,
                       "option_selling": True if stock > 0 else "preserve",
                       "availability": "in_stock" if stock > 0 else "soldout"})
    for channel in CHANNELS:
        ids = expected[channel]
        require(isinstance(ids, list) and len(ids) == len(set(ids)) and set(ids) == seen_ids[channel], "전체 옵션 누락/중복/불일치")
    return {"status": "review_plan", "rows": result,
            "preserve": ["price", "discount", "shipping", "product_sale_status"],
            "shared_stock_warning": "동일 실재고를 두 채널에 표시해도 재고가 두 배가 되지 않음. 판매 후 양쪽 차감 필요"}


def seo_plan(spec):
    require(evidence(spec.get("source")), "해당 연식·국내 사양 확인 근거 필요")
    fields = ("model", "drivetrain", "rear_speed", "frame_material", "bike_type")
    require(all(spec.get(k) for k in fields), "확인된 모델·구동계·뒤 기어 단수·프레임 소재·차종 필요")
    year = spec.get("year")
    require(type(year) is int and 2000 <= year <= 2099, "4자리 연식 필요")
    require(type(spec["rear_speed"]) is int and 1 <= spec["rear_speed"] <= 30, "뒤 기어 단수 확인 필요")
    generation = spec.get("generation", "")
    title = " ".join(str(x) for x in (str(year)[-2:], "트렉", spec["model"], generation,
                                    spec["drivetrain"], str(spec["rear_speed"]) + "단",
                                    spec["frame_material"], spec["bike_type"]) if x)
    uses = spec.get("use_terms", [])
    require(isinstance(uses, list) and all(isinstance(x, str) and x.strip() for x in uses), "용도 검색어 목록 오류")
    terms = list(dict.fromkeys(["트렉 " + spec["model"], spec["model"], spec["drivetrain"],
                               str(spec["rear_speed"]) + "단 자전거", spec["bike_type"]] + uses))
    description = title + ". 색상·사이즈별 판매 옵션과 재고를 확인하세요."
    return {"status": "review_plan", "cafe24": {"name": title, "search_terms": ",".join(terms),
        "meta_title": title + " | YBBIKE", "meta_author": "YBBIKE", "meta_description": description,
        "meta_keywords": ",".join(terms), "alttag": "트렉 " + spec["model"]},
        "smartstore": {"name": title, "page_title": title, "meta_description": description,
                       "tags": uses}, "note": "태그 등록 가능 여부·길이·금칙어는 현재 채널 화면에서 확인. 검색 순위 보장 없음"}


def validate_scope(channel, workflow, changes):
    require(channel in CHANNELS, "채널 오류")
    require(workflow in {"inventory", "seo"}, "업무 오류")
    if workflow == "seo":
        require(set(changes) <= SEO_FIELDS[channel], "SEO 작업에 재고·옵션·가격·상태 등 범위 외 변경 포함")


def verified(records, product_ids, workflow, expected):
    """Expected/read-back dictionaries must include every intended field/option.

    User reports alone do not certify persistence. Evidence is self-reported,
    not cryptographic or live proof. Keep raw evidence outside public GitHub.
    """
    if set(product_ids) != CHANNELS or set(expected) != CHANNELS or len(records) != 2:
        return False
    if {r.get("channel") for r in records} != CHANNELS:
        return False
    for record in records:
        c = record["channel"]
        if (record.get("product_id") != product_ids[c] or not product_ids[c]
            or record.get("workflow") != workflow or workflow not in {"inventory", "seo"}
            or record.get("status") != "reverified"
            or record.get("actor") not in {"assistant", "user"}
            or not evidence(record.get("save")) or not evidence(record.get("reread"))
            or not expected[c] or record.get("actual") != expected[c]):
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["inventory", "seo"])
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = inventory_plan(data) if args.mode == "inventory" else seo_plan(data)
    except (ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "hold", "changes": {}, "reason": str(error)}, ensure_ascii=False))
        raise SystemExit(2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
