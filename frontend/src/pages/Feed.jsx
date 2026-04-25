import { useState, useEffect } from 'react'
import { getRecommendations, sendFeedback } from '../api'
import TrackCard from '../components/TrackCard'
import { usePlayer } from '../hooks/usePlayer'

const USERS = [1, 2, 3, 42, 99, 200, 500, 750]

export default function Feed() {
  const [userId, setUserId]     = useState(1)
  const [results, setResults]   = useState([])
  const [variant, setVariant]   = useState('')
  const [loading, setLoading]   = useState(false)
  const { playing, liked, skipped, play, skip, like } = usePlayer(userId)

  const fetchRecs = async (uid) => {
    setLoading(true)
    try {
      const r = await getRecommendations(uid)
      setResults(r.data.results)
      setVariant(r.data.variant)
      // Log impressions
      r.data.results.forEach(res =>
        sendFeedback(uid, res.artist_id, 'impression').catch(() => {})
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchRecs(userId) }, [userId])

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '2rem' }}>
      {/* Main feed */}
      <div>
        {/* Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{ fontSize: 20, fontWeight: 600, letterSpacing: '-0.02em' }}>
                For you
              </h1>
              <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 2 }}>
                Personalized via two-tower neural network
              </p>
            </div>
            <div style={{
              fontSize: 11, padding: '4px 10px',
              borderRadius: 4, letterSpacing: '0.05em',
              background: variant === 'treatment' ? '#7c6af720' : '#fbbf2420',
              border: `1px solid ${variant === 'treatment' ? '#7c6af750' : '#fbbf2450'}`,
              color: variant === 'treatment' ? 'var(--accent2)' : 'var(--amber)'
            }}>
              {variant === 'treatment' ? 'TWO-TOWER' : 'POPULARITY'}
            </div>
          </div>
        </div>

        {/* Track list */}
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[...Array(8)].map((_, i) => (
              <div key={i} style={{
                height: 72, borderRadius: 10,
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                animation: 'pulse 1.5s infinite',
                animationDelay: `${i * 0.05}s`
              }}/>
            ))}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {results.map(r => (
              <TrackCard
                key={r.artist_id}
                result={r}
                playing={playing}
                liked={liked}
                skipped={skipped}
                onPlay={play}
                onSkip={skip}
                onLike={like}
              />
            ))}
          </div>
        )}
      </div>

      {/* Sidebar */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* User selector */}
        <div style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 10, padding: '1rem'
        }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.06em', marginBottom: 10 }}>
            USER
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {USERS.map(u => (
              <button key={u} onClick={() => setUserId(u)} style={{
                padding: '4px 10px', borderRadius: 6, fontSize: 12,
                background: userId === u ? 'var(--accent)' : 'var(--border)',
                border: `1px solid ${userId === u ? 'var(--accent)' : 'var(--border2)'}`,
                color: userId === u ? '#fff' : 'var(--muted)',
                transition: 'all 0.15s'
              }}>
                {u}
              </button>
            ))}
          </div>
        </div>

        {/* Model info */}
        <div style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 10, padding: '1rem'
        }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.06em', marginBottom: 10 }}>
            MODEL
          </div>
          {[
            { label: 'Architecture', value: 'Two-tower NN' },
            { label: 'Embedding dim', value: '64' },
            { label: 'Recall@10', value: '46.3%' },
            { label: 'Index', value: 'FAISS (IP)' },
            { label: 'Feedback', value: 'Implicit (Hu 2008)' },
          ].map(({ label, value }) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', marginBottom: 8
            }}>
              <span style={{ color: 'var(--muted)', fontSize: 12 }}>{label}</span>
              <span style={{ fontSize: 12, fontWeight: 500 }}>{value}</span>
            </div>
          ))}
        </div>

        {/* Activity */}
        <div style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 10, padding: '1rem'
        }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.06em', marginBottom: 10 }}>
            SESSION
          </div>
          {[
            { label: 'Liked',   value: liked.size,   color: 'var(--red)' },
            { label: 'Skipped', value: skipped.size, color: 'var(--muted)' },
            { label: 'Playing', value: playing !== null ? 1 : 0, color: 'var(--green)' },
          ].map(({ label, value, color }) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', marginBottom: 8
            }}>
              <span style={{ color: 'var(--muted)', fontSize: 12 }}>{label}</span>
              <span style={{ fontSize: 13, fontWeight: 600, color }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}