import React, { useEffect, useState } from 'react'
import axios from 'axios'

type Item = {
  document_id: string
  document_title: string
  page_number: number
  snippet: string
  relevance_score: number
  match_type: string
}

export default function App() {
  const [q, setQ] = useState('test')
  const [items, setItems] = useState<Item[]>([])
  const [page, setPage] = useState(1)
  const [size, setSize] = useState(10)
  const [loading, setLoading] = useState(false)

  async function search() {
    setLoading(true)
    try {
      const r = await axios.post('/api/search/advanced', { query: q, page, size })
      setItems(r.data.items || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { search() }, [])

  return (
    <div style={{ fontFamily: 'sans-serif', padding: 16 }}>
      <h1>GlobalSearch (Web)</h1>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <input value={q} onChange={e => setQ(e.target.value)} placeholder='Search…' />
        <button onClick={search} disabled={loading}>{loading ? 'Searching…' : 'Search'}</button>
      </div>
      <ul>
        {items.map((it, idx) => (
          <li key={`${it.document_id}_${idx}`}>
            <b>{it.document_title}</b> — {it.snippet} <i>[{it.match_type}]</i>
          </li>
        ))}
      </ul>
    </div>
  )
}

