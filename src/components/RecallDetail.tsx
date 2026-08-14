import { AlertTriangle, ArrowUpRight, Box, CalendarDays, CircleCheck, Factory, Tag } from 'lucide-react'
import type { RecallRecord } from '../types'

const sourceNames = {
  cpsc: 'U.S. CPSC',
  openfda_food: 'openFDA Food',
  openfda_device: 'openFDA Device',
}

const categoryNames = {
  consumer_product: 'Consumer product',
  food: 'Food',
  medical_device: 'Medical device',
}

interface RecallDetailProps {
  recall: RecallRecord | null
}

export function RecallDetail({ recall }: RecallDetailProps) {
  if (!recall) {
    return (
      <section className="recall-detail recall-detail--empty">
        <AlertTriangle size={28} />
        <h2>Select a recall</h2>
        <p>Choose a record to review the hazard, affected identifiers, and official source.</p>
      </section>
    )
  }

  const image = recall.images[0]
  const indexedAt = new Date(recall.synced_at)
  const indexedLabel = Number.isNaN(indexedAt.getTime())
    ? 'Index time unavailable'
    : `Indexed ${indexedAt.toLocaleString()}`

  return (
    <section className="recall-detail" aria-labelledby="recall-detail-title">
      <div className="detail-heading">
        <div className="detail-tags">
          <span>{categoryNames[recall.category]}</span>
          <span>{sourceNames[recall.source]}</span>
          {recall.is_demo && <span className="demo-tag">Demo record</span>}
        </div>
        <h2 id="recall-detail-title">{recall.title}</h2>
        <p>{recall.product_description}</p>
      </div>

      {image && (
        <figure className="recall-image">
          <img
            src={image.url}
            alt={image.caption || recall.title}
            loading="lazy"
            referrerPolicy="no-referrer"
          />
          {image.caption && <figcaption>{image.caption}</figcaption>}
        </figure>
      )}

      <dl className="detail-facts">
        <div><dt><CalendarDays size={15} /> Recall date</dt><dd>{new Date(`${recall.recall_date}T00:00:00`).toLocaleDateString()}</dd></div>
        <div><dt><Factory size={15} /> Manufacturer</dt><dd>{recall.manufacturer || 'Not listed'}</dd></div>
        <div><dt><Tag size={15} /> Status</dt><dd>{recall.status}</dd></div>
        <div><dt><Box size={15} /> Units</dt><dd>{recall.affected_units || 'Not listed'}</dd></div>
      </dl>

      <div className="safety-block safety-block--hazard">
        <span><AlertTriangle size={18} /> Hazard</span>
        <p>{recall.hazard || 'The source did not provide a hazard summary.'}</p>
      </div>
      <div className="safety-block">
        <span><CircleCheck size={18} /> Official action</span>
        <p>{recall.remedy || 'Review the official record for the recommended action.'}</p>
      </div>

      {recall.identifiers.length > 0 && (
        <div className="identifier-block">
          <h3>Affected identifiers</h3>
          <div>{recall.identifiers.map((item) => <code key={`${item.kind}:${item.value}`}>{item.kind}: {item.value}</code>)}</div>
        </div>
      )}

      <a className="official-link" href={recall.source_url} target="_blank" rel="noopener noreferrer">
        Open official source <ArrowUpRight size={16} />
      </a>
      <p className="detail-disclaimer">{indexedLabel}. Verify model, lot, serial, or UPC details on the official page before taking action.</p>
    </section>
  )
}
