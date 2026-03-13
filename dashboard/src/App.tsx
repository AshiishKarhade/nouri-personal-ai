import { BrowserRouter, Route, Routes, NavLink } from 'react-router-dom'
import { LayoutDashboard, History, TrendingUp, Settings } from 'lucide-react'
import { Today } from './pages/Today'
import { HistoryPage } from './pages/History'
import { Progress } from './pages/Progress'
import { SettingsPage } from './pages/Settings'
import './index.css'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Today', end: true },
  { to: '/history', icon: History, label: 'History', end: false },
  { to: '/progress', icon: TrendingUp, label: 'Progress', end: false },
  { to: '/settings', icon: Settings, label: 'Settings', end: false },
]

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg)' }}>
        {/* Page content */}
        <main style={{ flex: 1, overflowY: 'auto', paddingBottom: 72 }}>
          <div style={{ maxWidth: 480, margin: '0 auto' }}>
            <Routes>
              <Route path="/" element={<Today />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/progress" element={<Progress />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>

        {/* Bottom nav */}
        <nav
          style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'var(--bg-card)',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            zIndex: 50,
          }}
        >
          {NAV.map(({ to, icon: Icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              style={({ isActive }) => ({
                flex: 1,
                display: 'flex',
                flexDirection: 'column' as const,
                alignItems: 'center',
                justifyContent: 'center',
                padding: '10px 0 14px',
                textDecoration: 'none',
                color: isActive ? 'var(--accent-green)' : 'var(--text-secondary)',
                gap: 4,
                transition: 'color 0.15s',
              })}
            >
              <Icon size={22} />
              <span style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.04em' }}>
                {label.toUpperCase()}
              </span>
            </NavLink>
          ))}
        </nav>
      </div>
    </BrowserRouter>
  )
}
