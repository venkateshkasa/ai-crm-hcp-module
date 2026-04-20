import { configureStore } from '@reduxjs/toolkit'
import crmReducer from './interactionSlice'

export const store = configureStore({
  reducer: {
    crm: crmReducer,
  },
})
