import { useMemo } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { setMode, setSelectedHcpId } from '../store/interactionSlice'
import ChatPanel from './ChatPanel'
import InteractionForm from './InteractionForm'

export default function LogInteractionScreen() {
  const dispatch = useDispatch()
  const { mode, hcps, interactions, selectedHcpId, status, agentEnabled } = useSelector((s) => s.crm)

  const filtered = useMemo(() => {
    if (!selectedHcpId) return interactions
    return interactions.filter((i) => i.hcp_id === selectedHcpId)
  }, [interactions, selectedHcpId])

  if (status === 'loading') {
    return (
      <div style={{ padding: '2rem', fontFamily: 'Inter, sans-serif' }}>
        Loading CRM…
      </div>
    )
  }

  if (status === 'failed') {
    return (
      <div style={{ padding: '2rem', fontFamily: 'Inter, sans-serif', color: '#b91c1c' }}>
        Could not reach the API. Start the FastAPI server on port 8000 and keep Vite dev server running.
      </div>
    )
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        fontFamily: 'Inter, sans-serif',
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1fr) 320px',
        gap: '1.25rem',
        padding: '1.25rem 1.5rem 2rem',
        maxWidth: '1200px',
        margin: '0 auto',
      }}
    >
      <div>
        <header style={{ marginBottom: '1rem' }}>
          <p style={{ margin: 0, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b' }}>
            AI-first CRM · HCP module
          </p>
          <h1 style={{ margin: '0.25rem 0 0.5rem', fontSize: '1.65rem' }}>Log interaction</h1>
          <p style={{ margin: 0, color: '#475569', maxWidth: '52rem', fontSize: '0.95rem' }}>
            Capture calls and visits with a structured form, or drive the same backend through a LangGraph agent
            (Groq <code>gemma2-9b-it</code>) that can search HCPs, log and edit interactions, pull history, and schedule follow-ups.
          </p>
          <div style={{ marginTop: '0.75rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b' }}>Active HCP</span>
            <select
              value={selectedHcpId ?? ''}
              onChange={(e) => dispatch(setSelectedHcpId(Number(e.target.value)))}
              style={{ padding: '0.35rem 0.5rem', borderRadius: '8px', border: '1px solid #cbd5e1' }}
            >
              {hcps.map((h) => (
                <option key={h.id} value={h.id}>
                  {h.name}
                </option>
              ))}
            </select>
            <span
              style={{
                fontSize: '0.75rem',
                padding: '0.2rem 0.5rem',
                borderRadius: '999px',
                background: agentEnabled ? '#ecfdf5' : '#fff7ed',
                color: agentEnabled ? '#047857' : '#c2410c',
              }}
            >
              Agent {agentEnabled ? 'online' : 'offline'}
            </span>
          </div>
        </header>

        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          {['form', 'chat'].map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => dispatch(setMode(m))}
              style={{
                border: mode === m ? '2px solid #0f766e' : '1px solid #cbd5e1',
                background: mode === m ? '#ecfdf5' : '#fff',
                borderRadius: '999px',
                padding: '0.4rem 0.9rem',
                fontWeight: 600,
                cursor: 'pointer',
                textTransform: 'capitalize',
              }}
            >
              {m === 'form' ? 'Structured form' : 'Chat'}
            </button>
          ))}
        </div>

        {mode === 'form' ? <InteractionForm /> : <ChatPanel />}
      </div>

      <aside
        style={{
          background: '#fff',
          border: '1px solid #e2e8f0',
          borderRadius: '12px',
          padding: '1rem',
          height: 'fit-content',
          position: 'sticky',
          top: '1rem',
        }}
      >
        <h2 style={{ margin: '0 0 0.75rem', fontSize: '1rem' }}>Recent interactions</h2>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
          {filtered.slice(0, 12).map((i) => {
            const hcp = hcps.find((h) => h.id === i.hcp_id)
            return (
              <li
                key={i.id}
                style={{
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  padding: '0.5rem 0.6rem',
                  fontSize: '0.82rem',
                }}
              >
                <div style={{ fontWeight: 600 }}>{hcp?.name ?? `HCP #${i.hcp_id}`}</div>
                <div style={{ color: '#64748b' }}>{i.channel} · {new Date(i.occurred_at).toLocaleString()}</div>
                <div style={{ marginTop: '0.35rem' }}>{i.summary || i.raw_notes.slice(0, 120)}</div>
              </li>
            )
          })}
          {filtered.length === 0 && (
            <li style={{ color: '#64748b', fontSize: '0.9rem' }}>No interactions yet for this HCP.</li>
          )}
        </ul>
      </aside>
    </div>
  )
}
