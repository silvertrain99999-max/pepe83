"""TREK 상품 원장 검증 및 채널별 반영안 생성.

온라인 쇼핑몰을 직접 수정하지 않는다. 확인된 원장 JSON을 검증하고
스마트스토어/카페24에 입력할 가격·할인·재고 값을 계산한다.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CatalogError(ValueError):
    pass


def _positive_int(value: Any, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise CatalogError(f"{field}: 0보다 큰 정수가 필요합니다")
    return value


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(catalog: dict[str, Any]) -> list[str]:
    """오류 목록을 반환한다. 빈 목록이면 원장 구조가 유효하다."""
    errors: list[str] = []
    products = catalog.get("products")
    if not isinstance(products, list):
        return ["products 배열이 필요합니다"]

    product_ids: set[str] = set()
    skus: set[str] = set()
    for pi, product in enumerate(products):
        prefix = f"products[{pi}]"
        product_id = str(product.get("trek_product_id", "")).strip()
        if not product_id:
            errors.append(f"{prefix}: trek_product_id 누락")
        elif product_id in product_ids:
            errors.append(f"{prefix}: 제품번호 중복 {product_id}")
        product_ids.add(product_id)

        if not str(product.get("official_name", "")).strip():
            errors.append(f"{prefix}: 공식 상품명 누락")
        variants = product.get("variants")
        if not isinstance(variants, list) or not variants:
            errors.append(f"{prefix}: variants가 비어 있습니다")
            continue

        seen: set[str] = set()
        for vi, variant in enumerate(variants):
            vp = f"{prefix}.variants[{vi}]"
            sku = str(variant.get("sku", "")).strip()
            if not sku:
                errors.append(f"{vp}: TREK SKU 누락")
            elif sku in seen:
                errors.append(f"{vp}: 상품 내부 SKU 중복 {sku}")
            elif sku in skus:
                errors.append(f"{vp}: 원장 전체 SKU 중복 {sku}")
            seen.add(sku)
            skus.add(sku)

            for field in ("regular_price", "supplier_stock"):
                value = variant.get(field)
                if type(value) is not int or value < 0:
                    errors.append(f"{vp}: {field}는 0 이상의 정수여야 합니다")
            sale = variant.get("sale_price")
            regular = variant.get("regular_price")
            if sale is not None and (type(sale) is not int or sale <= 0 or
                                     type(regular) is not int or sale > regular):
                errors.append(f"{vp}: sale_price가 정상가보다 크거나 유효하지 않습니다")

        channels = product.get("channels", {})
        for channel in ("smartstore", "cafe24"):
            listing = channels.get(channel)
            if listing is None:
                continue
            if not str(listing.get("product_id", "")).strip():
                errors.append(f"{prefix}.channels.{channel}: 상품번호 누락")
            mapped = listing.get("skus", [])
            if not isinstance(mapped, list) or len(mapped) != len(set(mapped)):
                errors.append(f"{prefix}.channels.{channel}: SKU 매핑 누락 또는 중복")
            unknown = set(mapped) - seen
            if unknown:
                errors.append(f"{prefix}.channels.{channel}: 알 수 없는 SKU {sorted(unknown)}")
            if len(set(mapped)) > 1:
                prices = {(v["regular_price"], v.get("sale_price"))
                          for v in variants if v.get("sku") in mapped}
                if len(prices) > 1:
                    errors.append(
                        f"{prefix}.channels.{channel}: 서로 다른 가격 정책의 SKU가 한 상품에 혼합됨"
                    )
    return errors


def channel_values(variant: dict[str, Any], channel: str,
                   *, include_store_stock: bool = False) -> dict[str, Any]:
    """옵션 하나의 채널 입력값을 계산한다."""
    regular = _positive_int(variant.get("regular_price"), "regular_price")
    sale = variant.get("sale_price") or regular
    _positive_int(sale, "sale_price")
    supplier = variant.get("supplier_stock")
    if type(supplier) is not int or supplier < 0:
        raise CatalogError("supplier_stock: 0 이상의 정수가 필요합니다")
    stock = supplier
    if include_store_stock:
        store = variant.get("store_stock")
        if type(store) is not int or store < 0:
            raise CatalogError("매장 재고 합산 시 store_stock 확인값이 필요합니다")
        stock += store

    result = {"sku": str(variant["sku"]), "stock": stock,
              "availability": "품절" if stock == 0 else "판매중"}
    if channel == "smartstore":
        result.update(regular_price=regular,
                      immediate_discount=regular - sale,
                      displayed_price=sale)
    elif channel == "cafe24":
        result.update(consumer_price=regular, selling_price=sale,
                      separate_discount=False)
    else:
        raise CatalogError(f"지원하지 않는 채널: {channel}")
    return result


def build_plan(catalog: dict[str, Any], channel: str) -> list[dict[str, Any]]:
    errors = validate(catalog)
    if errors:
        raise CatalogError("\n".join(errors))
    output = []
    for product in catalog["products"]:
        listing = product.get("channels", {}).get(channel)
        if not listing:
            continue
        include_store = product.get("stock_policy") == "supplier_plus_store"
        wanted = set(listing["skus"])
        values = [channel_values(v, channel, include_store_stock=include_store)
                  for v in product["variants"] if v["sku"] in wanted]
        output.append({"trek_product_id": product["trek_product_id"],
                       "official_name": product["official_name"],
                       "channel_product_id": listing["product_id"],
                       "values": values})
    return output

