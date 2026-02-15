import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    this.setState({
      error,
      errorInfo
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(165deg, #1a1f2e 0%, #1e2535 40%, #161b28 100%)',
          padding: '2rem'
        }}>
          <div style={{
            maxWidth: '600px',
            background: 'rgba(139, 92, 246, 0.1)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '1rem',
            padding: '2rem',
            backdropFilter: 'blur(12px)',
            textAlign: 'center'
          }}>
            <div style={{
              width: '80px',
              height: '80px',
              margin: '0 auto 1.5rem',
              background: 'linear-gradient(135deg, #a78bfa, #38bdf8)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2.5rem'
            }}>
              ⚠️
            </div>
            
            <h1 style={{
              fontSize: '1.75rem',
              fontWeight: '700',
              color: '#f5f2ed',
              marginBottom: '0.75rem',
              fontFamily: 'Sora, sans-serif'
            }}>
              Oops! Something went wrong
            </h1>
            
            <p style={{
              fontSize: '1rem',
              color: 'rgba(245, 242, 237, 0.7)',
              marginBottom: '2rem',
              lineHeight: '1.6'
            }}>
              We're sorry for the inconvenience. The MedWing dashboard encountered an unexpected error. 
              Please try refreshing the page or contact support if the problem persists.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details style={{
                marginBottom: '1.5rem',
                textAlign: 'left',
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '1rem',
                borderRadius: '0.5rem',
                fontSize: '0.85rem',
                color: '#fb7185'
              }}>
                <summary style={{ cursor: 'pointer', marginBottom: '0.5rem', fontWeight: '600' }}>
                  Error Details (Development Mode)
                </summary>
                <pre style={{
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  fontSize: '0.75rem',
                  lineHeight: '1.4'
                }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button
                onClick={() => window.location.reload()}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'linear-gradient(135deg, #a78bfa, #38bdf8)',
                  color: '#0f172a',
                  border: 'none',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  fontFamily: 'Plus Jakarta Sans, sans-serif'
                }}
                onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
                onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
              >
                Refresh Page
              </button>
              
              <button
                onClick={() => window.location.href = '/'}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'rgba(139, 92, 246, 0.2)',
                  color: '#a78bfa',
                  border: '1px solid rgba(139, 92, 246, 0.4)',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  fontFamily: 'Plus Jakarta Sans, sans-serif'
                }}
                onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
                onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
              >
                Go to Home
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
