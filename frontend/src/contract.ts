export const roles = { consolidator: 'Консолидация', transit: 'Транзит', distributor: 'Распределение', terminal: 'Конечный получатель', coordinator: 'Координация', peripheral: 'Периферия' } as const
export type Role = keyof typeof roles
export const roleColors: Record<Role,string> = {consolidator:'#2563eb',transit:'#0891b2',distributor:'#7c3aed',terminal:'#a16207',coordinator:'#be185d',peripheral:'#64748b'}
export interface TemporalExample { incoming_date:string; outgoing_date:string }
export interface TemporalEvidence {
 incoming_tx_count?:number; outgoing_tx_count?:number; outgoing_after_1d_count?:number; outgoing_after_1_or_2d_count?:number;
 after_1_or_2d_examples?:TemporalExample[];
 incoming_profile?:{active_days:number;total_kzt:number;distinct_payers:number;median_kzt:number};
 synchronous_incoming?:null|{date:string;distinct_payers:number;tx_count:number;sum_kzt:number};
 peak_day?:null|{date:string;count:number;share:number;baseline_daily_count:number};
}
export interface NodeRecord { gid:string; depth:number; is_seed:boolean; role:Role; role_score:number; cluster_id:number; priority_score:number; evidence:string; in_degree:number; out_degree:number; in_sum:number; out_sum:number; pass_through:number|null; boundary_censored:boolean; seed_ancestors:number; betweenness:number; warnings:string[]; temporal?:TemporalEvidence; next_data_requests?:string[] }
export interface EdgeRecord {src:string;dst:string;sum_kzt:number;n_tx:number}
export interface ClusterRecord {cluster_id:number;n_nodes:number;n_seed:number;sum_kzt_internal:number;top_gids:string[];hypothesis:string}
export interface TopRecord {rank:number;gid:string;role:Role;priority_score:number;why:string}
export interface Report {schema_version:'1.0';meta:{n_nodes:number;n_edges:number;n_transactions:number;n_seed:number;total_kzt:number;period_start:string;period_end:string;elapsed_seconds:number;warnings:string[]};nodes:NodeRecord[];edges:EdgeRecord[];clusters:ClusterRecord[];top_nodes:TopRecord[];has_invalid_optional?:boolean}
const object = (v:unknown):v is Record<string,unknown> => typeof v==='object' && v!==null && !Array.isArray(v)
const strings = (v:unknown):v is string[] => Array.isArray(v)&&v.every(x=>typeof x==='string')
const number = (v:unknown):v is number => typeof v==='number'&&Number.isFinite(v)
const nums = (v:Record<string,unknown>,keys:string[]) => keys.every(k=>number(v[k]))
const nonnegative = (v:unknown):v is number => number(v)&&v>=0
const integer = (v:unknown):v is number => nonnegative(v)&&Number.isSafeInteger(v)
const date = (v:unknown):v is string => {
 if(typeof v!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(v)) return false
 const parsed=new Date(`${v}T00:00:00Z`)
 return !Number.isNaN(parsed.getTime())&&parsed.toISOString().slice(0,10)===v
}
function parseTemporal(value:unknown):{temporal?:TemporalEvidence;invalid:boolean} {
 if(!object(value)) return {invalid:true}
 const temporal:TemporalEvidence={}
 let invalid=false
 const counts=['incoming_tx_count','outgoing_tx_count','outgoing_after_1d_count','outgoing_after_1_or_2d_count'] as const
 for(const key of counts) if(key in value) {if(integer(value[key])) temporal[key]=value[key];else invalid=true}
 if('after_1_or_2d_examples' in value) {
  if(Array.isArray(value.after_1_or_2d_examples)) {
   const examples=value.after_1_or_2d_examples.filter((item):item is TemporalExample=>object(item)&&date(item.incoming_date)&&date(item.outgoing_date))
   if(examples.length!==value.after_1_or_2d_examples.length||examples.length>3) invalid=true
   temporal.after_1_or_2d_examples=examples.slice(0,3)
  } else invalid=true
 }
 if('incoming_profile' in value) {
  const profile=value.incoming_profile
  if(object(profile)&&integer(profile.active_days)&&nonnegative(profile.total_kzt)&&integer(profile.distinct_payers)&&nonnegative(profile.median_kzt)) temporal.incoming_profile=profile as unknown as NonNullable<TemporalEvidence['incoming_profile']>
  else invalid=true
 }
 if('synchronous_incoming' in value) {
  const sync=value.synchronous_incoming
  if(sync===null) temporal.synchronous_incoming=null
  else if(object(sync)&&date(sync.date)&&integer(sync.distinct_payers)&&sync.distinct_payers>=3&&integer(sync.tx_count)&&sync.tx_count>=sync.distinct_payers&&nonnegative(sync.sum_kzt)) temporal.synchronous_incoming=sync as unknown as NonNullable<TemporalEvidence['synchronous_incoming']>
  else invalid=true
 }
 if('peak_day' in value) {
  const peak=value.peak_day
  if(peak===null) temporal.peak_day=null
  else if(object(peak)&&date(peak.date)&&integer(peak.count)&&peak.count>=3&&number(peak.share)&&peak.share>=0&&peak.share<=1&&nonnegative(peak.baseline_daily_count)) temporal.peak_day=peak as unknown as NonNullable<TemporalEvidence['peak_day']>
  else invalid=true
 }
 if(Object.keys(temporal).length===0) return {invalid}
 return {temporal,invalid}
}
export function parseReport(value:unknown):Report {
 if(!object(value)) throw new Error('Некорректный формат отчёта.')
 if(value.schema_version!=='1.0') throw new Error('Неподдерживаемая версия схемы отчёта.')
 const {meta,nodes,edges,clusters,top_nodes}=value
 if(!object(meta)||!nums(meta,['n_nodes','n_edges','n_transactions','n_seed','total_kzt','elapsed_seconds'])||!strings(meta.warnings)||typeof meta.period_start!=='string'||typeof meta.period_end!=='string'||![nodes,edges,clusters,top_nodes].every(Array.isArray)) throw new Error('Некорректная структура отчёта.')
 if(!(nodes as unknown[]).every(n=>object(n)&&typeof n.gid==='string'&&n.gid.length>0&&typeof n.role==='string'&&Object.hasOwn(roles,n.role)&&typeof n.evidence==='string'&&typeof n.is_seed==='boolean'&&typeof n.boundary_censored==='boolean'&&strings(n.warnings)&&nums(n,['depth','role_score','cluster_id','priority_score','in_degree','out_degree','in_sum','out_sum','seed_ancestors','betweenness'])&&(n.pass_through===null||number(n.pass_through)))) throw new Error('Некорректные данные узлов.')
 const ids=new Set((nodes as NodeRecord[]).map(n=>n.gid))
 if(ids.size!==(nodes as NodeRecord[]).length) throw new Error('Повторяющиеся gid в отчёте.')
 if(!(edges as unknown[]).every(e=>object(e)&&typeof e.src==='string'&&typeof e.dst==='string'&&ids.has(e.src)&&ids.has(e.dst)&&nums(e,['sum_kzt','n_tx']))) throw new Error('Некорректные связи узлов.')
 if(!(clusters as unknown[]).every(c=>object(c)&&nums(c,['cluster_id','n_nodes','n_seed','sum_kzt_internal'])&&typeof c.hypothesis==='string'&&strings(c.top_gids)&&c.top_gids.every(id=>ids.has(id)))) throw new Error('Некорректные данные кластеров.')
 if(!(top_nodes as unknown[]).every(t=>object(t)&&typeof t.gid==='string'&&ids.has(t.gid)&&typeof t.role==='string'&&Object.hasOwn(roles,t.role)&&nums(t,['rank','priority_score'])&&typeof t.why==='string')) throw new Error('Некорректный список приоритетов.')
 let has_invalid_optional=false
 const parsedNodes=(nodes as Record<string,unknown>[]).map(raw=>{
  const clean={...raw} as unknown as NodeRecord
  if('temporal' in raw){const parsed=parseTemporal(raw.temporal);clean.temporal=parsed.temporal;has_invalid_optional ||=parsed.invalid}
  if('next_data_requests' in raw){
   if(Array.isArray(raw.next_data_requests)) {
    clean.next_data_requests=raw.next_data_requests.filter((request):request is string=>typeof request==='string'&&request.trim().length>0)
    has_invalid_optional ||=clean.next_data_requests.length!==raw.next_data_requests.length
   } else {clean.next_data_requests=undefined;has_invalid_optional=true}
  }
  return clean
 })
 return {...value,nodes:parsedNodes,has_invalid_optional} as unknown as Report
}
export const count = (n:number) => new Intl.NumberFormat('ru-RU',{maximumFractionDigits:0}).format(n)
export const money = (n:number) => `${count(n)} ₸`
