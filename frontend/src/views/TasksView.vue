<script setup>
import { Check, Plus } from 'lucide-vue-next'
import { useDashboard } from '../composables/useDashboard'
import TaskDialog from '../components/TaskDialog.vue'
import { formatDate } from '../utils/format'

const { dashboard, taskDialog, toggleTask } = useDashboard()
</script>

<template>
  <div class="page-heading">
    <div>
      <p class="eyebrow">KEEP YOUR LEARNING ON TRACK</p>
      <h1>作业与考试</h1>
      <p class="subheading">所有截止日期都在这里，安排好你的学习计划。</p>
    </div>
    <el-button type="primary" @click="taskDialog = true">
      <Plus :size="15" /> 添加任务
    </el-button>
  </div>

  <div class="task-cards">
    <div class="card task-summary">
      <span>全部任务</span>
      <strong>{{ dashboard.tasks.length }}</strong>
      <small>个人课程任务</small>
    </div>
    <div class="card task-summary">
      <span>待完成</span>
      <strong>{{ dashboard.tasks.filter((t) => !t.completed).length }}</strong>
      <small>记得按时完成</small>
    </div>
    <div class="card task-summary">
      <span>本周截止</span>
      <strong>
        {{ dashboard.tasks.filter((t) => !t.completed && t.days_left >= 0 && t.days_left <= 7).length }}
      </strong>
      <small>最近任务优先处理</small>
    </div>
  </div>

  <section class="card wide-card task-table">
    <div class="section-head">
      <div><h2>近期任务</h2><small>按截止时间排序</small></div>
    </div>

    <div v-for="task in dashboard.tasks" :key="task.id" class="task-list-row">
      <button
        class="task-check"
        :class="{ checked: task.completed }"
        @click="toggleTask(task)"
      >
        <Check :size="12" />
      </button>
      <div class="task-date">
        <b>{{ formatDate(task.due_date).slice(-2) }}</b>
        {{ formatDate(task.due_date).slice(0, 2) }}月
      </div>
      <div class="task-main">
        <b :class="{ strikethrough: task.completed }">{{ task.title }}</b>
        <small>{{ task.course_name }} · 截止 {{ formatDate(task.due_date) }}</small>
      </div>
      <span class="task-kind">{{ task.kind }}</span>
      <span class="status-pill" :class="task.completed ? 'done' : ''">
        {{ task.completed ? '已完成' : task.days_left < 0 ? '已逾期' : task.days_left === 0 ? '今天截止' : `${task.days_left} 天后` }}
      </span>
    </div>
    <div v-if="!dashboard.tasks.length" class="empty-state">暂时没有任务安排。添加一项试试。</div>
  </section>

  <TaskDialog />
</template>
