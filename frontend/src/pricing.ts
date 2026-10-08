import type { Service } from './types'

export function quoteFor(
  service: Service | undefined,
  barberId?: number,
): string | null {
  return (
    service?.prices.find((quote) => quote.barber_id === barberId)?.price ?? null
  )
}
