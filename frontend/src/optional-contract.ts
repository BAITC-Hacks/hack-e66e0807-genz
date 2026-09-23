import type { EdgeRecord, NodeRecord, Report } from './contract'

export interface RouteEvidence { gids:string[]; legs:EdgeRecord[]; strict_date_examples:{dates:string[]}[]; same_day_ambiguous_examples:{dates:string[]}[]; strict_episode_days:number; repeated:boolean; date_search_truncated:boolean; limitations:string[] }
export interface Routes { max_routes_per_node:number; max_cycles_per_node:number; max_candidate_tuples_per_node:number; max_date_combinations_per_candidate:number; truncated_nodes:string[]; paths:RouteEvidence[]; cycles:RouteEvidence[] }
export interface Connectivity { n_nodes:number; n_weak_components:number; largest_component_nodes:number; n_isolates:number; largest_share_surviving:number; largest_share_original:number }
export interface Scenario extends Connectivity { n_removed:number; removed_gids:string[] }
export interface Resilience { selection:'fixed-priority-prefix'; max_n:number; baseline:Connectivity; scenarios:Scenario[] }
export interface Anomaly { kind:'depth_peer_profile'|'observed_near_cutoff'; metric:string; value:number; peer_depth:number; peer_n:number; peer_median:number; peer_mad:number|null; deviation:number|null; method:string; limitations:string[] }
const obj=(v:unknown):v is Record<string,unknown>=>typeof v==='object'&&v!==null&&!Array.isArray(v)
const num=(v:unknown):v is number=>typeof v==='number'&&Number.isFinite(v)&&v>=0
const int=(v:unknown):v is number=>num(v)&&Number.isSafeInteger(v)
const strs=(v:unknown):v is string[]=>Array.isArray(v)&&v.every(x=>typeof x==='string')
const validDate=(v:unknown):v is string=>typeof v==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(v)&&!Number.isNaN(Date.parse(v))&&new Date(v).toISOString().slice(0,10)===v
export function parseRoutes(value:unknown,ids:Set<string>,edges:EdgeRecord[]):Routes|undefined {
 if(!obj(value)||!['max_routes_per_node','max_cycles_per_node','max_candidate_tuples_per_node','max_date_combinations_per_candidate'].every(k=>int(value[k]))||!strs(value.truncated_nodes)||!value.truncated_nodes.every(id=>ids.has(id)))return
 const valid=(v:unknown,cycle:boolean)=>{
  if(!obj(v)||!strs(v.gids)||!v.gids.every(id=>ids.has(id))||new Set(v.gids).size!==v.gids.length||(cycle?![2,3].includes(v.gids.length):v.gids.length!==3)||!Array.isArray(v.legs)||v.legs.length!==(cycle?v.gids.length:2)||!int(v.strict_episode_days)||typeof v.repeated!=='boolean'||v.repeated!==(v.strict_episode_days>=2)||typeof v.date_search_truncated!=='boolean'||!strs(v.limitations))return false
  const gids=v.gids
  if(!v.legs.every((leg,i)=>obj(leg)&&leg.src===gids[i]&&leg.dst===gids[(i+1)%gids.length]&&edges.some(e=>e.src===leg.src&&e.dst===leg.dst&&e.sum_kzt===leg.sum_kzt&&e.n_tx===leg.n_tx)))return false
  const legCount=v.legs.length
  return ['strict_date_examples','same_day_ambiguous_examples'].every(key=>Array.isArray(v[key])&&v[key].length<=3&&v[key].every(ex=>obj(ex)&&Array.isArray(ex.dates)&&ex.dates.length===legCount&&ex.dates.every(validDate)&&(key==='strict_date_examples'?ex.dates.every((d,i,all)=>i===0||d>all[i-1]):ex.dates.some((d,i,all)=>i>0&&d===all[i-1])&&ex.dates.every((d,i,all)=>i===0||d>=all[i-1]))))
 }
 if(!Array.isArray(value.paths)||!Array.isArray(value.cycles)||!value.paths.every(v=>valid(v,false))||!value.cycles.every(v=>valid(v,true)))return
 return value as unknown as Routes
}
export function parseResilience(value:unknown,report:Pick<Report,'nodes'|'top_nodes'>):Resilience|undefined {
 if(!obj(value)||value.selection!=='fixed-priority-prefix'||!int(value.max_n)||value.max_n>20||value.max_n>report.top_nodes.length||!Array.isArray(value.scenarios)||value.scenarios.length!==value.max_n+1)return
 const original=report.nodes.length
 const valid=(v:unknown,n:number)=>obj(v)&&['n_nodes','n_weak_components','largest_component_nodes','n_isolates'].every(k=>int(v[k]))&&v.n_nodes===n&&(v.n_weak_components as number)<=n&&(v.largest_component_nodes as number)<=n&&(v.n_isolates as number)<=n&&num(v.largest_share_surviving)&&num(v.largest_share_original)&&Math.abs(v.largest_share_surviving-(n?(v.largest_component_nodes as number)/n:0))<1e-8&&Math.abs(v.largest_share_original-(original?(v.largest_component_nodes as number)/original:0))<1e-8
 if(!valid(value.baseline,original)||!value.scenarios.every((v,i)=>obj(v)&&v.n_removed===i&&strs(v.removed_gids)&&v.removed_gids.length===i&&v.removed_gids.every((id,j)=>id===report.top_nodes[j]?.gid)&&valid(v,original-i)))return
 return value as unknown as Resilience
}
export function parseAnomalies(value:unknown,node:NodeRecord):Anomaly[]|undefined {
 if(!Array.isArray(value))return
 const metrics=['in_degree','out_degree','in_sum','out_sum','incoming_tx_count','outgoing_tx_count','near_cutoff_share']
 if(!value.every(v=>obj(v)&&['depth_peer_profile','observed_near_cutoff'].includes(String(v.kind))&&metrics.includes(String(v.metric))&&num(v.value)&&v.peer_depth===node.depth&&int(v.peer_n)&&v.peer_n>=10&&num(v.peer_median)&&(v.peer_mad===null||num(v.peer_mad))&&(v.deviation===null||num(v.deviation))&&typeof v.method==='string'&&strs(v.limitations)&&!(node.is_seed&&['in_degree','in_sum','incoming_tx_count'].includes(String(v.metric)))&&!(node.boundary_censored&&['out_degree','out_sum','outgoing_tx_count'].includes(String(v.metric)))))return
 return value as Anomaly[]
}
