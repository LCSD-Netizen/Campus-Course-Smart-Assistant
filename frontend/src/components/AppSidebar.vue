<script setup>
import { useRoute, useRouter } from 'vue-router'
import {
  BookOpen,
  CalendarDays,
  Check,
  ClipboardList,
  LayoutDashboard,
  LibraryBig,
  LogOut,
  MessageCircle,
  Settings,
  Sparkles,
  Users,
} from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'
import { useDashboard } from '../composables/useDashboard'
import { notify } from '../composables/useToast'

const route = useRoute()
const router = useRouter()
const { user, firstName, logout } = useAuth()
const { dashboard } = useDashboard()

// 学习空间导航项，id 与路由 name 保持一致。
const studyNavItems = [
  { id: 'home', label: '学习总览', icon: LayoutDashboard },
  { id: 'schedule', label: '我的课表', icon: CalendarDays },
  { id: 'courses', label: '课程资料', icon: BookOpen },
  { id: 'tasks', label: '作业与考试', icon: ClipboardList },
  { id: 'plans', label: '学习计划', icon: Check },
]

function navigate(name) {
  router.push({ name })
}

function handleLogout() {
  logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <aside class="sidebar">
    <a class="brand" href="#" @click.prevent="navigate('home')">
      <span class="brand-mark">知</span>
      <span><b>知课</b><small>CAMPUS COPILOT</small></span>
    </a>

    <div class="workspace-label">工作空间 <span>⌄</span></div>
    <div class="workspace">
      <div class="avatar avatar-blue">{{ firstName.slice(0, 1) }}</div>
      <span>
        <b>{{ firstName }}</b>
        <small>{{ user.department || '计算机科学与技术' }}</small>
      </span>
      <span class="role-badge">{{ user.role === 'admin' ? '管理员' : '学生' }}</span>
    </div>

    <div class="nav-label">学习空间</div>
    <nav class="nav-list">
      <button
        v-for="item in studyNavItems"
        :key="item.id"
        class="nav-item"
        :class="{ active: route.name === item.id }"
        @click="navigate(item.id)"
      >
        <component :is="item.icon" :size="17" />
        <span>{{ item.label }}</span>
        <span
          v-if="item.id === 'tasks' && dashboard.stats.pending_tasks"
          class="nav-count"
        >
          {{ dashboard.stats.pending_tasks }}
        </span>
      </button>
    </nav>

    <div class="nav-label assistant-label">智能助手</div>
    <nav class="nav-list">
      <button
        class="nav-item"
        :class="{ active: route.name === 'chat' }"
        @click="navigate('chat')"
      >
        <MessageCircle :size="17" />
        <span>课程问答</span>
      </button>
      <button
        class="nav-item"
        :class="{ active: route.name === 'knowledge' }"
        @click="navigate('knowledge')"
      >
        <LibraryBig :size="17" />
        <span>知识库</span>
      </button>
      <button
        v-if="user.role === 'admin'"
        class="nav-item"
        :class="{ active: route.name === 'admin' }"
        @click="navigate('admin')"
      >
        <Users :size="17" />
        <span>管理后台</span>
      </button>
    </nav>

    <div class="sidebar-bottom">
      <div class="plan-card">
        <div class="plan-icon"><Sparkles :size="15" /></div>
        <b>让学习更进一步</b>
        <p>连接课程资料，获得专属 AI 学习伙伴。</p>
        <button @click="navigate('knowledge')">管理智能知识库 <span>→</span></button>
      </div>
      <button class="nav-item settings" @click="notify('账户设置即将开放')">
        <Settings :size="16" />
        <span>设置</span>
      </button>
      <div class="sidebar-user">
        <div class="avatar avatar-green">{{ firstName.slice(0, 1) }}</div>
        <span><b>{{ firstName }}</b><small>{{ user.username }}</small></span>
        <button title="退出登录" class="logout" @click="handleLogout"><LogOut :size="15" /></button>
      </div>
    </div>
  </aside>
</template>
