import { useEffect, useState } from 'react'
import { getABTest } from '../api'

function Metric({ label, control, treatment, higherIsBetter = true }) {
  const better = higherIsBetter
    ? treatment > control
    : treatment < control
  const diff = ((treatment - control) / Math.max(control, 0.001) * 100).toFixed(1)

  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 10, padding: '1.2rem'
    }}>
      <div style={{ fontSize: 11, color: 'var(--muted)', letterSpacing: '0.06em', marginBottom: 12 }}>
        {label}
      </div>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: 12 }}>
        {[
          { name: 'Control', value: control, color: 'var(--amber)' },
          { name: 'Treatment', value: treatment, color: 'var(--accent2)' }
        ].map(({ name, value, color }) => (
          <div key={name} style={{ flex: 1 }}>
            <div style={{ fontSize: 22, fontWeight: 600, color, letterSpacing: '-0.02em' }}>
              {typeof value === 'number' && value < 1
                ? `${(value * 100).toFixed(1)}%`
                : value}
            </div>
            <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 2 }}>{name}</div>
          </div>
        ))}
      </div>
      <div style={{
        fontSize: 12, fontWeight: 500,
        color: better ? 'var(--green)' : 'var(--red)',
        display: 'flex', alignItems: 'center', gap: 4
      }}>
        <span>{better ? '▲' : '▼'}</span>
        <span>{Math.abs(diff)}% {better ? 'improvement' : 'regression'}</span>
      </div>
    </div>
  )
}

export default function ABTest() {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getABTest()
      .then(r => setData(r.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ color: 'var(--muted)', padding: '2rem' }}>Loading...</div>
  )

  const ctrl = data?.variants?.control
  const trt  = data?.variants?.treatment

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: 20, fontWeight: 600, letterSpacing: '-0.02em' }}>
          A/B Test Results
        </h1>
        <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 4 }}>
          Two-tower neural net vs popularity baseline · {data?.total_events?.toLocaleString()} events
        </p>
      </div>

      {/* Winner banner */}
      <div style={{
        background: data?.winner === 'treatment' ? '#34d39910' : '#f8717110',
        border: `1px solid ${data?.winner === 'treatment' ? '#34d39940' : '#f8717140'}`,
        borderRadius: 10, padding: '1rem 1.5rem',
        marginBottom: '1.5rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
      }}>
        <div>
          <div style={{
            fontSize: 13, fontWeight: 600,
            color: data?.winner === 'treatment' ? 'var(--green)' : 'var(--red)'
          }}>
            {data?.winner === 'treatment' ? '✓ Treatment wins' : '✗ Control wins'}
          </div>
          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
            {data?.winner === 'treatment'
              ? `Two-tower model outperforms popularity baseline`
              : `Popularity baseline outperforms neural model`}
          </div>
        </div>
        <div style={{
          fontSize: 28, fontWeight: 700, letterSpacing: '-0.02em',
          color: data?.winner === 'treatment' ? 'var(--green)' : 'var(--red)'
        }}>
          +{data?.lift_pct}%
          <div style={{ fontSize: 11, fontWeight: 400, color: 'var(--muted)' }}>CTR lift</div>
        </div>
      </div>

      {/* Metrics grid */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '1rem', marginBottom: '2rem'
      }}>
        <Metric
          label="CLICK-THROUGH RATE"
          control={ctrl?.ctr}
          treatment={trt?.ctr}
          higherIsBetter={true}
        />
        <Metric
          label="SKIP RATE"
          control={ctrl?.skip_rate}
          treatment={trt?.skip_rate}
          higherIsBetter={false}
        />
        <Metric
          label="LIKE RATE"
          control={ctrl?.like_rate}
          treatment={trt?.like_rate}
          higherIsBetter={true}
        />
      </div>

      {/* Variant detail */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {[
          { key: 'control',   label: 'Control',   color: 'var(--amber)',   v: ctrl },
          { key: 'treatment', label: 'Treatment',  color: 'var(--accent2)', v: trt }
        ].map(({ key, label, color, v }) => (
          <div key={key} style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 10, padding: '1.2rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
              <span style={{ fontSize: 11, color, letterSpacing: '0.06em' }}>
                {label.toUpperCase()}
              </span>
              <span style={{
                fontSize: 11, color: 'var(--muted)',
                background: 'var(--border)', borderRadius: 3,
                padding: '1px 6px'
              }}>
                {v?.model}
              </span>
            </div>
            {[
              { label: 'Impressions', value: v?.impressions?.toLocaleString() },
              { label: 'Clicks',      value: v?.clicks?.toLocaleString() },
              { label: 'CTR',         value: `${(v?.ctr * 100).toFixed(1)}%` },
              { label: 'Skip rate',   value: `${(v?.skip_rate * 100).toFixed(1)}%` },
              { label: 'Like rate',   value: `${(v?.like_rate * 100).toFixed(1)}%` },
            ].map(({ label, value }) => (
              <div key={label} style={{
                display: 'flex', justifyContent: 'space-between',
                marginBottom: 8, fontSize: 13
              }}>
                <span style={{ color: 'var(--muted)' }}>{label}</span>
                <span style={{ fontWeight: 500 }}>{value}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}