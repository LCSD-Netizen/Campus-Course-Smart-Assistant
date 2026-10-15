import { computed, ref } from 'vue'
import { api, errorMessage } from '../api/client'
import { notify } from './useToast'
import { loadDashboard } from './useDashboard'
import { clearChat } from './useChat'

// 登录信息和账户状态。
const token = ref(localStorage.getItem('campus-token'))
const user = ref(null)
const loginForm = ref({ username: 'demo', password: 'demo1234' })
const registerMode = ref(false)
const registerName = ref('')
const loginError = ref('')
const busy = ref(false)

const firstName = computed(() => user.value?.display_name || '同学')

export function useAuth() {
  // 登录成功后保存令牌并读取学习总览。
  async function login() {
    busy.value = true
    loginError.value = ''

    try {
      const { data } = await api.post('/auth/login', loginForm.value)
      localStorage.setItem('campus-token', data.access_token)
      token.value = data.access_token
      user.value = data.user
      await loadDashboard()
      notify(`欢迎回来，${data.user.display_name}`)
    } catch (error) {
      loginError.value = errorMessage(error)
    } finally {
      busy.value = false
    }
  }

  // 创建账户后自动登录新账户。
  async function register() {
    busy.value = true
    loginError.value = ''

    try {
      const { data } = await api.post('/auth/register', {
        username: loginForm.value.username,
        password: loginForm.value.password,
        display_name: registerName.value || '新同学',
      })
      localStorage.setItem('campus-token', data.access_token)
      token.value = data.access_token
      user.value = data.user
      await loadDashboard()
      notify('账户已创建，欢迎加入知课')
    } catch (error) {
      loginError.value = errorMessage(error)
    } finally {
      busy.value = false
    }
  }

  // 清除本地登录状态；由调用方在需要时跳转到登录页。
  function logout() {
    localStorage.removeItem('campus-token')
    token.value = null
    user.value = null
    loginForm.value = { username: '', password: '' }
    registerName.value = ''
    registerMode.value = false
    loginError.value = ''
    clearChat()
  }

  // 切换登录和注册表单。
  function toggleAuthMode() {
    registerMode.value = !registerMode.value
    loginError.value = ''

    if (registerMode.value) {
      loginForm.value = { username: '', password: '' }
      registerName.value = ''
    }
  }

  // 刷新页面时验证并恢复上一次登录状态。
  async function restoreSession() {
    if (!token.value) return

    try {
      const { data } = await api.get('/auth/me')
      user.value = data
      await loadDashboard()
    } catch {
      logout()
    }
  }

  return {
    token,
    user,
    loginForm,
    registerMode,
    registerName,
    loginError,
    busy,
    firstName,
    login,
    register,
    logout,
    toggleAuthMode,
    restoreSession,
  }
}
