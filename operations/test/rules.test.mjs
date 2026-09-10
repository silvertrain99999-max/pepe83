import test from 'node:test';
import assert from 'node:assert/strict';
import {plan, verified} from '../src/rules.mjs';
import {inventory} from '../data/inventory.mjs';
const item=inventory[0];
const ctx={sync:'independent',snapshotCurrent:true,matched:true,regularTotal:90000,options:[{key:'그린'},{key:'블랙'}]};
test('실물 합계와 채널 저장 이력',()=>{
 assert.equal(inventory.length,18); assert.equal(inventory.reduce((n,i)=>n+i.quantity,0),22);
 assert.equal(inventory.filter(i=>i.channels.cafe24.stockShipping==='saved').length,14);
 assert.equal(inventory.filter(i=>i.channels.smartstore.stockShipping==='saved').length,15);
});
test('카페24 할인은 사용자, 미보유 옵션은0',()=>{
 const p=plan(item,'cafe24',ctx);
 assert.equal(p.find(a=>a.type==='discount').owner,'user');
 assert.equal(p.find(a=>a.option==='블랙').quantity,0);
 assert.equal(p.find(a=>a.type==='discount').targetTotal,72000);
});
test('연동·현재재고·모델 미확인은 실행안 대신 인계',()=>{
 for(const c of [{...ctx,sync:'unknown'},{...ctx,snapshotCurrent:false},{...ctx,matched:false}])
 assert.equal(plan(item,'smartstore',c)[0].type,'handoff');
 assert.equal(plan(item,'coupang',ctx)[0].type,'handoff');
});
test('허들은 즉시 인계하고 할인 중복을 금지',()=>{
 assert.equal(plan(item,'smartstore',{...ctx,hurdle:'저장 오류'}).length,1);
 assert.equal(plan(item,'smartstore',ctx).find(a=>a.type==='discount').replaceExisting,true);
});
test('저장 성공만으로 완료하지 않음',()=>{
 assert.equal(verified({saved:true}),false);
 const e={saved:true,storefront:true,price:true,stock:true,shipping:true,linked:false};
 assert.equal(verified(e),true); assert.equal(verified({...e,linked:true}),false);
});
test('사용자 보고 미적용과 신규 업로드 상태 보존',()=>{
 assert.equal(inventory.find(i=>i.id==='aero-wedge').channels.smartstore.discount,'issue');
 assert.equal(inventory.find(i=>i.id==='cagemount-2').channels.smartstore.stockShipping,'uploaded');
});
