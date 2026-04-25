import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Feed      from './pages/Feed'
import ABTest    from './pages/ABTest'
import Dashboard from './pages/Dashboard'

const navStyle = ({ isActive }) => ({
  color: isActive ? 'var(--accent2)' : 'var(--muted)',
  fontWeight: isActive ? 500 : 400,
  fontSize: 13,
  letterSpacing: '0.01em',
  paddingBottom: 2,
  borderBottom: isActive ? '1px solid var(--accent)' : '1px solid transparent',
  transition: 'all 0.15s'
})

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
        {/* Topbar */}
        <header style={{
          position: 'sticky', top: 0, zIndex: 100,
          background: 'rgba(10,10,15,0.85)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid var(--border)',
          padding: '0 2rem',
          display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', height: 52
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 22, height: 22, borderRadius: 6,
              background: 'linear-gradient(135deg, var(--accent), var(--accent2))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 11, fontWeight: 700, color: '#fff'
            }}>R</div>
            <span style={{ fontWeight: 600, fontSize: 14, letterSpacing: '-0.01em' }}>
              RecSys
            </span>
          </div>
          <nav style={{ display: 'flex', gap: 28 }}>
            <NavLink to="/"          style={navStyle}>Feed</NavLink>
            <NavLink to="/ab-test"   style={navStyle}>A/B Test</NavLink>
            <NavLink to="/dashboard" style={navStyle}>Dashboard</NavLink>
          </nav>
          <div style={{
            fontSize: 11, color: 'var(--muted)',
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 4, padding: '3px 8px',
            letterSpacing: '0.05em'
          }}>
            TWO-TOWER
          </div>
        </header>

        <main style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 1.5rem' }}>
          <Routes>
            <Route path="/"          element={<Feed />} />
            <Route path="/ab-test"   element={<ABTest />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}