import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './Dashboard.css'

export default function Dashboard() {
  const [message, setMessage] = useState('')
  const [sentMessages, setSentMessages] = useState([])
  const [liveTranscript, setLiveTranscript] = useState([])
  const textareaRef = useRef(null)

  // Connect to live transcript SSE endpoint
  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8000/live-transcript')

    eventSource.onmessage = (event) => {
      const transcript = JSON.parse(event.data)
      setLiveTranscript((prev) => [...prev, transcript])
    }

    eventSource.onerror = (error) => {
      console.error('SSE error:', error)
      eventSource.close()
    }

    return () => eventSource.close()
  }, [])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`
  }, [message])

  const handleSend = () => {
    const text = message.trim()
    if (text) {
      const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      setSentMessages((prev) => [...prev, { text, time, id: Date.now() }])
      setMessage('')
    }
  }

  const handleSaveTranscripts = () => {
    // Combine all transcripts
    const allTranscripts = [...activity, ...liveTranscript, ...sentMessages.map(m => ({
      speaker: 'You',
      text: m.text,
      time: m.time
    }))]

    if (allTranscripts.length === 0) {
      alert('No transcripts to save')
      return
    }

    // Deduplicate: Remove incremental duplicates
    // Keep only the longest message from each speaker at each timestamp
    const deduped = []
    const seen = new Map() // key: speaker+time, value: index in deduped array

    for (const transcript of allTranscripts) {
      const key = `${transcript.speaker || transcript.name}|${transcript.time}`
      const existingIndex = seen.get(key)

      if (existingIndex !== undefined) {
        // Already have a message from this speaker at this time
        // Keep the longer one (more complete)
        if (transcript.text.length > deduped[existingIndex].text.length) {
          deduped[existingIndex] = transcript
        }
      } else {
        // New speaker+time combination
        seen.set(key, deduped.length)
        deduped.push(transcript)
      }
    }

    // Create call record
    const callRecord = {
      id: Date.now(),
      date: new Date().toLocaleString(),
      duration: 0, // Could calculate from timestamps
      transcripts: deduped
    }

    // Get existing saved calls
    const existing = localStorage.getItem('medwing_saved_calls')
    const savedCalls = existing ? JSON.parse(existing) : []

    // Add new call
    savedCalls.unshift(callRecord) // Add to beginning

    // Save to localStorage
    localStorage.setItem('medwing_saved_calls', JSON.stringify(savedCalls))

    // Show success message
    alert(`✅ Call saved! ${deduped.length} unique messages saved.\n\nView in Saved Calls tab.`)
  }
  const deliveries = [
    { title: 'Valle Alto - Insulin & supplies', status: 'in-progress', time: '4h' },
    { title: 'Sierra Norte - Vaccines batch', status: 'on-hold', time: '8h' },
    { title: 'Amazonas región - Emergency kit', status: 'done', time: '2h' },
  ]

  const activity = [
    { name: 'Drone Alpha-01', time: '10:32 AM', text: 'Completed delivery to Valle Alto. Recipient verified via facial ID.', color: 'coral' },
    { name: 'Voice Agent', time: '09:15 AM', text: 'New request received: "Send antibiotics to Sector 7"', color: 'blue' },
  ]

  return (
    <div className="dashboard">
      <aside className="dashboard-sidebar">
        <Link to="/" className="dashboard-logo">
          <span className="dashboard-logo-icon">✦</span>
          MedWing
        </Link>
        <nav className="dashboard-nav">
          <a href="#" className="dashboard-nav-item active">
            <span className="dashboard-nav-icon">◉</span>
            Overview
          </a>
          <a href="#" className="dashboard-nav-item">
            <span className="dashboard-nav-icon">▦</span>
            Deliveries
          </a>
          <a href="#" className="dashboard-nav-item">
            <span className="dashboard-nav-icon">◐</span>
            Fleet
          </a>
          <a href="#" className="dashboard-nav-item">
            <span className="dashboard-nav-icon">◎</span>
            Mapping
          </a>
          <a href="#" className="dashboard-nav-item">
            <span className="dashboard-nav-icon">⚙</span>
            Settings
          </a>
          <Link to="/saved-calls" className="dashboard-nav-item">
            <span className="dashboard-nav-icon">📞</span>
            Saved Calls
          </Link>
        </nav>
        <div className="dashboard-sidebar-user">
          <img src="/strange.jpeg" alt="Dr. Stephen Strange" className="dashboard-sidebar-user-avatar" />
          <span className="dashboard-sidebar-user-name">Dr. Stephen Strange</span>
        </div>
        <button className="dashboard-configure-btn">Configure profile</button>
        <div className="dashboard-footer">
          <a href="#">Help</a>
          <Link to="/">Back to home</Link>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <h1>Hello, Dr. Strange</h1>
            <p>Monitor deliveries and fleet status. You're on track today.</p>
          </div>
          <div className="dashboard-date">14 Feb, 2025</div>
        </header>

        <section className="dashboard-list">
          <div className="dashboard-list-header">
            <h2>Active Deliveries</h2>
            <select className="dashboard-select">
              <option>This week</option>
            </select>
          </div>
          <ul className="dashboard-deliveries">
            {deliveries.map((d, i) => (
              <li key={i} className="dashboard-delivery">
                <span className="dashboard-delivery-icon">◉</span>
                <div className="dashboard-delivery-info">
                  <span className="dashboard-delivery-title">{d.title}</span>
                  <span className={`dashboard-delivery-status status-${d.status}`}>
                    {d.status === 'in-progress' && 'In progress'}
                    {d.status === 'on-hold' && 'On hold'}
                    {d.status === 'done' && 'Done'}
                  </span>
                </div>
                <span className="dashboard-delivery-time">{d.time}</span>
              </li>
            ))}
          </ul>
        </section>
      </main>

      <aside className="dashboard-activity">
        <div className="dashboard-profile">
          <div className="dashboard-avatar">MW</div>
          <div>
            <strong>MedWing AI</strong>
            <span>@medwing_ai</span>
          </div>
        </div>
        <div className="dashboard-activity-feed">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0 }}>Activity</h3>
            <button
              onClick={handleSaveTranscripts}
              style={{
                padding: '6px 12px',
                fontSize: '13px',
                background: 'rgba(100, 200, 255, 0.1)',
                border: '1px solid rgba(100, 200, 255, 0.3)',
                borderRadius: '6px',
                color: '#64c8ff',
                cursor: 'pointer',
                fontWeight: '500'
              }}
              onMouseOver={(e) => e.target.style.background = 'rgba(100, 200, 255, 0.2)'}
              onMouseOut={(e) => e.target.style.background = 'rgba(100, 200, 255, 0.1)'}
            >
              Save Transcripts
            </button>
          </div>
          {activity.map((a, i) => (
            <div key={i} className="dashboard-activity-item">
              <div className={`dashboard-activity-avatar avatar-${a.color}`}>{a.name[0]}</div>
              <div>
                <span className="dashboard-activity-name">{a.name}</span>
                <span className="dashboard-activity-time">{a.time}</span>
                <p>{a.text}</p>
              </div>
            </div>
          ))}
          {liveTranscript.map((t, i) => (
            <div key={i} className="dashboard-activity-item">
              <div className={`dashboard-activity-avatar avatar-${t.speaker === 'VAPI Agent' ? 'blue' : 'green'}`}>
                {t.speaker === 'VAPI Agent' ? 'V' : 'U'}
              </div>
              <div>
                <span className="dashboard-activity-name">{t.speaker}</span>
                <span className="dashboard-activity-time">{t.time}</span>
                <p>{t.text}</p>
              </div>
            </div>
          ))}
          {sentMessages.map((msg) => (
            <div key={msg.id} className="dashboard-activity-item dashboard-activity-item-sent">
              <img src="/strange.jpeg" alt="You" className="dashboard-activity-avatar avatar-you-img" />
              <div>
                <span className="dashboard-activity-name">You</span>
                <span className="dashboard-activity-time">{msg.time}</span>
                <p>{msg.text}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="dashboard-message-input">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
            placeholder="Send command..."
            rows={1}
          />
          <button
            type="button"
            className="dashboard-send-btn"
            onClick={handleSend}
            aria-label="Send message"
          >
            →
          </button>
        </div>
      </aside>
    </div>
  )
}
