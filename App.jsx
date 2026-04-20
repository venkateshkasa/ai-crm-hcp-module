import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import LogInteractionScreen from './components/LogInteractionScreen'
import { bootstrap } from './store/interactionSlice'

export default function App() {
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(bootstrap())
  }, [dispatch])

  return <LogInteractionScreen />
}
