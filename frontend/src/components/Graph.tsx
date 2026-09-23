import { useMemo, useRef, useState } from 'react'
import { Minus, Plus, Maximize2, Move } from 'lucide-react'
import { Button } from './ui/button'
import { roles, roleColors, count, money, type Report, type Role } from '../contract'
const palette=['#2563eb','#7c3aed','#0891b2','#be185d','#a16207','#64748b','#059669']
export default function Graph({report,selectedGid,onSelect}:{report:Report;selectedGid:string;onSelect:(gid:string)=>void}) {
 const [mode,setMode]=useState<'roles'|'clusters'>('roles'),[view,setView]=useState({x:0,y:0,z:1})
 const drag=useRef<{x:number;y:number;ox:number;oy:number}|null>(null)
 const data=useMemo(()=>{
  const allEdges=report.edges.filter(e=>e.src===selectedGid||e.dst===selectedGid)
  const neighbors=Array.from(new Set(allEdges.flatMap(e=>[e.src,e.dst]))).filter(id=>id!==selectedGid).sort()
  const ids=[selectedGid,...neighbors.slice(0,36)]
  const positions=new Map(ids.map((id,i)=>{const angle=(i-1)*Math.PI*2/Math.max(1,ids.length-1)-Math.PI/2;return [id,i===0?{x:450,y:265}:{x:450+315*Math.cos(angle),y:265+195*Math.sin(angle)}]}))
  return {nodes:report.nodes.filter(n=>positions.has(n.gid)),edges:allEdges.filter(e=>positions.has(e.src)&&positions.has(e.dst)),positions,total:neighbors.length+1}
 },[report,selectedGid])
 const zoom=(factor:number)=>setView(v=>({...v,z:Math.max(.45,Math.min(3,v.z*factor))}))
 return <section className="graph-section" aria-label="Граф связей">
  <div className="graph-toolbar"><div className="segmented" aria-label="Цвет графа"><Button variant={mode==='roles'?'secondary':'ghost'} aria-pressed={mode==='roles'} onClick={()=>setMode('roles')}>Цвет: роли</Button><Button variant={mode==='clusters'?'secondary':'ghost'} aria-pressed={mode==='clusters'} onClick={()=>setMode('clusters')}>Кластеры</Button></div><div className="controls"><Button variant="outline" size="icon" aria-label="Приблизить" onClick={()=>zoom(1.2)}><Plus/></Button><Button variant="outline" size="icon" aria-label="Отдалить" onClick={()=>zoom(1/1.2)}><Minus/></Button><Button variant="outline" size="icon" aria-label="Показать целиком" onClick={()=>setView({x:0,y:0,z:1})}><Maximize2/></Button></div></div>
  <div className="graph-canvas"><svg viewBox="0 0 900 540" role="img" aria-label="Направленный граф выбранного узла" onPointerDown={e=>{if((e.target as Element).closest('[data-node]'))return;e.currentTarget.setPointerCapture(e.pointerId);drag.current={x:e.clientX,y:e.clientY,ox:view.x,oy:view.y}}} onPointerMove={e=>{if(!drag.current)return;const d=drag.current;const scale=900/e.currentTarget.getBoundingClientRect().width;setView(v=>({...v,x:d.ox+(e.clientX-d.x)*scale,y:d.oy+(e.clientY-d.y)*scale}))}} onPointerUp={()=>{drag.current=null}} onPointerCancel={()=>{drag.current=null}}>
   <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#94a3b8"/></marker><pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#e2e8f0"/></pattern></defs>
   <rect width="900" height="540" fill="url(#dots)"/>
   <g transform={`translate(${450+view.x} ${270+view.y}) scale(${view.z}) translate(-450 -270)`}>
    {data.edges.map((e,i)=>{const a=data.positions.get(e.src)!,b=data.positions.get(e.dst)!;const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy)||1;return <g key={`${e.src}-${e.dst}-${i}`}><line x1={a.x+dx/len*24} y1={a.y+dy/len*24} x2={b.x-dx/len*29} y2={b.y-dy/len*29} stroke="#94a3b8" strokeWidth="1.5" markerEnd="url(#arrow)"/><title>{e.src} → {e.dst}: {money(e.sum_kzt)}, {count(e.n_tx)} переводов</title></g>})}
    {data.nodes.map(n=>{const p=data.positions.get(n.gid)!,chosen=n.gid===selectedGid;return <g key={n.gid} data-node="true" onClick={()=>{onSelect(n.gid);setView({x:0,y:0,z:1})}} className="graph-node" aria-label={`Узел ${n.gid}: ${roles[n.role]}`}><title>{n.gid} — {roles[n.role]}</title>{chosen&&<circle cx={p.x} cy={p.y} r="34" fill="#f0fdfa" stroke="#0f766e" strokeWidth="2"/>}<circle cx={p.x} cy={p.y} r={chosen?24:17} fill={mode==='roles'?roleColors[n.role]:palette[Math.abs(n.cluster_id)%palette.length]} stroke="white" strokeWidth="3"/><text x={p.x} y={p.y+(chosen?52:36)} textAnchor="middle" fill="#334155" fontSize="14" fontWeight={chosen?600:400}>{chosen?n.gid:`…${n.gid.slice(-6)}`}</text>{chosen&&<text x={p.x} y={p.y+72} textAnchor="middle" fill="#64748b" fontSize="14">Выбранный узел</text>}</g>})}
   </g>
  </svg><div className="graph-hint"><Move size={16}/> Перетаскивайте поле для перемещения</div></div>
  <div className="graph-foot"><p>Показано {data.nodes.length} из {count(report.nodes.length)} узлов <span>· Стрелка: плательщик → получатель</span></p>{data.total>37&&<p>В окружении {data.total} узлов; на графе первые 37. Все соседи доступны в карточке узла.</p>}<div className="legend">{mode==='roles'?Object.entries(roles).map(([role,label])=><span key={role}><i style={{background:roleColors[role as Role]}}/>{label} <b>{count(report.nodes.filter(n=>n.role===role).length)}</b></span>):report.clusters.map(c=><span key={c.cluster_id}><i style={{background:palette[Math.abs(c.cluster_id)%palette.length]}}/>Кластер {c.cluster_id} · {count(c.n_nodes)}</span>)}</div></div>
 </section>
}
