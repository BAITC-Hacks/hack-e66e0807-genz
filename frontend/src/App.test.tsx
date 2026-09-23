import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, fireEvent } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App'
import { parseReport } from './contract'
// Entirely synthetic fixture: never imported into production code.
const gid = '999999999999999991'
const node = {gid,depth:4,is_seed:false,role:'peripheral',role_score:0.2,cluster_id:0,priority_score:0.3,evidence:'Синтетический узел для проверки точности gid',in_degree:0,out_degree:0,in_sum:0,out_sum:0,pass_through:null,boundary_censored:true,seed_ancestors:0,betweenness:0,warnings:[]}
const fixture = {schema_version:'1.0',meta:{n_nodes:1,n_edges:0,n_transactions:0,n_seed:0,total_kzt:0,period_start:'2025-01-01',period_end:'2025-02-01',elapsed_seconds:0,warnings:[]},nodes:[node],edges:[],clusters:[{cluster_id:0,n_nodes:1,n_seed:0,sum_kzt_internal:0,top_gids:[gid],hypothesis:'Синтетическое сообщество'}],top_nodes:[]}
afterEach(() => { cleanup(); vi.unstubAllGlobals() })
test('exact string gid beyond safe integer finds fetched evidence', async () => {
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>fixture}))
 render(<App />)
 fireEvent.change(await screen.findByLabelText('Поиск по gid'),{target:{value:gid}})
 fireEvent.click(screen.getByRole('button',{name:'Найти узел'}))
 expect(await screen.findByText(node.evidence)).toBeVisible()
})
test('isolated boundary node keeps selection after unknown search and explains limits',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,top_nodes:[{rank:1,gid,role:'peripheral',priority_score:0.3,why:'Проверить изолят'}]})}))
 render(<App />)
 expect(await screen.findByText('Граница выгрузки: отсутствие исходящих не доказывает конечного получателя')).toBeVisible()
 expect(screen.getByText('В этой выгрузке у узла нет связей. Это не доказывает отсутствие переводов за её пределами.')).toBeVisible()
 fireEvent.change(screen.getByLabelText('Поиск по gid'),{target:{value:'missing'}})
 fireEvent.click(screen.getByRole('button',{name:'Найти узел'}))
 expect(screen.getByText('Узел не найден. Проверьте gid и повторите поиск.')).toBeVisible()
 expect(screen.getByRole('heading',{name:`Узел ${gid}`})).toBeVisible()
})
test('ranking and directed neighbor buttons use same selection',async()=>{
 const other={...node,gid:'999999999999999992',evidence:'Второй синтетический узел',is_seed:true}
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,nodes:[node,other],edges:[{src:gid,dst:other.gid,sum_kzt:120,n_tx:2}],top_nodes:[{rank:1,gid,role:'peripheral',priority_score:0.3,why:'Проверить'}]})}))
 render(<App />)
 fireEvent.click(await screen.findByRole('button',{name:`Открыть соседний узел ${other.gid}`}))
 expect(screen.getByRole('heading',{name:`Узел ${other.gid}`})).toBeVisible()
 expect(screen.getByText('Входящие переводы вне выборки не видны')).toBeVisible()
 fireEvent.click(screen.getByRole('button',{name:`Открыть узел ${gid} из рейтинга`}))
 expect(screen.getByRole('heading',{name:`Узел ${gid}`})).toBeVisible()
})
test('loading, fetch failure and retry have actionable distinct states',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce({ok:true,json:async()=>fixture}))
 render(<App />)
 expect(screen.getByText('Загружаем граф и результаты анализа…')).toBeVisible()
 expect(await screen.findByRole('alert')).toHaveTextContent('Не удалось загрузить результаты анализа.')
 fireEvent.click(screen.getByRole('button',{name:'Повторить загрузку'}))
 expect(await screen.findByLabelText('Поиск по gid')).toBeVisible()
})
test('empty report and unsupported schema are explained',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,nodes:[],clusters:[]})}))
 const view=render(<App />)
 expect(await screen.findByText('В выгрузке пока нет узлов')).toBeVisible()
 view.unmount()
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,schema_version:'2.0'})}))
 render(<App />)
 expect(await screen.findByRole('alert')).toHaveTextContent('Неподдерживаемая версия схемы отчёта.')
})
test('validator rejects unsafe identifiers, dangling references and nonfinite numbers',()=>{
 expect(()=>parseReport({...fixture,nodes:[{...node,gid:999}]})).toThrow()
 expect(()=>parseReport({...fixture,edges:[{src:gid,dst:'missing',sum_kzt:1,n_tx:1}]})).toThrow()
 expect(()=>parseReport({...fixture,nodes:[{...node,in_sum:Infinity}]})).toThrow()
 expect(()=>parseReport({...fixture,nodes:[node,node]})).toThrow()
})
test('CSV links and graph controls have accessible names',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,top_nodes:[{rank:1,gid,role:'peripheral',priority_score:0.3,why:'Проверить'}]})}))
 render(<App />)
 expect(await screen.findByRole('link',{name:'Скачать роли CSV'})).toHaveAttribute('href','/data/nodes_roles.csv')
 expect(screen.getByRole('link',{name:'Скачать кластеры CSV'})).toHaveAttribute('href','/data/clusters.csv')
 expect(screen.getByRole('link',{name:'Скачать приоритеты CSV'})).toHaveAttribute('href','/data/top_nodes.csv')
 fireEvent.click(screen.getByRole('button',{name:'Кластеры'}))
 expect(screen.getByRole('button',{name:'Кластеры'})).toHaveAttribute('aria-pressed','true')
 fireEvent.click(screen.getByRole('button',{name:'Приблизить'}))
 expect(screen.getByRole('img',{name:'Направленный граф выбранного узла'})).toBeVisible()
})
test('selected node shows dated temporal evidence, incoming profile and ordered requests',async()=>{
 const temporal={incoming_tx_count:5,outgoing_tx_count:4,outgoing_after_1d_count:2,outgoing_after_1_or_2d_count:3,after_1_or_2d_examples:[{incoming_date:'2025-01-02',outgoing_date:'2025-01-03'},{incoming_date:'2025-01-02',outgoing_date:'2025-01-04'}],incoming_profile:{active_days:2,total_kzt:900,distinct_payers:3,median_kzt:150},synchronous_incoming:{date:'2025-01-02',distinct_payers:3,tx_count:4,sum_kzt:800},peak_day:{date:'2025-01-03',count:3,share:0.3,baseline_daily_count:0.5}}
 const requests=['Запросить продолжение после глубины 4 для '+gid,'Запросить время и идентификаторы переводов 2025-01-02 для '+gid]
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,nodes:[{...node,temporal,next_data_requests:requests}],top_nodes:[{rank:1,gid,role:'peripheral',priority_score:0.3,why:'Проверить'}]})}))
 render(<App />)
 expect(await screen.findByRole('heading',{name:'Временные признаки'})).toBeVisible()
 expect(screen.getByText('Через 1 день после поступления')).toBeVisible()
 expect(screen.getByText('Через 1–2 дня после поступления')).toBeVisible()
 expect(screen.getByText('2025-01-02 → 2025-01-03')).toBeVisible()
 expect(screen.getByText('Совпадение дат не доказывает, что переводились те же деньги.')).toBeVisible()
 expect(screen.getByText(/3 плательщика/)).toBeVisible()
 expect(screen.getByText(/Граница глубины 4/)).toBeVisible()
 expect(screen.getByRole('heading',{name:'Какие данные запросить дальше'})).toBeVisible()
 expect(screen.getByText(requests[0])).toBeVisible()
 expect(screen.getByText(requests[1])).toBeVisible()
})
test('older reports omit temporal sections and malformed optional evidence is nonfatal',async()=>{
 expect(parseReport(fixture).nodes[0].temporal).toBeUndefined()
 const invalid=parseReport({...fixture,nodes:[{...node,temporal:{incoming_tx_count:-1},next_data_requests:[' ',42]}]})
 expect(invalid.nodes[0].temporal).toBeUndefined()
 expect(invalid.nodes[0].next_data_requests).toEqual([])
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({...fixture,nodes:[{...node,temporal:{incoming_tx_count:-1},next_data_requests:[' ',42]}],top_nodes:[{rank:1,gid,role:'peripheral',priority_score:0.3,why:'Проверить'}]})}))
 render(<App />)
 expect(await screen.findByText('Часть дополнительных данных недоступна. Основные сведения об узле сохранены.')).toBeVisible()
 expect(screen.getByRole('heading',{name:`Узел ${gid}`})).toBeVisible()
 expect(screen.queryByRole('heading',{name:'Временные признаки'})).not.toBeInTheDocument()
})
