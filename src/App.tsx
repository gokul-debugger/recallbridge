import { useCallback, useEffect, useRef, useState } from 'react'
import { AlertTriangle, CalendarClock, Database, ShieldCheck, X } from 'lucide-react'
import './App.css'
import { fetchStats, matchProduct, searchRecalls } from './api'
import { AppHeader } from './components/AppHeader'
import { BrowseView } from './components/BrowseView'
import { MatchView } from './components/MatchView'
import { RecallDetail } from './components/RecallDetail'
import { Sidebar } from './components/Sidebar'
import { WatchlistView } from './components/WatchlistView'
import { createWatchItem, loadWatchlist, saveWatchlist } from './lib/watchlist'
import { emptyProduct } from './lib/product'
import type {
  AppView,
  MatchResponse,
  ProductInput,
  RecallCategory,
  RecallMatch,
  RecallRecord,
  RecallStats,
  WatchItem,
} from './types'

function App() {
  const [view, setView] = useState<AppView>('browse')
  const [stats, setStats] = useState<RecallStats | null>(null)
  const [recalls, setRecalls] = useState<RecallRecord[]>([])
  const [total, setTotal] = useState(0)
  const [selectedRecall, setSelectedRecall] = useState<RecallRecord | null>(null)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState<RecallCategory | ''>('')
  const [browseLoading, setBrowseLoading] = useState(true)
  const [product, setProduct] = useState<ProductInput>(emptyProduct)
  const [matchResult, setMatchResult] = useState<MatchResponse | null>(null)
  const [matchLoading, setMatchLoading] = useState(false)
  const [matchError, setMatchError] = useState<string | null>(null)
  const [detailOverlay, setDetailOverlay] = useState<RecallRecord | null>(null)
  const [watchlist, setWatchlist] = useState<WatchItem[]>(loadWatchlist)
  const [notice, setNotice] = useState<string | null>(null)
  const [appError, setAppError] = useState<string | null>(null)
  const browseRequestId = useRef(0)

  const loadRecalls = useCallback(async (search: string, filter: RecallCategory | '') => {
    const requestId = ++browseRequestId.current
    setBrowseLoading(true)
    try {
      const response = await searchRecalls(search, filter)
      if (requestId !== browseRequestId.current) return
      setRecalls(response.items)
      setTotal(response.total)
      setSelectedRecall((current) => response.items.find((item) => item.id === current?.id) ?? response.items[0] ?? null)
      setAppError(null)
    } catch (error) {
      if (requestId !== browseRequestId.current) return
      setAppError(error instanceof Error ? error.message : 'Recall records could not be loaded.')
    } finally {
      if (requestId === browseRequestId.current) setBrowseLoading(false)
    }
  }, [])

  useEffect(() => {
    const initialize = async () => {
      try {
        const [nextStats] = await Promise.all([
          fetchStats(),
          loadRecalls('', ''),
        ])
        setStats(nextStats)
      } catch (error) {
        setAppError(error instanceof Error ? error.message : 'RecallBridge could not connect to its API.')
      }
    }
    void initialize()
  }, [loadRecalls])

  useEffect(() => {
    saveWatchlist(watchlist)
  }, [watchlist])

  useEffect(() => {
    if (!notice) return
    const timeout = window.setTimeout(() => setNotice(null), 3500)
    return () => window.clearTimeout(timeout)
  }, [notice])

  const changeCategory = (next: RecallCategory | '') => {
    setCategory(next)
    void loadRecalls(query, next)
  }

  const runMatch = async (input: ProductInput = product) => {
    setMatchLoading(true)
    setMatchError(null)
    try {
      const response = await matchProduct(input)
      setMatchResult(response)
    } catch (error) {
      setMatchError(error instanceof Error ? error.message : 'The product could not be checked.')
    } finally {
      setMatchLoading(false)
    }
  }

  const saveProduct = () => {
    const identifiers = [product.model, product.upc, product.lot].filter(Boolean)
    const duplicate = watchlist.some((item) => {
      const savedIdentifiers = [item.model, item.upc, item.lot]
      return identifiers.some((identifier) => savedIdentifiers.includes(identifier))
    })
    if (duplicate) {
      setNotice('That identifier is already in your watchlist.')
      return
    }
    setWatchlist((items) => [createWatchItem(product), ...items])
    setNotice('Product saved in this browser.')
  }

  const checkWatchItem = (item: WatchItem) => {
    const input: ProductInput = {
      product_name: item.product_name,
      brand: item.brand,
      model: item.model,
      upc: item.upc,
      lot: item.lot,
      category: item.category,
    }
    setProduct(input)
    setView('match')
    void runMatch(input)
  }

  const selectMatch = (match: RecallMatch) => setDetailOverlay(match.recall)

  return (
    <div className="app-shell">
      <AppHeader connected={Boolean(stats)} />
      <Sidebar activeView={view} watchCount={watchlist.length} onViewChange={setView} />

      <main className="main-content">
        {appError && <div className="connection-error" role="alert"><AlertTriangle size={18} /><span><strong>API unavailable</strong>{appError}. Start the backend on port 8000.</span></div>}
        {stats?.demo_mode && <div className="demo-banner"><Database size={16} /><span><strong>Demo dataset active.</strong> Run the sync command to replace these fictional examples with recent official records.</span></div>}

        {view === 'browse' && (
          <BrowseView
            query={query}
            category={category}
            items={recalls}
            total={total}
            selected={selectedRecall}
            loading={browseLoading}
            onQueryChange={setQuery}
            onCategoryChange={changeCategory}
            onSearch={() => void loadRecalls(query, category)}
            onSelect={setSelectedRecall}
          />
        )}
        {view === 'match' && (
          <MatchView
            product={product}
            result={matchResult}
            loading={matchLoading}
            error={matchError}
            onProductChange={setProduct}
            onCheck={() => void runMatch()}
            onSave={saveProduct}
            onSelectMatch={selectMatch}
          />
        )}
        {view === 'watchlist' && (
          <WatchlistView
            items={watchlist}
            onCheck={checkWatchItem}
            onRemove={(id) => setWatchlist((items) => items.filter((item) => item.id !== id))}
          />
        )}
      </main>

      <footer className="app-footer">
        <span><ShieldCheck size={14} /> Source-linked results</span>
        <span><CalendarClock size={14} /> Index freshness shown per record</span>
        <p>RecallBridge organizes public recall data. Always verify details with the publishing agency.</p>
      </footer>

      {notice && <div className="toast" role="status">{notice}</div>}
      {detailOverlay && (
        <div className="detail-overlay" role="dialog" aria-modal="true" aria-label="Recall details">
          <button className="overlay-backdrop" onClick={() => setDetailOverlay(null)} aria-label="Close details" />
          <div className="overlay-panel">
            <button className="overlay-close" onClick={() => setDetailOverlay(null)} title="Close details"><X size={18} /></button>
            <RecallDetail recall={detailOverlay} />
          </div>
        </div>
      )}
    </div>
  )
}

export default App
