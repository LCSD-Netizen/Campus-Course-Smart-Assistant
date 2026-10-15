<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search } from 'lucide-vue-next'
import { useDashboard } from '../composables/useDashboard'
import { useSchedule } from '../composables/useSchedule'

const router = useRouter()
const { dashboard } = useDashboard()
const { weekdays } = useSchedule()

const courseSearch = ref('')

// 根据搜索关键字过滤已选课程。
const visibleCourses = computed(() =>
  dashboard.value.courses.filter((course) =>
    course.name.includes(courseSearch.value),
  ),
)
</script>

<template>
  <div class="page-heading">
    <div>
      <p class="eyebrow">COURSE SPACE</p>
      <h1>课程资料</h1>
      <p class="subheading">整理课程内容，快速回到你的学习现场。</p>
    </div>
    <el-button type="primary" @click="router.push({ name: 'knowledge' })">
      <Plus :size="15" /> 添加资料
    </el-button>
  </div>

  <section class="card wide-card">
    <div class="toolbar">
      <label class="search-field">
        <Search :size="15" />
        <input v-model="courseSearch" placeholder="搜索课程名称、教师..." />
      </label>
      <span class="muted small">{{ visibleCourses.length }} 门课程</span>
    </div>

    <div class="course-grid">
      <article
        v-for="(course, index) in visibleCourses"
        :key="course.id"
        class="course-card"
        @click="router.push({ name: 'knowledge' })"
      >
        <div class="course-cover" :class="course.color">
          <span>{{ ['⌘', '⌁', '◉', '▤', '⌬', '文'][index % 6] }}</span>
          <small>{{ course.credits }} 学分</small>
        </div>
        <h3>{{ course.name }}</h3>
        <p>{{ course.teacher }} · {{ course.room }}</p>
        <div class="course-progress">
          <span>{{ weekdays[course.weekday - 1] }} {{ course.start_time }}</span>
          <span>{{ course.weeks }}</span>
        </div>
      </article>
      <div v-if="!visibleCourses.length" class="empty-state">还没有课程安排。</div>
    </div>
  </section>
</template>
