import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { parseReport, type Report } from './contract'
export default function App() {
 const [report,setReport]=useState<Report|null>(null),[error,setError]=useState(''),[query,setQuery]=useState(''),[selected,setSelected]=useState(''),[retry,setRetry]=useState(0)
 useEffect(()=>{let ignore=false;setError('');setReport(null);fetch('/data/report.json').then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then(parseReport).then(r=>{if(!ignore){setReport(r);setSelected(r.top_nodes[0]?.gid??'')}}).catch(e=>{if(!ignore)setError(String(e.message))});return()=>{ignore=true}},[retry])
 const node=report?.nodes.find(n=>n.gid===selected)
 return <main><h1>Граф денег</h1>{error?<div role="alert">Не удалось загрузить результаты анализа. {error}<Button onClick={()=>setRetry(retry+1)}>Повторить загрузку</Button></div>:!report?<p role="status">Загружаем граф и результаты анализа…</p>:<><form onSubmit={e=>{e.preventDefault();if(report.nodes.some(n=>n.gid===query.trim()))setSelected(query.trim())}}><label htmlFor="gid">Поиск по gid</label><input id="gid" value={query} onChange={e=>setQuery(e.target.value)}/><Button>Найти узел</Button></form>{node&&<Card><CardContent><h2>Узел {node.gid}</h2><p>{node.evidence}</p></CardContent></Card>}</>}</main>
}
