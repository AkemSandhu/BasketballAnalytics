import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getAllPlayerSeasons = (limit = 2000, offset = 0) =>
  api.get('/seasons/all', { params: { limit, offset } })