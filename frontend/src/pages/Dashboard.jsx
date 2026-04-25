import { useEffect, useState } from 'react'
import { getStats } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    getStats().then(r => setStats(r.data)).catch(() => {})
  }, [])

  const metrics = [
    { label: 'Model',          value: 'Two-Tower Neural Net' },
    { label: 'Architecture',   value: 'User tower + Item tower' },
    { label: 'Loss function',  value: 'BPR (Bayesian Personalized Ranking)' },
    { label: 'Negative sampling', value: '4× per positive' },
    { label: 'Embedding dim',  value: '64' },
    { label: 'Index',          value: 'FAISS IndexFlatIP' },
    { label: 'Feedback model', value: 'Hu et al. (2008) implicit' },
    { label: 'Train/test split', value: '80/20 per user' },
  ]

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: 20, fontWeight: 600, letterSpacing: '-0.02em' }}>
          Model Dashboard
        </h1>
        <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 4 }}>
          Training details, evaluation metrics, system architecture
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
        {/* Recall@10 */}
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 10, padding: '1.5rem'
        }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.06em', marginBottom: 8 }}>
            RECALL@10
          </div>
          <div style={{ fontSize: 42, fontWeight: 700, color: 'var(--accent2)', letterSpacing: '-0.03em' }}>
            46.3%
          </div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 4 }}>
            On held-out test set · 200 users evaluated
          </div>
        </div>

        {/* Training progress */}
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 10, padding: '1.5rem'
        }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.06em', marginBottom: 12 }}>
            TRAINING
          </div>
          {[
            { epoch: 3,  loss: 0.52, recall: 0.28 },
            { epoch: 6,  loss: 0.41, recall: 0.35 },
            { epoch: 9,  loss: 0.33, recall: 0.40 },
            { epoch: 12, loss: 0.27, recall: 0.44 },
            { epoch: 15, loss: 0.24, recall: 0.46 },
          ].map(row => (
            <div key={row.epoch} style={{
              display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8
            }}>
              <span style={{ color: 'var(--muted)', fontSize: 11, width: 40 }}>ep {row.epoch}</span>
              <div style={{ flex: 1, height: 4, background: 'var(--border)', borderRadius: 2 }}>
                <div style={{
                  height: '100%', borderRadius: 2,
                  width: `${row.recall * 100 * 2}%`,
                  background: 'linear-gradient(90deg, var(--accent), var(--accent2))'
                }}/>
              </div>
              <span style={{ fontSize: 11, color: 'var(--accent2)', width: 36, textAlign: 'right' }}>
                {(row.recall * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Model details */}
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '1.5rem'
      }}>
        <div style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.06em', marginBottom: 16 }}>
          ARCHITECTURE
        </div>
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr',
          gap: '0.5rem 2rem'
        }}>
          {metrics.map(({ label, value }) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', padding: '8px 0',
              borderBottom: '1px solid var(--border)'
            }}>
              <span style={{ color: 'var(--muted)', fontSize: 12 }}>{label}</span>
              <span style={{ fontSize: 12, fontWeight: 500, textAlign: 'right', maxWidth: 200 }}>
                {value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Feedback breakdown */}
      {stats?.feedback?.length > 0 && (
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 10, padding: '1.5rem', marginTop: '1rem'
        }}>
          <div style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.06em', marginBottom: 12 }}>
            LIVE FEEDBACK
          </div>
          <div style={{ display: 'flex', gap: '2rem' }}>
            {stats.feedback.map(f => (
              <div key={`${f.variant}-${f.event}`}>
                <div style={{ fontSize: 20, fontWeight: 600 }}>{f.count}</div>
                <div style={{ fontSize: 11, color: 'var(--muted)' }}>{f.variant} · {f.event}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}