import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import './App.css'

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="app">
      <div className="particles">
        {[...Array(28)].map((_, i) => (
          <div key={i} className="particle" style={{ '--i': i }} />
        ))}
      </div>

      <nav className={`nav ${scrolled ? 'nav-scrolled' : ''}`}>
        <div className="nav-inner">
          <Link to="/" className="logo">
            <span className="logo-icon">✦</span> MedWing
          </Link>
          <div className="nav-links">
            <Link to="/dashboard">Explore</Link>
          </div>
        </div>
      </nav>

      <header className="hero">
        <div className="hero-bg">
          <div className="hero-bg-image" />
          <div className="hero-overlay" />
          <div className="hero-gradient" />
        </div>

        <div className="hero-content">
          <p className="hero-badge">Fully Agentic AI Platform</p>
          <h1 className="hero-title">
            <span className="hero-title-line">Medicine delivery</span>
            <span className="hero-title-line accent">beyond boundaries</span>
          </h1>
          <p className="hero-subtitle">
            Reaching geographically deprived communities with voice agents,
            facial identification, and SLAM mapping—so no one is left behind.
          </p>
          
          <div className="hero-phone-box">
            <div className="phone-icon">📞</div>
            <div className="phone-content">
              <p className="phone-label">Order Emergency Medicine Now</p>
              <a href="tel:+16502527766" className="phone-number">+1 (650) 252-7766</a>
              <p className="phone-subtitle">Voice-controlled drone delivery • Available 24/7</p>
            </div>
          </div>
          
          <div className="hero-cta">
            <Link to="/dashboard" className="btn btn-primary">
              Explore the platform
            </Link>
            <a href="#" className="btn btn-ghost">
              Our mission
            </a>
          </div>
        </div>

        <div className="hero-scroll">
          <div className="scroll-line" />
        </div>
      </header>
    </div>
  )
}
