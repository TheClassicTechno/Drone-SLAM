import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './SavedCalls.css'

export default function SavedCalls() {
  const [savedCalls, setSavedCalls] = useState([])

  useEffect(() => {
    // Load saved calls from localStorage
    const stored = localStorage.getItem('medwing_saved_calls')
    if (stored) {
      setSavedCalls(JSON.parse(stored))
    }
  }, [])

  const handleDelete = (callId) => {
    const updated = savedCalls.filter(call => call.id !== callId)
    setSavedCalls(updated)
    localStorage.setItem('medwing_saved_calls', JSON.stringify(updated))
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="saved-calls-container">
      <Link to="/dashboard" className="back-button">← Back to Dashboard</Link>
      <div className="saved-calls-header">
        <h1>Saved Call Transcripts</h1>
        <p>{savedCalls.length} call{savedCalls.length !== 1 ? 's' : ''} saved</p>
      </div>

      {savedCalls.length === 0 ? (
        <div className="no-calls">
          <div className="no-calls-icon">📞</div>
          <h2>No saved calls yet</h2>
          <p>Call transcripts will appear here after you save them from the Activity feed</p>
        </div>
      ) : (
        <div className="calls-list">
          {savedCalls.map((call) => (
            <div key={call.id} className="call-card">
              <div className="call-card-header">
                <div className="call-card-title">
                  <h3>Call on {call.date}</h3>
                  <div className="call-card-meta">
                    <span>Duration: {formatDuration(call.duration || 0)}</span>
                    <span>•</span>
                    <span>{call.transcripts.length} messages</span>
                  </div>
                </div>
                <button
                  className="delete-btn"
                  onClick={() => handleDelete(call.id)}
                  title="Delete call"
                >
                  ✕
                </button>
              </div>

              <div className="call-transcripts">
                <table className="transcripts-table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Speaker</th>
                      <th>Message</th>
                    </tr>
                  </thead>
                  <tbody>
                    {call.transcripts.map((t, i) => (
                      <tr key={i} className={`transcript-row ${t.role || ''}`}>
                        <td className="time-col">{t.time}</td>
                        <td className="speaker-col">
                          <span className={`speaker-badge ${t.speaker === 'VAPI Agent' ? 'agent' : 'user'}`}>
                            {t.speaker || t.name}
                          </span>
                        </td>
                        <td className="message-col">{t.text}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
