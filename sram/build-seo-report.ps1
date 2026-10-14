param(
    [Parameter(Mandatory=$true)][string]$ProgressPath,
    [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$data = Get-Content -LiteralPath $ProgressPath -Raw -Encoding UTF8 | ConvertFrom-Json
$items = @($data.items)
$labels = @{
    verified='저장 확인'; unavailable_redirect='접근 불가·이전 상품으로 이동'
    deleted_on_platform='플랫폼 삭제 안내'; not_found_all_status_search='전체 상태·기간 검색 결과 없음'
    pending='미처리'
}
$keys = @{}
foreach ($item in $items) {
    $key = "$($item.channel):$($item.product_id)"
    if ($keys.ContainsKey($key)) { throw "중복 상품: $key" }
    if ($item.channel -notin @('cafe24','smartstore')) { throw "알 수 없는 플랫폼: $key" }
    if (-not $labels.ContainsKey([string]$item.status)) { throw "알 수 없는 상태: $key" }
    $keys[$key] = $true
}
function Encode($value) { [System.Net.WebUtility]::HtmlEncode([string]$value) }
function MakeRows($records) {
    foreach ($item in $records) {
        $channel = if ($item.channel -eq 'cafe24') {'카페24'} else {'스토어팜'}
        "<tr><td>$channel</td><td>$(Encode $item.product_id)</td><td>$(Encode $item.name)</td><td>$(Encode $labels[$item.status])</td></tr>"
    }
}
$done = @($items | Where-Object status -eq 'verified')
$exceptions = @($items | Where-Object status -ne 'verified')
$cf = @($done | Where-Object channel -eq 'cafe24').Count
$ss = @($done | Where-Object channel -eq 'smartstore').Count
$allRows = (MakeRows $items) -join "`n"
$exceptionRows = (MakeRows $exceptions) -join "`n"
$head = '<tr><th>플랫폼</th><th>상품번호</th><th>대상 식별명</th><th>결과</th></tr>'
$html = @"
<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>SRAM 검색 최적화 결과</title>
<style>body{font:16px/1.65 'Malgun Gothic',sans-serif;max-width:1150px;margin:40px auto;padding:0 24px;background:#f5f7fa;color:#203040}section{background:white;border:1px solid #dde3e9;border-radius:12px;padding:24px;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd}th{background:#eaf0f5}img{max-width:100%}.count{font-size:24px;font-weight:bold}</style></head><body>
<h1>SRAM MTB·ROAD 검색 최적화 결과</h1><p>$(Encode $data.date) · YBBIKE · 신규 등록 2건 포함</p>
<section><p class="count">저장 확인 $($done.Count)건 / 대상 $($items.Count)건</p><p>카페24 $cf 건 · 스토어팜 $ss 건 · 미반영 $($exceptions.Count)건</p><p>플랫폼별 등록 건수입니다. 동일 제품의 양 채널 등록은 각각 집계했습니다.</p></section>
<section><h2>작업 범위와 검증</h2><p>상품명 → 검색어 → SEO 설명 순서로 정리했습니다. 카페24는 9개 검색정보 항목, 스토어팜은 대표·전용 상품명과 Page Title·Meta description을 반영했습니다. 태그는 일괄 변경하지 않았습니다.</p><p>가격·할인·재고·옵션·배송·상세본문·카테고리·브랜드·제조사는 이번 PE 수정 범위에서 제외했습니다.</p><p>카페24는 입력 전후 보호 항목 비교와 저장 후 SEO 제목 재조회, 스토어팜은 수정 완료 안내로 저장을 확인했습니다. 실제 검색 순위·유입 성과는 측정하지 않았습니다.</p><p>원장의 name은 대상 식별명입니다. 전체 상품의 변경 전후 본문은 원장에 수록되어 있지 않으므로 완전한 변경 이력으로 취급하지 않습니다.</p></section>
<section><h2>신규 등록 2건 교정</h2><p>카페24 13844 / 스토어팜 13810172390</p><p><b>스램 SRAM RED XG-1290 E1 카세트 스프라켓</b></p><p>복사 등록에 남아 있던 FORCE XG-1270 검색어와 XX SL 파워미터 SEO 제목·설명을 RED 카세트 정보로 교정했습니다. 신규 등록은 기존 번호의 미반영 기록과 별도로 관리합니다.</p></section>
<section><h2>미반영 목록</h2><table>$head$exceptionRows</table><p>검색 결과 없음은 삭제·단종 확정이 아닙니다. PM 가격·옵션 보류도 PE 작업으로 해결된 것으로 기록하지 않습니다.</p></section>
<section><h2>전체 작업 목록</h2><table>$head$allRows</table></section>
<section><h2>저장 증빙</h2><p>신규 RED 카세트 카페24 저장 확인</p><img src="cafe24-13844-seo.png" alt="RED 카세트 검색정보 저장 화면"><p>스토어팜 수정 완료 안내</p><img src="smartstore-13810172390.png" alt="스토어팜 수정 완료"></section>
</body></html>
"@
$html | Set-Content -LiteralPath $OutputPath -Encoding UTF8
[pscustomobject]@{total=$items.Count;verified=$done.Count;cafe24=$cf;smartstore=$ss;exceptions=$exceptions.Count;report=$OutputPath}
