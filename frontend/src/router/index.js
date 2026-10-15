import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import MainLayout from '../layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../views/HomeView.vue'),
        meta: { title: '学习总览' },
      },
      {
        path: 'schedule',
        name: 'schedule',
        component: () => import('../views/ScheduleView.vue'),
        meta: { title: '我的课表' },
      },
      {
        path: 'courses',
        name: 'courses',
        component: () => import('../views/CoursesView.vue'),
        meta: { title: '课程资料' },
      },
      {
        path: 'tasks',
        name: 'tasks',
        component: () => import('../views/TasksView.vue'),
        meta: { title: '作业与考试' },
      },
      {
        path: 'plans',
        name: 'plans',
        component: () => import('../views/PlansView.vue'),
        meta: { title: '学习计划' },
      },
      {
        path: 'chat',
        name: 'chat',
        component: () => import('../views/ChatView.vue'),
        meta: { title: '课程问答' },
      },
      {
        path: 'knowledge',
        name: 'knowledge',
        component: () => import('../views/KnowledgeView.vue'),
        meta: { title: '智能知识库' },
      },
      {
        path: 'admin',
        name: 'admin',
        component: () => import('../views/AdminView.vue'),
        meta: { title: '管理后台', requiresAdmin: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：恢复会话、校验登录状态和管理员权限。
router.beforeEach(async (to) => {
  const { token, user, restoreSession } = useAuth()

  // 有令牌但尚未恢复用户信息（如刷新页面），先恢复会话。
  if (token.value && !user.value) await restoreSession()

  // 已登录却访问登录页，直接进入学习总览。
  if (to.name === 'login' && user.value) return { name: 'home' }

  // 需要登录的页面未登录时跳转登录页。
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  if (requiresAuth && !user.value) return { name: 'login' }

  // 管理后台仅管理员可访问。
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)
  if (requiresAdmin && user.value?.role !== 'admin') return { name: 'home' }

  return true
})

export default router
