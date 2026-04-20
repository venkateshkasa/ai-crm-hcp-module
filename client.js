import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export async function getHealth() {
  const { data } = await api.get('/health')
  return data
}

export async function listHcps() {
  const { data } = await api.get('/hcps')
  return data
}

export async function listInteractions(hcpId) {
  const { data } = await api.get('/interactions', {
    params: hcpId ? { hcp_id: hcpId } : {},
  })
  return data
}

export async function createInteraction(payload) {
  const { data } = await api.post('/interactions', payload)
  return data
}

export async function agentChat(messages, hcpId) {
  const { data } = await api.post('/agent/chat', {
    messages,
    hcp_id: hcpId ?? null,
  })
  return data
}
