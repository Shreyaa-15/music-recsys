const GENRE_COLORS = {
  rock:        '#f87171',
  pop:         '#fb923c',
  'hip-hop':   '#fbbf24',
  electronic:  '#34d399',
  jazz:        '#60a5fa',
  classical:   '#a78bfa',
  metal:       '#94a3b8',
  indie:       '#f472b6',
  'r&b':       '#c084fc',
  folk:        '#86efac',
}

const ARTISTS = [
  { name: "Radiohead",          genre: "rock" },
  { name: "Coldplay",           genre: "pop" },
  { name: "Kendrick Lamar",     genre: "hip-hop" },
  { name: "Daft Punk",          genre: "electronic" },
  { name: "Miles Davis",        genre: "jazz" },
  { name: "Bach",               genre: "classical" },
  { name: "Metallica",          genre: "metal" },
  { name: "Arctic Monkeys",     genre: "indie" },
  { name: "Frank Ocean",        genre: "r&b" },
  { name: "Fleet Foxes",        genre: "folk" },
  { name: "Portishead",         genre: "electronic" },
  { name: "The Beatles",        genre: "rock" },
  { name: "Drake",              genre: "hip-hop" },
  { name: "Aphex Twin",         genre: "electronic" },
  { name: "Coltrane",           genre: "jazz" },
  { name: "Pink Floyd",         genre: "rock" },
  { name: "Taylor Swift",       genre: "pop" },
  { name: "Kanye West",         genre: "hip-hop" },
  { name: "Brian Eno",          genre: "electronic" },
  { name: "Nick Drake",         genre: "folk" },
  { name: "Thom Yorke",         genre: "indie" },
  { name: "Billie Eilish",      genre: "pop" },
  { name: "Tyler the Creator",  genre: "hip-hop" },
  { name: "Four Tet",           genre: "electronic" },
  { name: "Bill Evans",         genre: "jazz" },
  { name: "Black Sabbath",      genre: "metal" },
  { name: "Bon Iver",           genre: "indie" },
  { name: "SZA",                genre: "r&b" },
  { name: "Sufjan Stevens",     genre: "folk" },
  { name: "LCD Soundsystem",    genre: "electronic" },
  { name: "The Strokes",        genre: "rock" },
  { name: "Lorde",              genre: "pop" },
  { name: "J. Cole",            genre: "hip-hop" },
  { name: "Burial",             genre: "electronic" },
  { name: "Thelonious Monk",    genre: "jazz" },
  { name: "Tool",               genre: "metal" },
  { name: "Vampire Weekend",    genre: "indie" },
  { name: "Solange",            genre: "r&b" },
  { name: "Iron & Wine",        genre: "folk" },
  { name: "Massive Attack",     genre: "electronic" },
  { name: "Joy Division",       genre: "rock" },
  { name: "Lana Del Rey",       genre: "pop" },
  { name: "Pusha T",            genre: "hip-hop" },
  { name: "Boards of Canada",   genre: "electronic" },
  { name: "Charles Mingus",     genre: "jazz" },
  { name: "Opeth",              genre: "metal" },
  { name: "Tame Impala",        genre: "indie" },
  { name: "Erykah Badu",        genre: "r&b" },
  { name: "Elliot Smith",       genre: "folk" },
  { name: "The Chemical Brothers", genre: "electronic" },
]

export default function TrackCard({ result, playing, liked, skipped, onPlay, onSkip, onLike }) {
  const artist  = ARTISTS[result.artist_id] || { name: `Artist ${result.artist_id}`, genre: 'electronic' }
  const color   = GENRE_COLORS[artist.genre] || '#a78bfa'
  const isPlay  = playing === result.artist_id
  const isLiked = liked.has(result.artist_id)
  const isSkip  = skipped.has(result.artist_id)

  return (
    <div style={{
      background: isPlay ? 'var(--surface)' : 'transparent',
      border: `1px solid ${isPlay ? 'var(--border2)' : 'var(--border)'}`,
      borderRadius: 10,
      padding: '14px 16px',
      display: 'flex',
      alignItems: 'center',
      gap: 14,
      transition: 'all 0.15s',
      opacity: isSkip ? 0.35 : 1,
      cursor: 'pointer',
    }}
      onClick={() => !isSkip && onPlay(result.artist_id)}
    >
      {/* Avatar */}
      <div style={{
        width: 42, height: 42, borderRadius: 8, flexShrink: 0,
        background: `${color}20`,
        border: `1px solid ${color}40`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 16, fontWeight: 600, color,
        position: 'relative'
      }}>
        {artist.name[0]}
        {isPlay && (
          <div style={{
            position: 'absolute', bottom: -2, right: -2,
            width: 10, height: 10, borderRadius: '50%',
            background: 'var(--green)',
            border: '2px solid var(--bg)',
            animation: 'pulse 1.5s infinite'
          }}/>
        )}
      </div>

      {/* Info */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontWeight: 500, fontSize: 14,
          color: isPlay ? 'var(--text)' : 'var(--text)',
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
        }}>
          {artist.name}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 2 }}>
          <span style={{
            fontSize: 11, color,
            background: `${color}15`,
            border: `1px solid ${color}30`,
            borderRadius: 3, padding: '1px 6px',
            letterSpacing: '0.04em'
          }}>
            {artist.genre}
          </span>
          <span style={{ fontSize: 11, color: 'var(--muted)' }}>
            #{result.rank}
          </span>
        </div>
      </div>

      {/* Score bar */}
      <div style={{ width: 60, flexShrink: 0 }}>
        <div style={{ height: 2, background: 'var(--border)', borderRadius: 1, marginBottom: 4 }}>
          <div style={{
            height: '100%', borderRadius: 1,
            width: `${result.score * 100}%`,
            background: `linear-gradient(90deg, ${color}80, ${color})`
          }}/>
        </div>
        <div style={{ fontSize: 10, color: 'var(--muted)', textAlign: 'right' }}>
          {(result.score * 100).toFixed(0)}%
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}
           onClick={e => e.stopPropagation()}>
        <ActionBtn
          label="♥"
          active={isLiked}
          activeColor="var(--red)"
          onClick={() => onLike(result.artist_id)}
        />
        <ActionBtn
          label="↷"
          active={isSkip}
          activeColor="var(--muted)"
          onClick={() => onSkip(result.artist_id)}
        />
      </div>
    </div>
  )
}

function ActionBtn({ label, active, activeColor, onClick }) {
  return (
    <button onClick={onClick} style={{
      width: 28, height: 28, borderRadius: 6,
      background: active ? `${activeColor}20` : 'var(--border)',
      border: `1px solid ${active ? activeColor : 'var(--border2)'}`,
      color: active ? activeColor : 'var(--muted)',
      fontSize: 13, display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      transition: 'all 0.15s'
    }}>
      {label}
    </button>
  )
}