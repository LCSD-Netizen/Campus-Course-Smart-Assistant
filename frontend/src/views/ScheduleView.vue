<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useDashboard } from '../composables/useDashboard'
import { useSchedule } from '../composables/useSchedule'

const { dashboard } = useDashboard()
const { weekdays, weekOffset, weekDays, dayCourses } = useSchedule()
</script>

<template>
  <div class="page-heading">
    <div>
      <p class="eyebrow">
        {{ weekDays[0]?.date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' }) }}
        —
        {{ weekDays[6]?.date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' }) }}
      </p>
      <h1>我的课表</h1>
      <p class="subheading">只展示你已选课程的安排。</p>
    </div>
    <div class="week-nav">
      <el-button circle plain @click="weekOffset--"><ChevronLeft :size="16" /></el-button>
      <el-button plain @click="weekOffset = 0">本周</el-button>
      <el-button circle plain @click="weekOffset++"><ChevronRight :size="16" /></el-button>
    </div>
  </div>

  <section class="card wide-card">
    <div class="schedule">
      <div class="schedule-corner"></div>
      <div
        v-for="day in weekDays"
        :key="day.date.toISOString()"
        class="schedule-head"
        :class="{ today: day.selected }"
      >
        {{ day.label }}<b>{{ day.day }}</b>
      </div>

      <template v-for="hour in ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00']" :key="hour">
        <div class="schedule-time">{{ hour }}</div>
        <div
          v-for="day in weekDays"
          :key="`${hour}-${day.label}`"
          class="schedule-cell"
        >
          <div
            v-for="course in dayCourses(weekdays.indexOf(day.label)).filter(
              (c) => parseInt(c.start_time.slice(0, 2)) === parseInt(hour.slice(0, 2)),
            )"
            :key="course.id"
            class="schedule-lesson"
            :class="course.color"
          >
            <b>{{ course.name }}</b>
            <small>{{ course.start_time }}-{{ course.end_time }} · {{ course.room }}</small>
          </div>
        </div>
      </template>
    </div>

    <div class="schedule-legend">
      <span><i class="legend-dot blue"></i>课程时间以教务安排为准</span>
      <span>{{ dashboard.courses.length }} 门已选课程</span>
    </div>
  </section>
</template>
