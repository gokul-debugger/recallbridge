import { Database, ShieldCheck } from 'lucide-react'

interface AppHeaderProps {
  connected: boolean
}

export function AppHeader({ connected }: AppHeaderProps) {
  return (
    <header className="app-header">
      <div className="brand" aria-label="RecallBridge">
        <span className="brand-mark"><ShieldCheck size={22} /></span>
        <span><strong>RecallBridge</strong><small>Official recall search</small></span>
      </div>
      <div className={`connection-state${connected ? ' connection-state--online' : ''}`}>
        <Database size={15} />
        <span>{connected ? 'Recall index ready' : 'Connecting to index'}</span>
      </div>
    </header>
  )
}
