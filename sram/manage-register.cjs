// Local register maintenance only. Never connects to or modifies selling channels.
const fs = require('node:fs');
const path = require('node:path');
const file = path.join(__dirname, 'registered-products.json');
const data = JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const seen = new Set(), codes = new Set();
const counts = {products:data.products.length,cafe24:0,smartstore:0,linked:0,new_products:5};
for (const p of data.products) {
  if (!p.code || codes.has(p.code)) throw Error('관리코드 중복/누락: '+p.code);
  codes.add(p.code);
  const channels = new Set();
  for (const l of p.listings) {
    if (!['cafe24','smartstore'].includes(l.channel) || !/^\d+$/.test(l.id)) throw Error('채널/상품번호 오류');
    const key = l.channel+':'+l.id;
    if (seen.has(key)) throw Error('상품번호 중복: '+key);
    if (!l.observed_date || !l.source) throw Error('확인일/근거 누락: '+key);
    seen.add(key); channels.add(l.channel); counts[l.channel]++;
  }
  if (channels.size===2) counts.linked++;
}
for(const key of ['products','cafe24','smartstore','linked'])
  if(counts[key]!==data.counts[key]) throw Error('집계 불일치 '+key+' — JSON counts도 갱신하세요');
const esc=s=>String(s??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cell=(p,c)=>p.listings.filter(l=>l.channel===c).map(l=>`<a href="${c==='cafe24'?'https://koolling.cafe24.com/disp/admin/shop1/product/ProductRegister?product_no='+l.id:'https://smartstore.naver.com/ybbike/products/'+l.id}">${l.id}</a><small>${esc(l.observed_date)} · ${esc(l.registration)}</small>`).join('<br>')||'미연결';
const rows=data.products.map(p=>`<tr data-date="${esc(p.listings.map(l=>l.observed_date).sort().at(-1))}"><td>${esc(p.code)}</td><td>${esc(p.name)}<small>${esc(p.category_code||'분류 미확인')}</small></td><td>${cell(p,'cafe24')}</td><td>${cell(p,'smartstore')}</td><td>${p.supplier_url?`<a href="${esc(p.supplier_url)}">본사</a>`:'연결 미확인'}</td><td>${p.listings.map(l=>`<small>${esc(l.channel)}: ${esc(l.pm?.status||'상세 기록 대조 필요')}</small>`).join('')}</td><td>${p.listings.map(l=>`<small>${esc(l.channel)}: ${esc(l.seo?.date)} ${esc(l.seo?.status||'점검 기록 없음')}</small>`).join('')}</td></tr>`).join('');
const html=`<!doctype html><html lang="ko"><meta charset="utf-8"><title>SRAM 등록상품 기준표</title><style>body{font:15px system-ui;margin:30px;color:#24313d}h1{color:#b3202a}aside{background:#fff3d7;padding:18px;line-height:1.8}table{border-collapse:collapse;width:100%}td,th{padding:12px;border:1px solid #ddd;text-align:left}th{background:#edf1f4;position:sticky;top:0}small{display:block;color:#576574;margin-top:5px}input,button{padding:10px;margin:16px 8px 16px 0}a{color:#1763a3}</style><h1>SRAM 등록상품 기준표</h1><p>정리일 ${esc(data.compiled_at)} · 카페24 ${counts.cafe24}건 · 스토어팜 ${counts.smartstore}건 · 연결 ${counts.linked}종 · 관리 ${counts.products}행</p><aside>${esc(data.scope)}<br>미연결은 미등록 확정이 아닙니다. 과거 기록은 현재 가격·재고의 근거로 사용하지 않습니다.<br>카페24 13859의 앞변속기→뒷변속기 변경은 별도 이력으로 보존했습니다.</aside><input id="q" placeholder="상품명·상품번호 검색" size="45"><button id="recent">11월 12일 신규 5종</button><button id="all">전체</button><a href="registered-products.json">기준 데이터</a><table><thead><tr><th>코드</th><th>상품 / 분류</th><th>카페24</th><th>스토어팜</th><th>본사</th><th>상품관리</th><th>검색최적화</th></tr></thead><tbody>${rows}</tbody></table><script>let recent=false;function apply(){const q=document.querySelector('#q').value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q)||(recent&&r.dataset.date!=='2026-11-12'))}document.querySelector('#q').oninput=apply;document.querySelector('#recent').onclick=()=>{recent=true;apply()};document.querySelector('#all').onclick=()=>{recent=false;apply()};</script></html>`;
if(process.argv.includes('--render')) fs.writeFileSync(path.join(__dirname,'registered-products.html'),html);
console.log(JSON.stringify({valid:true,counts,rendered:process.argv.includes('--render')},null,2));
