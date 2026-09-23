export const roles = { consolidator: 'Консолидация', transit: 'Транзит', distributor: 'Распределение', terminal: 'Конечный получатель', coordinator: 'Координация', peripheral: 'Периферия' } as const
export type Role = keyof typeof roles
export const roleColors: Record<Role,string> = {consolidator:'#2563eb',transit:'#0891b2',distributor:'#7c3aed',terminal:'#a16207',coordinator:'#be185d',peripheral:'#64748b'}
export interface NodeRecord { gid:string; depth:number; is_seed:boolean; role:Role; role_score:number; cluster_id:number; priority_score:number; evidence:string; in_degree:number; out_degree:number; in_sum:number; out_sum:number; pass_through:number|null; boundary_censored:boolean; seed_ancestors:number; betweenness:number; warnings:string[] }
export interface EdgeRecord {src:string;dst:string;sum_kzt:number;n_tx:number}
export interface ClusterRecord {cluster_id:number;n_nodes:number;n_seed:number;sum_kzt_internal:number;top_gids:string[];hypothesis:string}
export interface TopRecord {rank:number;gid:string;role:Role;priority_score:number;why:string}
export interface Report {schema_version:'1.0';meta:{n_nodes:number;n_edges:number;n_transactions:number;n_seed:number;total_kzt:number;period_start:string;period_end:string;elapsed_seconds:number;warnings:string[]};nodes:NodeRecord[];edges:EdgeRecord[];clusters:ClusterRecord[];top_nodes:TopRecord[]}
const object = (v:unknown):v is Record<string,unknown> => typeof v==='object' && v!==null && !Array.isArray(v)
const strings = (v:unknown):v is string[] => Array.isArray(v)&&v.every(x=>typeof x==='string')
const number = (v:unknown) => typeof v==='number'&&Number.isFinite(v)
const nums = (v:Record<string,unknown>,keys:string[]) => keys.every(k=>number(v[k]))
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
 return value as unknown as Report
}
export const count = (n:number) => new Intl.NumberFormat('ru-RU',{maximumFractionDigits:0}).format(n)
export const money = (n:number) => `${count(n)} ₸`
