import { Bookmark, ScanSearch, Search, ShieldCheck } from 'lucide-react'
import type { AppView } from '../types'

interface SidebarProps {
  activeView: AppView
  watchCount: number
  onViewChange: (view: AppView) => void
}

const items = [
  { id: 'browse' as const, label: 'Browse recalls', icon: Search },
  { id: 'match' as const, label: 'Check a product', icon: ScanSearch },
  { id: 'watchlist' as const, label: 'My watchlist', icon: Bookmark },
]

export function Sidebar({ activeView, watchCount, onViewChange }: SidebarProps) {
  return (
    <aside className="sidebar">
      <nav aria-label="RecallBridge sections">
        {items.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={activeView === id ? 'active' : ''}
            aria-label={label}
            title={label}
            onClick={() => onViewChange(id)}
          >
            <Icon size={18} />
            <span>{label}</span>
            {id === 'watchlist' && watchCount > 0 && <b>{watchCount}</b>}
          </button>
        ))}
      </nav>
      <div className="source-note">
        <ShieldCheck size={17} />
        <span><strong>Source-first results</strong>Every record links back to the publishing agency.</span>
      </div>
    </aside>
  )
}
