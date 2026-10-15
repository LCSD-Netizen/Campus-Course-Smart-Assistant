<script setup>
import { useRouter } from 'vue-router'
import { Sparkles } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const {
  user,
  loginForm,
  registerMode,
  registerName,
  loginError,
  busy,
  login,
  register,
  toggleAuthMode,
} = useAuth()

// 根据当前模式执行登录或注册，成功后进入学习总览。
async function submit() {
  if (registerMode.value) {
    await register()
  } else {
    await login()
  }

  if (user.value) router.push({ name: 'home' })
}
</script>

<template>
  <div class="login-page">
    <div class="login-art">
      <div class="art-glow"></div>
      <div class="art-brand">
        <span class="brand-mark">知</span>
        <span><b>知课</b><small>CAMPUS COPILOT</small></span>
      </div>
      <div class="art-copy">
        <div class="eyebrow">YOUR CAMPUS, CONNECTED</div>
        <h1>让每一门课，<br />都变得更清晰。</h1>
        <p>课程安排、学习资料与智能问答，<br />一个学习空间，陪你把知识学得更扎实。</p>
        <div class="floating-note">
          <Sparkles :size="16" />
          <span>你的课程 AI 助手已准备就绪</span>
          <i></i>
        </div>
      </div>
      <div class="art-bottom">课程 · 知识 · 计划　　为学习而连接</div>
    </div>

    <div class="login-side">
      <form class="login-form" @submit.prevent="submit">
        <div class="mobile-brand"><span class="brand-mark">知</span><b>知课</b></div>
        <div class="eyebrow">{{ registerMode ? 'CREATE YOUR ACCOUNT' : 'WELCOME BACK' }}</div>
        <h2>{{ registerMode ? '创建学习账户' : '登录你的学习空间' }}</h2>
        <p class="muted">
          {{ registerMode ? '创建账户，开始管理你的校园学习。' : '输入账户信息，继续你的校园学习旅程。' }}
        </p>

        <label v-if="registerMode">
          你的称呼
          <el-input
            v-model="registerName"
            size="large"
            placeholder="例如：林同学"
            autocomplete="name"
          />
        </label>
        <label>
          用户名
          <el-input
            v-model="loginForm.username"
            size="large"
            placeholder="输入用户名"
            autocomplete="username"
          />
        </label>
        <label>
          密码
          <el-input
            v-model="loginForm.password"
            size="large"
            type="password"
            show-password
            :placeholder="registerMode ? '至少 8 位' : '输入密码'"
            autocomplete="current-password"
          />
        </label>

        <div v-if="loginError" class="form-error">{{ loginError }}</div>
        <el-button
          class="login-button"
          type="primary"
          size="large"
          native-type="submit"
          :loading="busy"
        >
          {{ registerMode ? '创建账户' : '登录' }}
        </el-button>

        <div class="auth-switch">
          {{ registerMode ? '已有账户？' : '还没有账户？' }}
          <button type="button" @click="toggleAuthMode">
            {{ registerMode ? '返回登录' : '注册一个账户' }}
          </button>
        </div>
        <div v-if="!registerMode" class="demo-hint">
          <span>演示账户</span>
          <b>学生 demo / demo1234</b>
          <b>管理员 admin / admin1234</b>
        </div>
      </form>
    </div>
  </div>
</template>
