"""Offline policy gate. No network, browser, uploads or shop writes.

Input evidence must be collected and confirmed by the operator; this module
does not certify observations or infer product identity from names.
"""
import argparse
import json
from copy import deepcopy
from pathlib import Path

VERSION = '2026-09-16'
USER_ONLY = {'stop_sale', 'resume_sale', 'delete', 'upload', 'create_product'}
ALLOWED = {'sync', 'seo', 'correction', 'today_shipping'}
SEO_FIELDS = {'page_title', 'meta_description', 'tags', 'name', 'category',
              'brand', 'attributes'}
STOPPED = {'판매중지', 'stopped', 'SUSPENSION'}


def quantity(value):
    return type(value) is int and value >= 0


def plan(item, previous=None):
    """Return either a complete review plan or a handoff with NO changes.

    Never call legacy supplier planners directly from a live adapter.
    Evidence revisions are operator-issued: retries do not make new evidence.
    """
    current = item.get('current', {})
    result = {'policy_version': VERSION, 'product_id': item.get('product_id'),
              'name': current.get('name'), 'supplier': item.get('supplier'),
              'brand': item.get('brand'), 'checked_at': item.get('checked_at'),
              'evidence_revision': item.get('evidence_revision'),
              'before': deepcopy(current), 'changes': {}, 'owner': 'assistant',
              'status': 'hold', 'reason': None,
              'preserve': ['discount', 'discount_dates', 'discount_conditions'],
              'verification': {'saved': False, 'reread': False}}

    def hold(reason, status='hold'):
        result.update(status=status, reason=reason, owner='user', changes={})
        result['question'] = item.get('question') or reason
        result['source_evidence'] = deepcopy(item.get('source', {}))
        return result

    if previous and previous.get('product_id') == item.get('product_id'):
        if (previous.get('status') in {'hold', 'handoff'}
                and previous.get('evidence_revision') == item.get('evidence_revision')
                and item.get('user_recheck') is not True):
            return hold('보류 유지: 새 근거 또는 사용자 재검토 지시 필요')
    actions = item.get('actions', ['sync'])
    if not isinstance(actions, list) or not actions or any(not isinstance(a, str) for a in actions):
        return hold('작업 종류 확인 필요')
    if set(actions) & USER_ONLY or current.get('status') in STOPPED:
        return hold('판매중지 설정·해제, 삭제, 신규 업로드는 사용자 담당', 'handoff')
    if set(actions) - ALLOWED:
        return hold('합의되지 않은 작업')
    if not item.get('product_id') or not item.get('checked_at') or not item.get('evidence_revision'):
        return hold('상품번호·확인일·근거 버전 필요')
    registry = Path(__file__).resolve().parent.parent / 'suppliers'
    supplier = item.get('supplier')
    if supplier not in ('trek', 'odbike', 'glnco', 'nnxsports', 'sports55', 'hlsc'):
        return hold('공급사 미확인')
    config = json.loads((registry / (supplier + '.json')).read_text(encoding='utf-8'))
    if item.get('brand') not in config['brands']:
        return hold('공급사와 브랜드 대응 미확인')
    if item.get('match_confirmed') is not True or item.get('all_options_confirmed') is not True:
        return hold('모델·용량·색상·옵션·포장 단위 기본 대조 후 불명확: 즉시 인계')
    if current.get('status') not in {'판매중', '품절', 'selling', 'soldout'}:
        return hold('현재 판매상태 확인 필요')
    channel = item.get('channel')
    if channel not in {'smartstore', 'cafe24'}:
        return hold('채널별 표현 미합의')
    changes = {}
    if 'sync' in actions:
        source = item.get('source', {})
        if source.get('current') is not True or source.get('listed') is not True:
            return hold('본사 미등록 또는 최신 확인 불가: 단종·품절로 추정 금지')
        # Each row represents an exact sellable option/package, never a fuzzy name.
        rows = item.get('rows', [])
        expected = current.get('option_ids')
        if not isinstance(expected, list) or not expected or len(set(expected)) != len(expected):
            return hold('현재 전체 옵션 목록 필요 (옵션 없는 상품은 default)')
        ids = [row.get('id') for row in rows]
        if len(ids) != len(set(ids)) or set(ids) != set(expected):
            return hold('전체 옵션 대응 누락·중복')
        targets = {}
        for row in rows:
            if row.get('confirmed') is not True:
                return hold('옵션별 근거 미확인')
            available = row.get('supplier_in_stock')
            if type(available) is not bool:
                return hold('본사 재고 미확인')
            if available:
                if supplier == 'sports55':
                    stock = 20
                else:
                    policy = item.get('supplier_stock_policy', {})
                    if policy.get('confirmed') is not True or not quantity(policy.get('quantity')) or policy['quantity'] == 0:
                        return hold('해당 공급사의 본사 입고 수량 정책 확인 필요')
                    stock = policy['quantity']
            else:
                if row.get('store_confirmed') is not True or not quantity(row.get('store_quantity')):
                    return hold('매장재고 미확인: 누락을 0으로 간주하지 않음')
                stock = row['store_quantity']
            price = row.get('base_price')
            if type(price) is not int or price <= 0 or row.get('price_confirmed') is not True:
                return hold('기본 판매가·포장 환산·옵션 금액 확인 필요')
            targets[row['id']] = {'stock': stock, 'base_price': price}
        changes['options'] = targets
        whole_soldout = all(row['stock'] == 0 for row in targets.values())
        changes['availability'] = '품절' if whole_soldout else '판매중'
        if channel == 'cafe24':
            changes['soldout_display_enabled'] = True
            changes['replacement_enabled'] = whole_soldout
            changes['replacement_text'] = '[품절]' if whole_soldout else ''
    for action in ('seo', 'correction'):
        if action in actions:
            proposal = item.get(action, {})
            fields = proposal.get('fields', {})
            if proposal.get('confirmed') is not True or not fields or set(fields) - SEO_FIELDS:
                return hold('검색설정·오표기 정정 근거 또는 수정 범위 미확인')
            for key, value in fields.items():
                if key in changes and changes[key] != value:
                    return hold('동일 필드 변경안 충돌')
                changes[key] = deepcopy(value)
    if 'today_shipping' in actions:
        shipping = item.get('shipping', {})
        if (shipping.get('store_confirmed') is not True
                or not quantity(shipping.get('store_quantity')) or shipping['store_quantity'] == 0
                or not shipping.get('confirmed_cutoff')):
            return hold('오늘출발 실재고·출고 기준시간 확인 필요')
        changes['today_shipping'] = {'enabled': True, 'cutoff': shipping['confirmed_cutoff']}
    result.update(status='ready_for_review', changes=changes)
    return result


def verified(result, *, saved=False, reread=False):
    """A plan or save alone never counts as completed."""
    output = deepcopy(result)
    output['verification'] = {'saved': saved is True, 'reread': reread is True}
    if output['status'] == 'ready_for_review' and saved is True and reread is True:
        output['status'] = 'verified'
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='공통 상품관리 변경안·인계 목록 생성 (온라인 수정 없음)')
    parser.add_argument('input', help='JSON: items 배열 및 선택적 previous 배열')
    parser.add_argument('output', help='출력 JSON 경로')
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding='utf-8'))
    previous = {p['product_id']: p for p in data.get('previous', [])}
    results = [plan(i, previous.get(i.get('product_id'))) for i in data['items']]
    Path(args.output).write_text(json.dumps({'results': results,
        'handoff': [r for r in results if r['status'] in {'hold', 'handoff'}]},
        ensure_ascii=False, indent=2), encoding='utf-8')
