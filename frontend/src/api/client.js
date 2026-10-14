import axios from 'axios'

// 统一配置业务 API 地址和请求超时。
export const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 每次请求自动附带当前登录令牌。
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('campus-token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

// 令牌失效时清除本地状态，由页面引导用户重新登录。
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('campus-token')
    }

    return Promise.reject(error)
  },
)

// 将后端错误信息转换为可以直接展示给用户的文字。
export const errorMessage = (error) =>
  error.response?.data?.detail || error.message || '请求失败，请稍后重试'
