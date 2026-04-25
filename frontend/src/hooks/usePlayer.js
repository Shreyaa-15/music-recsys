import { useState, useCallback } from 'react'
import { sendFeedback } from '../api'

export function usePlayer(userId) {
  const [playing, setPlaying]   = useState(null)
  const [liked, setLiked]       = useState(new Set())
  const [skipped, setSkipped]   = useState(new Set())

  const play = useCallback((artistId) => {
    setPlaying(artistId)
    sendFeedback(userId, artistId, 'click').catch(() => {})
  }, [userId])

  const skip = useCallback((artistId) => {
    setPlaying(null)
    setSkipped(s => new Set([...s, artistId]))
    sendFeedback(userId, artistId, 'skip').catch(() => {})
  }, [userId])

  const like = useCallback((artistId) => {
    setLiked(s => new Set([...s, artistId]))
    sendFeedback(userId, artistId, 'like').catch(() => {})
  }, [userId])

  return { playing, liked, skipped, play, skip, like }
}