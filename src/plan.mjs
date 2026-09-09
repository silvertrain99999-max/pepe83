import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';

export function plan(products) {
  const changes = [], reviews = [];
  const change = (id, field, before, after, optionId) => {
    if (before !== after) changes.push({id, ...(optionId ? {optionId} : {}), field, before, after});
  };
  const stock = (p, current, available, optionId) => {
    if (!Number.isInteger(current) || current < 0) throw new Error(`Invalid stock: ${p.id}`);
    if (available === false) change(p.id, 'stock', current, 0, optionId);
    else if (available === true && current === 0) change(p.id, 'stock', 0, 5, optionId);
    else if (available !== true) reviews.push({id:p.id, optionId, reason:'availability_unknown'});
  };
  for (const p of products) {
    if (p.matched !== true) { reviews.push({id:p.id,reason:'match_required'}); continue; }
    if (p.regularPrice != null) {
      if (!Number.isInteger(p.regularPrice) || p.regularPrice <= 0) throw new Error(`Invalid price: ${p.id}`);
      change(p.id, 'salePrice', p.salePrice, p.regularPrice);
    } else reviews.push({id:p.id,reason:'price_unknown'});
    const options = p.options ?? [];
    if (options.length) {
      for (const o of options) {
        if (o.matched !== true) {reviews.push({id:p.id,optionId:o.id,reason:'option_match_required'});continue;}
        stock(p,o.stock,o.available,o.id);
        if (o.confirmedExtraPrice != null) {
          if (!Number.isInteger(o.confirmedExtraPrice)) throw new Error(`Invalid option price: ${o.id}`);
          change(p.id,'extraPrice',o.extraPrice,o.confirmedExtraPrice,o.id);
        }
      }
    } else stock(p,p.stock,p.available);
    const inStock = options.length ? options.some(o=>o.matched === true && o.available === true) : p.available === true;
    if (p.status === '판매중지' && inStock) reviews.push({id:p.id,reason:'resume_review',note:'공급처 입고 확인. 판매중지 사유를 확인한 뒤 판매 재개 검토.'});
  }
  return {changes,reviews};
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(JSON.stringify(plan(JSON.parse(readFileSync(process.argv[2],'utf8'))),null,2));
}
