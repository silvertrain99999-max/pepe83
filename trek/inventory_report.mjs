import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "outputs/trek-inventory";
await fs.mkdir(outputDir, { recursive: true });

const wb = Workbook.create();
const sh = wb.worksheets.add("재고관리");
sh.showGridLines = false;
sh.tabColor = "#111111";

const headers = [
  "카테고리", "상품명", "SKU", "옵션", "본사 표시", "본사 기준수량", "매장 재고",
  "카페24 재고", "스토어팜 재고", "정가", "카페24 기존할인가", "스토어팜 기존할인가",
  "카페24 차이", "스토어팜 차이", "작업상태", "수정 제외", "최종 확인일", "비고", "출처"
];

// 상품관리에서 확인된 옵션별 데이터만 기록한다. 다른 공급처에는 이 표를 사용하지 않는다.
const rows = [
  ["가방", "트렉 안장 가방", "5318515", "블랙 / 1.73-2.23L", "50+", 50, 0, null, null, 79000, null, null, "신규등록 대기", "N", new Date("2026-09-22"), "양 채널 미등록", "TREK B2B"],
  ["가방", "트렉 핸들바 가방", "5317800", "블랙 / 1.7L", "0", 0, 0, 0, 0, 69000, null, null, "완료", "N", new Date("2026-09-22"), "품절 유지", "TREK B2B / 채널 확인"],
  ["가방", "트렉 핸들바 가방", "5317802", "세도나 레드 / 1.7L", "19", 19, 0, 19, 19, 69000, null, null, "완료", "N", new Date("2026-09-22"), "카페24 9→19, 스토어팜 10→19", "TREK B2B / 채널 확인"],
  ["가방", "트렉 어드벤처 프레임 가방", "", "2L", "0", 0, 0, null, 0, 189000, null, null, "완료", "N", new Date("2026-09-22"), "SKU 확인 필요, 스토어팜 품절", "TREK B2B / 스토어팜"],
  ["가방", "트렉 어드벤처 프레임 가방", "5323149", "2.6L", "11", 11, 0, null, 11, 189000, null, null, "완료", "N", new Date("2026-09-22"), "스토어팜 가격·재고 수정", "TREK B2B / 스토어팜"],
  ["가방", "트렉 어드벤처 트라이앵글 가방", "5323152", "단일", "재고 없음", 0, 0, null, 0, 119000, null, null, "품절 유지", "N", new Date("2026-09-22"), "본사 가용 재고 없음", "TREK B2B / 스토어팜"],
  ["가방", "트렉 싱글 패니어", "5315136", "단일", "0", 0, 0, null, null, 99000, null, null, "업로드 제외", "N", new Date("2026-09-22"), "입고 예정 없음", "TREK B2B"],
  ["가방", "트렉 어드벤처 탑 튜브 가방", "5325334", "단일", "50+", 50, 0, null, 50, 69000, null, null, "완료", "N", new Date("2026-09-22"), "스토어팜 19→50", "TREK B2B / 스토어팜"],
  ["가방", "본트래거 어드벤처 프레임 가방", "5263832", "1.31L", "15", 15, 0, null, null, 119000, null, 69000, "삭제상품 확인", "N", new Date("2026-09-22"), "과거 스토어팜 상품 삭제 상태", "TREK B2B / 스토어팜"],
  ["가방", "트렉 어드벤처 보스 풀 프레임 가방", "5288904", "단일", "재고 없음", 0, 0, null, 0, 139000, null, 39900, "품절 유지", "N", new Date("2026-09-22"), "기존 스토어팜 할인 유지", "TREK B2B / 스토어팜"],
  ["가방", "트렉 BITS 공구 가방", "5323565", "단일", "0", 0, 0, null, null, 39900, null, null, "업로드 제외", "N", new Date("2026-09-22"), "입고 예정 없음", "TREK B2B"],
  ["가방", "트렉 BITS 튜브 가방", "5323564", "단일", "0", 0, 0, null, null, 29900, null, null, "업로드 제외", "N", new Date("2026-09-22"), "입고 예정 없음", "TREK B2B"],
  ["타이어", "트렉 XR1", "", "16인치", "", null, 6, null, null, null, null, null, "본사 재고 확인", "N", new Date("2026-09-22"), "매장 보유", "사용자 제공"],
  ["타이어", "트렉 XR1", "", "20인치", "", null, 1, null, null, null, null, null, "본사 재고 확인", "N", new Date("2026-09-22"), "매장 보유", "사용자 제공"],
  ["타이어", "트렉 XR1", "", "24인치", "", null, 2, null, null, null, null, null, "본사 재고 확인", "N", new Date("2026-09-22"), "매장 보유", "사용자 제공"],
  ["타이어", "Connection Comp", "", "26인치", "", null, 1, null, null, null, null, null, "SKU 확인 필요", "N", new Date("2026-09-22"), "매장 보유", "사용자 제공"],
  ["타이어", "Connection Comp", "", "29인치", "", null, 1, null, null, null, null, null, "SKU 확인 필요", "N", new Date("2026-09-22"), "매장 보유", "사용자 제공"],
  ["타이어", "H2 Comp", "", "700x32", "", null, 1, null, null, null, null, null, "SKU 확인 필요", "N", new Date("2026-09-22"), "매장 보유", "사용자 제공"],
  ["타이어", "AW1", "", "700x25", "", null, 2, null, null, null, null, null, "SKU 확인 필요", "N", new Date("2026-09-22"), "매장 보유", "사용자 제공"],
  ["타이어", "Kwaremont Comp HCL", "", "700x32", "", null, 4, null, null, null, null, null, "SKU 확인 필요", "N", new Date("2026-09-22"), "매장 보유", "사용자 제공"],
  ["안장", "트렉 안장 젤 커버 NEW", "", "로드 타입", "", null, 2, null, null, null, null, null, "수정 제외", "Y", new Date("2026-09-22"), "가격·옵션·수량 보호", "사용자 제공"],
  ["안장", "트렉 안장 젤 커버 NEW", "", "피트니스 타입", "", null, 1, null, null, null, null, null, "수정 제외", "Y", new Date("2026-09-22"), "가격·옵션·수량 보호", "사용자 제공"],
  ["안장", "트렉 안장 젤 커버 NEW", "", "컴포트 타입", "", null, 1, null, null, null, null, null, "수정 제외", "Y", new Date("2026-09-22"), "가격·옵션·수량 보호", "사용자 제공"],
  ["안장", "트렉 에올루스 엘리트 안장", "", "145mm", "", null, 1, null, null, null, null, null, "수정 제외", "Y", new Date("2026-09-22"), "가격·옵션·수량 보호", "사용자 제공"],
  ["안장", "트렉 본트래거 에올루스 엘리트 안장", "", "145mm", "", null, 1, null, null, null, null, null, "수정 제외", "Y", new Date("2026-09-22"), "가격·옵션·수량 보호", "사용자 제공"],
  ["안장", "트렉 본트래거 벌스 쇼트 엘리트 안장", "", "145mm", "", null, 1, null, null, null, null, null, "수정 제외", "Y", new Date("2026-09-22"), "가격·옵션·수량 보호", "사용자 제공"],
  ["안장", "트렉 본트래거 벌스 프로 안장", "", "145mm", "", null, 1, null, null, null, null, null, "수정 제외", "Y", new Date("2026-09-22"), "가격·옵션·수량 보호", "사용자 제공"],
  ["자전거", "트렉 프로칼리버 9.5 3세대 MTB 2027", "", "색상·사이즈별", "", null, null, null, null, null, null, null, "SKU 입력 필요", "N", new Date("2026-09-22"), "옵션별 SKU와 수량 입력 필요", "TREK B2B"]
];

sh.getRange("A2:S2").merge();
sh.getRange("A2").values = [["TREK 재고 관리표"]];
sh.getRange("A2:S2").format = { font: { name: "Arial", size: 15, bold: true, color: "#111111" } };
sh.getRange("A3:S3").merge();
sh.getRange("A3").values = [["TREK 상품관리 완료 후 갱신합니다. 할인가는 본사 할인이 아니라 YB샵의 기존 채널별 할인가입니다."]];
sh.getRange("A3:S3").format = { font: { name: "Arial", size: 10, italic: true, color: "#666666" } };

sh.getRange("A4:N4").values = [["총 옵션 수", "", "수정 필요", "", "확인 필요", "", "신규등록", "", "수정 제외", "", "본사와 카페24 불일치", "", "본사와 스토어팜 불일치", ""]];
sh.getRange("B4").formulas = [["=COUNTA(B7:B200)"]];
sh.getRange("D4").formulas = [["=COUNTIF(O7:O200,\"수정 필요\")"]];
sh.getRange("F4").formulas = [["=COUNTIF(O7:O200,\"본사 재고 확인\")+COUNTIF(O7:O200,\"SKU 확인 필요\")+COUNTIF(O7:O200,\"SKU 입력 필요\")+COUNTIF(O7:O200,\"삭제상품 확인\")"]];
sh.getRange("H4").formulas = [["=COUNTIF(O7:O200,\"신규등록 대기\")"]];
sh.getRange("J4").formulas = [["=COUNTIF(P7:P200,\"Y\")"]];
sh.getRange("L4").formulas = [["=COUNTIF(M7:M200,\">0\")+COUNTIF(M7:M200,\"<0\")"]];
sh.getRange("N4").formulas = [["=COUNTIF(N7:N200,\">0\")+COUNTIF(N7:N200,\"<0\")"]];
sh.getRange("A4:N4").format = { font: { name: "Arial", size: 10, bold: true }, verticalAlignment: "center" };
for (const c of ["A4", "C4", "E4", "G4", "I4", "K4", "M4"]) sh.getRange(c).format.fill = "#E7E6E6";
for (const c of ["B4", "D4", "F4", "H4", "J4", "L4", "N4"]) sh.getRange(c).format = { fill: "#FFF2CC", font: { name: "Arial", size: 11, bold: true, color: "#7F6000" }, horizontalAlignment: "center" };

sh.getRange("A6:S6").values = [headers];
sh.getRange("A7").write(rows);
const endRow = 6 + rows.length;
for (let r = 7; r <= endRow; r++) {
  sh.getRange(`M${r}`).formulas = [[`=IF(OR(F${r}=\"\",H${r}=\"\"),\"\",H${r}-F${r})`]];
  sh.getRange(`N${r}`).formulas = [[`=IF(OR(F${r}=\"\",I${r}=\"\"),\"\",I${r}-F${r})`]];
}

const table = sh.tables.add(`A6:S${endRow}`, true, "TrekInventoryTable");
table.style = "TableStyleMedium2";
table.showBandedRows = true;
table.showFilterButton = true;
sh.getRange(`A6:S${endRow}`).format.font = { name: "Arial", size: 10 };
sh.getRange("A6:S6").format = { fill: "#1F1F1F", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true };
sh.getRange(`A7:S${endRow}`).format.verticalAlignment = "center";
sh.getRange(`B7:B${endRow}`).format.wrapText = true;
sh.getRange(`D7:D${endRow}`).format.wrapText = true;
sh.getRange(`R7:S${endRow}`).format.wrapText = true;
sh.getRange(`F7:I${endRow}`).format.numberFormat = "#,##0";
sh.getRange(`J7:L${endRow}`).format.numberFormat = "#,##0\"원\"";
sh.getRange(`K7:L${endRow}`).format.fill = "#FFF2CC";
sh.getRange(`M7:N${endRow}`).format.numberFormat = "+0;-0;0";
sh.getRange(`Q7:Q${endRow}`).format.numberFormat = "yyyy-mm-dd";
sh.getRange("O7:O200").dataValidation = { rule: { type: "list", values: ["완료", "수정 필요", "본사 재고 확인", "SKU 확인 필요", "SKU 입력 필요", "신규등록 대기", "품절 유지", "업로드 제외", "삭제상품 확인", "수정 제외"] } };
sh.getRange("P7:P200").dataValidation = { rule: { type: "list", values: ["Y", "N"] } };
sh.getRange(`O7:O${endRow}`).conditionalFormats.add("containsText", { text: "필요", format: { fill: "#FFF2CC", font: { color: "#9C6500", bold: true } } });
sh.getRange(`O7:O${endRow}`).conditionalFormats.add("containsText", { text: "완료", format: { fill: "#E2F0D9", font: { color: "#375623", bold: true } } });
sh.getRange(`O7:O${endRow}`).conditionalFormats.add("containsText", { text: "제외", format: { fill: "#E7E6E6", font: { color: "#595959" } } });
sh.getRange(`P7:P${endRow}`).conditionalFormats.add("containsText", { text: "Y", format: { fill: "#FCE4D6", font: { color: "#C00000", bold: true } } });
sh.getRange(`M7:N${endRow}`).conditionalFormats.add("cellIs", { operator: "notEqual", formula: 0, format: { fill: "#F4CCCC", font: { color: "#9C0006", bold: true } } });

const widths = { A: 12, B: 31, C: 13, D: 22, E: 13, F: 13, G: 12, H: 13, I: 14, J: 13, K: 17, L: 18, M: 13, N: 14, O: 17, P: 11, Q: 14, R: 29, S: 23 };
for (const [col, width] of Object.entries(widths)) sh.getRange(`${col}:${col}`).format.columnWidth = width;
sh.getRange("2:2").format.rowHeight = 25;
sh.getRange("3:3").format.rowHeight = 20;
sh.getRange("6:6").format.rowHeight = 32;
sh.freezePanes.freezeRows(6);
sh.freezePanes.freezeColumns(4);

wb.recalculate();
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 100 }, summary: "final formula error scan" });
console.log(errors.ndjson);
const preview = await wb.render({ sheetName: "재고관리", range: `A1:S${endRow}`, scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/trek-inventory-preview.png`, new Uint8Array(await preview.arrayBuffer()));
const out = await SpreadsheetFile.exportXlsx(wb);
await out.save(`${outputDir}/TREK_재고관리표.xlsx`);
