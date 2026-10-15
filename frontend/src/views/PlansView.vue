<script setup>
import { Check, Sparkles } from 'lucide-vue-next'
import { useDashboard } from '../composables/useDashboard'
import { useChat } from '../composables/useChat'
import { formatDate } from '../utils/format'

const { dashboard } = useDashboard()
const { ask } = useChat()
</script>

<template>
  <div class="page-heading">
    <div>
      <p class="eyebrow">PLAN WITH INTENTION</p>
      <h1>学习计划</h1>
      <p class="subheading">你和 AI 一起整理的学习安排，会保存在这里。</p>
    </div>
    <el-button type="primary" @click="ask('帮我制定并保存本周学习计划')">
      <Sparkles :size="15" /> 让 AI 帮我规划
    </el-button>
  </div>

  <div class="plan-list">
    <article v-for="plan in dashboard.plans" :key="plan.id" class="card plan-row">
      <div class="plan-icon"><Check :size="16" /></div>
      <div>
        <h3>{{ plan.title }}</h3>
        <div class="plan-content">{{ plan.content }}</div>
        <small class="muted">
          创建于 {{ new Date(plan.created_at).toLocaleDateString('zh-CN') }}
          <span v-if="plan.due_date"> · 目标日期 {{ formatDate(plan.due_date) }}</span>
        </small>
      </div>
    </article>

    <div v-if="!dashboard.plans?.length" class="card empty-state plan-empty">
      <span class="ai-spark"><Sparkles /></span>
      <b>还没有保存的学习计划</b>
      <p>告诉助手你的目标，它会帮你生成并保存计划。</p>
      <el-button type="primary" plain @click="ask('帮我制定并保存本周学习计划')">开始规划</el-button>
    </div>
  </div>
</template>
