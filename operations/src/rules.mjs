export const channels = ['cafe24', 'smartstore', 'coupang'];
export const states = ['pending', 'saved', 'verified', 'issue', 'handoff', 'uploaded'];

// API 접속·상품 저장을 하지 않는 검토 계획 생성기.
export function plan(item, channel, context = {}) {
  if (!channels.includes(channel)) throw new Error('지원하지 않는 채널');
  if (!Number.isInteger(item.quantity) || item.quantity < 0) throw new Error('재고 수량 오류');
  const handoff = reason => ({type: 'handoff', owner: 'user', reason});
  if (context.hurdle) return [handoff(context.hurdle)];
  if (channel === 'coupang') return [handoff('쿠팡 운영·재고·할인 조건 미확정')];
  if (context.sync !== 'independent' && context.sync !== 'reviewed')
    return [handoff('연동 범위와 수정 기준 미확인')];
  if (context.snapshotCurrent !== true) return [handoff('과거 실물 수량: 판매·입출고 반영 후 재확인 필요')];
  if (context.matched !== true) return [handoff('모델·품번·옵션 대응 확인 필요; 신규 업로드는 사용자 담당')];
  if (!Array.isArray(context.options) || context.options.length === 0)
    return [handoff('대상 상품의 전체 옵션 목록 확인 필요')];
  if (context.options.filter(o => o.key === item.option).length !== 1)
    return [handoff('매장 재고 옵션이 정확히 하나로 연결되지 않음')];
  if (new Set(context.options.map(o => o.key)).size !== context.options.length)
    return [handoff('중복 옵션 키')];
  const actions = context.options.map(o => ({type: 'stock', owner: 'assistant', option: o.key,
    quantity: o.key === item.option ? item.quantity : 0,
    selling: o.key === item.option && item.quantity > 0}));
  actions.push({type: 'shipping', owner: 'assistant', mode: 'paid', amount: 3000});
  if (!Number.isInteger(context.regularTotal) || context.regularTotal <= 0 || context.regularTotal % 5)
    actions.push(handoff('옵션 추가금을 포함한 정상가·원단위 처리 확인 필요'));
  else actions.push({type: 'discount', owner: channel === 'cafe24' ? 'user' : 'assistant',
    regularTotal: context.regularTotal, targetTotal: context.regularTotal * 4 / 5,
    percent: 20, replaceExisting: true});
  if (channel === 'cafe24') actions.push({type: 'regular_price_check', owner: 'assistant',
    note: '정상가 변경 시 소비자가·판매가 함께 관리. 할인은 사용자 담당.'});
  actions.push({type: 'verify', owner: 'assistant', checks: ['saved_values', 'storefront_price', 'options', 'shipping', 'sync_persistence_if_linked']});
  return actions;
}

export function verified(evidence) {
  return evidence?.saved === true && evidence?.storefront === true &&
    evidence?.price === true && evidence?.stock === true && evidence?.shipping === true &&
    (evidence?.linked === false || (evidence?.linked === true && evidence?.syncPersistence === true));
}
