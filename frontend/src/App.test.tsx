import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, fireEvent } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App'
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
