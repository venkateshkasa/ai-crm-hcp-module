import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { setSelectedHcpId, submitStructuredInteraction } from '../store/interactionSlice'

const channels = [
  { value: 'in_person', label: 'In person' },
  { value: 'virtual', label: 'Virtual' },
  { value: 'phone', label: 'Phone' },
]

export default function InteractionForm() {
  const dispatch = useDispatch()
  const { hcps, selectedHcpId } = useSelector((s) => s.crm)
  const [channel, setChannel] = useState('in_person')
  const [rawNotes, setRawNotes] = useState('')
  const [localStatus, setLocalStatus] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!selectedHcpId) {
      setLocalStatus('Select an HCP first.')
      return
    }
    setLocalStatus(null)
    setSubmitting(true)
    try {
      await dispatch(
        submitStructuredInteraction({
          hcp_id: selectedHcpId,
          channel,
          raw_notes: rawNotes,
        }),
      ).unwrap()
      setRawNotes('')
      setLocalStatus('Saved. Summary and entities were generated with Groq.')
    } catch (err) {
      setLocalStatus(err?.message || 'Save failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.85rem',
        background: '#fff',
        padding: '1.25rem',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 2px rgb(15 23 42 / 6%)',
      }}
    >
      <div>
        <label
          htmlFor="hcp"
          style={{ display: 'block', fontWeight: 600, marginBottom: '0.35rem', fontSize: '0.9rem' }}
        >
          Healthcare professional
        </label>
        <select
          id="hcp"
          value={selectedHcpId ?? ''}
          onChange={(e) => dispatch(setSelectedHcpId(Number(e.target.value)))}
          style={{ width: '100%', padding: '0.5rem 0.6rem', borderRadius: '8px', border: '1px solid #cbd5e1' }}
        >
          {hcps.map((h) => (
            <option key={h.id} value={h.id}>
              {h.name} — {h.specialty}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor="channel"
          style={{ display: 'block', fontWeight: 600, marginBottom: '0.35rem', fontSize: '0.9rem' }}
        >
          Channel
        </label>
        <select
          id="channel"
          value={channel}
          onChange={(e) => setChannel(e.target.value)}
          style={{ width: '100%', padding: '0.5rem 0.6rem', borderRadius: '8px', border: '1px solid #cbd5e1' }}
        >
          {channels.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor="notes"
          style={{ display: 'block', fontWeight: 600, marginBottom: '0.35rem', fontSize: '0.9rem' }}
        >
          Visit notes (raw)
        </label>
        <textarea
          id="notes"
          required
          value={rawNotes}
          onChange={(e) => setRawNotes(e.target.value)}
          rows={8}
          placeholder="e.g. Discussed lipid data, asked about renal cohort eligibility. Left leave-behind on dosing card."
          style={{
            width: '100%',
            padding: '0.65rem 0.75rem',
            borderRadius: '8px',
            border: '1px solid #cbd5e1',
            resize: 'vertical',
          }}
        />
      </div>

      <button
        type="submit"
        disabled={submitting}
        style={{
          alignSelf: 'flex-start',
          background: '#0f766e',
          color: '#fff',
          border: 'none',
          borderRadius: '8px',
          padding: '0.55rem 1.1rem',
          fontWeight: 600,
          cursor: submitting ? 'wait' : 'pointer',
        }}
      >
        Log interaction (structured)
      </button>
      {localStatus && (
        <p style={{ margin: 0, fontSize: '0.85rem', color: localStatus.includes('failed') ? '#b91c1c' : '#0f766e' }}>
          {localStatus}
        </p>
      )}
    </form>
  )
}
