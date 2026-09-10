// 사용자가 9월10~11일 확인했다고 보고한 역사적 실물 목록. 현재 재고가 아님.
const rows = [
  ['midloader-6l','미드로더 6L',null,'그린',1,'11002','687730574'],
  ['cagepack','케이지팩','TC2298B','블랙옐로',1,'3531','486646623'],
  ['escape-l','이스케이프 POD L','TEP-LB','850cc',1,'11012','4867505469'],
  ['modula-ii','모듈라 케이지 II',null,'블랙-실버',1,'3791','507055390'],
  ['modula-java','모듈라 자바 케이지','TMD07B','기본',2,null,'507059047'],
  ['ninja-z','닌자 마스터 케이지 Z','TNJC-Z','기본',2,'11950','5609387486'],
  ['ninja-sk','닌자 마스터 케이지 SK',null,'기본',1,'11880','5540964455'],
  ['ninja-sk-plus','닌자 마스터 케이지 SK+',null,'Righty',1,'11949','5609385799'],
  ['modula-ex','모듈라 케이지 EX','TMD05B','블랙',2,'3787','507027375'],
  ['aero-wedge','에어로 웨지 팩 Large',null,'스트랩',1,'10756','4888021280'],
  ['utf-light','UTF 라이트 바','TC1042','기본',2,'13164','8324224616'],
  ['cagemount-2','케이지마운트 2','TCM02','기본',1,null,null],
  ['ninja-cagemount','닌자+ 케이지마운트',null,'일반형·모델 확인 필요',1,null,null],
  ['versamount','버사마운트',null,'기본',1,'11718','5351484510'],
  ['ninja-airtag','닌자+ 케이지마운트 for AirTag',null,'에어태그용',1,null,'6941503801'],
  ['alt-position','ALT-Position 케이지 마운트',null,'기본',1,'6914','2799965270'],
  ['x15','X-15 어댑터',null,'기본',1,'3788','507029792'],
  ['rain-rx-ex','RX 트렁크백 EX 레인커버',null,'RX EX 전용',1,'3880',null]
];
export const inventory = rows.map(([id,name,sku,option,quantity,cafe24,smartstore]) => ({
  id,name,sku,option,quantity,
  channels: {
    cafe24: {productId:cafe24, stockShipping:cafe24?'saved':'handoff', discount:'handoff', verification:'pending'},
    smartstore: {productId:smartstore, stockShipping:smartstore?'saved':'handoff', discount:smartstore?'saved':'handoff', verification:'pending'},
    coupang: {productId:null, stockShipping:'pending', discount:'pending', verification:'pending'}
  }
}));
inventory.find(i=>i.id==='aero-wedge').channels.smartstore.discount='issue';
inventory.find(i=>i.id==='cagemount-2').channels.smartstore.stockShipping='uploaded';
export const metadata = {brand:'TOPEAK', period:'사용자 보고: 2026-09-10~11', historicalSnapshot:true,
  allocation:'카페24·스토어팜 동일수량, 주문 후 사용자 수동차감',
  userReview:'토픽 전 상품 확인 완료 보고; 개별 미적용 해결 여부와 구분',
  caveat:'saved는 저장 이력이며 판매 화면 검증 완료가 아님. 쿠팡은 미적용.'};
