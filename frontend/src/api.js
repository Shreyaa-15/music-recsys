import axios from 'axios'

const api = axios.create({ baseURL: '' })

export const getRecommendations = (userId, topK = 10) =>
  api.get(`/recommend/${userId}?top_k=${topK}`)

export const sendFeedback = (userId, artistId, event) =>
  api.post('/feedback', { user_id: userId, artist_id: artistId, event })

export const getABTest    = () => api.get('/ab-test')
export const getStats     = () => api.get('/stats')
export const getEmbeddings = () => api.get('/embeddings')