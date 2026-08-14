import { BookmarkPlus, CircleCheck, LoaderCircle, ScanSearch, Sparkles } from 'lucide-react'
import { emptyProduct } from '../lib/product'
import type { MatchResponse, ProductInput, RecallMatch } from '../types'

interface MatchViewProps {
  product: ProductInput
  result: MatchResponse | null
  loading: boolean
  error: string | null
  onProductChange: (product: ProductInput) => void
  onCheck: () => void
  onSave: () => void
  onSelectMatch: (match: RecallMatch) => void
}

export function MatchView({
  product,
  result,
  loading,
  error,
  onProductChange,
  onCheck,
  onSave,
  onSelectMatch,
}: MatchViewProps) {
  const set = (key: keyof ProductInput, value: string) => onProductChange({ ...product, [key]: value })
  const canSubmit = Object.entries(product).some(([key, value]) => key !== 'category' && value.trim())

  return (
    <section className="view" aria-labelledby="match-title">
      <div className="view-heading">
        <div><span className="eyebrow">Explainable matching</span><h1 id="match-title">Check a product</h1></div>
        <p>Identifiers are treated as exact only when their normalized values match.</p>
      </div>

      <div className="match-layout">
        <form className="match-form" onSubmit={(event) => { event.preventDefault(); onCheck() }}>
          <div className="form-heading">
            <span><ScanSearch size={20} /></span>
            <div><h2>Product details</h2><p>Add what you can. A model, UPC, or lot gives the strongest result.</p></div>
          </div>
          <div className="form-grid">
            <label className="wide"><span>Product name</span><input maxLength={160} value={product.product_name} onChange={(event) => set('product_name', event.target.value)} placeholder="QuickHeat two-slice toaster" /></label>
            <label><span>Brand</span><input maxLength={120} value={product.brand} onChange={(event) => set('brand', event.target.value)} placeholder="Northstar" /></label>
            <label><span>Category</span><select value={product.category} onChange={(event) => set('category', event.target.value)}><option value="">Any category</option><option value="consumer_product">Consumer product</option><option value="food">Food</option><option value="medical_device">Medical device</option></select></label>
            <label><span>Model</span><input maxLength={100} value={product.model} onChange={(event) => set('model', event.target.value)} placeholder="QH-220" /></label>
            <label><span>UPC or barcode</span><input maxLength={50} inputMode="numeric" value={product.upc} onChange={(event) => set('upc', event.target.value)} placeholder="012345678905" /></label>
            <label className="wide"><span>Lot or batch</span><input maxLength={100} value={product.lot} onChange={(event) => set('lot', event.target.value)} placeholder="MM2407A" /></label>
          </div>
          <div className="form-actions">
            <button type="button" className="text-button" onClick={() => onProductChange({ ...emptyProduct, product_name: 'QuickHeat toaster', brand: 'Northstar', model: 'QH-220', category: 'consumer_product' })}><Sparkles size={16} /> Fill example</button>
            <div>
              <button type="button" className="secondary-button" onClick={onSave} disabled={!canSubmit}><BookmarkPlus size={16} /> Save product</button>
              <button className="primary-button" type="submit" disabled={!canSubmit || loading}>{loading ? <LoaderCircle className="spin" size={17} /> : <ScanSearch size={17} />} Check recalls</button>
            </div>
          </div>
        </form>

        <section className="match-results" aria-live="polite">
          <div className="match-results__heading"><div><h2>Match results</h2><p>{result ? `${result.checked} records checked` : 'Results will appear here'}</p></div>{result?.exact_identifier_match && <span><CircleCheck size={16} /> Exact ID found</span>}</div>
          {error && <div className="error-message">{error}</div>}
          {!result && !error && <div className="result-empty"><ScanSearch size={28} /><strong>Ready to check</strong><p>RecallBridge explains why each result was returned.</p></div>}
          {result && result.matches.length === 0 && <div className="result-empty"><CircleCheck size={28} /><strong>No matches in this index</strong><p>This does not prove a product is safe. Search the official sources if you remain concerned.</p></div>}
          {result?.matches.map((match) => (
            <button key={match.recall.id} className="match-row" onClick={() => onSelectMatch(match)}>
              <span className={`confidence confidence--${match.confidence}`}>{match.confidence}</span>
              <span><strong>{match.recall.title}</strong><small>{match.reasons.join(' · ')}</small></span>
              <b aria-label={`Match score ${match.score}`}>{match.score}</b>
            </button>
          ))}
        </section>
      </div>
    </section>
  )
}
