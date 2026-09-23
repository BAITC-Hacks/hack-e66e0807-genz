import { expect, test } from 'vitest'
import { parseRoutes, parseResilience, parseAnomalies } from './optional-contract'
import type { NodeRecord, Report } from './contract'
const ids=new Set(['1','2','3'])
const edges=[{src:'1',dst:'2',sum_kzt:6000,n_tx:1},{src:'2',dst:'3',sum_kzt:7000,n_tx:1}]
const path={gids:['1','2','3'],legs:edges,strict_date_examples:[{dates:['2026-07-01','2026-07-02']}],same_day_ambiguous_examples:[],strict_episode_days:1,repeated:false,date_search_truncated:false,limitations:['Не доказывает движение тех же денег']}
const routes={max_routes_per_node:20,max_cycles_per_node:20,max_candidate_tuples_per_node:2000,max_date_combinations_per_candidate:2000,truncated_nodes:[],paths:[path],cycles:[]}
test('route reader preserves actual directed legs and distinguishes strict from same-day dates',()=>{
 expect(parseRoutes(routes,ids,edges)?.paths[0].legs).toEqual(edges)
 expect(parseRoutes({...routes,paths:[{...path,legs:[edges[1],edges[0]]}]},ids,edges)).toBeUndefined()
 expect(parseRoutes({...routes,paths:[{...path,strict_date_examples:[{dates:['2026-07-01','2026-07-01']}]}]},ids,edges)).toBeUndefined()
 expect(parseRoutes({...routes,paths:[{...path,gids:['1','2','unknown']}]},ids,edges)).toBeUndefined()
})
test('resilience rejects wrong priority prefixes and misleading share denominators',()=>{
 const report={nodes:[{gid:'1'},{gid:'2'},{gid:'3'}],top_nodes:[{gid:'2'}]} as Report
 const baseline={n_nodes:3,n_weak_components:1,largest_component_nodes:3,n_isolates:0,largest_share_surviving:1,largest_share_original:1}
 const scenario={n_nodes:2,n_weak_components:2,largest_component_nodes:1,n_isolates:2,largest_share_surviving:.5,largest_share_original:1/3,n_removed:1,removed_gids:['2']}
 const data={selection:'fixed-priority-prefix',max_n:1,baseline,scenarios:[{...baseline,n_removed:0,removed_gids:[]},scenario]}
 expect(parseResilience(data,report)?.scenarios[1].n_nodes).toBe(2)
 expect(parseResilience({...data,scenarios:[data.scenarios[0],{...scenario,removed_gids:['1']}]},report)).toBeUndefined()
 expect(parseResilience({...data,scenarios:[data.scenarios[0],{...scenario,largest_share_original:.5}]},report)).toBeUndefined()
})
test('anomalies distinguish evaluated-empty from absent and reject censored seed incoming comparisons',()=>{
 const node={depth:0,is_seed:true,boundary_censored:false} as NodeRecord
 const finding={kind:'depth_peer_profile',metric:'in_sum',value:100,peer_depth:0,peer_n:30,peer_median:20,peer_mad:4,deviation:13.4,method:'MAD',limitations:[]}
 expect(parseAnomalies([],node)).toEqual([])
 expect(parseAnomalies(undefined,node)).toBeUndefined()
 expect(parseAnomalies([finding],node)).toBeUndefined()
 expect(parseAnomalies([{...finding,metric:'out_sum'}],node)).toHaveLength(1)
})
