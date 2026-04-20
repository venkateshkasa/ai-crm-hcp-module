import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { clearChat, pushUserMessage, sendChat } from '../store/interactionSlice'

export default function ChatPanel() {
  const dispatch = useDispatch()
  const { chatMessages, lastToolTrace, selectedHcpId, agentEnabled, error } = useSelector((s) => s.crm)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)

  const onSend = async () => {
    const text = input.trim()
    if (!text) return
    setSending(true)
    dispatch(pushUserMessage(text))
    setInput('')
    const history = [...chatMessages, { role: 'user', content: text }]
    try {
      await dispatch(sendChat({ messages: history, hcpId: selectedHcpId })).unwrap()
    } finally {
      setSending(false)
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
        background: '#fff',
        padding: '1.25rem',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 2px rgb(15 23 42 / 6%)',
        minHeight: '420px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0, fontSize: '1.05rem' }}>Conversational logging</h2>
        <button
          type="button"
          onClick={() => dispatch(clearChat())}
          style={{
            background: 'transparent',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
            padding: '0.35rem 0.65rem',
            cursor: 'pointer',
            fontSize: '0.85rem',
          }}
        >
          Clear thread
        </button>
      </div>

      {agentEnabled === false && (
        <p style={{ margin: 0, fontSize: '0.85rem', color: '#b45309', background: '#fffbeb', padding: '0.65rem', borderRadius: '8px' }}>
          Agent offline: set <code>GROQ_API_KEY</code> in <code>backend/.env</code> and restart the API. The structured form still works for logging.
        </p>
      )}

      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '0.75rem',
          background: '#f8fafc',
          maxHeight: '280px',
        }}
      >
        {chatMessages.length === 0 && (
          <p style={{ margin: 0, color: '#64748b', fontSize: '0.9rem' }}>
            Ask in natural language, for example: &quot;Search for Dr. Chen, log that we discussed renal outcomes and
            samples, then schedule follow-up next Friday.&quot;
          </p>
        )}
        {chatMessages.map((m, i) => (
          <div
            key={`${m.role}-${i}`}
            style={{
              marginBottom: '0.65rem',
              textAlign: m.role === 'user' ? 'right' : 'left',
            }}
          >
            <span
              style={{
                display: 'inline-block',
                maxWidth: '92%',
                padding: '0.5rem 0.65rem',
                borderRadius: '10px',
                background: m.role === 'user' ? '#0f766e' : '#e2e8f0',
                color: m.role === 'user' ? '#fff' : '#0f172a',
                fontSize: '0.9rem',
                whiteSpace: 'pre-wrap',
              }}
            >
              {m.content}
            </span>
          </div>
        ))}
      </div>

      {lastToolTrace?.length > 0 && (
        <details style={{ fontSize: '0.8rem', color: '#334155' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 600 }}>LangGraph tool trace (last reply)</summary>
          <pre
            style={{
              margin: '0.5rem 0 0',
              padding: '0.5rem',
              background: '#0f172a',
              color: '#e2e8f0',
              borderRadius: '8px',
              overflow: 'auto',
              maxHeight: '160px',
            }}
          >
            {JSON.stringify(lastToolTrace, null, 2)}
          </pre>
        </details>
      )}

      {agentEnabled !== false && error && (
        <p style={{ margin: 0, fontSize: '0.85rem', color: '#b91c1c' }}>{error}</p>
      )}

      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              onSend()
            }
          }}
          placeholder="Message the CRM agent…"
          disabled={sending}
          style={{
            flex: 1,
            padding: '0.55rem 0.65rem',
            borderRadius: '8px',
            border: '1px solid #cbd5e1',
          }}
        />
        <button
          type="button"
          onClick={onSend}
          disabled={sending}
          style={{
            background: '#0f172a',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            padding: '0 1rem',
            fontWeight: 600,
            cursor: sending ? 'wait' : 'pointer',
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}
