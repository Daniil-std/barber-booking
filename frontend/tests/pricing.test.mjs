import assert from 'node:assert/strict'
import test from 'node:test'
import { quoteFor } from '../src/pricing.ts'

test('the selected barber determines the server-provided quote', () => {
  const service = {
    price: '70.00',
    min_price: '70.00',
    prices: [
      { barber_id: 1, level: 'junior', price: '70.00' },
      { barber_id: 2, level: 'senior', price: '100.00' },
      { barber_id: 3, level: 'top', price: '140.00' },
    ],
  }
  assert.equal(quoteFor(service, 1), '70.00')
  assert.equal(quoteFor(service, 2), '100.00')
  assert.equal(quoteFor(service, 3), '140.00')
  assert.equal(quoteFor(service, 99), null)
  assert.equal(quoteFor(service), null)
})

test('a training quote belongs only to the assigned trainee', () => {
  const service = {
    price: '35.00',
    min_price: '35.00',
    is_training: true,
    prices: [{ barber_id: 4, level: 'trainee', price: '35.00' }],
  }
  assert.equal(quoteFor(service, 4), '35.00')
  assert.equal(quoteFor(service, 3), null)
  assert.equal(quoteFor(undefined, 4), null)
})
