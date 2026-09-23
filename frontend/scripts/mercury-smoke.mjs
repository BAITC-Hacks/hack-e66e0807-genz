import { chromium } from 'playwright'
import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
const base=process.argv[2]||'http://127.0.0.1:8000'
const report=await (await fetch(`${base}/data/report.json`)).json()
const directory='/tmp/money-graph-mercury'
await mkdir(directory,{recursive:true})
const browser=await chromium.launch({headless:true})
try {
 const page=await browser.newPage({viewport:{width:1440,height:1000}})
 const errors=[];page.on('pageerror',e=>errors.push(e.message))
 await page.goto(base);await page.getByLabel('Поиск по gid').waitFor()
 const gid=report.top_nodes[0].gid
 await page.screenshot({path:`${directory}/desktop-workspace.png`,fullPage:false})
 const edge=page.locator('.graph-edge').first();await edge.locator('.svg-amount').click()
 assert(await page.getByLabel('Данные выбранной связи').isVisible())
 await page.screenshot({path:`${directory}/desktop-selected-edge.png`,fullPage:false})
 await page.getByRole('button',{name:'Переводы',exact:true}).click()
 const expected=report.edges.filter(e=>e.src===gid||e.dst===gid).length
 assert.equal(await page.locator('.transfers-table tbody tr').count(),expected)
 await page.screenshot({path:`${directory}/desktop-transfers.png`,fullPage:false})
 await page.getByRole('button',{name:'Маршруты и возвраты',exact:true}).click()
 assert(await page.locator('.route-row').count()>0,'actual routes render after validation')
 await page.locator('.route-row details summary').first().click()
 assert((await page.locator('.route-row').first().innerText()).includes('Дней начала'))
 await page.screenshot({path:`${directory}/desktop-routes.png`,fullPage:false})
 await page.getByRole('button',{name:'Устойчивость сети',exact:true}).click()
 await page.getByLabel('Число удаляемых участников').selectOption('5')
 assert.equal(await page.locator('.removed-gids button').count(),5)
 assert((await page.locator('.analysis-panel').innerText()).includes(String(report.nodes.length-5)))
 await page.screenshot({path:`${directory}/desktop-resilience.png`,fullPage:false})
 const anomaly=report.nodes.find(n=>n.anomalies?.length)
 await page.getByLabel('Поиск по gid').fill(anomaly.gid);await page.getByLabel('Поиск по gid').press('Enter')
 await page.locator('.inspector-details>summary').filter({hasText:'Необычно для колена'}).click()
 assert.equal(await page.locator('.anomaly-item').count(),anomaly.anomalies.length)
 await page.getByRole('button',{name:'Рабочая область',exact:true}).click()
 await page.getByLabel('Поиск по gid').fill(gid);await page.getByLabel('Поиск по gid').press('Enter')
 await page.setViewportSize({width:390,height:844})
 await page.screenshot({path:`${directory}/mobile-workspace.png`,fullPage:true})
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile page has no overflow')
 assert(await page.locator('.mobile-selected').isVisible(),'selected gid is readable on mobile')
 await page.locator('.mobile-queue-toggle').click();assert(await page.getByRole('button',{name:'Вся выборка',exact:true}).isVisible())
 await page.locator('.mobile-queue-toggle').click()
 await page.getByRole('button',{name:'Переводы',exact:true}).click()
 await page.screenshot({path:`${directory}/mobile-transfers.png`,fullPage:true})
 assert.deepEqual(errors,[])
 console.log(JSON.stringify({status:'passed',checks:['adjacent-edge','real-transfers','validated-routes','resilience-prefix-5','real-anomalies','mobile-queue','mobile-identity','mobile-no-overflow','no-console-errors'],screenshots:directory}))
}finally{await browser.close()}
