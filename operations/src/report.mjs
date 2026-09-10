import {writeFile, mkdir} from 'node:fs/promises';
import {inventory, metadata} from '../data/inventory.mjs';
const root = new URL('../reports/', import.meta.url);
await mkdir(root,{recursive:true});
const header = `# 토픽 매장 실물 재고\n\n${metadata.period}\n\n${metadata.caveat}\n\n실물 확인 당시 수량이며 현재 판매 가능 수량이 아닙니다.\n\n|상품|품번|옵션|수량|카페24 번호|스토어팜 번호|\n|---|---|---|---:|---|---|\n`;
const body=inventory.map(i=>`|${i.name}|${i.sku??'미확인'}|${i.option}|${i.quantity}|${i.channels.cafe24.productId??'미확인'}|${i.channels.smartstore.productId??'미확인'}|`).join('\n');
await writeFile(new URL('inventory.md',root),header+body+`\n\n합계: ${inventory.length}종 / ${inventory.reduce((n,i)=>n+i.quantity,0)}개\n`);
await writeFile(new URL('inventory.json',root),JSON.stringify({metadata,inventory},null,2));
console.log('reports/inventory.md 및 inventory.json 생성 완료');
