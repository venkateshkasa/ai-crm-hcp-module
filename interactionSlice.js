import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import * as api from '../api/client'

const initialState = {
  hcps: [],
  interactions: [],
  chatMessages: [],
  lastToolTrace: [],
  mode: 'form',
  selectedHcpId: null,
  status: 'idle',
  error: null,
  agentEnabled: null,
}

export const bootstrap = createAsyncThunk('crm/bootstrap', async () => {
  const health = await api.getHealth()
  const hcps = await api.listHcps()
  const interactions = await api.listInteractions()
  return { health, hcps, interactions }
})

export const refreshInteractions = createAsyncThunk(
  'crm/refreshInteractions',
  async (hcpId) => api.listInteractions(hcpId || undefined),
)

export const submitStructuredInteraction = createAsyncThunk(
  'crm/submitStructured',
  async (payload, { dispatch }) => {
    const row = await api.createInteraction(payload)
    await dispatch(refreshInteractions())
    return row
  },
)

export const sendChat = createAsyncThunk(
  'crm/sendChat',
  async ({ messages, hcpId }, { dispatch }) => {
    const res = await api.agentChat(messages, hcpId)
    await dispatch(refreshInteractions())
    return res
  },
)

const slice = createSlice({
  name: 'crm',
  initialState,
  reducers: {
    setMode(state, action) {
      state.mode = action.payload
      state.error = null
    },
    setSelectedHcpId(state, action) {
      state.selectedHcpId = action.payload
    },
    pushUserMessage(state, action) {
      state.chatMessages.push({ role: 'user', content: action.payload })
    },
    clearChat(state) {
      state.chatMessages = []
      state.lastToolTrace = []
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(bootstrap.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(bootstrap.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.error = null
        state.agentEnabled = action.payload.health.agent_enabled
        state.hcps = action.payload.hcps
        state.interactions = action.payload.interactions
        if (!state.selectedHcpId && action.payload.hcps.length) {
          state.selectedHcpId = action.payload.hcps[0].id
        }
      })
      .addCase(bootstrap.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.error.message
      })
      .addCase(refreshInteractions.fulfilled, (state, action) => {
        state.interactions = action.payload
      })
      .addCase(submitStructuredInteraction.rejected, (state, action) => {
        state.error = action.error.message
      })
      .addCase(sendChat.pending, (state) => {
        state.error = null
      })
      .addCase(sendChat.fulfilled, (state, action) => {
        state.chatMessages.push({
          role: 'assistant',
          content: action.payload.reply,
        })
        state.lastToolTrace = action.payload.tool_calls_trace || []
        state.error = null
      })
      .addCase(sendChat.rejected, (state, action) => {
        state.error = action.error.message
      })
  },
})

export const { setMode, setSelectedHcpId, pushUserMessage, clearChat } = slice.actions
export default slice.reducer
