import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { Button } from './ui/button'
import { Anomalies } from './AnalysisEvidence'
import { ArrowDownLeft, ArrowUpRight } from "lucide-react"
import { Card, CardContent } from "./ui/card"
import { Badge } from "./ui/badge"
import { roles, count, money, type Report, type NodeRecord, type TemporalEvidence } from "../contract"
import { readableEvidence } from '../presentation'
const observations=(value:number|undefined)=>value===undefined?"Нет данных":`${count(value)} наблюдений`
function TemporalSection({temporal,boundary}:{temporal:TemporalEvidence;boundary:boolean}) {
 const peak=temporal.peak_day,profile=temporal.incoming_profile,sync=temporal.synchronous_incoming
 return <section className="temporal-section"><h3>Временные признаки</h3><p className="small muted">Наблюдаемые переводы и совпадения календарных дат</p>
 <dl className="temporal-metrics"><div><dt>Входящие транзакции</dt><dd>{observations(temporal.incoming_tx_count)}</dd></div><div><dt>Исходящие транзакции</dt><dd>{observations(temporal.outgoing_tx_count)}</dd></div><div><dt>Через 1 день после поступления</dt><dd>{observations(temporal.outgoing_after_1d_count)}</dd></div><div><dt>Через 1–2 дня после поступления</dt><dd>{observations(temporal.outgoing_after_1_or_2d_count)}</dd></div></dl>
 <p className="small muted">Каждый подходящий исходящий перевод учтён один раз. Показатель за 1–2 дня накопительный: он включает переводы за 1 день; эти значения не складываются.</p>
 {!!temporal.after_1_or_2d_examples?.length&&<div className="temporal-subsection"><h3>Примеры дат</h3><ul>{temporal.after_1_or_2d_examples.map((pair,i)=><li key={`${pair.incoming_date}-${pair.outgoing_date}-${i}`}>{pair.incoming_date} → {pair.outgoing_date}</li>)}</ul></div>}
 {profile&&<div className="temporal-subsection"><h3>Профиль входящих</h3><p>{count(profile.distinct_payers)} плательщика · {count(profile.active_days)} активных дней</p><p>{money(profile.total_kzt)} всего · {money(profile.median_kzt)} медиана перевода</p>{boundary&&<p className="small muted">Граница глубины 4: наблюдаемые поступления не доказывают, что узел — конечный получатель.</p>}</div>}
 {sync&&<div className="temporal-subsection"><h3>Синхронные поступления</h3><p>{sync.date}: {count(sync.distinct_payers)} плательщика, {count(sync.tx_count)} транзакций, {money(sync.sum_kzt)}</p><p className="small muted">Совпадение календарного дня не задаёт порядок переводов внутри дня.</p></div>}
 {peak&&<div className="temporal-subsection"><h3>Пик дневной активности</h3><p>{peak.date}: {count(peak.count)} транзакций · {new Intl.NumberFormat('ru-RU',{style:'percent',maximumFractionDigits:1}).format(peak.share)} от всех наблюдаемых · базовый уровень {new Intl.NumberFormat('ru-RU',{maximumFractionDigits:2}).format(peak.baseline_daily_count)} в день</p><p className="small muted">Пик показан при трёх и более транзакциях за день и уровне не ниже двойного среднего за весь период.</p></div>}
 <p className="temporal-caution">Совпадение дат не доказывает, что переводились те же деньги.</p></section>
}
export default function Inspector({node,report,onSelect}:{node:NodeRecord;report:Report;onSelect:(gid:string)=>void}) {
 const [copied,setCopied]=useState(false)
 const copy=async()=>{try{await navigator.clipboard.writeText(node.gid);setCopied(true)}catch{setCopied(false)}}
 const cluster=report.clusters.find(c=>c.cluster_id===node.cluster_id),incoming=report.edges.filter(e=>e.dst===node.gid),outgoing=report.edges.filter(e=>e.src===node.gid)
 const sourcePriority=report.top_nodes.find(item=>item.gid===node.gid)?.why
 const hasReadableSource=readableEvidence(node.evidence)!==node.evidence||(sourcePriority!==undefined&&readableEvidence(sourcePriority)!==sourcePriority)
 const metrics=[['Приоритет проверки',node.priority_score.toFixed(2)],['Оценка правила роли',node.role_score.toFixed(2)],['Входящие связи',count(node.in_degree)],['Исходящие связи',count(node.out_degree)],['Входящая сумма',money(node.in_sum)],['Исходящая сумма',money(node.out_sum)],['Выход / вход',node.pass_through===null?'Нет данных':node.pass_through.toFixed(2)],['Исходных узлов с путём сюда',count(node.seed_ancestors)]]
 return <Card className="inspector" id="participant-details" tabIndex={-1}><CardContent><div className="eyebrow">КАРТОЧКА УЧАСТНИКА</div><div className="inspector-identity"><h2>Узел {node.gid}</h2><Button variant="ghost" size="icon" aria-label={copied?"gid скопирован":"Скопировать полный gid"} onClick={()=>void copy()}>{copied?<Check size={15}/>:<Copy size={15}/>}</Button></div><div className="badges"><Badge variant="secondary">{roles[node.role]}</Badge><Badge variant="outline">Глубина {node.depth}</Badge>{node.is_seed&&<Badge variant="outline">Исходный узел</Badge>}</div><p className="evidence">{readableEvidence(node.evidence)}</p><p className="muted small">Роль — гипотеза по наблюдаемым переводам.</p>{sourcePriority&&<section className="priority-explanation"><h3>Основание приоритета</h3><p>{readableEvidence(sourcePriority)}</p></section>}<dl className="metrics">{metrics.map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
 {(node.is_seed||node.boundary_censored||node.warnings.length>0)&&<div className="node-warnings">{node.is_seed&&<p>Входящие переводы вне выборки не видны</p>}{node.boundary_censored&&<p>Граница выгрузки: отсутствие исходящих не доказывает конечного получателя</p>}{node.warnings.map((w,i)=><p key={i}>{w}</p>)}</div>}
 <Anomalies node={node}/>
 {node.temporal&&<details className="inspector-details"><summary>Временные признаки</summary><TemporalSection temporal={node.temporal} boundary={node.boundary_censored}/></details>}
 {node.next_data_requests&&<details className="inspector-details"><summary>Какие данные запросить дальше</summary><section className="request-section"><h3>Какие данные запросить дальше</h3>{node.next_data_requests.length?<ul>{node.next_data_requests.map((request,i)=><li key={i}>{request}</li>)}</ul>:<p className="small muted">Дополнительный запрос данных не определён для этого узла.</p>}</section></details>}
 {!incoming.length&&!outgoing.length&&<p className="isolate">В этой выгрузке у узла нет связей. Это не доказывает отсутствие переводов за её пределами.</p>}
 {[{label:'Входящие',edges:incoming,in:true},{label:'Исходящие',edges:outgoing,in:false}].map(group=><details className="neighbors inspector-details" key={group.label}><summary>{group.label} связи · {group.edges.length}</summary><section><h3>{group.in?<ArrowDownLeft size={16}/>:<ArrowUpRight size={16}/>} {group.label} <span>{group.edges.length}</span></h3>{group.edges.length===0?<p className="muted small">В выборке не наблюдаются</p>:<ul>{group.edges.map((e,i)=>{const id=group.in?e.src:e.dst;return <li key={`${id}-${i}`}><button aria-label={`Открыть соседний узел ${id}`} onClick={()=>onSelect(id)}>{id}<ArrowUpRight size={14}/></button><span>{money(e.sum_kzt)} · переводов: {count(e.n_tx)}</span></li>})}</ul>}</section></details>)}
 {cluster&&<details className="inspector-details"><summary>Кластер {cluster.cluster_id}</summary><section className="cluster-details"><h3>Кластер {cluster.cluster_id}</h3><p className="small muted">{count(cluster.n_nodes)} узлов · исходных узлов: {count(cluster.n_seed)} · {money(cluster.sum_kzt_internal)} внутри</p><p>{cluster.hypothesis}</p><div className="cluster-gids">{cluster.top_gids.map(id=><button key={id} onClick={()=>onSelect(id)} aria-label={`Открыть узел ${id} из кластера`}>{id}</button>)}</div></section></details>}
 {hasReadableSource&&<details className="inspector-details source-evidence"><summary>Исходный текст расчёта</summary><section><p>{node.evidence}</p>{sourcePriority&&<p>{sourcePriority}</p>}</section></details>}
 </CardContent></Card>
}
