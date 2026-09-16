"""Finish Line review plans from explicitly verified product identities.

Offline only: no browser, credentials, or live store writes.
"""
from copy import deepcopy
from .rules import build_plan, parse_price


def identity(value):
    """No inferred g/ml equivalence or DOT/mineral equivalence."""
    keys = ('family', 'formulation', 'capacity', 'unit')
    if not isinstance(value, dict) or any(not str(value.get(k, '')).strip() for k in keys):
        raise ValueError('Product family, formulation, capacity and unit required')
    return tuple(str(value[k]).strip().casefold() for k in keys)


def positive_count(value):
    if type(value) is not int or value <= 0:
        raise ValueError('Confirmed positive package quantity required')
    return value


def package_price(source_price, source_units, listing_units):
    """Only homogeneous packs with confirmed counts; no mixed-set division."""
    numerator = parse_price(source_price) * positive_count(listing_units)
    divisor = positive_count(source_units)
    if numerator % divisor:
        raise ValueError('Fractional won price requires review')
    return parse_price(numerator // divisor)


def plan(*, channel, current, listing, source, store_quantity=None,
         store_confirmed=False, source_current=False, confirmed_match=False,
         homogeneous_pack=False, hold=False):
    def held(reason):
        return {'status': 'hold', 'reason': reason, 'changes': {}}

    if hold:
        return held('user_hold')
    if source is None:
        return held('supplier_missing')
    if not source_current:
        return held('refresh_supplier_snapshot')
    if not confirmed_match:
        return held('match_unconfirmed')
    try:
        if identity(listing) != identity(source):
            return held('capacity_or_formulation_mismatch')
        if not homogeneous_pack:
            return held('package_contents_unconfirmed')
        price = package_price(source['price'], source['units'], listing['units'])
    except (ValueError, KeyError) as exc:
        return held(str(exc))
    if type(source.get('soldout')) is not bool:
        return held('supplier_status_unknown')
    if source['soldout'] and (not store_confirmed or type(store_quantity) is not int or store_quantity < 0):
        return held('confirm_physical_stock_in_listing_units')
    return build_plan(channel=channel, current=deepcopy(current),
                      source={'price': price, 'soldout': source['soldout']},
                      store_quantity=store_quantity if source['soldout'] else 0,
                      confirmed_match=True)


def option_plan(*, channel, current, rows, expected_option_ids, **context):
    """Each option supplies listing/source/store evidence; no partial lists.

    Outputs absolute option selling prices, never guesses store base/add-on prices.
    The browser adapter must map these totals to base + option additions.
    """
    held = lambda reason: {'status': 'hold', 'reason': reason, 'changes': {}}
    ids = [r['id'] for r in rows]
    if not ids or len(set(ids)) != len(ids) or set(ids) != set(expected_option_ids):
        return held('complete_unique_option_mapping_required')
    plans = {}
    for row in rows:
        args = {**context, **{k: v for k, v in row.items() if k != 'id'}}
        p = plan(channel=channel, current={}, **args)
        if p['status'] == 'hold':
            return held(f"{row['id']}: {p['reason']}")
        plans[row['id']] = p['changes']
    changes = {'option_stock': {k: p['stock'] for k, p in plans.items()},
               'option_total_prices': {k: p['sale_price'] for k, p in plans.items()}}
    if channel == 'cafe24':
        soldout = all(p['stock'] == 0 for p in plans.values())
        changes.update(replacement_enabled=soldout,
                       replacement_text='[품절]' if soldout else '',
                       soldout_display_enabled=True)
    return {'status': 'ready_for_ui_verification', 'changes': changes,
            'preserve': ['discount_amount_or_rate', 'discount_dates', 'discount_conditions'],
            'review': ['Map option totals to verified base price and option additions']}
