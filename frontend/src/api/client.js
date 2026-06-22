import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// ---------- General ----------
export const getAllPlayerSeasons = (limit = 2000, offset = 0) =>
  api.get('/seasons/all', { params: { limit, offset } })

// ---------- Players ----------
export const getPlayers = (skip = 0, limit = 100, search = '') =>
  api.get('/players/', { params: { skip, limit, search } })

export const getPlayer = (playerId) =>
  api.get(`/players/${playerId}`)

export const getPlayerSeasons = (playerId, skip = 0, limit = 100) =>
  api.get(`/players/${playerId}/seasons`, { params: { skip, limit } })

export const getPlayerSeason = (playerId, seasonId) =>
  api.get(`/players/${playerId}/seasons/${seasonId}`)

// ---------- Seasons ----------
export const getSeasons = (skip = 0, limit = 100) =>
  api.get('/seasons/', { params: { skip, limit } })

export const getSeason = (seasonId) =>
  api.get(`/seasons/${seasonId}`)

export const getPlayerSeasonsBySeason = (seasonId, limit = 100, offset = 0) =>
  api.get(`/seasons/${seasonId}/player-seasons`, { params: { limit, offset } })

export const getLeaderboard = (seasonId, stat = 'impact_score', n = 20) =>
  api.get(`/seasons/${seasonId}/leaders`, { params: { stat, n } })

// ---------- Stats ----------
export const getRadarData = (playerId, seasonId) =>
  api.get(`/stats/player/${playerId}/radar/${seasonId}`)

export const getTimeline = (playerId) =>
  api.get(`/stats/player/${playerId}/timeline`)

export const getSimilar = (playerId, seasonId) =>
  api.get(`/stats/similar/${playerId}/${seasonId}`)

export default api