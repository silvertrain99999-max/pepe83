"""SPORTS55 comparison rules. Produces review plans; never edits live shops."""
from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

MODEL_ALIASES = {"MW-SET2": "MW-SET.2", "RP-SET2": "RP-SET.2"}


def clean_name(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\ufeff", "")).strip()


def remove_stars(value: str) -> str:
    return value.replace("★", "").replace("☆", "").strip()


def canonical_model(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A nonempty, confirmed model is required")
    model = clean_name(value).upper()
    return MODEL_ALIASES.get(model, model)


def package_kind(name: str) -> str | None:
    name = clean_name(name)
    if re.search(r"카운터|디스플레이", name):
        return "display_box"
    if re.search(r"카드\s*패킹|카디드", name):
        return "card_pack"
    if re.search(r"2개\s*1패킹", name):
        return "two_pins_per_pack"
    if "묶음" in name or "패킹" in name:
        return "needs_package_review"
    return None


def model_candidates(model: str, listing_name: str, catalog: list[dict]) -> list[dict]:
    """Exact version boundary and package check; never match an empty model.

    The caller supplies the confirmed model (including AOK/AC suffixes).
    Finish Line requires capacity/formulation matching outside this Park Tool helper.
    """
    key = canonical_model(model)
    expression = re.compile(r"(?<![A-Z0-9.-])" + re.escape(key) + r"(?![A-Z0-9.-])")
    listing_model_text = clean_name(listing_name).upper()
    for alias, canonical in MODEL_ALIASES.items():
        listing_model_text = re.sub(r"(?<![A-Z0-9.-])" + re.escape(alias) + r"(?![A-Z0-9.-])",
                                    canonical, listing_model_text)
    if not expression.search(listing_model_text):
        return []
    listing_pack = package_kind(listing_name)
    matches = []
    for item in catalog:
        source_name = clean_name(item["name"]).upper()
        source_name = re.sub(r"^파크툴\s+", "", source_name)
        # Main supplier model must occur at the start, not inside a clamp description.
        match = expression.match(source_name)
        if not match:
            continue
        # 106 versus 106-AC / 106 AC, or PRS-33.2 versus its AOK accessory.
        suffix = source_name[match.end():].lstrip(" _")
        if suffix.startswith("AC") or suffix.startswith("AOK"):
            continue
        source_pack = package_kind(item["name"])
        if "needs_package_review" in (listing_pack, source_pack):
            continue
        if listing_pack != source_pack:
            continue
        matches.append(deepcopy(item))
    return matches


def parse_price(value: str | int) -> int:
    if isinstance(value, bool):
        raise ValueError("Invalid price")
    if isinstance(value, int):
        amount = value
    elif isinstance(value, str) and re.fullmatch(r"\s*\d[\d,]*\s*원?\s*", value):
        amount = int(re.sub(r"\D", "", value))
    else:
        raise ValueError("Supplier price needs confirmation")
    if amount <= 0:
        raise ValueError("Supplier price must be positive")
    return amount


def inventory_target(in_stock: bool | None, store_quantity: int) -> int | None:
    if isinstance(store_quantity, bool) or not isinstance(store_quantity, int) or store_quantity < 0:
        raise ValueError("Store quantity must be a nonnegative integer")
    if in_stock is True:
        return 20
    if in_stock is False:
        return store_quantity
    return None


def build_plan(*, channel: str, current: dict[str, Any], source: dict | None,
               store_quantity: int = 0, confirmed_match: bool = False,
               hold: bool = False, option_status: dict | None = None,
               option_store: dict | None = None) -> dict:
    """Return only explicitly authorized changed fields. Discounts never appear.

    source: {price: consumer/base price, soldout: bool}; option_status maps exact
    option identifiers to in-stock booleans. None means unknown, never soldout.
    """
    if channel not in {"smartstore", "cafe24"}:
        raise ValueError("Unknown channel")
    if hold:
        return {"status": "hold", "reason": "user_hold", "changes": {}}
    changes: dict[str, Any] = {}
    for field in ("name", "channel_name"):
        if field in current:
            cleaned = remove_stars(current[field])
            if cleaned != current[field]:
                changes[field] = cleaned
    if not confirmed_match or source is None:
        return {"status": "hold", "reason": "supplier_match_unconfirmed", "changes": changes}
    if not isinstance(source.get("soldout"), bool):
        return {"status": "hold", "reason": "supplier_status_unknown", "changes": changes}
    changes["sale_price"] = parse_price(source["price"])
    if option_status is not None:
        option_store = option_store or {}
        quantities = {key: inventory_target(status, option_store.get(key, 0))
                      for key, status in option_status.items()}
        if not quantities or any(value is None for value in quantities.values()):
            return {"status": "hold", "reason": "option_status_unknown", "changes": {
                key: value for key, value in changes.items() if key in {"name", "channel_name"}}}
        changes["option_stock"] = quantities
        whole_soldout = all(quantity == 0 for quantity in quantities.values())
    else:
        quantity = inventory_target(not source["soldout"], store_quantity)
        changes["stock"] = quantity
        whole_soldout = quantity == 0
    if channel == "cafe24":
        changes["replacement_enabled"] = whole_soldout
        changes["replacement_text"] = "[품절]" if whole_soldout else ""
        changes["soldout_display_enabled"] = True
    return {"status": "ready_for_ui_verification", "changes": changes,
            "preserve": ["discount_amount_or_rate", "discount_dates", "discount_conditions"]}
