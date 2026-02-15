import { Routes, Route } from 'react-router-dom'
import LandingPage from './LandingPage.jsx'
import Dashboard from './Dashboard.jsx'
import SavedCalls from './SavedCalls.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/saved-calls" element={<SavedCalls />} />
    </Routes>
  )
}
