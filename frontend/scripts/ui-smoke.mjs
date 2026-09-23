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
 page.on('pageerror',error=>failures.push(error.message))
 await page.goto(baseURL)
 await page.getByLabel('Поиск по gid').waitFor()
 const search=async gid=>{await page.getByLabel('Поиск по gid').fill(gid);await page.getByLabel('Поиск по gid').press('Enter');await page.getByRole('heading',{name:`Узел ${gid}`,exact:true}).waitFor()}
 await search(report.nodes.at(-1).gid)
 if(report.top_nodes.length){const id=report.top_nodes[0].gid;await page.getByRole('button',{name:`Открыть узел ${id} из рейтинга`,exact:true}).click();await page.getByRole('heading',{name:`Узел ${id}`,exact:true}).waitFor()}
 await page.getByRole('img',{name:'Направленный граф выбранного узла'}).waitFor()
 const connected=report.nodes.find(n=>report.edges.some(e=>e.src===n.gid||e.dst===n.gid))
 if(connected){await search(connected.gid);assert(await page.locator('line[marker-end]').count()>0,'directed links have arrows')}
 await page.getByRole('button',{name:'Кластеры',exact:true}).click()
 assert.equal(await page.getByRole('button',{name:'Кластеры',exact:true}).getAttribute('aria-pressed'),'true')
 await page.getByRole('button',{name:'Приблизить',exact:true}).click()
 await page.getByRole('button',{name:'Показать целиком',exact:true}).click()
 const linkedIds=new Set(report.edges.flatMap(e=>[e.src,e.dst]))
 const isolate=report.nodes.find(n=>!linkedIds.has(n.gid))
 if(isolate){await search(isolate.gid);await page.getByText('В этой выгрузке у узла нет связей. Это не доказывает отсутствие переводов за её пределами.',{exact:true}).waitFor()}
 const boundary=report.nodes.find(n=>n.boundary_censored)
 if(boundary){await search(boundary.gid);await page.getByText('Граница выгрузки: отсутствие исходящих не доказывает конечного получателя',{exact:true}).waitFor()}
 for(const file of ['nodes_roles','clusters','top_nodes']){assert.equal(await page.locator(`a[download][href="/data/${file}.csv"]`).count(),1);assert((await fetch(`${baseURL}/data/${file}.csv`)).ok)}
 await page.getByLabel('Поиск по gid').focus()
 await page.keyboard.press('Tab')
 assert.equal(await page.evaluate(()=>document.activeElement?.textContent?.trim()),'Найти узел')
 await page.setViewportSize({width:390,height:844})
 await search(report.nodes[0].gid)
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile page must not overflow horizontally')
 await page.screenshot({path:process.env.UI_SCREENSHOT||'/tmp/money-graph-mobile.png',fullPage:true})
 assert.deepEqual(failures,[],'no browser runtime errors')
 console.log(JSON.stringify({status:'passed',nodes:report.nodes.length,edges:report.edges.length,checks:['real-data','string-gid','ranking','arrows','cluster-mode','zoom','isolate','boundary','downloads','keyboard','390px-no-overflow'],isolateTested:!!isolate,boundaryTested:!!boundary}))
} finally { await browser.close() }
