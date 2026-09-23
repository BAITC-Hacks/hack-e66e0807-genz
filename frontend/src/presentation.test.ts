import { expect, test } from 'vitest'
import { roles } from './contract'
import { readableEvidence } from './presentation'

test.each(Object.entries(roles))('translates the %s hypothesis without changing its measurements', (role, label) => {
  const source = `Гипотеза ${role}: вход 110000.00 KZT; выход/вход 0.000 ≤ 0.2; gid 999999999999999991.`
  expect(readableEvidence(source)).toBe(`Гипотеза «${label.toLocaleLowerCase('ru-RU')}»: вход 110000.00 KZT; выход/вход 0.000 ≤ 0.2; gid 999999999999999991.`)
})

test('explains seed reachability and preserves unknown report prose', () => {
  expect(readableEvidence('Гипотеза coordinator: связь с 7 seed по путям; посредничество 0.00847.')).toBe('Гипотеза «координация»: достижим из исходных узлов: 7; посредничество 0.00847.')
  expect(readableEvidence('Приоритет 0.837; путей от seed 7; оборот 1513002.00 KZT.')).toBe('Приоритет 0.837; исходных узлов с путём к участнику: 7; оборот 1513002.00 KZT.')
  const unknown = 'Гипотеза custom: seed-атрибут; 100000000000000001; неизвестное правило.'
  expect(readableEvidence(unknown)).toBe(unknown)
})
