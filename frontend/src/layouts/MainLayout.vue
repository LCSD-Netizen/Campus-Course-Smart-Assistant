<script setup>
import { useAuth } from '../composables/useAuth'
import AppSidebar from '../components/AppSidebar.vue'
import AppTopbar from '../components/AppTopbar.vue'

// 用户信息为空时不渲染主界面，避免退出登录跳转瞬间访问空对象。
const { user } = useAuth()
</script>

<template>
  <div v-if="user" class="app-shell">
    <AppSidebar />
    <main class="main-area">
      <AppTopbar />
      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>
