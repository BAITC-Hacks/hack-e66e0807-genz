import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import Graph from './Graph'
import { type NodeRecord, type Report } from '../contract'
const center='900000000000000100'
const makeNode=(gid:string):NodeRecord=>({gid,depth:1,is_seed:false,role:'transit',role_score:.5,cluster_id:0,priority_score:.5,evidence:'Synthetic',in_degree:1,out_degree:1,in_sum:100,out_sum:100,pass_through:1,boundary_censored:false,seed_ancestors:0,betweenness:0,warnings:[]})
function fixture():Report {
 const nodes=[makeNode(center),...Array.from({length:14},(_,i)=>makeNode(String(BigInt(center)+BigInt(i+1)*1000n)))]
 return {schema_version:'1.0',meta:{n_nodes:15,n_edges:14,n_transactions:14,n_seed:0,total_kzt:1000,period_start:'2026-07-01',period_end:'2026-07-31',elapsed_seconds:0,warnings:[]},nodes,edges:nodes.slice(1).map((n,i)=>i<7?{src:n.gid,dst:center,sum_kzt:100*(i+1),n_tx:1}:{src:center,dst:n.gid,sum_kzt:100*(i+1),n_tx:1}),clusters:[],top_nodes:[]}
}
afterEach(cleanup)
test('directional lanes preserve arrows, amount evidence and independent access to every neighbor',()=>{
 const report=fixture(); const {container}=render(<Graph report={report} selectedGid={center} onSelect={vi.fn()}/>)
 expect(screen.getAllByText('Отправители').length).toBeGreaterThan(0)
 expect(screen.getByText('Получатели')).toBeVisible()
 expect(screen.getByText('Показано 12 из 14 связей. Суммы за весь период, KZT.')).toBeVisible()
 const paths=container.querySelectorAll('.graph-edge path[marker-end]')
 expect(paths).toHaveLength(12)
 paths.forEach(p=>expect(p).toHaveAttribute('marker-end','url(#flow-arrow)'))
 expect(container.querySelectorAll('.svg-amount')).toHaveLength(12)
 const incoming=container.querySelector('.graph-edge')!
 expect(incoming.getAttribute('aria-label')).toContain(`→ ${center}:`)
 expect(screen.queryByRole('button',{name:`Узел ${report.nodes[1].gid}: Транзит`})).not.toBeInTheDocument()
 fireEvent.click(screen.getByRole('button',{name:'Следующие отправители'}))
 expect(screen.getByRole('button',{name:`Узел ${report.nodes[1].gid}: Транзит`})).toBeVisible()
 expect(screen.getByRole('button',{name:'Следующие отправители'})).toBeDisabled()
 expect(screen.getByText('Показано 7 из 14 связей. Суммы за весь период, KZT.')).toBeVisible()
 fireEvent.click(screen.getByRole('button',{name:'Следующие получатели'}))
 expect(screen.getByText('Показано 2 из 14 связей. Суммы за весь период, KZT.')).toBeVisible()
})
test('full gids remain distinct, keyboard selects neighbors, cluster mode and zoom respond',()=>{
 const report=fixture(),select=vi.fn();render(<Graph report={report} selectedGid={center} onSelect={select}/>)
 const id=report.nodes[7].gid,neighbor=screen.getByRole('button',{name:`Узел ${id}: Транзит`})
 expect(neighbor.querySelector('.svg-gid')).toHaveTextContent(id)
 fireEvent.focus(neighbor)
 expect(screen.getAllByText(id).length).toBeGreaterThanOrEqual(2)
 fireEvent.keyDown(neighbor,{key:'Enter'})
 expect(select).toHaveBeenCalledWith(id)
 fireEvent.click(screen.getByRole('button',{name:'Кластеры'}))
 expect(screen.getByRole('button',{name:'Кластеры'})).toHaveAttribute('aria-pressed','true')
 fireEvent.click(screen.getByRole('button',{name:'Приблизить'}))
 expect(screen.getByText('125%')).toBeVisible()
 fireEvent.click(screen.getByRole('button',{name:'Показать целиком'}))
 expect(screen.getByText('100%')).toBeVisible()
})
test('isolate remains selectable and self transfers have explicit evidence',()=>{
 const report=fixture();report.edges=[];const view=render(<Graph report={report} selectedGid={center} onSelect={vi.fn()}/>)
 expect(screen.getByText('Нет входящих связей')).toBeVisible()
 expect(screen.getByText('Нет исходящих связей')).toBeVisible()
 expect(screen.getByRole('button',{name:`Узел ${center}: Транзит`})).toBeVisible()
 view.unmount();report.edges=[{src:center,dst:center,sum_kzt:250,n_tx:1}]
 render(<Graph report={report} selectedGid={center} onSelect={vi.fn()}/>)
 expect(screen.getByLabelText('Самоперевод')).toBeVisible()
 expect(screen.getByLabelText('Самоперевод')).toHaveTextContent('Самоперевод · 250 ₸')
})
test('mobile flow keeps selected identity visible while direction switching preserves neighbor amounts',()=>{
 const report=fixture(),select=vi.fn();render(<Graph report={report} selectedGid={center} onSelect={select}/>)
 const mobile=within(screen.getByLabelText('Связи выбранного участника на узком экране'))
 expect(mobile.getByText(center)).toBeVisible()
 expect(mobile.getByText('Отправитель → выбранный участник')).toBeVisible()
 expect(screen.getByText('Показано 6 из 7 входящих связей. Суммы за весь период, KZT.')).toBeInTheDocument()
 expect(mobile.getAllByRole('button',{name:/на мобильной схеме$/})).toHaveLength(6)
 fireEvent.click(mobile.getByRole('button',{name:'Исходящие · 7'}))
 expect(mobile.getByText('Выбранный участник → получатель')).toBeVisible()
 expect(screen.getByText('Показано 6 из 7 исходящих связей. Суммы за весь период, KZT.')).toBeInTheDocument()
 expect(mobile.getByText(center)).toBeVisible()
 const destination=report.nodes[14].gid
 fireEvent.click(mobile.getByRole('button',{name:`Открыть ${destination} на мобильной схеме`}))
 expect(select).toHaveBeenCalledWith(destination)
})
