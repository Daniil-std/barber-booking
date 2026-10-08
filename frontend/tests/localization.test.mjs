import assert from 'node:assert/strict'
import test from 'node:test'
import fs from 'node:fs'
import path from 'node:path'
import { createTranslator, translateError } from '../src/localization.ts'
import { polish } from '../src/translations/pl.ts'
import { parsers } from 'prettier/plugins/typescript'

test('English is the source language and Polish has a separate translation', () => {
  assert.equal(createTranslator('en')('Book a visit'), 'Book a visit')
  assert.equal(createTranslator('pl')('Book a visit'), 'Umów wizytę')
})

test('customer names and numeric values survive interpolation', () => {
  assert.equal(
    createTranslator('pl')('Good to see you, {name}.', { name: 'Jordan' }),
    'Miło Cię widzieć, Jordan.',
  )
  assert.equal(
    createTranslator('pl')('{minutes} minutes', { minutes: 75 }),
    '75 min',
  )
})

test('all static UI translation calls have a nonempty Polish translation', () => {
  const root = path.resolve('src')
  const missing = []
  function visit(node, filename) {
    if (!node || typeof node !== 'object') return
    if (
      node.type === 'CallExpression' &&
      node.callee?.name === 't' &&
      typeof node.arguments[0]?.value === 'string'
    ) {
      const key = node.arguments[0].value
      if (!polish[key]?.trim()) missing.push(`${filename}: ${key}`)
    }
    for (const [key, value] of Object.entries(node)) {
      if (['loc', 'range', 'tokens', 'comments'].includes(key)) continue
      if (Array.isArray(value)) value.forEach((item) => visit(item, filename))
      else if (value && typeof value === 'object') visit(value, filename)
    }
  }
  function checkDirectory(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const filename = path.join(directory, entry.name)
      if (entry.isDirectory()) checkDirectory(filename)
      else if (entry.name.endsWith('.tsx')) {
        visit(
          parsers.typescript.parse(fs.readFileSync(filename, 'utf8')),
          filename,
        )
      }
    }
  }
  checkDirectory(root)
  assert.deepEqual(missing, [])
})

test('booking conflicts and validator errors are understandable in Polish', () => {
  assert.equal(
    translateError(
      'This time is no longer available. Please choose another slot.',
      'pl',
    ),
    'Ten termin nie jest już dostępny. Wybierz inną godzinę.',
  )
  assert.equal(
    translateError('Ensure this field has no more than 500 characters.', 'pl'),
    'Pole może zawierać maksymalnie 500 znaków.',
  )
  assert.equal(
    translateError('Unknown internal failure', 'pl'),
    'Nie udało się wykonać tej operacji. Sprawdź dane i spróbuj ponownie.',
  )
})

test('the entire seeded service catalog has Polish names and descriptions', () => {
  const source = fs.readFileSync(
    '../backend/studio/management/commands/seed_demo.py',
    'utf8',
  )
  const services = source.split('SERVICES = [')[1].split(/^BARBERS =/m)[0]
  const namesAndDescriptions = [
    ...services.matchAll(/\(\s*"([^"]+)",\s*"([^"]+)"/g),
  ].flatMap((match) => [match[1], match[2]])
  assert.equal(namesAndDescriptions.length, 8)
  const training = source.match(/TRAINING = \("([^"]+)", "([^"]+)"/)
  assert.ok(training)
  namesAndDescriptions.push(training[1], training[2])
  for (const text of namesAndDescriptions)
    assert.ok(polish[text], `Missing translation: ${text}`)
})
