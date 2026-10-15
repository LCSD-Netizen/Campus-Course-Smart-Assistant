<script setup>
import { useRoute, useRouter } from 'vue-router'
import { Bell, LogOut, Search } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const router = useRouter()
const { logout } = useAuth()

function handleLogout() {
  logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="topbar">
    <div class="breadcrumb">学习空间 <span>/</span> <b>{{ route.meta.title }}</b></div>
    <div class="top-actions">
      <button
        class="icon-btn"
        title="搜索课程"
        @click="router.push({ name: 'courses' })"
      >
        <Search :size="19" />
      </button>
      <button
        class="icon-btn notification"
        title="通知"
        @click="router.push({ name: 'tasks' })"
      >
        <Bell :size="18" />
        <i></i>
      </button>
      <button class="account-exit" title="退出当前账号并切换登录" @click="handleLogout">
        <LogOut :size="14" />
        <span>退出</span>
      </button>
    </div>
  </header>
</template>
