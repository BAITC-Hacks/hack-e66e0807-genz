import { roles, type Role } from './contract'

// Translate only known report phrases. Keep all measurements and the original
// report untouched; the inspector exposes the source text for verification.
export function readableEvidence(text: string): string {
  return text
    .replace(/^Гипотеза (consolidator|transit|distributor|terminal|coordinator|peripheral):/, (_, role: Role) => `Гипотеза «${roles[role].toLocaleLowerCase('ru-RU')}»:`)
    .replace(/связь с (\d+) seed по путям/g, 'достижим из исходных узлов: $1')
    .replace(/путей от seed (\d+)/g, 'исходных узлов с путём к участнику: $1')
}
