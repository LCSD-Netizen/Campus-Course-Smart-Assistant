<script setup>
import { useRouter } from 'vue-router'
import {
  ArrowUp,
  BookOpen,
  CalendarDays,
  Check,
  ClipboardList,
  Clock3,
  LibraryBig,
  Sparkles,
} from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'
import { useDashboard } from '../composables/useDashboard'
import { useSchedule } from '../composables/useSchedule'
import { useChat } from '../composables/useChat'
import { formatDate } from '../utils/format'

const router = useRouter()
const { firstName } = useAuth()
const { dashboard, toggleTask } = useDashboard()
const { weekDays, selectedDate, dayCourses } = useSchedule()
const { chatInput, sendMessage, ask } = useChat()

function navigate(name) {
  router.push({ name })
}
</script>

<template>
  <div class="page-heading">
    <div>
      <p class="eyebrow">
        {{ new Date().toLocaleDateString('zh-CN', { weekday: 'long', month: 'long', day: 'numeric' }) }}
      </p>
      <h1>早上好，{{ firstName }} <span class="wave">👋</span></h1>
      <p class="subheading">新的一天，继续保持学习节奏。</p>
    </div>
    <el-button class="date-chip" plain>
      <CalendarDays :size="15" /> {{ new Date().getFullYear() }} 学年 · 秋季学期
    </el-button>
  </div>

  <div class="stats-grid">
    <div class="card stat-card">
      <div class="stat-top">本学期课程<span class="stat-icon lilac"><BookOpen :size="16" /></span></div>
      <div class="stat-value">{{ dashboard.stats.courses || 0 }}<small> 门</small></div>
      <div class="stat-foot">课程表已同步</div>
    </div>
    <div class="card stat-card">
      <div class="stat-top">待完成任务<span class="stat-icon amber"><Clock3 :size="16" /></span></div>
      <div class="stat-value">{{ dashboard.stats.pending_tasks || 0 }}<small> 项</small></div>
      <div class="stat-foot">安排好截止时间</div>
    </div>
    <div class="card stat-card">
      <div class="stat-top">学习计划<span class="stat-icon mint"><Check :size="16" /></span></div>
      <div class="stat-value">{{ dashboard.plans?.length || 0 }}<small> 份</small></div>
      <div class="stat-foot">由你和 AI 共同整理</div>
    </div>
    <div class="card stat-card">
      <div class="stat-top">课程资料<span class="stat-icon sky"><LibraryBig :size="16" /></span></div>
      <div class="stat-value">{{ dashboard.stats.documents || 0 }}<small> 份</small></div>
      <div class="stat-foot">检索增强问答已就绪</div>
    </div>
  </div>

  <div class="dashboard-grid">
    <div>
      <section class="card section-card">
        <div class="section-head">
          <div><h2>本周课程</h2><small>按时间顺序安排好你的学习</small></div>
          <button class="text-link" @click="navigate('schedule')">完整课表　→</button>
        </div>
        <div class="week-strip">
          <button
            v-for="day in weekDays"
            :key="day.date.toISOString()"
            class="week-day"
            :class="{ selected: day.selected }"
            @click="selectedDate = day.date"
          >
            <span>{{ day.label }}</span>
            <b>{{ day.day }}</b>
          </button>
        </div>
        <div
          v-if="dayCourses((selectedDate.getDay() + 6) % 7).length"
          class="lesson-list"
        >
          <div
            v-for="course in dayCourses((selectedDate.getDay() + 6) % 7)"
            :key="course.id"
            class="lesson"
          >
            <div class="lesson-time">{{ course.start_time }}<small>{{ course.end_time }}</small></div>
            <div class="lesson-bar" :class="course.color"></div>
            <div>
              <div class="lesson-name">{{ course.name }}</div>
              <div class="lesson-meta">{{ course.teacher }} · {{ course.room }}</div>
            </div>
            <span class="status-pill">{{ course.weeks }}</span>
          </div>
        </div>
        <div v-else class="empty-state">今天没有排课，给自己留一些自由学习时间。</div>
      </section>

      <section class="card section-card upcoming-card">
        <div class="section-head">
          <div><h2>近期任务</h2><small>记得按时完成哦</small></div>
          <button class="text-link" @click="navigate('tasks')">查看全部　→</button>
        </div>
        <div v-for="task in dashboard.tasks.slice(0, 3)" :key="task.id" class="task-row">
          <button
            class="task-check"
            :class="{ checked: task.completed }"
            @click="toggleTask(task)"
          >
            <Check :size="12" />
          </button>
          <div class="task-info">
            <b>{{ task.title }}</b>
            <small>{{ task.course_name }} · {{ task.kind }}</small>
          </div>
          <div class="task-due">
            {{ task.days_left < 0 ? '已逾期' : task.days_left === 0 ? '今天截止' : `${task.days_left} 天后` }}
            <small>{{ formatDate(task.due_date) }}</small>
          </div>
        </div>
        <div v-if="!dashboard.tasks.length" class="empty-state compact">还没有任务，保持轻松。</div>
      </section>
    </div>

    <div>
      <section class="card ai-card">
        <div class="ai-top">
          <span class="ai-spark"><Sparkles :size="16" /></span>
          <b>知课 AI 助手</b>
          <span class="online">在线</span>
        </div>
        <h3>今天想学点什么？</h3>
        <p>我可以帮你查课表、解答课程问题，或整理一份学习计划。</p>
        <div class="prompt-chips">
          <button class="prompt-chip" @click="ask('这周我的课表是什么？')">✦　这周我的课表是什么？</button>
          <button class="prompt-chip" @click="ask('帮我总结数据结构课程重点')">▧　帮我总结课程重点</button>
          <button class="prompt-chip" @click="ask('帮我制定并保存本周学习计划')">◷　制定本周学习计划</button>
        </div>
        <form class="chat-entry" @submit.prevent="sendMessage()">
          <input v-model="chatInput" placeholder="问问你的课程..." />
          <button class="send-btn"><ArrowUp :size="15" /></button>
        </form>
      </section>

      <section class="card quick-card">
        <div class="section-head"><h2>快捷入口</h2></div>
        <div class="quick-links">
          <button class="quick-link" @click="navigate('courses')"><BookOpen />课程资料</button>
          <button class="quick-link" @click="navigate('tasks')"><ClipboardList />待办任务</button>
          <button class="quick-link" @click="navigate('schedule')"><CalendarDays />查看课表</button>
          <button class="quick-link" @click="navigate('knowledge')"><LibraryBig />智能知识库</button>
        </div>
      </section>
    </div>
  </div>
</template>
