import { chromium } from 'playwright'
import assert from 'node:assert/strict'
const baseURL=process.argv[2]||process.env.BASE_URL||'http://127.0.0.1:8765'
const response=await fetch(`${baseURL}/data/report.json`)
assert(response.ok,'real report must be served')
const report=await response.json()
assert(report.nodes.length>0,'acceptance requires actual nonempty dataset')
const browser=await chromium.launch({headless:true})
try {
 const page=await browser.newPage({viewport:{width:1440,height:1080}})
 const failures=[]
 const external=[]
 page.on('request',request=>{if(!request.url().startsWith(baseURL+'/'))external.push(request.url())})
 page.on('pageerror',error=>failures.push(error.message))
 await page.goto(baseURL)
 await page.getByLabel('Поиск по gid').waitFor()
 const search=async gid=>{await page.getByLabel('Поиск по gid').fill(gid);await page.getByLabel('Поиск по gid').press('Enter');await page.getByRole('heading',{name:`Узел ${gid}`,exact:true}).waitFor()}
 assert.equal(await page.getByRole('button',{name:/из рейтинга$/}).count(),report.top_nodes.length,'all ranked nodes remain accessible')
 assert(report.top_nodes.length>=20,'case requires at least twenty priorities')
 const arbitraryStarted=Date.now()
 for(const fraction of [.17,.49,.83]){
  const sample=report.nodes[Math.floor((report.nodes.length-1)*fraction)]
  await search(sample.gid)
  const visibleEvidence=(await page.locator('.inspector .evidence').innerText()).trim()
  assert(visibleEvidence.length>0 && visibleEvidence.includes('Гипотеза'),'arbitrary gid has readable role evidence')
  if(visibleEvidence!==sample.evidence){
   const source=page.locator('.inspector .source-evidence')
   await source.locator('summary').click()
   assert.equal((await source.locator('p').first().innerText()).trim(),sample.evidence,'original calculated evidence remains available')
  }
  assert(await page.locator('.inspector .metrics').innerText(),'metrics are available for explanation')
 }
 const arbitraryGidSeconds=(Date.now()-arbitraryStarted)/1000
 assert(arbitraryGidSeconds<60,'three arbitrary accounts can be opened within one minute')
 await search(report.nodes.at(-1).gid)
 if(report.top_nodes.length){const id=report.top_nodes[0].gid;await page.getByRole('button',{name:`Открыть узел ${id} из рейтинга`,exact:true}).click();await page.getByRole('heading',{name:`Узел ${id}`,exact:true}).waitFor()}
 await page.getByRole('img',{name:'Направленный граф выбранного узла'}).waitFor()
 const connected=report.nodes.find(n=>report.edges.some(e=>e.src===n.gid||e.dst===n.gid))
 if(connected){await search(connected.gid);assert(await page.locator('.graph-edge path[marker-end]').count()>0,'directed links have arrows')}
 await page.getByRole('button',{name:'Кластеры',exact:true}).click()
 assert.equal(await page.getByRole('button',{name:'Кластеры',exact:true}).getAttribute('aria-pressed'),'true')
 await page.getByRole('button',{name:'Приблизить',exact:true}).click()
 await page.getByRole('button',{name:'Показать целиком',exact:true}).click()
 const linkedIds=new Set(report.edges.flatMap(e=>[e.src,e.dst]))
 const isolate=report.nodes.find(n=>!linkedIds.has(n.gid))
 if(isolate){await search(isolate.gid);await page.getByText('В этой выгрузке у узла нет связей. Это не доказывает отсутствие переводов за её пределами.',{exact:true}).waitFor()}
 const boundary=report.nodes.find(n=>n.boundary_censored)
 if(boundary){await search(boundary.gid);await page.getByText('Граница выгрузки: отсутствие исходящих не доказывает конечного получателя',{exact:true}).waitFor()}
 const temporal=report.nodes.find(n=>n.temporal?.incoming_profile&&n.next_data_requests?.length)
 if(temporal){
  await search(temporal.gid)
  await page.locator('.inspector-details > summary').filter({hasText:/^Временные признаки$/}).click()
  await page.getByRole('heading',{name:'Профиль входящих'}).waitFor()
  await page.getByText('Совпадение дат не доказывает, что переводились те же деньги.',{exact:true}).waitFor()
  await page.locator('.inspector-details > summary').filter({hasText:'Какие данные запросить дальше'}).click()
  await page.getByText(temporal.next_data_requests[0],{exact:true}).waitFor()
  if(temporal.temporal.synchronous_incoming) await page.getByRole('heading',{name:'Синхронные поступления'}).waitFor()
 }
 await page.locator('.header-menu > summary').filter({hasText:'Как читать анализ'}).click()
 assert(await page.getByRole('heading',{name:'Как устроен анализ'}).isVisible(),'method explanation is accessible')
 assert((await page.locator('.methodology').innerText()).includes('Данные →'),'analysis flow is explained')
 await page.locator('.header-menu > summary').filter({hasText:'Как читать анализ'}).click()
 await page.getByRole('button',{name:'Вся выборка',exact:true}).click()
 assert.equal(await page.getByRole('button',{name:/^Открыть узел \d+$/}).count(),Math.min(20,report.nodes.length),'initial exploration is paged')
 if(report.nodes.length>20){await page.getByRole('button',{name:'Показать ещё'}).click();assert.equal(await page.getByRole('button',{name:/^Открыть узел \d+$/}).count(),40,'more reveals twenty rows')}
 const choose=async(label,option)=>{await page.getByRole('combobox',{name:label}).click();await page.getByRole('option',{name:option,exact:true}).click()}
 await choose('Роль','Транзит')
 const outside=report.nodes.find(n=>n.role!=='transit')
 if(outside){await search(outside.gid);await page.getByRole('heading',{name:`Узел ${outside.gid}`,exact:true}).waitFor()}
 const firstCluster=report.clusters.find(c=>report.nodes.some(n=>n.cluster_id===c.cluster_id))
 await page.locator('.cluster-overview > summary').click()
 if(firstCluster){await page.getByRole('button',{name:`Исследовать кластер ${firstCluster.cluster_id}`}).click();assert(await page.getByRole('heading',{name:'Результаты исследования'}).evaluate(el=>el===document.activeElement),'cluster action focuses results')}
 await choose('Исходные узлы (seed)','Только исходные')
 await choose('Граница выгрузки','Граничные')
 assert(await page.getByRole('combobox',{name:'Роль'}).textContent()!=='Все','role filter remains active with other filters')
 await page.getByRole('button',{name:'Сбросить фильтры'}).click()
 assert((await page.getByRole('combobox',{name:'Роль'}).textContent()).includes('Все'),'reset clears role')
 const roleControl=page.getByRole('combobox',{name:'Роль'})
 await roleControl.focus()
 await roleControl.press('Enter')
 await page.getByRole('option',{name:'Транзит',exact:true}).press('Enter')
 assert((await roleControl.textContent()).includes('Транзит'),'keyboard selects a shadcn option')
 await page.getByRole('button',{name:'Сбросить фильтры'}).click()
 const firstResult=page.getByRole('button',{name:/^Открыть узел \d+$/}).first()
 const firstResultId=(await firstResult.getAttribute('aria-label')).replace('Открыть узел ','')
 await firstResult.click()
 await page.getByRole('heading',{name:`Узел ${firstResultId}`,exact:true}).waitFor()
 await page.getByRole('button',{name:/^Приоритеты/}).click()
 await search(report.top_nodes[0].gid)
 const dense=report.nodes.reduce((best,n)=>n.out_degree>best.out_degree?n:best,report.nodes[0])
 await search(dense.gid)
 const expectedOut=report.edges.filter(e=>e.src===dense.gid&&e.dst!==dense.gid).sort((a,b)=>b.sum_kzt-a.sum_kzt||(BigInt(a.dst)<BigInt(b.dst)?-1:1))
 if(expectedOut.length>6){
  let seen=[]
  for(let offset=0;offset<expectedOut.length;offset+=6){
   const labels=await page.locator('.graph-edge').evaluateAll(items=>items.map(item=>item.getAttribute('aria-label')))
   for(const edge of expectedOut.slice(offset,offset+6))assert(labels.some(label=>label.startsWith(`${edge.src} → ${edge.dst}:`)),'paged edge direction matches source')
   seen.push(...expectedOut.slice(offset,offset+6).map(e=>e.dst))
   if(offset+6<expectedOut.length)await page.getByRole('button',{name:'Следующие получатели',exact:true}).click()
  }
  assert.equal(new Set(seen).size,expectedOut.length,'every outgoing neighbor is reachable through graph paging')
 }
 await search(report.top_nodes[0].gid)
 const graphLabel=await page.locator('.graph-edge').first().getAttribute('aria-label')
 const sourceEdge=report.edges.find(e=>graphLabel.startsWith(`${e.src} → ${e.dst}:`))
 assert(sourceEdge,'visible direction references an actual edge')
 const neighbor=sourceEdge.src===report.top_nodes[0].gid?sourceEdge.dst:sourceEdge.src
 await page.locator(`.graph-node[data-node="${neighbor}"]`).first().press('Enter')
 await page.getByRole('heading',{name:`Узел ${neighbor}`,exact:true}).waitFor()
 await search(report.top_nodes[0].gid)
 await page.screenshot({path:process.env.UI_DESKTOP_SCREENSHOT||'/tmp/money-graph-desktop-phase3.png',fullPage:true})
 await page.locator('.header-menu > summary').filter({hasText:'Выгрузить CSV'}).click()
 for(const file of ['nodes_roles','clusters','top_nodes']){assert.equal(await page.locator(`a[download][href="/data/${file}.csv"]`).count(),1);assert((await fetch(`${baseURL}/data/${file}.csv`)).ok)}
 await page.locator('.header-menu > summary').filter({hasText:'Выгрузить CSV'}).click()
 await page.getByLabel('Поиск по gid').focus()
 await page.keyboard.press('Tab')
 assert.equal(await page.evaluate(()=>document.activeElement?.textContent?.trim()),'Найти узел')
 await page.setViewportSize({width:390,height:844})
 await search(report.top_nodes[0].gid)
 assert.equal(await page.locator('.mobile-selected strong').innerText(),report.top_nodes[0].gid,'selected identity remains visible on mobile')
 await page.locator('.mobile-flow-tabs').getByRole('button',{name:/^Исходящие/}).click()
 const mobileOut=report.edges.filter(e=>e.src===report.top_nodes[0].gid&&e.dst!==e.src)
 assert.equal(await page.locator('.mobile-connections > button').count(),Math.min(6,mobileOut.length),'mobile flow pages recipients')
 assert((await page.locator('.mobile-count').innerText()).includes(`из ${mobileOut.length} исходящих`),'mobile scope describes active direction')
 const mobileFirst=page.locator('.mobile-connections > button').first()
 if(mobileOut.length){
  const mobileId=(await mobileFirst.getAttribute('aria-label')).match(/Открыть (.+) на мобильной/)[1]
  assert(mobileOut.some(e=>e.dst===mobileId),'mobile outgoing node is an actual recipient')
  await mobileFirst.click()
  assert.equal(await page.locator('.mobile-selected strong').innerText(),mobileId,'mobile selection updates graph context')
 }
 await search(report.top_nodes[0].gid)
 await page.getByRole('button',{name:'Вся выборка',exact:true}).click()
 await choose('Граница выгрузки','Граничные')
 assert((await page.getByRole('combobox',{name:'Граница выгрузки'}).textContent()).includes('Граничные'),'mobile select is usable')
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile page must not overflow horizontally')
 await page.screenshot({path:process.env.UI_SCREENSHOT||'/tmp/money-graph-mobile-phase3.png',fullPage:true})
 assert.deepEqual(failures,[],'no browser runtime errors')
 assert.deepEqual(external,[],'runtime loads no external resources')
 console.log(JSON.stringify({status:'passed',nodes:report.nodes.length,edges:report.edges.length,checks:['real-data','string-gid','ranking','arrows','cluster-mode','zoom','isolate','boundary','temporal','analysis-flow','exploration-paging','select-filters','global-search','cluster-focus','reset','downloads','keyboard','390px-no-overflow','arbitrary-three-gids','all-graph-pages','graph-keyboard-selection','local-resources-only','mobile-direction-scope','mobile-neighbor-navigation'],isolateTested:!!isolate,boundaryTested:!!boundary,temporalTested:!!temporal,arbitraryGidSeconds}))
} finally { await browser.close() }
