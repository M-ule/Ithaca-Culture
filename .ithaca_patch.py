from pathlib import Path
import re, sys
p=Path('index.html')
s=p.read_text(encoding='utf-8')
original=s

def must_replace(old,new,count=1,label='replacement'):
    global s
    found=s.count(old)
    if found < count:
        raise SystemExit(f'{label}: expected at least {count}, found {found}')
    s=s.replace(old,new,count)

# Require the restored pre-final baseline, so this patch cannot silently run on the wrong version.
required=[
    "metricBox('생산 계획 부족',shortageValues,'metric-wide2')",
    "모든 생산 건물 0채",
    "count:0,mode:i.stage===2?30",
    "<label data-tip-key=\"상세 설정 적용\"><input id=\"detailEnabled\" type=\"checkbox\"> 상세 설정 적용</label>",
    "$('cityView').textContent=S.cityView?'상세 숨기기':'상세 보기';",
]
for x in required:
    if x not in s: raise SystemExit('baseline assertion failed: '+x[:80])

# Reset defaults.
must_replace('모든 생산 건물 0채','모든 생산 건물 1채',label='reset note')
must_replace("count:0,mode:i.stage===2?30","count:1,mode:i.stage===2?30",label='reset count')

# Help text requested in this chat.
repls={
"'불가사의':'선택한 불가사의의 보너스를 계산에 반영합니다. 보너스 적용 레벨에 따라 드라크마 생산 보너스와 추가 일반 일꾼·어부가 달라집니다.',":"'불가사의':'선택한 불가사의 종류에 따라 적용되는 보너스가 달라집니다.',",
"'중간 자원':'완료된 생산 주기만 생산량에 반영합니다. 상품 생산에 필요한 양을 계산하며, 불가사의가 직접 요구하는 중간 자원은 ‘불가사의 목표’에서 반영합니다.',":"'중간 자원':'상품 생산에 필요한 양을 계산하며, 불가사의가 직접 요구하는 중간 자원은 ‘불가사의 목표’에서 반영합니다. 생산량은 완료된 생산 주기만 반영합니다.',",
"'상품':'완료된 생산 주기만 생산량에 반영합니다. 생산에 필요한 중간 자원·매스틱을 차감하며, 현재 보유량은 ‘불가사의 목표’ 계산에 사용됩니다.',":"'상품':'생산에 필요한 중간 자원·매스틱을 차감하며, 현재 보유량은 ‘불가사의 목표’ 계산에 사용됩니다. 생산량은 완료된 생산 주기만 반영합니다.',",
"'목표 달성 현황':'현재 레벨부터 목표 레벨까지 필요한 중간 자원·상품과 보유량을 비교합니다. 상품이 부족하면 그 상품을 만드는 데 필요한 중간 자원도 자동으로 필요량에 추가합니다.',":"'목표 달성 현황':'현재 레벨부터 목표 레벨까지 필요한 중간 자원·상품과 예상 보유량을 비교합니다. 부족한 상품의 생산에 필요한 중간 자원도 자동으로 반영합니다.',",
"'수면 대비 자원 확보':'생산 계산기에 입력한 현재 건물 구성으로 취침 전까지 필요한 재료를 확보할 수 있는지 확인합니다. 생산력과 수면 중 필요량을 함께 비교하며, 수면 중 기초 자원 생산은 계산하지 않습니다.',":"'수면 대비 자원 확보':'수면 중 생산에 필요한 자원을 취침 전까지 충분히 확보할 수 있는지 확인합니다. 수면 중 기초 자원 생산은 제외합니다. 생산력 수치와 부족 규모는 아래 ‘목표 레벨 생산력 비교’를 참고하세요.',",
"'자원':'수면 전에 확보할 수 있는 양과 수면 중 필요한 양을 비교하는 재료입니다.',":"'자원':'수면 중 생산에 필요한 자원입니다.',",
"'생산 계획 부족':'현재 입력한 생산 계획을 실행할 때, 보유량과 예상 생산량을 반영해도 상위 생산에 필요한 재료가 부족한 항목입니다.',":"'조정 필요 생산 항목':'현재 생산 설정으로 필요한 양을 충당하지 못하는 생산 항목입니다. 표시된 항목은 건물 수·생산 방식·운영 시간 등을 조정해 보세요.',",
"'생산력 부족 항목':'불가사의 목표 레벨까지 필요한 수량을 운영 시간 안에 생산하기에 현재 생산력이 부족한 항목입니다.',":"'생산력 부족 항목':'현재 생산력으로 목표 레벨까지 필요한 수량을 운영 시간 내 생산하지 못하는 항목입니다.',",
}
for a,b in repls.items(): must_replace(a,b,label='tooltip '+a[:18])

# Retired summary tooltip definitions are removed completely.
s=s.replace("'예상 생산 시간':'목표까지 부족한 중간 자원·상품을 현재 건물 구성으로 생산하는 데 걸리는 예상 시간입니다.',\n",'')
s=s.replace("'최장 소요':'필요한 양을 확보하는 데 가장 오래 걸리는 항목과 시간을 표시합니다.',\n",'')

# Put 상세 설정 적용 help before the checkbox.
must_replace(
    '<label data-tip-key="상세 설정 적용"><input id="detailEnabled" type="checkbox"> 상세 설정 적용</label>',
    '<label><span class="term-wrap"><span class="term-text">상세 설정 적용</span><span class="info-tip" tabindex="0" role="button" aria-label="상세 설정 적용 설명" data-tip="같은 생산 항목의 건물 구성이 서로 다를 때 켭니다. 끄면 기본 설정으로 계산하며, 입력해 둔 상세 설정 값은 그대로 남아 있습니다.">i</span></span> <input id="detailEnabled" type="checkbox"></label>',
    label='detail toggle help position')

# Product is a final output: omit meaningless balance/time columns only for stage 2.
setup_start=s.index('function setupProduction(){')
setup_end=s.index('\nfunction metricValue',setup_start)
setup_new="""function setupProduction(){let html='';for(let st=0;st<3;st++){const title=['기초 자원','중간 자원','상품'][st],items=D.items.filter(i=>i.stage===st),labels=['생산 항목','레벨','생산 방식','건물 수','운영 시간(h)','현재 보유량','예상 생산량','소비·필요량'];if(st!==2)labels.push({label:'잔여/부족',tip:'보유량 + 예상 생산량 − 상위 생산 필요량입니다. 양수면 잔여, 음수면 부족입니다.'},'소요 시간');html+='<div class=\"card\" id=\"stage'+st+'\"><div class=\"sectionbar\"><h2>'+termHtml(title)+'</h2><span class=\"section-actions\"><button data-detail-group=\"'+st+'\">'+title+' 상세 설정</button>'+infoIcon('상세 설정',TOOLTIPS['상세 설정'])+'</span></div><div class=\"wrap\"><table class=\"prodtable\">'+head(labels)+'<tbody>';for(const i of items){const s=S.items[i.id];html+='<tr data-item=\"'+i.id+'\">'+td(i.name+(s.detail?'<span class=\"badge\">상세</span>':''))+td(inp(s.lv,'data-field=\"lv\" min=\"'+(st===2?4:1)+'\" max=\"6\" '+(s.detail?'disabled':'')))+td(st===0?'연속':selectMode(i.id,s,'data-field=\"mode\" '+(s.detail?'disabled':'')))+td(inp(s.detail?totals(i.id).count:s.count,'data-field=\"count\" min=\"0\" '+(s.detail?'disabled':'')))+td(inp(s.hours,'data-field=\"hours\" placeholder=\"기본\" '+(s.detail?'disabled':'')))+td(inp(s.stock,'data-field=\"stock\"'))+td('<b id=\"out_'+i.id+'\"></b>','calc detailcol')+td('<span id=\"use_'+i.id+'\"></span>','calc detailcol')+(st===2?'':td('<span id=\"remain_'+i.id+'\"></span>','calc')+td('<span id=\"needtime_'+i.id+'\"></span>','calc'))+'</tr>'}html+='</tbody></table></div></div>'}$('productionSections').innerHTML=html;labelInputs('productionSections');$('productionSections').querySelectorAll('thead tr').forEach(row=>[...row.children].forEach((th,j)=>{if(j===6||j===7)th.classList.add('detailcol')}));updateViews()}"""
s=s[:setup_start]+setup_new+s[setup_end:]

# Production summary: rename card and remove dead longest-time calculation.
slow=re.compile(r",needed=overview\.filter\(x=>x\.need>1e-8\);let slowValue=\['없음'\];if\(needed\.length\)\{const unresolved=needed\.find\(x=>x\.h===null\);if\(unresolved\)slowValue=\[\[unresolved\.i\.name,'생산 설정 확인'\]\];else\{const x=needed\.reduce\(\(a,b\)=>b\.h>a\.h\?b:a\);slowValue=\[\[x\.i\.name,time\(x\.h\)\]\]\}\}")
s,n=slow.subn('',s,count=1)
if n!=1: raise SystemExit('slow-time cleanup failed')
must_replace("metricBox('생산 계획 부족',shortageValues,'metric-wide2')","metricBox('조정 필요 생산 항목',shortageValues,'metric-wide2')",label='summary rename')

# Product rows no longer have remain_/needtime_ elements, so guard those updates.
old_loop="for(const i of D.items){const remaining=stock(i.id)+t[i.id].out-c[i.id];$('remain_'+i.id).textContent=fmt(remaining);$('remain_'+i.id).className=remaining<0?'bad':'ok';$('needtime_'+i.id).textContent=time(timeToAmount(i.id,Math.max(0,c[i.id]-stock(i.id))));$('out_'+i.id).textContent=fmt(t[i.id].out);"
new_loop="for(const i of D.items){const remaining=stock(i.id)+t[i.id].out-c[i.id];if(i.stage<2){$('remain_'+i.id).textContent=fmt(remaining);$('remain_'+i.id).className=remaining<0?'bad':'ok';$('needtime_'+i.id).textContent=time(timeToAmount(i.id,Math.max(0,c[i.id]-stock(i.id))))}$('out_'+i.id).textContent=fmt(t[i.id].out);"
must_replace(old_loop,new_loop,label='product recalc guard')

# Goal table product description, concise wording.
must_replace("{label:'상품',tip:'불가사의 목표에서 필요량을 확인하는 중간 자원·상품 항목입니다.'}","{label:'상품',tip:'목표 달성에 필요한 중간 자원·상품입니다.'}",label='goal product tooltip')

# Modal dialog tooltips must live in the modal top layer, not under it.
s=s.replace('z-index:10000;display:none;width:max-content','z-index:2147483647;display:none;width:max-content',1)
tip_start=s.index('function initTermTooltips()')
tip_end=s.index('\nfunction syncWonderLevels()',tip_start)
tip_new="""function initTermTooltips(){if($('termTooltip'))return;const box=document.createElement('div');box.id='termTooltip';box.className='term-tooltip';box.setAttribute('role','tooltip');document.body.appendChild(box);let active=null;const hide=()=>{box.classList.remove('show');active=null};const show=el=>{if(!el?.dataset.tip)return;const dialog=el.closest('dialog'),host=dialog||document.body;if(box.parentElement!==host)host.appendChild(box);active=el;box.textContent=el.dataset.tip;box.classList.add('show');box.style.left='12px';box.style.top='12px';requestAnimationFrame(()=>{const r=el.getBoundingClientRect(),b=box.getBoundingClientRect(),pad=12,bounds=dialog?dialog.getBoundingClientRect():{left:0,top:0,right:innerWidth,bottom:innerHeight};let left=r.left+r.width/2-b.width/2;left=Math.max(bounds.left+pad,Math.min(left,bounds.right-b.width-pad));let top=r.top-b.height-10;if(top<bounds.top+pad)top=r.bottom+10;top=Math.max(bounds.top+pad,Math.min(top,bounds.bottom-b.height-pad));box.style.left=left+'px';box.style.top=top+'px'})};document.addEventListener('pointerover',e=>{const el=e.target.closest?.('.info-tip');if(el)show(el)});document.addEventListener('pointerout',e=>{const el=e.target.closest?.('.info-tip');if(el&&!el.contains(e.relatedTarget))hide()});document.addEventListener('focusin',e=>{const el=e.target.closest?.('.info-tip');if(el)show(el)});document.addEventListener('focusout',e=>{if(e.target.closest?.('.info-tip'))hide()});document.addEventListener('click',e=>{const el=e.target.closest?.('.info-tip');if(el){e.preventDefault();e.stopPropagation();if(active===el&&box.classList.contains('show'))hide();else{el.focus({preventScroll:true});show(el)}}else hide()});addEventListener('scroll',hide,true);addEventListener('resize',hide)}"""
s=s[:tip_start]+tip_new+s[tip_end:]

# Final safety checks: do not allow the previously reintroduced summaries back in.
assert "metricBox('최장 소요'" not in s
assert "['예상 생산 시간'" not in s
assert "'최장 소요':" not in s
assert "'예상 생산 시간':" not in s
assert "if(st!==2)labels.push" in s and "if(i.stage<2)" in s
assert "metricBox('조정 필요 생산 항목',shortageValues,'metric-wide2')" in s
assert "['생산력 부족 항목',powerShortValues,'metric-wide3']" in s
assert "dialog=el.closest('dialog')" in s

p.write_text(s,encoding='utf-8')
print('patched',len(original.encode('utf-8')),'->',len(s.encode('utf-8')),'bytes')
