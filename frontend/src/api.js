import axios from 'axios'

export const api = axios.create({ baseURL: '/api', timeout: 30000 })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('campus-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use((response) => response, (error) => {
  if (error.response?.status === 401) localStorage.removeItem('campus-token')
  return Promise.reject(error)
})
export const errorMessage = (error) => error.response?.data?.detail || error.message || '请求失败，请稍后重试'
