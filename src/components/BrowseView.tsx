import { Filter, Search } from 'lucide-react'
import type { RecallCategory, RecallRecord } from '../types'
import { RecallDetail } from './RecallDetail'
import { RecallList } from './RecallList'

interface BrowseViewProps {
  query: string
  category: RecallCategory | ''
  items: RecallRecord[]
  total: number
  selected: RecallRecord | null
  loading: boolean
  onQueryChange: (value: string) => void
  onCategoryChange: (value: RecallCategory | '') => void
  onSearch: () => void
  onSelect: (recall: RecallRecord) => void
}

const categories: Array<{ value: RecallCategory | ''; label: string }> = [
  { value: '', label: 'All' },
  { value: 'consumer_product', label: 'Products' },
  { value: 'food', label: 'Food' },
  { value: 'medical_device', label: 'Devices' },
]

export function BrowseView({
  query,
  category,
  items,
  total,
  selected,
  loading,
  onQueryChange,
  onCategoryChange,
  onSearch,
  onSelect,
}: BrowseViewProps) {
  return (
    <section className="view" aria-labelledby="browse-title">
      <div className="view-heading">
        <div><span className="eyebrow">Recall index</span><h1 id="browse-title">Browse official recalls</h1></div>
        <p>Search titles, manufacturers, hazards, models, lots, and UPCs.</p>
      </div>

      <form className="search-toolbar" onSubmit={(event) => { event.preventDefault(); onSearch() }}>
        <label className="search-input">
          <Search size={18} />
          <span className="visually-hidden">Search recall records</span>
          <input maxLength={120} value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Try toaster, Northstar, QH-220, or a UPC" />
        </label>
        <button className="primary-button" type="submit"><Search size={17} /> Search</button>
      </form>

      <div className="filter-row">
        <span><Filter size={15} /> Category</span>
        <div className="segmented-control">
          {categories.map((item) => (
            <button key={item.label} type="button" aria-pressed={category === item.value} className={category === item.value ? 'active' : ''} onClick={() => onCategoryChange(item.value)}>
              {item.label}
            </button>
          ))}
        </div>
        <small>{total} {total === 1 ? 'record' : 'records'}</small>
      </div>

      <div className="browse-grid">
        <RecallList items={items} selectedId={selected?.id ?? null} loading={loading} onSelect={onSelect} />
        <RecallDetail recall={selected} />
      </div>
    </section>
  )
}
