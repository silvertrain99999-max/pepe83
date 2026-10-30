"""Offline Schwalbe change planner. Does not log in, save, or delete products."""

IDENTITY_FIELDS = ("model", "grade", "construction", "size", "color")
SEO_FIELDS = {
    "cafe24": {"name", "search_keywords", "summary", "meta_title", "meta_author",
               "meta_description", "meta_keywords", "alt"},
    "smartstore": {"name", "channel_name", "tags", "page_title", "meta_description"},
}


def plan_option(current, supplier, *, channel, store_stock=0):
    """Exact confirmed identity only; unknown/missing data is a hold, not zero."""
    if channel not in SEO_FIELDS:
        return {"status": "hold", "reason": "unknown_channel"}
    if store_stock != 0:
        return {"status": "hold", "reason": "store_stock_policy_needs_confirmation"}
    if supplier is None:
        return {"status": "hold", "reason": "supplier_product_not_found"}
    if any(not current.get(k) or not supplier.get(k) or current[k] != supplier[k]
           for k in IDENTITY_FIELDS):
        return {"status": "hold", "reason": "identity_mismatch_or_missing"}
    stock = {"재고있음": 5, "재고없음": 0}.get(supplier.get("stock"))
    price = supplier.get("retail")
    if stock is None or type(price) is not int or price <= 0:
        return {"status": "hold", "reason": "stock_or_retail_unconfirmed"}
    changes = {"quantity": stock, "option_total_price": price}
    if channel == "smartstore":
        changes["option_use"] = "Y"
    else:
        changes["option_sale"] = "판매함" if stock else "판매안함"
    return {"status": "planned", "changes": changes,
            "preserve": ["display", "shipping", "discount", "images"],
            "note": "Keep displayed; zero quantity uses automatic sold-out. Never stop product."}


def validate_seo_patch(channel, patch):
    """Reject accidental price/stock/option/shipping changes in PE work."""
    if channel not in SEO_FIELDS:
        raise ValueError("unknown_channel")
    invalid = set(patch) - SEO_FIELDS[channel]
    if invalid:
        raise ValueError("Non-SEO fields: " + ", ".join(sorted(invalid)))
    return dict(patch)


def verification_status(*, save_notice, reopened, fields_match):
    if not save_notice:
        return "save_unconfirmed"
    if reopened and fields_match:
        return "verified"
    return "saved_pending_reopen"
