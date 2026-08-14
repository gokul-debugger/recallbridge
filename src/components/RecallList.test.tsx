import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { RecallRecord } from '../types'
import { RecallList } from './RecallList'

const recall: RecallRecord = {
  id: 'cpsc:1',
  source: 'cpsc',
  source_id: '1',
  source_url: 'https://example.gov/1',
  title: 'Example toaster recall',
  category: 'consumer_product',
  product_description: 'A toaster',
  hazard: 'Overheating',
  remedy: 'Stop use',
  recall_date: '2026-08-01',
  status: 'Open',
  severity: 'Official recall',
  manufacturer: 'Example Co',
  affected_units: '10',
  identifiers: [],
  images: [],
  synced_at: '2026-08-14T00:00:00Z',
  is_demo: false,
}

describe('RecallList', () => {
  it('selects a rendered recall record', () => {
    const onSelect = vi.fn()
    render(<RecallList items={[recall]} selectedId={null} loading={false} onSelect={onSelect} />)

    fireEvent.click(screen.getByRole('button', { name: /Example toaster recall/ }))

    expect(onSelect).toHaveBeenCalledWith(recall)
  })

  it('shows an explicit empty state', () => {
    render(<RecallList items={[]} selectedId={null} loading={false} onSelect={() => undefined} />)

    expect(screen.getByText('No recalls matched those filters.')).toBeInTheDocument()
  })
})
