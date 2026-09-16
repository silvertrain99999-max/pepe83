"""Supplier-first route resolution. Offline; never executes or edits shops."""
import argparse
import json
from pathlib import Path

SUPPLIER_IDS = ('trek', 'odbike', 'glnco', 'nnxsports', 'sports55', 'hlsc')


def resolve(supplier, brand):
    if supplier not in SUPPLIER_IDS:
        return {'status': 'hold', 'reason': 'unknown_supplier'}
    config = json.loads(Path(__file__).with_name(supplier + '.json').read_text(encoding='utf-8'))
    route = config['brands'].get(brand)
    if route is None:
        return {'status': 'hold', 'reason': 'brand_not_assigned_to_supplier'}
    if route['status'] != 'planner_ready':
        return {'status': 'hold', 'reason': 'supplier_brand_rules_not_implemented',
                'supplier': supplier, 'brand': brand}
    return {'status': 'planner_ready', 'supplier': supplier, 'brand': brand,
            'source_url': config['url'], **route}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='공급사와 브랜드에 대응하는 변경안 생성 코드 조회')
    parser.add_argument('supplier', choices=SUPPLIER_IDS)
    parser.add_argument('brand')
    args = parser.parse_args()
    print(json.dumps(resolve(args.supplier, args.brand), ensure_ascii=False, indent=2))
